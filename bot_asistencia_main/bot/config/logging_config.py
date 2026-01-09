"""
Configuración de logging para el bot
"""

import logging
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any

from .settings import Settings


class LimaFormatter(logging.Formatter):
    """Formatter que usa la zona horaria de Lima"""
    
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.tz = Settings.TIMEZONE
    
    def formatTime(self, record: logging.LogRecord, datefmt: str = None) -> str:
        """Formatea el tiempo usando la zona horaria de Lima"""
        dt = datetime.fromtimestamp(record.created, tz=self.tz)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.strftime(self.datefmt if hasattr(self, 'datefmt') and self.datefmt else '%Y-%m-%d %H:%M:%S')
        return s


def setup_logging(level: str = None) -> None:
    """Configura el sistema de logging del bot"""
    settings = Settings()
    log_level = level or settings.LOG_LEVEL
    
    # Configurar formato
    formatter = LimaFormatter(
        fmt='%(asctime)s %(levelname)-8s %(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    root_logger.addHandler(console_handler)
    
    # Silenciar loggers de librerías externas si es necesario
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("aiomysql").setLevel(logging.WARNING)


