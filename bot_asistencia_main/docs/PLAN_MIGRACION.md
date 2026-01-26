# Plan de Migración y Mejoras - Bot de Asistencia RP Soft

Este documento detalla las mejoras realizadas al sistema de reportes, el nuevo control Anti-AFK y las opciones para migrar el bot a un entorno gratuito tras la caída del VPS.

## 🛠️ Mejoras Implementadas

### 1. Formato de Duración [HH]:MM:SS
Se corrigió el formato en los reportes de Google Sheets. Ahora, las duraciones mayores a 24 horas se muestran como horas totales (ej. `37:28:18`) en lugar de `1 day, 13:28:18`.
- **Archivo modificado:** `google_sheets.py` (función `format_duration`).

### 2. Limpieza en "Reporte Detallado"
Siguiendo tu solicitud, se eliminó la columna **"Total Acumulado"** de la pestaña de reportes diarios, dejando esa información exclusivamente para la pestaña de **"Resumen General"**.
- **Archivo modificado:** `google_sheets.py`.

### 3. Sistema Anti-AFK (Límite de Horas)
Para evitar que los practicantes "fameen" horas quedándose conectados más tiempo del debido:
- Se estableció un **límite de 6 horas** por sesión (configurable).
- Al usar `/salida`, si el bot detecta que la sesión duró más de 6 horas, **ajustará automáticamente la hora de salida** para que el total sea exactamente 6 horas.
- El usuario recibirá un aviso indicando que sus horas han sido ajustadas.
- **Archivo modificado:** `cogs/asistencia/commands.py`.

---

## ☁️ Opciones de Hosting Gratuito

Como el VPS se cayó, aquí tienes las mejores opciones para volver a estar online sin costo:

### Opción A: Render (Recomendado para el Bot)
- **Tipo:** Blueprints / Web Service.
- **Pros:** Muy fácil de configurar con GitHub.
- **Cons:** El servicio entra en "reposo" si no recibe peticiones HTTP (se puede solucionar con un "ping" básico o usándolo como Worker).

### Opción B: TiDB Cloud (Para la Base de Datos MySQL)
- **Tipo**: Serverless MySQL.
- **Pros**: 100% compatible con tu código actual. Hosting gratuito generoso. Requiere SSL.
- **Configuración Especial**:
    *   `DB_PORT`: `4000`
    *   `DB_USE_SSL`: `True`
    *   `SSL_CA_PATH`: `isrgrootx1.pem` (Ya incluido en el repositorio).

---

## 💾 Estrategia de Migración de Datos (TiDB Cloud)

1.  **Conexión**: Usa los datos que te dio TiDB (Host, User, Password).
2.  **Base de Datos**: Te recomiendo crear una base de datos propia (ej. `asistencia_db`) en lugar de usar la de `test`.
3.  **Variables de Entorno**: Configura tu hosting (Render/Railway) con estos valores:
    ```env
    DB_HOST=gateway01.us-east-1.prod.aws.tidbcloud.com
    DB_USER=4H85vqbbpvRhXiZ.root
    DB_PASSWORD=vrVL3o5ytoXF0wa9
    DB_NAME=asistencia_db  # O la que elijas
    DB_PORT=4000
    DB_USE_SSL=True
    ```

3. **Google Sheets como "Bote de Salvavidas":**
   Dado que el bot sincroniza con Sheets, si la base de datos se pierde totalmente:
   - Los nombres y IDs se recuperarán automáticamente de la hoja **"Practicantes_RP_Soft"**.
   - Las horas base se pueden cargar en la columna de horas acumuladas del Excel para que el bot empiece a contar desde ahí.

---

## 🚀 Próximos Pasos sugeridos
1. **Verificar el límite de 6 horas**: ¿Te parece bien ese tiempo o prefieres que sea 4 u 8?
2. **Definir Hosting**: Si decides por Render + TiDB Cloud, puedo ayudarte con los archivos de configuración específicos.
3. **Monitoreo**: He dejado logs detallados para que veas quién está intentando exceder el límite de horas en el servidor.
