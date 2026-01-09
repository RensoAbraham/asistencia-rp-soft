"""Utilidades para manejo de fechas y horas"""

from datetime import datetime, date, time
from typing import Optional

from bot.config import Settings, DIAS_SEMANA_PERMITIDOS
from bot.core.exceptions import ValidationError


def get_current_datetime() -> datetime:
    """Obtiene la fecha y hora actual en la zona horaria configurada"""
    return datetime.now(Settings.TIMEZONE)


def get_current_date() -> date:
    """Obtiene la fecha actual en la zona horaria configurada"""
    return get_current_datetime().date()


def get_current_time() -> time:
    """Obtiene la hora actual en la zona horaria configurada"""
    return get_current_datetime().time()


def is_weekday(dt: Optional[datetime] = None) -> bool:
    """
    Verifica si la fecha es un día laborable
    
    Args:
        dt: Fecha a verificar. Si es None, usa la fecha actual
        
    Returns:
        True si es día laborable, False si es fin de semana
    """
    if dt is None:
        dt = get_current_datetime()
    
    return dt.weekday() in DIAS_SEMANA_PERMITIDOS


def is_time_in_range(current_time: time, start_time: time, end_time: time) -> bool:
    """
    Verifica si una hora está dentro de un rango
    
    Args:
        current_time: Hora a verificar
        start_time: Hora de inicio del rango
        end_time: Hora de fin del rango
        
    Returns:
        True si está en el rango
    """
    return start_time <= current_time <= end_time


