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

# Configuración TiDB Cloud (ORIGEN - Tomada del .env local)
TIDB_CONFIG = {
    "host": "gateway01.us-east-1.prod.aws.tidbcloud.com",
    "port": 4000,
    "user": "4H85vqbbpvRhXiZ.root",
    "password": "vrVL3o5ytoXF0wa9",
    "db": "asistencia_db",
    "ssl": ssl.create_default_context(cafile="isrgrootx1.pem")
}

# Configuración MySQL VPS (DESTINO)
# ¡REEMPLAZA CON LA IP DE TU VPS!
MYSQL_CONFIG = {
    "host": "TU_IP_DEL_VPS", 
    "port": 3306,
    "user": "bot_user",
    "password": "BotPassword2024!Segura", 
    "db": "asistencia_rp_soft"
}

async def get_tidb_connection():
    """Conectar a TiDB Cloud"""
    conn = await aiomysql.connect(**TIDB_CONFIG)
    logging.info("✅ Conectado a TiDB Cloud")
    return conn

async def get_mysql_connection():
    """Conectar a MySQL del VPS"""
    conn = await aiomysql.connect(**MYSQL_CONFIG)
    logging.info("✅ Conectado a MySQL en el VPS")
    return conn

async def export_table_data(tidb_conn, table_name):
    """Exportar datos de una tabla desde TiDB"""
    async with tidb_conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(f"SELECT * FROM {table_name}")
        rows = await cursor.fetchall()
        logging.info(f"📊 {table_name}: {len(rows)} registros encontrados.")
        return rows

async def import_table_data(mysql_conn, table_name, rows):
    """Importar datos a MySQL VPS"""
    if not rows:
        logging.info(f"⏭️  {table_name}: Sin datos.")
        return
    
    async with mysql_conn.cursor() as cursor:
        columns = list(rows[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        # Desactivar chequeo de llaves foráneas temporalmente para evitar errores al insertar
        await cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        
        for row in rows:
            values = [row[col] for col in columns]
            try:
                await cursor.execute(query, values)
            except Exception as e:
                logging.warning(f"⚠️  {table_name}: Error en registro: {e}")
        
        await cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        await mysql_conn.commit()
        logging.info(f"✅ {table_name}: Importados {len(rows)} registros.")

async def migrate_data():
    """Migrar todos los datos"""
    logging.info("🚀 Iniciando migración de datos...")
    
    try:
        tidb_conn = await get_tidb_connection()
        mysql_conn = await get_mysql_connection()
        
        # Orden específico para mantener integridad
        tables = [
            'estado_asistencia',
            'practicante',
            'asistencia',
            'asistencia_recuperacion',
            'reportes_enviados'
        ]
        
        for table in tables:
            logging.info(f"\n📦 Migrando: {table}")
            rows = await export_table_data(tidb_conn, table)
            
            # Limpiar tabla en destino antes de insertar
            async with mysql_conn.cursor() as cursor:
                await cursor.execute(f"DELETE FROM {table}")
                await mysql_conn.commit()
            
            await import_table_data(mysql_conn, table, rows)
        
        logging.info("\n✅ ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        
    except Exception as e:
        logging.error(f"❌ Error durante la migración: {e}")
    finally:
        if 'tidb_conn' in locals(): tidb_conn.close()
        if 'mysql_conn' in locals(): mysql_conn.close()

if __name__ == "__main__":
    print("\n⚠️  ADVERTENCIA: Esto borrará los datos actuales en el VPS e importará los de TiDB.")
    confirm = input("¿Estás seguro de que quieres continuar? (s/n): ")
    if confirm.lower() == 's':
        asyncio.run(migrate_data())
    else:
        print("Operación cancelada.")
