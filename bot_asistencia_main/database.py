import os
import aiomysql
import ssl
from dotenv import load_dotenv
from typing import Optional, Union, Tuple, Dict, Any, List
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

# Evitar import circular si es posible, pero mantenemos si es necesario o eliminamos si no se usa
# import database as db  <-- Esto parece redundante si estams en database.py, lo comento.

load_dotenv()

def get_ssl_context():
    if os.getenv("DB_USE_SSL") == "True":
        ctx = ssl.create_default_context(cafile=os.getenv("SSL_CA_PATH", "isrgrootx1.pem"))
        # TiDB Cloud requiere SSL pero a veces hay temas de compatibilidad con check_hostname
        # Ajustamos según sea necesario. Para la mayoría de nubes, esto es suficiente.
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_REQUIRED
        return ctx
    return None

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "db": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306)), # MySQL usa 3306, TiDB usa 4000
    "autocommit": False,
    "ssl": get_ssl_context()
}

# Pool de conexiones global
_pool: Optional[aiomysql.Pool] = None

# Inicializar el pool de conexiones
async def init_db_pool(minsize: int = 1, maxsize: int = 10) -> aiomysql.Pool:
    global _pool
    if _pool is None:
        _pool = await aiomysql.create_pool(minsize=minsize, maxsize=maxsize, **DB_CONFIG)
    return _pool

# Cerrar el pool de conexiones
async def close_db_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        await _pool.wait_closed()
        _pool = None

# Context manager para obtener una conexión del pool
@asynccontextmanager
async def get_connection() -> AsyncIterator[aiomysql.Connection]:
    pool = await init_db_pool()
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        pool.release(conn)

