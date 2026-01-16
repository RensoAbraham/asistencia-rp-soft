# 🛠️ Scripts de Mantenimiento

Esta carpeta contiene utilidades para administrar el bot y recuperar desastres.

## 📄 `reset_hours.py`
**USO:** Reinicia todos los contadores de asistencia a CERO, pero **mantiene** a los usuarios registrados.
Se usa al iniciar un nuevo ciclo de prácticas.

```bash
docker compose run --rm bot python scripts/reset_hours.py
```

## 📂 `sql/`
Contiene scripts SQL puros para consultas manuales o reconstrucción de base de datos.
*   `init_db_corrected.sql`: Esquema original de la base de datos (tablas `asistencia`, `practicante`, etc.).
*   `clean_hours.sql`: Comandos manuales para limpiar horas (alternativa a `reset_hours.py`).
