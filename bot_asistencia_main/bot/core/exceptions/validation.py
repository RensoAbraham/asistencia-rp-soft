"""Excepciones de validación"""

from .base import BotException


class ValidationError(BotException):
    """Error de validación"""
    pass


class PermissionError(BotException):
    """Error de permisos"""
    pass


class NotFoundError(BotException):
    """Recurso no encontrado"""
    pass


