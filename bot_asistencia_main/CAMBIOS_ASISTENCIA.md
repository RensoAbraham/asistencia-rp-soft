# Cambios realizados

## 1. Ajuste de Horarios de Asistencia
Se han modificado los límites de tiempo para el registro de entrada:
- **Nueva hora de inicio**: 7:50 AM (antes 8:00 AM).
- **Nuevo límite para "Presente"**: Hasta las 8:10:59 AM.
- **Tardanza**: A partir de las 8:11:00 AM.
- Se han actualizado estos valores en `bot/config/constants.py` y se ha refactorizado `cogs/asistencia/commands.py` para utilizar estas constantes de forma centralizada.

## 2. Mejora del Reporte Detallado (Google Sheets)
Se ha mejorado la legibilidad de la hoja "Reporte Detallado":
- **Encabezados de Fecha**: Ahora cada día tiene una fila de separación con el nombre del día y la fecha completa en español (ej: "Miércoles 11 Febrero 2026").
- **Formato Visual**: Estas filas de encabezado tienen un fondo celeste claro y fuente en negrita para diferenciar claramente las jornadas.
- **Limpieza**: Se eliminó la columna "Total Acumulado" en esta vista específica para evitar redundancia con el Resumen General, según lo conversado.

## 3. Sincronización
El bot continuará sincronizando estos cambios automáticamente cada 10 minutos o al finalizar la jornada laboral.
