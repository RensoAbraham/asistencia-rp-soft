"""Utilidades para formatear datos"""

from datetime import date, time, datetime
from typing import Optional


def format_time(t: time) -> str:
    """Formatea una hora a string HH:MM"""
    return t.strftime("%H:%M")


def format_date(d: date, format_str: str = "%d/%m/%Y") -> str:
    """Formatea una fecha a string"""
    return d.strftime(format_str)


def format_datetime(dt: datetime, format_str: str = "%d/%m/%Y %H:%M") -> str:
    """Formatea una fecha y hora a string"""
    return dt.strftime(format_str)


def format_date_short(d: date) -> str:
    """Formatea una fecha a formato corto MM-DD"""
    return d.strftime("%m-%d")


def format_time_or_none(t: Optional[time]) -> str:
    """Formatea una hora o retorna 'No registrada'"""
    return format_time(t) if t else "No registrada"


def format_date_or_none(d: Optional[date]) -> str:
    """Formatea una fecha o retorna 'No registrada'"""
    return format_date(d) if d else "No registrada"


