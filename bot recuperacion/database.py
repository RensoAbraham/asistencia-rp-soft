import os
from typing import Any, Optional, List, Dict, Tuple, Union, AsyncIterator
import aiomysql
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv


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
