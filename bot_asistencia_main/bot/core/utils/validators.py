"""Funciones de validación"""

from datetime import time, date
from typing import Optional

from bot.config.constants import (
    DIAS_HISTORIAL_MIN,
    DIAS_HISTORIAL_MAX,
    DIAS_HISTORIAL_RECUPERACION_MIN,
    DIAS_HISTORIAL_RECUPERACION_MAX,
)
from bot.core.exceptions import ValidationError
from bot.core.utils.datetime_utils import is_time_in_range


def validate_horario(
    current_time: time,
    start_time: time,
    end_time: time,
    error_message: str
) -> None:
    """
    Valida que la hora actual esté dentro del rango permitido
    
    Args:
        current_time: Hora a validar
        start_time: Hora de inicio permitida
        end_time: Hora de fin permitida
        error_message: Mensaje de error si no está en el rango
        
    Raises:
        ValidationError: Si la hora no está en el rango
    """
    if not is_time_in_range(current_time, start_time, end_time):
        raise ValidationError(error_message)


def validate_dias_historial(
    dias: int,
    min_dias: int = DIAS_HISTORIAL_MIN,
    max_dias: int = DIAS_HISTORIAL_MAX
) -> None:
    """
    Valida el rango de días para historial
    
    Args:
        dias: Cantidad de días a validar
        min_dias: Mínimo permitido
        max_dias: Máximo permitido
        
    Raises:
        ValidationError: Si está fuera del rango
    """
    if dias < min_dias or dias > max_dias:
        raise ValidationError(
            f"El número de días debe estar entre {min_dias} y {max_dias}."
        )


def validate_dias_recuperacion(dias: int) -> None:
    """Valida el rango de días para historial de recuperación"""
    validate_dias_historial(
        dias,
        DIAS_HISTORIAL_RECUPERACION_MIN,
        DIAS_HISTORIAL_RECUPERACION_MAX
    )


def validate_fecha(fecha: date) -> None:
    """Valida que la fecha sea válida (básico)"""
    if fecha is None:
        raise ValidationError("La fecha no puede ser None")