# Funciones para ejecutar consultas
async def fetch_one(query: str, params: Optional[Union[Tuple, Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        try:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchone()
        except aiomysql.Error as e:
            raise RuntimeError(f"Error ejecutando fetch_one: {e}") from e

async def fetch_all(query: str, params: Optional[Union[Tuple, Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    async with get_connection() as conn:
        try:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                return list(await cursor.fetchall())
        except aiomysql.Error as e:
            raise RuntimeError(f"Error ejecutando fetch_all: {e}") from e

async def execute_query(query: str, params: Optional[Union[Tuple, Dict[str, Any]]] = None) -> int:
    async with get_connection() as conn:
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                await conn.commit()
                return cursor.lastrowid or 0
        except aiomysql.Error as e:
            await conn.rollback()
            raise RuntimeError(f"Error ejecutando execute_query: {e}") from e

async def ensure_db_setup():
    """Verifica y crea las tablas necesarias y datos iniciales."""
    import logging
    logging.info("Verificando integridad de la base de datos...")
    
    # 1. Tabla practicante (Esquema Simplificado: Solo ID, Nombre Completo, Horas Base)
    # Nota: Eliminamos correo, semestre, estado, is_active, apellido.
    await execute_query("""
    CREATE TABLE IF NOT EXISTS practicante (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_discord BIGINT NOT NULL UNIQUE,
        nombre_completo VARCHAR(255) NOT NULL,
        horas_base TIME DEFAULT '00:00:00'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # 2. Tabla estado_asistencia
    await execute_query("""
    CREATE TABLE IF NOT EXISTS estado_asistencia (
        id INT AUTO_INCREMENT PRIMARY KEY,
        estado VARCHAR(50) NOT NULL UNIQUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # 3. Insertar estados base
    for estado in ['Presente', 'Tardanza', 'Falta Injustificada', 'Falta Recuperada', 'Permiso']:
        await execute_query("INSERT IGNORE INTO estado_asistencia (estado) VALUES (%s)", (estado,))

    # 4. Tabla asistencia
    await execute_query("""
    CREATE TABLE IF NOT EXISTS asistencia (
        id INT AUTO_INCREMENT PRIMARY KEY,
        practicante_id INT NOT NULL,
        estado_id INT NOT NULL,
        fecha DATE NOT NULL,
        hora_entrada TIME,
        hora_salida TIME,
        horas_extra TIME DEFAULT '00:00:00',
        observaciones TEXT,
        motivo VARCHAR(255),
        FOREIGN KEY (practicante_id) REFERENCES practicante(id) ON DELETE CASCADE,
        FOREIGN KEY (estado_id) REFERENCES estado_asistencia(id),
        UNIQUE KEY unique_asistencia_dia (practicante_id, fecha)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # 5. Tabla asistencia_recuperacion
    await execute_query("""
    CREATE TABLE IF NOT EXISTS asistencia_recuperacion (
        id INT AUTO_INCREMENT PRIMARY KEY,
        practicante_id INT NOT NULL,
        fecha_recuperacion DATE NOT NULL,
        hora_entrada TIME NOT NULL,
        hora_salida TIME NULL,
        motivo TEXT NULL,
        estado VARCHAR(20) DEFAULT 'Pendiente',
        FOREIGN KEY (practicante_id) REFERENCES practicante(id) ON DELETE CASCADE,
        UNIQUE KEY unique_recuperacion_dia (practicante_id, fecha_recuperacion)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # 6. Tabla para rastrear reportes diarios enviados
    await execute_query("""
    CREATE TABLE IF NOT EXISTS reportes_enviados (
        fecha DATE PRIMARY KEY,
        enviado_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # 7. Tabla de configuración por servidor
    await execute_query("""
    CREATE TABLE IF NOT EXISTS configuracion_servidor (
        guild_id BIGINT PRIMARY KEY,
        canal_asistencia_id BIGINT NULL,
        canal_reportes_id BIGINT NULL,
        usuarios_mencion_reporte TEXT NULL, -- IDs separados por comas
        mensaje_bienvenida TEXT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # 8. Tabla de administradores (Equipo de Desarrollo)
    await execute_query("""
    CREATE TABLE IF NOT EXISTS bot_admins (
        discord_id BIGINT PRIMARY KEY,
        nombre_referencia VARCHAR(255),
        rol VARCHAR(100) DEFAULT 'Developer'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # Insertar equipo inicial si no existe
    query_admin = "INSERT IGNORE INTO bot_admins (discord_id, nombre_referencia, rol) VALUES (%s, %s, %s)"
    admins = [
        (615932763161362636, 'Renso Mamani', 'Dev Principal'),
        (824692049084678144, 'Wilber Peralta', 'Product Owner'),
        (1395195164779347988, 'Jordy', 'Developer')
    ]
    for admin_data in admins:
        await execute_query(query_admin, admin_data)

    # 7. Vista para Reporte Excel (Incluye Total: Horas Base + Horas Bot)
    await execute_query("""
    CREATE OR REPLACE VIEW reporte_asistencia AS
    SELECT 
        a.id AS Asistencia_ID,
        p.id_discord AS ID_Discord,
        p.nombre_completo AS Nombre_Completo,
        a.fecha AS Fecha,
        a.hora_entrada AS Entrada,
        a.hora_salida AS Salida,
        ea.estado AS Estado,
        
        -- Horas trabajadas en esta sesión específica
        TIMEDIFF(a.hora_salida, a.hora_entrada) AS Horas_Sesion,
        
        -- Horas Base fijas desde Excel
        p.horas_base AS Horas_Base,

        -- Total Horas Bot (histórico hasta hoy)
        (
            SELECT SEC_TO_TIME(SUM(TIME_TO_SEC(TIMEDIFF(a2.hora_salida, a2.hora_entrada))))
            FROM asistencia a2
            WHERE a2.practicante_id = p.id AND a2.hora_salida IS NOT NULL
        ) AS Total_Horas_Bot,

        -- GRAN TOTAL (Base + Bot)
        ADDTIME(
            IFNULL(p.horas_base, '00:00:00'),
            IFNULL((
                SELECT SEC_TO_TIME(SUM(TIME_TO_SEC(TIMEDIFF(a3.hora_salida, a3.hora_entrada))))
                FROM asistencia a3
                WHERE a3.practicante_id = p.id AND a3.hora_salida IS NOT NULL
            ), '00:00:00')
        ) AS Gran_Total_Acumulado

    FROM asistencia a
    JOIN practicante p ON a.practicante_id = p.id
    JOIN estado_asistencia ea ON a.estado_id = ea.id;
    """)
    

    # 7. Vista simplificada para consultas rápidas (Resumen por Practicante)
    await execute_query("""
    CREATE OR REPLACE VIEW resumen_practicantes AS
    SELECT 
        p.id,
        p.id_discord AS ID_Discord,
        p.nombre_completo AS Nombre_Completo,
        p.horas_base AS Horas_Base,
        
        -- Total Horas Bot (todas las sesiones completadas)
        IFNULL(
            (SELECT SEC_TO_TIME(SUM(TIME_TO_SEC(TIMEDIFF(a.hora_salida, a.hora_entrada))))
             FROM asistencia a
             WHERE a.practicante_id = p.id AND a.hora_salida IS NOT NULL),
            '00:00:00'
        ) AS Horas_Bot,
        
        -- Gran Total (Base + Bot)
        ADDTIME(
            IFNULL(p.horas_base, '00:00:00'),
            IFNULL(
                (SELECT SEC_TO_TIME(SUM(TIME_TO_SEC(TIMEDIFF(a.hora_salida, a.hora_entrada))))
                 FROM asistencia a
                 WHERE a.practicante_id = p.id AND a.hora_salida IS NOT NULL),
                '00:00:00'
            )
        ) AS Total_Acumulado
    FROM practicante p
    ORDER BY Total_Acumulado DESC;
    """)
    
    logging.info("Base de datos inicializada Correctamente (Esquema Simplificado).")
