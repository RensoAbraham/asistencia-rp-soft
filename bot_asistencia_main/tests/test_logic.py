import pytest
from datetime import datetime, time, timedelta

# Simulación de lógica de negocio (si estuviera en una función aislada, importáríamos la función)
# Aquí replicamos la lógica usada en el bot para testearla

def calcular_tardanza(hora_entrada: time) -> bool:
    """Retorna True si la entrada es después de las 08:20"""
    limite = time(8, 20)
    return hora_entrada > limite

def calcular_horas_trabajadas(entrada: time, salida: time) -> str:
    """Calcula diferencia y retorna HH:MM:SS"""
    dt_entrada = datetime.combine(datetime.today(), entrada)
    dt_salida = datetime.combine(datetime.today(), salida)
    
    diff = dt_salida - dt_entrada
    return str(diff)

# --- TESTS ---

def test_tardanza_detectada():
    entrada = time(8, 25) # 08:25 (Tardanza)
    assert calcular_tardanza(entrada) == True

def test_puntualidad_detectada():
    entrada = time(8, 15) # 08:15 (Puntual)
    assert calcular_tardanza(entrada) == False

def test_calculo_horas_correcto():
    entrada = time(9, 0, 0)
    salida = time(14, 0, 0)
    resultado = calcular_horas_trabajadas(entrada, salida)
    assert resultado == "5:00:00"

def test_calculo_con_minutos():
    entrada = time(9, 15, 0)
    salida = time(13, 45, 0)
    resultado = calcular_horas_trabajadas(entrada, salida)
    assert resultado == "4:30:00"
