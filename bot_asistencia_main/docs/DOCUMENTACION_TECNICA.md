# 📚 Documentación Técnica - Bot de Asistencia RP Soft

## 📋 Tabla de Contenidos
1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Módulos Principales](#módulos-principales)
4. [Base de Datos](#base-de-datos)
5. [Integración con Google Sheets](#integración-con-google-sheets)
6. [Configuración y Variables de Entorno](#configuración-y-variables-de-entorno)
7. [Comandos del Bot](#comandos-del-bot)
8. [Mantenimiento y Modificaciones](#mantenimiento-y-modificaciones)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

### Propósito del Bot
El Bot de Asistencia RP Soft es un sistema automatizado para gestionar el registro de asistencia de practicantes en Discord. Permite:
- Registro de entrada y salida diaria
- Seguimiento de tardanzas y faltas
- Sesiones de recuperación
- Sincronización bidireccional con Google Sheets
- Reportes automáticos y manuales
- Sistema anti-farming (prevención de horas falsas)

### Tecnologías Utilizadas
- **Python 3.10+** - Lenguaje principal
- **discord.py** - Librería para interactuar con Discord
- **aiomysql** - Conexión asíncrona a MySQL/TiDB
- **gspread** - Integración con Google Sheets API
- **Docker** - Containerización y deployment

---

## 🏗️ Arquitectura del Sistema

### Estructura de Directorios

```
bot_asistencia_main/
├── bot.py                      # Archivo principal del bot
├── database.py                 # Gestión de base de datos
├── google_sheets.py            # Sincronización con Google Sheets
├── utils.py                    # Funciones auxiliares
├── requirements.txt            # Dependencias Python
├── Dockerfile                  # Configuración Docker
├── docker-compose.yml          # Orquestación de contenedores
├── credentials.json            # Credenciales Google Service Account
├── .env                        # Variables de entorno (NO COMMITEAR)
│
├── bot/
│   └── config/
│       ├── __init__.py
│       ├── constants.py        # Constantes del sistema
│       └── settings.py         # Configuraciones
│
├── cogs/                       # Módulos de comandos (extensiones)
│   ├── asistencia/
│   │   └── commands.py         # Comandos de asistencia
│   ├── recuperacion/
│   │   └── commands.py         # Comandos de recuperación
│   ├── admin/
│   │   └── commands.py         # Comandos administrativos
│   └── test/
│       └── commands.py         # Comandos de prueba
│
└── docs/
    └── DOCUMENTACION_TECNICA.md  # Este archivo
```

### Flujo de Datos

```
Usuario Discord
    ↓
Comando Slash (/)
    ↓
Bot (bot.py) → Cog correspondiente
    ↓
Validaciones (utils.py)
    ↓
Base de Datos (database.py)
    ↓
Google Sheets (google_sheets.py) [Sincronización cada 10 min]
```

---

## 🔧 Módulos Principales

### 1. `bot.py` - Núcleo del Bot

**Responsabilidades:**
- Inicialización del bot y conexión a Discord
- Carga de extensiones (cogs)
- Tareas programadas (tasks)
- Health check para hosting
- Envío de métricas al backend (opcional)

**Configuraciones Importantes:**

```python
# Líneas 66-75: Canales permitidos por servidor
bot.canales_permitidos = {
    1389959112556679239: [1390353417079361607],  # RP Soft (Producción)
    1405602519635202048: [1468308523539628208]   # Laboratorios (Pruebas)
}
```

**⚠️ IMPORTANTE:** Para cambiar los canales donde funciona el bot, modifica estos IDs.

**Tareas Programadas:**

| Tarea | Intervalo | Descripción |
|-------|-----------|-------------|
| `sync_google_sheets_task` | 10 minutos | Sincroniza practicantes y reportes con Google Sheets |
| `auto_reporte_diario_task` | 15 minutos | Envía reporte automático cuando todos han salido (después de 14:30) |
| `send_metrics_to_backend` | 1 minuto | Envía métricas al backend (opcional) |

**Cómo modificar intervalos:**
```python
# Línea 205 - Cambiar intervalo de sincronización
@tasks.loop(minutes=10)  # Cambiar este número
async def sync_google_sheets_task():
    ...
```

---

### 2. `database.py` - Gestión de Base de Datos

**Responsabilidades:**
- Conexión con TiDB Cloud (MySQL compatible)
- Pool de conexiones asíncronas
- Creación y mantenimiento de esquema
- Funciones de consulta (`fetch_one`, `fetch_all`, `execute_query`)

**Esquema de Base de Datos:**

#### Tabla: `practicante`
```sql
CREATE TABLE practicante (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_discord BIGINT NOT NULL UNIQUE,
    nombre_completo VARCHAR(255) NOT NULL,
    horas_base TIME DEFAULT '00:00:00'
);
```

#### Tabla: `asistencia`
```sql
CREATE TABLE asistencia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    practicante_id INT NOT NULL,
    estado_id INT NOT NULL,
    fecha DATE NOT NULL,
    hora_entrada TIME,
    hora_salida TIME,
    horas_extra TIME DEFAULT '00:00:00',
    observaciones TEXT,
    motivo VARCHAR(255),
    UNIQUE KEY unique_asistencia_dia (practicante_id, fecha)
);
```

#### Tabla: `estado_asistencia`
Estados predefinidos:
- `Presente`
- `Tardanza`
- `Falta Injustificada`
- `Falta Recuperada`
- `Permiso`

#### Tabla: `asistencia_recuperacion`
```sql
CREATE TABLE asistencia_recuperacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    practicante_id INT NOT NULL,
    fecha_recuperacion DATE NOT NULL,
    hora_entrada TIME NOT NULL,
    hora_salida TIME NULL,
    motivo TEXT NULL,
    estado VARCHAR(20) DEFAULT 'Pendiente'
);
```

**Vistas SQL:**
- `reporte_asistencia` - Vista completa con cálculo de horas
- `resumen_practicantes` - Resumen por practicante con totales

---

### 3. `google_sheets.py` - Integración con Google Sheets

**Responsabilidades:**
- Leer practicantes desde Google Forms/Sheets
- Exportar reportes a Google Sheets
- Validación de horas extra (Anti-Farming)

**Flujo de Sincronización:**

```
Google Sheets (Practicantes_RP_Soft)
    ↓
get_practicantes_from_sheet()
    ↓
sync_practicantes_to_db()
    ↓
Base de Datos (INSERT/UPDATE)
```

**Hojas Generadas:**

1. **Reporte Detallado**
   - Fecha, Nombre, Entrada, Salida, Horas Sesión, Estado
   - Actualizado cada 10 minutos

2. **Resumen General**
   - Nombre, Horas Base, Horas Bot, Total Acumulado, Meta (480h)
   - Muestra progreso de cada practicante

3. **Reporte Anti-Farming**
   - Detecta sesiones con horas extra (>6 horas)
   - Permite validación manual marcando "OK"
   - Al marcar "OK", las horas extra se suman automáticamente

**Configuración de Credenciales:**

El archivo `credentials.json` debe ser un Service Account de Google Cloud con permisos:
- Google Sheets API
- Google Drive API

```json
{
  "type": "service_account",
  "project_id": "tu-proyecto",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "bot-asistencia@tu-proyecto.iam.gserviceaccount.com",
  ...
}
```

**⚠️ IMPORTANTE:** Compartir la hoja de Google Sheets con el email del Service Account.

---

### 4. `utils.py` - Funciones Auxiliares

**Funciones Principales:**

| Función | Descripción |
|---------|-------------|
| `obtener_practicante(interaction, discord_id)` | Busca practicante en BD, muestra link de registro si no existe |
| `verificar_entrada(practicante_id, fecha)` | Verifica si ya registró entrada hoy |
| `obtener_estado_asistencia(estado_nombre)` | Obtiene ID del estado desde la BD |
| `canal_permitido(interaction)` | Valida que el comando se use en canal correcto |
| `verificar_rol_permitido(interaction, roles)` | Valida roles del usuario |
| `es_domingo()` | Bloquea comandos los domingos |
| `format_timedelta(td)` | Formatea duración a HH:MM |

**Zona Horaria:**
```python
LIMA_TZ = ZoneInfo("America/Lima")
```
Todas las operaciones de tiempo usan la zona horaria de Lima.

---

## 🗄️ Base de Datos

### Conexión

**Variables de entorno requeridas (.env):**
```env
DB_HOST=gateway01.us-west-2.prod.aws.tidbcloud.com
DB_PORT=4000
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=asistencia_rp_soft
DB_USE_SSL=True
SSL_CA_PATH=isrgrootx1.pem
```

### Pool de Conexiones

```python
# database.py líneas 38-42
async def init_db_pool(minsize: int = 1, maxsize: int = 10):
    global _pool
    if _pool is None:
        _pool = await aiomysql.create_pool(minsize=minsize, maxsize=maxsize, **DB_CONFIG)
    return _pool
```

**Configuración recomendada:**
- `minsize=1` - Mínimo de conexiones activas
- `maxsize=10` - Máximo de conexiones simultáneas

### Migraciones

No hay sistema de migraciones formal. El esquema se crea/actualiza en:
```python
# database.py línea 92
async def ensure_db_setup():
    # Crea tablas si no existen
    # Inserta estados base
    # Crea vistas SQL
```

**Para agregar una nueva columna:**
1. Modificar `ensure_db_setup()` en `database.py`
2. Agregar `ALTER TABLE` si la tabla ya existe
3. Reiniciar el bot

---

## 📊 Integración con Google Sheets

### Configuración Inicial

1. **Crear Service Account en Google Cloud:**
   - Ir a [Google Cloud Console](https://console.cloud.google.com/)
   - Crear nuevo proyecto o usar existente
   - Habilitar APIs: Google Sheets API, Google Drive API
   - Crear Service Account
   - Generar clave JSON → guardar como `credentials.json`

2. **Compartir Google Sheet:**
   - Abrir la hoja de cálculo
   - Compartir con el email del Service Account
   - Dar permisos de "Editor"

3. **Configurar nombre de hoja:**
```env
# .env
GOOGLE_SHEET_NAME=Practicantes_RP_Soft
```

### Formato del Google Form/Sheet

**Columnas esperadas (Sheet1):**
| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| Timestamp | Fecha/hora del registro | 2026-02-10 08:00:00 |
| ID Discord | ID numérico de Discord | 615932763161362636 |
| Nombre Completo | Nombre y apellido | Juan Pérez García |
| Horas Base (opcional) | Horas acumuladas previas | 120:00:00 |

**Detección automática de columnas:**
```python
# google_sheets.py líneas 84-94
headers = [h.lower() for h in rows[0]]
idx_id = next(i for i, h in enumerate(headers) if 'id' in h and 'discord' in h)
idx_nombre = next(i for i, h in enumerate(headers) if 'nombre' in h)
```

### Sistema Anti-Farming

**¿Qué es?**
Previene que los practicantes registren más de 6 horas en una sola sesión.

**Flujo:**
1. Usuario registra salida después de 6 horas
2. Sistema calcula: `horas_extra = tiempo_total - 6 horas`
3. `hora_salida` se ajusta a `hora_entrada + 6 horas`
4. `horas_extra` se guarda en columna separada
5. Aparece en "Reporte Anti-Farming" en Google Sheets
6. Admin revisa y marca "OK" si es legítimo
7. En próxima sincronización, las horas extra se suman

**Código relevante:**
```python
# cogs/asistencia/commands.py líneas 130-160
if duracion_horas > self.MAX_SESSION_HOURS:
    horas_extra_segundos = (duracion_horas - self.MAX_SESSION_HOURS) * 3600
    horas_extra = timedelta(seconds=horas_extra_segundos)
    hora_salida_ajustada = hora_entrada_dt + timedelta(hours=self.MAX_SESSION_HOURS)
```

---

## ⚙️ Configuración y Variables de Entorno

### Archivo `.env`

```env
# Discord
DISCORD_TOKEN=tu_token_de_discord

# Base de Datos
DB_HOST=gateway01.us-west-2.prod.aws.tidbcloud.com
DB_PORT=4000
DB_USER=usuario
DB_PASSWORD=contraseña
DB_NAME=asistencia_rp_soft
DB_USE_SSL=True
SSL_CA_PATH=isrgrootx1.pem

# Google Sheets
GOOGLE_SHEET_NAME=Practicantes_RP_Soft

# Backend (Opcional)
BACKEND_URL=https://tu-backend.com
BACKEND_API_KEY=tu_api_key

# Hosting
PORT=10000
```

### Archivo `bot/config/constants.py`

**Horarios configurables:**

```python
# Horarios de entrada
HORARIO_ENTRADA_INICIO = time(8, 0)      # 8:00 AM
HORARIO_ENTRADA_FIN = time(14, 0)        # 2:00 PM
HORA_LIMITE_TARDANZA = time(8, 20, 59)   # 8:20:59 AM
HORARIO_SALIDA_MINIMA = time(14, 30)     # 2:30 PM

# Horarios de recuperación
HORARIO_RECUPERACION_INICIO = time(14, 30)  # 2:30 PM
HORARIO_RECUPERACION_FIN = time(20, 0)      # 8:00 PM
```

**Para cambiar horarios:**
1. Modificar `bot/config/constants.py`
2. Reiniciar el bot con `docker-compose up --build -d`

**Otros parámetros:**

```python
# Límites de historial
DIAS_HISTORIAL_MIN = 1
DIAS_HISTORIAL_MAX = 15
DIAS_HISTORIAL_RECUPERACION_MIN = 1
DIAS_HISTORIAL_RECUPERACION_MAX = 30

# Mensajes
MSG_CANAL_NO_PERMITIDO = "Este comando no está habilitado en este canal."
MSG_NO_REGISTRADO = "no estás registrado como practicante."
LINK_FORMULARIO_REGISTRO = "https://docs.google.com/forms/..."
```

---

## 🤖 Comandos del Bot

### Comandos de Usuario

#### `/entrada`
**Descripción:** Registra la hora de entrada del practicante.

**Validaciones:**
- ✅ No es domingo
- ✅ Canal permitido
- ✅ Usuario registrado en BD
- ✅ Hora entre 08:00 y 14:00
- ✅ No tiene entrada previa hoy

**Estados posibles:**
- `Presente` - Si marca antes de 08:20
- `Tardanza` - Si marca después de 08:20

**Código:** `cogs/asistencia/commands.py` líneas 22-100

---

#### `/salida`
**Descripción:** Registra la hora de salida del practicante.

**Validaciones:**
- ✅ Tiene entrada registrada hoy
- ✅ No tiene salida previa
- ✅ Sistema anti-farming (máx 6 horas)

**Lógica anti-farming:**
```python
if duracion_horas > 6:
    horas_extra = duracion_horas - 6
    hora_salida_ajustada = hora_entrada + 6 horas
```

**Código:** `cogs/asistencia/commands.py` líneas 102-180

---

#### `/estado`
**Descripción:** Consulta el estado de asistencia actual.

**Respuestas posibles:**
- 🟢 **Presente** - Tiene entrada y salida
- 🟡 **Esperando al inicio de Jornada** - Antes de 09:00 sin entrada
- ❌ **Falta injustificada** - Después de 09:00 sin entrada
- 🕒 **En curso** - Tiene entrada pero no salida

**Código:** `cogs/asistencia/commands.py` líneas 182-260

---

#### `/historial`
**Descripción:** Muestra historial de asistencia.

**Parámetros:**
- `dias` (opcional): 1-15 días (default: 7)

**Código:** `cogs/asistencia/commands.py` líneas 262-338

---

### Comandos de Recuperación

#### `/recuperación`
**Descripción:** Registra entrada de sesión de recuperación.

**Horario permitido:** 14:30 - 20:00

**Validaciones:**
- ✅ Horario permitido
- ✅ No tiene recuperación hoy
- ✅ Roles permitidos (si están configurados)

**Código:** `cogs/recuperacion/commands.py` líneas 19-104

---

#### `/recuperacion_salida`
**Descripción:** Registra salida de recuperación.

**Código:** `cogs/recuperacion/commands.py` líneas 106-142

---

#### `/recuperación_historial`
**Descripción:** Muestra historial de recuperaciones.

**Parámetros:**
- `dias` (opcional): 1-30 días (default: 15)

**Código:** `cogs/recuperacion/commands.py` líneas 144-214

---

### Comandos Administrativos

#### `/admin reporte_hoy`
**Descripción:** Reporte de asistencia del día actual.

**Muestra:**
- Lista de practicantes con estado
- Iconos: ✅ Presente, ❌ Falta, 🟡 Pendiente
- Resumen: Total, Presentes, Faltan

**Código:** `cogs/admin/commands.py` líneas 34-113

---

#### `/admin editar_asistencia`
**Descripción:** Edita o crea registro de asistencia manualmente.

**Parámetros:**
- `usuario`: @mención del usuario
- `fecha` (opcional): YYYY-MM-DD
- `entrada` (opcional): HH:MM
- `salida` (opcional): HH:MM
- `estado` (opcional): Presente/Tardanza/etc.

**Código:** `cogs/admin/commands.py` líneas 115-189

---

#### `/admin resumen_general`
**Descripción:** Resumen de horas acumuladas de todos los practicantes.

**Muestra:**
- Horas Bot (registradas por el bot)
- Horas Base (importadas de Sheets)
- Total Acumulado

**Paginación:** Divide en páginas de 25 usuarios si hay más.

**Código:** `cogs/admin/commands.py` líneas 191-248

---

#### `/admin sincronizar`
**Descripción:** Fuerza sincronización inmediata con Google Sheets.

**Código:** `cogs/admin/commands.py` líneas 250-262

---

## 🔧 Mantenimiento y Modificaciones

### Agregar un Nuevo Comando

1. **Editar el cog correspondiente:**
```python
# cogs/asistencia/commands.py

@app_commands.command(name='mi_comando', description="Descripción del comando")
async def mi_comando(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    # Tu lógica aquí
    
    await interaction.followup.send("Respuesta", ephemeral=True)
```

2. **Reiniciar el bot:**
```bash
docker-compose up --build -d
```

3. **Sincronización automática:** El bot sincroniza comandos al iniciar.

---

### Modificar Horarios

**Archivo:** `bot/config/constants.py`

```python
# Cambiar hora de entrada
HORARIO_ENTRADA_INICIO = time(9, 0)  # Ahora 9:00 AM

# Cambiar límite de tardanza
HORA_LIMITE_TARDANZA = time(9, 30, 0)  # Ahora 9:30 AM
```

**Reiniciar:**
```bash
docker-compose up --build -d
```

---

### Agregar un Nuevo Estado

1. **Insertar en base de datos:**
```sql
INSERT INTO estado_asistencia (estado) VALUES ('Permiso Médico');
```

2. **O agregar en `database.py`:**
```python
# database.py línea 117
for estado in ['Presente', 'Tardanza', 'Falta Injustificada', 'Falta Recuperada', 'Permiso', 'Permiso Médico']:
    await execute_query("INSERT IGNORE INTO estado_asistencia (estado) VALUES (%s)", (estado,))
```

---

### Cambiar Canales Permitidos

**Archivo:** `bot.py` líneas 66-75

```python
bot.canales_permitidos = {
    1389959112556679239: [
        1234567890123456789,  # Nuevo canal
        9876543210987654321   # Otro canal
    ]
}
```

**Obtener ID de canal:**
1. Activar "Modo Desarrollador" en Discord
2. Click derecho en el canal → Copiar ID

---

### Modificar Intervalo de Sincronización

**Archivo:** `bot.py` línea 205

```python
@tasks.loop(minutes=5)  # Cambiar de 10 a 5 minutos
async def sync_google_sheets_task():
    ...
```

**⚠️ ADVERTENCIA:** No usar intervalos menores a 5 minutos para evitar rate limiting de Google Sheets API.

---

## 🐛 Troubleshooting

### Problema: Bot no responde a comandos

**Posibles causas:**
1. Bot offline
2. Canal no permitido
3. Comandos no sincronizados

**Solución:**
```bash
# Ver logs
docker logs bot_asistencia_main-bot-asistencia-1

# Reiniciar
docker-compose restart

# Reconstruir
docker-compose up --build -d
```

---

### Problema: Error de conexión a base de datos

**Error típico:**
```
RuntimeError: Error ejecutando fetch_one: (2003, "Can't connect to MySQL server...")
```

**Solución:**
1. Verificar `.env`:
```env
DB_HOST=correcto
DB_USER=correcto
DB_PASSWORD=correcto
```

2. Verificar SSL:
```bash
# Debe existir
ls isrgrootx1.pem
```

3. Verificar conexión:
```bash
docker exec -it bot_asistencia_main-bot-asistencia-1 ping gateway01.us-west-2.prod.aws.tidbcloud.com
```

---

### Problema: Google Sheets no sincroniza

**Error típico:**
```
❌ No se encontró la hoja de cálculo: 'Practicantes_RP_Soft'
```

**Solución:**
1. Verificar nombre en `.env`:
```env
GOOGLE_SHEET_NAME=Practicantes_RP_Soft
```

2. Verificar que `credentials.json` existe:
```bash
docker exec bot_asistencia_main-bot-asistencia-1 ls /app/credentials.json
```

3. Verificar que la hoja está compartida con el Service Account email.

---

### Problema: Logs duplicados

**Síntoma:** Cada mensaje aparece 2 veces en los logs.

**Causa:** Múltiples instancias del bot corriendo.

**Solución:**
```bash
# Ver contenedores corriendo
docker ps

# Detener todos
docker-compose down

# Iniciar solo uno
docker-compose up -d
```

---

### Problema: ImportError al iniciar

**Error típico:**
```
ImportError: cannot import name 'DIAS_HISTORIAL_RECUPERACION_MIN' from 'bot.config.constants'
```

**Causa:** Constantes comentadas en `constants.py` pero importadas en `__init__.py`.

**Solución:**
Descomentar las constantes en `bot/config/constants.py`:
```python
DIAS_HISTORIAL_RECUPERACION_MIN = 1
DIAS_HISTORIAL_RECUPERACION_MAX = 30
```

---

## 📝 Notas Finales

### Buenas Prácticas

1. **Nunca commitear `.env`** - Contiene credenciales sensibles
2. **Hacer backup de la BD** - Antes de modificaciones grandes
3. **Probar en servidor de pruebas** - Antes de producción
4. **Documentar cambios** - En `CHANGELOG.md`
5. **Usar logs** - Para debugging: `logging.info()`, `logging.error()`

### Recursos Útiles

- [Discord.py Docs](https://discordpy.readthedocs.io/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [TiDB Cloud Docs](https://docs.pingcap.com/tidbcloud)
- [Docker Docs](https://docs.docker.com/)

### Contacto

Para dudas o soporte, contactar al equipo de desarrollo de RP Soft.

---

**Última actualización:** 2026-02-10
**Versión del documento:** 1.0
**Autor:** Equipo RP Soft
