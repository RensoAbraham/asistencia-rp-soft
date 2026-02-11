import aiomysql
import asyncio
import os
import sys
from dotenv import load_dotenv
import ssl
import logging

# --- PARCHE PARA WINDOWS ---
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# ---------------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

# Configuración TiDB Cloud (ORIGEN)
TIDB_CONFIG = {
    "host": "gateway01.us-east-1.prod.aws.tidbcloud.com",
    "port": 4000,
    "user": "4H85vqbbpvRhXiZ.root",
    "password": "vrVL3o5ytoXF0wa9",
    "db": "asistencia_db", # CORREGIDO: En tu .env dice 'asistencia_db'
    "ssl": ssl.create_default_context(cafile="isrgrootx1.pem")
}

# Configuración MySQL VPS (DESTINO)
MYSQL_CONFIG = {
    "host": "178.156.246.18",  # IP de tu Hetzner
    "port": 3306,
    "user": "bot_user",
    "password": "7tKJvtOffvMh6tussfZ7powXDOpCm543ZIw45k", # Asegúrate de que esta sea la que pusiste en el .env del VPS
    "db": "asistencia_rp_soft"
}

async def get_tidb_connection():
    """Conectar a TiDB Cloud"""
    try:
        conn = await aiomysql.connect(**TIDB_CONFIG)
        logging.info("✅ Conectado a TiDB Cloud")
        return conn
    except Exception as e:
        logging.error(f"❌ Error conectando a TiDB: {e}")
        logging.error("Pista: Revisa si tu IP está en el Whitelist de TiDB Cloud Console.")
        raise

async def get_mysql_connection():
    """Conectar a MySQL en VPS"""
    config = MYSQL_CONFIG.copy()
    config.pop('ssl', None)
    try:
        conn = await aiomysql.connect(**config)
        logging.info("✅ Conectado a MySQL en el VPS")
        return conn
    except Exception as e:
        logging.error(f"❌ Error conectando al VPS: {e}")
        logging.error("Pista: ¿Ejecutaste 'sudo ufw allow 3306/tcp' en el VPS?")
        raise

async def export_table_data(tidb_conn, table_name):
    """Exportar datos de una tabla desde TiDB"""
    async with tidb_conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(f"SELECT * FROM {table_name}")
        rows = await cursor.fetchall()
        logging.info(f"📊 {table_name}: {len(rows)} registros exportados.")
        return rows

async def import_table_data(mysql_conn, table_name, rows):
    """Importar datos a MySQL Local"""
    if not rows:
        return
    
    async with mysql_conn.cursor() as cursor:
        columns = list(rows[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        await cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        for row in rows:
            values = [row[col] for col in columns]
            try:
                await cursor.execute(query, values)
            except Exception as e:
                logging.warning(f"⚠️ Error en {table_name}: {e}")
        
        await cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        await mysql_conn.commit()
        logging.info(f"✅ {table_name}: Registros importados.")

async def migrate_data():
    """Migrar todos los datos"""
    logging.info("🚀 Iniciando migración de datos...")
    
    tidb_conn = None
    mysql_conn = None
    
    try:
        tidb_conn = await get_tidb_connection()
        mysql_conn = await get_mysql_connection()
        
        # Estas tablas se migran en orden por las llaves foráneas
        tables = [
            'estado_asistencia',
            'practicante',
            'asistencia',
            'asistencia_recuperacion',
            'reportes_enviados'
        ]
        
        for table in tables:
            logging.info(f"\n📦 Procesando: {table}")
            rows = await export_table_data(tidb_conn, table)
            
            async with mysql_conn.cursor() as cursor:
                await cursor.execute(f"DELETE FROM {table}")
                await mysql_conn.commit()
            
            await import_table_data(mysql_conn, table, rows)
        
        logging.info("\n✅ ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        
    except Exception as e:
        logging.error(f"❌ Error crítico en la migración: {e}")
    finally:
        if tidb_conn: tidb_conn.close()
        if mysql_conn: mysql_conn.close()

if __name__ == "__main__":
    print("\n¿Deseas iniciar la migración? (s/n): ")
    if input().lower() == 's':
        asyncio.run(migrate_data())
    else:
        print("❌ Operación cancelada.")
