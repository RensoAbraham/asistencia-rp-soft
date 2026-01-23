# Changelog del Bot de Asistencia

Este archivo documenta los cambios realizados en cada versión del bot.

## Versión 1.3.0 - Anti-Farming y Reportes Mejorados
**Fecha:** 2026-01-23

### ✨ Nuevas Funcionalidades
*   **Sistema Anti-Farming (Soft Cap):** 
    *   Se implementó un límite "blando" a las 2:30 PM (14:30).
    *   Si un usuario marca salida después de esa hora, el sistema registra su salida oficial a las 14:30.
    *   El tiempo excedente se calcula y almacena en una columna separada (`horas_extra`).
    *   El usuario recibe una alerta indicando que sus horas extra están pendientes de validación.
*   **Reporte de Incidentes en Excel:**
    *   Se creó una nueva pestaña "Reporte Anti-Farming" en Google Sheets.
    *   Lista automáticamente a los usuarios que excedieron el horario, mostrando la fecha y horas extra para revisión manual.
*   **Redirección de Canales:**
    *   Mejora en la experiencia de usuario (UX): Si alguien intenta usar comandos en un canal incorrecto, el bot ahora proporciona un enlace directo clickeable al canal oficial `#asistencia`.

### 🔧 Cambios Técnicos
*   Base de Datos: Nueva columna `horas_extra` en la tabla `asistencia`.
*   Lógica: Refactorización del comando `/salida` para manejar el cálculo diferencial de tiempos.

---

## Versión 1.2.0 - Sincronización con Google Sheets y Formato
**Fecha:** 2026-01-23

### ✨ Nuevas Funcionalidades
*   **Formato de Horas:** Se corrigió la visualización de duraciones mayores a 24 horas (ej. `37:28:18` en lugar de `1 day, 13:28:18`).
*   **Limpieza de Reportes:** Se eliminó la columna de "Total Acumulado" del reporte diario detallado para evitar confusión.

---

## Versión 1.1.0 - Estructura Modular
**Fecha:** 2026-01-20

### 🔧 Cambios Técnicos
*   Reorganización del código en `cogs/` (asistencia, faltas, recuperación).
*   Implementación de `database.py` con pool de conexiones asíncronas.

