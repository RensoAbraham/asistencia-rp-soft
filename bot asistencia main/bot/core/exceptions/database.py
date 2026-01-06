"""Excepciones relacionadas con la base de datos"""

from .base import BotException


class DatabaseError(BotException):
    """Error general de base de datos"""
    pass


class DatabaseConnectionError(DatabaseError):
    """Error al conectar con la base de datos"""
    pass


class DatabaseQueryError(DatabaseError):
    """Error al ejecutar una consulta"""
    pass


