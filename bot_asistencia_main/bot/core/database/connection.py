"""
Gestión de conexiones a la base de datos
Pool de conexiones asíncrono con aiomysql
"""

from typing import Any, Optional, List, Dict, Tuple, Union
from contextlib import asynccontextmanager
import aiomysql
from aiomysql import Pool, Connection, DictCursor

from bot.config import Settings, get_settings
from bot.core.exceptions.database import (
    DatabaseConnectionError,
    DatabaseQueryError,
)


class Database:
    """Gestor de base de datos con pool de conexiones"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._pool: Optional[Pool] = None
    
    async def initialize(self) -> None:
        """Inicializa el pool de conexiones"""
        if self._pool is not None:
            return
        
        try:
            self._pool = await aiomysql.create_pool(
                minsize=self.settings.DB_POOL_MINSIZE,
                maxsize=self.settings.DB_POOL_MAXSIZE,
                host=self.settings.DB_HOST,
                user=self.settings.DB_USER,
                password=self.settings.DB_PASSWORD,
                db=self.settings.DB_NAME,
                port=self.settings.DB_PORT,
                autocommit=False,
            )
        except Exception as e:
            raise DatabaseConnectionError(
                f"No se pudo conectar a la base de datos: {e}"
            ) from e
    
    async def close(self) -> None:
        """Cierra el pool de conexiones"""
        if self._pool is not None:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None
    
    @asynccontextmanager
    async def get_connection(self):
        """Obtiene una conexión del pool (context manager)"""
        if self._pool is None:
            await self.initialize()
        
        conn = await self._pool.acquire()
        try:
            yield conn
        finally:
            self._pool.release(conn)
    
    async def fetch_one(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Ejecuta una consulta y retorna un solo resultado
        
        Args:
            query: Query SQL
            params: Parámetros para la query
            
        Returns:
            Diccionario con el resultado o None
        """
        async with self.get_connection() as conn:
            try:
                async with conn.cursor(DictCursor) as cursor:
                    await cursor.execute(query, params)
                    return await cursor.fetchone()
            except Exception as e:
                raise DatabaseQueryError(
                    f"Error ejecutando fetch_one: {e}",
                    details=query
                ) from e
    
    async def fetch_all(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta y retorna todos los resultados
        
        Args:
            query: Query SQL
            params: Parámetros para la query
            
        Returns:
            Lista de diccionarios con los resultados
        """
        async with self.get_connection() as conn:
            try:
                async with conn.cursor(DictCursor) as cursor:
                    await cursor.execute(query, params)
                    return list(await cursor.fetchall())
            except Exception as e:
                raise DatabaseQueryError(
                    f"Error ejecutando fetch_all: {e}",
                    details=query
                ) from e
    
    async def execute(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict[str, Any]]] = None
    ) -> int:
        """
        Ejecuta una consulta de inserción/actualización/eliminación
        
        Args:
            query: Query SQL
            params: Parámetros para la query
            
        Returns:
            ID del último registro insertado o 0
        """
        async with self.get_connection() as conn:
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    await conn.commit()
                    return cursor.lastrowid or 0
            except Exception as e:
                await conn.rollback()
                raise DatabaseQueryError(
                    f"Error ejecutando execute: {e}",
                    details=query
                ) from e


# Instancia global de la base de datos
_database: Optional[Database] = None


def get_database() -> Database:
    """Obtiene la instancia de la base de datos (singleton)"""
    global _database
    if _database is None:
        _database = Database(get_settings())
    return _database


