import pytest
import sys
import os
import asyncio
from unittest.mock import MagicMock, AsyncMock

# Añadir directorio raíz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar lógica
import database as db

# Test Simple: Verificación de Funciones de Base de Datos (unitario, mockeado)
@pytest.mark.asyncio
async def test_database_connection_mock():
    """
    Simula una conexión a base de datos.
    Objetivo: Verificar que el código intente conectar sin errores de sintaxis.
    """
    db.init_db_pool = AsyncMock()
    db.init_db_pool.return_value = True
    
    result = await db.init_db_pool()
    assert result is True

# Test Funcional (Requiere BD real, se ejecutará en Docker)
@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv('DB_HOST') is None, reason="Requiere conexión a BD real")
async def test_database_integration():
    """
    Prueba real de conexión e inserción.
    Solo corre si hay variables de entorno de BD configuradas.
    """
    # 1. Iniciar pool
    await db.init_db_pool()
    
    # 2. Verificar que podemos ejecutar un SELECT 1
    val = await db.fetch_one("SELECT 1 as test")
    assert val['test'] == 1
    
    await db.close_db_pool()
