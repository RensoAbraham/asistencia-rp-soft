"""
Configuración del bot desde variables de entorno
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

# Cargar variables de entorno
load_dotenv()


class Settings:
    """Configuración centralizada del bot"""
    
    # Discord
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    
    # Base de datos
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "bot_db")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    
    # Backend API
    BACKEND_API_KEY: str = os.getenv("BACKEND_API_KEY", "")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "")
    
    # Zona horaria
    TIMEZONE: ZoneInfo = ZoneInfo("America/Lima")
    
    # Configuración de servidores (canales permitidos)
    CANALES_PERMITIDOS: Dict[int, List[int]] = {
        1389959112556679239: [1469777811924582602],  # Servidor RP Soft
        1405602519635202048: [1468308523539628208, 1406544076534190110],  # Servidor Laboratorios

    }
    
    # Configuración de roles para recuperación
    ROLES_RECUPERACION: Dict[int, List[int]] = {
        1389959112556679239: [],  # Todos pueden usar
        1405602519635202048: [],  # Todos pueden usar
    }
    
    # Pool de conexiones
    DB_POOL_MINSIZE: int = 1
    DB_POOL_MAXSIZE: int = 10
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Valida que las configuraciones esenciales estén presentes"""
        required = [
            cls.DISCORD_TOKEN,
            cls.BACKEND_API_KEY,
            cls.BACKEND_URL,
        ]
        return all(required)
    
    @classmethod
    def get_canales_permitidos(cls, guild_id: int) -> List[int]:
        """Obtiene los canales permitidos para un servidor"""
        return cls.CANALES_PERMITIDOS.get(guild_id, [])
    
    @classmethod
    def get_roles_recuperacion(cls, guild_id: int) -> List[int]:
        """Obtiene los roles permitidos para recuperación en un servidor"""
        return cls.ROLES_RECUPERACION.get(guild_id, [])


# Instancia global de configuración
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Obtiene la instancia de configuración (singleton)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


