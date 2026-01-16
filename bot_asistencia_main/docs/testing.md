# 🧪 Guía de Tests y Calidad

El proyecto incluye un conjunto de pruebas **funcionales** diseñadas para verificar que el sistema (base de datos y bot) responda correctamente sin necesidad de desplegar en producción.

## 📁 Ubicación
Los tests se encuentran en la carpeta `/tests` del proyecto.

## 🛠️ Herramientas
Usamos `pytest` como framework de pruebas principal debido a su simplicidad y potencia.

## 🚀 Cómo ejecutar los Tests

### En Local (Windows/Linux)
Asegúrate de tener instaladas las dependencias (`pip install -r requirements.txt`) y estar en la raíz del proyecto.

1.  **Correr todos los tests:**
    ```bash
    pytest
    ```

2.  **Correr tests específicos:**
    ```bash
    pytest tests/test_database.py
    ```

### En Docker (VPS)
Es la forma recomendada, ya que usa el entorno exacto de producción.

```bash
docker compose run --rm bot pytest
```

---

## 🔍 ¿Qué prueban estos tests?

### 1. Pruebas de Base de Datos (`test_database.py`)
Verifican que la conexión MySQL funcione y las tablas críticas existan.
*   ✅ Conexión exitosa a la BD.
*   ✅ Existencia de tablas: `practicante`, `asistencia`, `asistencia_recuperacion`.
*   ✅ Inserción y lectura de datos de prueba.

### 2. Pruebas de Lógica de Negocio (`test_logic.py`)
Verifican funciones puras como cálculos de horas.
*   ✅ Cálculo correcto de diferencia de horas (`14:00` - `09:00` = 5h).
*   ✅ Detección de tardanzas (Entrada > 09:10).

---

## 🛡️ Política de Calidad
Antes de cualquier despliegue a la rama `main` o subida al VPS, es obligatorio ejecutar `pytest`. Si algo falla ❌, **no se despliega**.
