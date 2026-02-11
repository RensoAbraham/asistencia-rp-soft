"""
Script para migrar datos de TiDB Cloud a MySQL local
Exporta datos de TiDB y los importa directamente a MySQL en el VPS
"""

import aiomysql
import asyncio
import os
from dotenv import load_dotenv
import ssl
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

# Configuración TiDB Cloud (ORIGEN)
TIDB_CONFIG = {
    "host": "gateway01.us-east-1.prod.aws.tidbcloud.com",
    "port": 4000,
    "user": "4H85vqbbpvRhXiZ.root",
    "password": "vrVL3o5ytoXF0wa9",
    "db": "asistencia_db",
    "ssl": ssl.create_default_context(cafile="isrgrootx1.pem")
}

# Configuración MySQL Local (DESTINO)
# Cambiar estos valores según tu configuración del VPS
MYSQL_CONFIG = {
    "host": "localhost",  # O la IP del VPS si lo ejecutas desde tu PC
    "port": 3306,
    "user": "bot_user",
    "password": "tu_contraseña_mysql",  # CAMBIAR ESTO
    "db": "asistencia_rp_soft"
}

async def get_tidb_connection():
    """Conectar a TiDB Cloud"""
    conn = await aiomysql.connect(**TIDB_CONFIG)
    logging.info("✅ Conectado a TiDB Cloud")
    return conn

async def get_mysql_connection():
    """Conectar a MySQL Local"""
    config = MYSQL_CONFIG.copy()
    config.pop('ssl', None)  # MySQL local no usa SSL
    conn = await aiomysql.connect(**config)
    logging.info("✅ Conectado a MySQL Local")
    return conn

async def export_table_data(tidb_conn, table_name):
    """Exportar datos de una tabla desde TiDB"""
    async with tidb_conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(f"SELECT * FROM {table_name}")
        rows = await cursor.fetchall()
        logging.info(f"📊 Exportados {len(rows)} registros de {table_name}")
        return rows

async def import_table_data(mysql_conn, table_name, rows):
    """Importar datos a MySQL Local"""
    if not rows:
        logging.info(f"⏭️  {table_name}: Sin datos para importar")
        return
    
    async with mysql_conn.cursor() as cursor:
        # Obtener nombres de columnas
        columns = list(rows[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        
        # Preparar query de inserción
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        # Insertar datos
        for row in rows:
            values = [row[col] for col in columns]
            try:
                await cursor.execute(query, values)
            except Exception as e:
                logging.warning(f"⚠️  Error insertando en {table_name}: {e}")
                continue
        
        await mysql_conn.commit()
        logging.info(f"✅ Importados {len(rows)} registros a {table_name}")

async def migrate_data():
    """Migrar todos los datos de TiDB a MySQL"""
    logging.info("🚀 Iniciando migración de datos...")
    
    # Conectar a ambas bases de datos
    tidb_conn = await get_tidb_connection()
    mysql_conn = await get_mysql_connection()
    
    try:
        # Lista de tablas a migrar (en orden por dependencias)
        tables = [
            'estado_asistencia',  # Primero (no tiene dependencias)
            'practicante',        # Segundo
            'asistencia',         # Tercero (depende de practicante y estado_asistencia)
            'asistencia_recuperacion',  # Cuarto (depende de practicante)
            'reportes_enviados'   # Último
        ]
        
        for table in tables:
            logging.info(f"\n📦 Procesando tabla: {table}")
            
            # Exportar de TiDB
            rows = await export_table_data(tidb_conn, table)
            
            # Limpiar tabla en MySQL (opcional, comentar si no quieres borrar)
            async with mysql_conn.cursor() as cursor:
                await cursor.execute(f"DELETE FROM {table}")
                await mysql_conn.commit()
                logging.info(f"🧹 Tabla {table} limpiada")
            
            # Importar a MySQL
            await import_table_data(mysql_conn, table, rows)
        
        logging.info("\n✅ ¡Migración completada exitosamente!")
        
        # Mostrar resumen
        logging.info("\n📊 Resumen de registros migrados:")
        for table in tables:
            async with mysql_conn.cursor() as cursor:
                await cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                result = await cursor.fetchone()
                logging.info(f"  - {table}: {result[0]} registros")
    
    except Exception as e:
        logging.error(f"❌ Error durante la migración: {e}")
        raise
    
    finally:
        tidb_conn.close()
        mysql_conn.close()
        logging.info("\n🔌 Conexiones cerradas")

async def verify_migration():
    """Verificar que la migración fue exitosa"""
    logging.info("\n🔍 Verificando migración...")
    
    tidb_conn = await get_tidb_connection()
    mysql_conn = await get_mysql_connection()
    
    try:
        tables = ['estado_asistencia', 'practicante', 'asistencia', 'asistencia_recuperacion', 'reportes_enviados']
        
        for table in tables:
            # Contar en TiDB
            async with tidb_conn.cursor() as cursor:
                await cursor.execute(f"SELECT COUNT(*) FROM {table}")
                tidb_count = (await cursor.fetchone())[0]
            
            # Contar en MySQL
            async with mysql_conn.cursor() as cursor:
                await cursor.execute(f"SELECT COUNT(*) FROM {table}")
                mysql_count = (await cursor.fetchone())[0]
            
            status = "✅" if tidb_count == mysql_count else "❌"
            logging.info(f"{status} {table}: TiDB={tidb_count}, MySQL={mysql_count}")
    
    finally:
        tidb_conn.close()
        mysql_conn.close()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║  🔄 Migración de Datos: TiDB Cloud → MySQL Local            ║
╚══════════════════════════════════════════════════════════════╝

⚠️  IMPORTANTE:
1. Asegúrate de que MySQL local está corriendo
2. La base de datos 'asistencia_rp_soft' debe existir
3. Las tablas deben estar creadas (el bot las crea automáticamente)
4. Cambia MYSQL_CONFIG con tus credenciales

¿Continuar? (s/n): """)
    
    respuesta = input().lower()
    
    if respuesta == 's':
        # Ejecutar migración
        asyncio.run(migrate_data())
        
        # Verificar
        print("\n¿Verificar migración? (s/n): ")
        if input().lower() == 's':
            asyncio.run(verify_migration())
    else:
        print("❌ Migración cancelada")
