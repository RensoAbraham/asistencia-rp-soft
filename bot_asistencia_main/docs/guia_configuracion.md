# ⚙️ Guía de Configuración y Uso Diario

Esta guía explica cómo gestionar los usuarios, entender los horarios y leer los reportes.

## 1. Configuración de Practicantes en Google Sheets

El bot está conectado a tu archivo Google Sheets (`Practicantes_RP_Soft`).
La hoja principal es **la fuente de la verdad**.

### Formato de Columnas (Hoja 1)
Debes tener estas columnas como mínimo:

| ID Discord | Nombre | Apellido | Horas Base |
|------------|--------|----------|------------|
| 123456...  | Renso  | Abraham  | 10         |
| 987654...  | Juan   | Perez    |            |

*   **ID Discord:** Obligatorio. Es el ID numérico del usuario en Discord.
*   **Horas Base (Opcional):**
    *   Puedes poner un número entero: `10` -> El bot entenderá `10:00:00`.
    *   Si lo dejas vacío, empieza desde 0.
    *   Útil para reconocer horas de ciclos anteriores.

## 2. Reglas de Asistencia y Tardanzas

El bot aplica reglas estrictas para mantener el orden.

### 🕒 Horario de Entrada
*   **Inicio Permitido:** 07:00 AM
*   **Hora Límite (Sin Tardanza):** 08:20 AM
*   **Hora Límite Asistencia:** 14:00 PM

### ⚠️ Regla de Tardanza (08:20 AM)
Si un practicante marca entrada **después de las 08:20:59**, el sistema marcará automáticamente:
*   Estado: `Tardanza` 🟠
*   El usuario recibirá una notificación indicando su llegada tarde.

### 🚪 Salida Anticipada
Si un usuario marca salida **antes de las 14:00**:
*   El bot lanzará una **alerta 🔴** indicando que deben avisar a su líder.
*   Esto **NO** borra las horas, pero queda registrado como salida temprana.

## 3. Reportes Automáticos

El bot actualiza dos hojas en tu Excel:

1.  **"Reporte Detallado":**
    *   Lista diaria de quién entró, a qué hora y quién faltó.
    *   Se actualiza cada hora.

2.  **"Resumen General":**
    *   Muestra el **Total Acumulado**.
    *   Fórmula: `Horas Base (Excel) + Horas Trabajadas (Bot) = Total`.
    *   Úselo para ver quién ya cumplió sus 480 horas.
