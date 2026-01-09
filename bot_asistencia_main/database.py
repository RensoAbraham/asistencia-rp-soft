import os
import aiomysql
from dotenv import load_dotenv
from typing import Optional, Union, Tuple, Dict, Any, List
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

# Evitar import circular si es posible, pero mantenemos si es necesario o eliminamos si no se usa
# import database as db  <-- Esto parece redundante si estams en database.py, lo comento.

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "db": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT")),
    "autocommit": False,
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
    
    # 1. Tabla practicante
    await execute_query("""
    CREATE TABLE IF NOT EXISTS practicante (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_discord BIGINT NOT NULL UNIQUE,
        nombre VARCHAR(100) NOT NULL,
        apellido VARCHAR(100) NOT NULL,
        correo VARCHAR(255) NOT NULL,
        semestre INT DEFAULT 1,
        estado VARCHAR(20) DEFAULT 'activo',
        horas_base TIME DEFAULT '00:00:00',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # 1.1 Migración: Asegurar que la columna horas_base exista (si la tabla ya existía)
    try:
        await execute_query("ALTER TABLE practicante ADD COLUMN horas_base TIME DEFAULT '00:00:00';")
    except Exception:
        pass # La columna ya existe o error ignorado

    # ... (Resto de tablas) ...

    # 6. Vista para Reporte Excel y Metabase (Cálculos automáticos con Horas Base)
    await execute_query("""
    CREATE OR REPLACE VIEW reporte_asistencia AS
    SELECT 
        p.nombre AS Nombre,
        p.apellido AS Apellido,
        a.fecha AS Fecha,
        a.hora_entrada AS Entrada,
        a.hora_salida AS Salida,
        TIMEDIFF(a.hora_salida, a.hora_entrada) AS Horas_Sesion,
        
        -- Cálculo de Horas Acumuladas (Sesiones Previas + Sesión Actual + Horas Base)
        ADDTIME(
            IFNULL(p.horas_base, '00:00:00'),
            (SELECT SEC_TO_TIME(SUM(TIME_TO_SEC(TIMEDIFF(a2.hora_salida, a2.hora_entrada))))
             FROM asistencia a2 
             WHERE a2.practicante_id = p.id AND a2.hora_salida IS NOT NULL AND a2.fecha <= a.fecha)
        ) AS Horas_Acumuladas_Hasta_Hoy,
        
        -- Metas y Faltantes (Calculado al vuelo)
        '480:00:00' AS Meta_Horas,
        
        TIMEDIFF('480:00:00', 
            ADDTIME(
                IFNULL(p.horas_base, '00:00:00'),
                (SELECT SEC_TO_TIME(SUM(TIME_TO_SEC(TIMEDIFF(a2.hora_salida, a2.hora_entrada))))
                 FROM asistencia a2 
                 WHERE a2.practicante_id = p.id AND a2.hora_salida IS NOT NULL AND a2.fecha <= a.fecha)
            )
        ) AS Horas_Restantes,
        
        ea.estado AS Estado
    FROM practicante p
    JOIN asistencia a ON p.id = a.practicante_id
    JOIN estado_asistencia ea ON a.estado_id = ea.id;
    """)
    
    logging.info("Base de datos verificada e inicializada correctamente.")
