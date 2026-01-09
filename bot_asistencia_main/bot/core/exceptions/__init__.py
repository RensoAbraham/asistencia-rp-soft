"""Excepciones personalizadas del bot"""

from .base import BotException
from .database import DatabaseError, DatabaseConnectionError, DatabaseQueryError
from .validation import ValidationError, PermissionError, NotFoundError

__all__ = [
    "BotException",
    "DatabaseError",
    "DatabaseConnectionError",
    "DatabaseQueryError",
    "ValidationError",
    "PermissionError",
    "NotFoundError",
]


