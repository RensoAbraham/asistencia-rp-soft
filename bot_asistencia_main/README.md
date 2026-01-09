# 🤖 Bot de Asistencia Discord

Sistema completo para la gestión de asistencia, faltas y recuperaciones de usuarios en Discord.

## 📋 Características

- ✅ **Registro de Entrada y Salida**: Control horario con validación de horarios
- ⏰ **Detección de Atrasos**: Registro automático de tardanzas
- 📝 **Gestión de Faltas**: Consulta de faltas justificadas e injustificadas
- 🔄 **Sistema de Recuperación**: Registro de sesiones de recuperación (2:30 PM - 8:00 PM)
- 📊 **Historial Completo**: Consulta de historial de asistencia y recuperaciones
- 🔐 **Control de Permisos**: Restricción por canales y roles
- 📈 **Métricas en Tiempo Real**: Envío de métricas al backend

## 🏗️ Arquitectura del Proyecto

### Estructura de Carpetas

```
Bot-Asistencia-Discord/
├── bot/
│   ├── config/                    # Configuración centralizada
│   │   ├── settings.py           # Variables de entorno
│   │   ├── constants.py          # Constantes del sistema
│   │   └── logging_config.py     # Configuración de logging
│   │
│   ├── core/                      # Núcleo reutilizable
│   │   ├── database/             # Gestión de base de datos
│   │   │   └── connection.py     # Pool de conexiones
│   │   ├── utils/                # Utilidades modulares
│   │   │   ├── validators.py     # Validaciones
│   │   │   ├── formatters.py     # Formateo de datos
│   │   │   ├── embeds.py         # Creación de embeds
│   │   │   ├── datetime_utils.py # Utilidades de fecha/hora
│   │   │   └── permissions.py    # Verificación de permisos
│   │   └── exceptions/           # Excepciones personalizadas
│   │
│   └── cogs/                      # Comandos del bot (organizados por carpetas)
│       ├── asistencia/           # Módulo de asistencia
│       │   ├── __init__.py
│       │   ├── commands.py       # Comandos de asistencia
│       │   └── modals.py         # Modales (salida anticipada)
│       ├── faltas/               # Módulo de faltas
│       │   ├── __init__.py
│       │   └── commands.py
│       └── recuperacion/         # Módulo de recuperación
│           ├── __init__.py
│           └── commands.py
│
├── bot.py                         # Clase principal del bot
├── database.py                    # Módulo de base de datos (legacy)
├── utils.py                       # Utilidades (legacy)
├── requirements.txt               # Dependencias
│
├── scripts/                       # Scripts y herramientas
│   ├── sql/                      # Scripts SQL
│   │   └── recuperacion_table.sql
│   └── README.md
│
├── docs/                          # Documentación adicional
│   ├── ESTRUCTURA_CARPETAS.md
│   └── README.md
│
├── docker-compose.yml            # Configuración de Docker Compose
├── Dockerfile                    # Configuración de Docker
└── README.md                     # Documentación principal
```

### Principios de Diseño

El proyecto sigue una **arquitectura modular** con separación clara de responsabilidades:

- **Configuración Centralizada**: Toda la configuración en `bot/config/`
- **Utilidades Reutilizables**: Funciones comunes en `bot/core/utils/`
- **Manejo de Errores**: Excepciones personalizadas y consistentes
- **Type Hints**: Tipado completo para mejor desarrollo
- **Código Limpio**: Sigue principios SOLID y DRY

## 🚀 Instalación

### Requisitos

- Python 3.10+
- MySQL/MariaDB
- Discord Bot Token

### Configuración

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd Bot-Asistencia-Discord
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**

   Crear un archivo `.env` en la raíz del proyecto:
   ```env
   DISCORD_TOKEN=tu_token_aqui
   DB_HOST=localhost
   DB_USER=usuario_db
   DB_PASSWORD=contraseña_db
   DB_NAME=nombre_db
   DB_PORT=3306
   BACKEND_API_KEY=tu_api_key
   BACKEND_URL=https://api.example.com
   LOG_LEVEL=INFO
   ```

4. **Configurar base de datos**

   Ejecutar los scripts SQL necesarios:
   ```bash
   mysql -u usuario -p nombre_db < scripts/sql/recuperacion_table.sql
   ```

5. **Configurar canales y roles**

   Los canales permitidos y roles se configuran en `bot.py`:
   ```python
   # Canales permitidos por servidor
   bot.canales_permitidos = {
       1389959112556679239: [1390353417079361607, ...],  # Servidor 1
       1405602519635202048: [1406544076534190110],       # Servidor 2
   }
   
   # Roles permitidos para recuperación (lista vacía = todos pueden usar)
   bot.roles_recuperacion = {
       1389959112556679239: [],  # Todos pueden usar
       1405602519635202048: [123456789012345678],  # Solo roles específicos
   }
   ```

## 📝 Comandos Disponibles

### Asistencia

- `/asistencia entrada` - Registrar hora de entrada (7:00 AM - 2:00 PM)
- `/asistencia salida` - Registrar hora de salida
- `/asistencia estado` - Consultar estado del día
- `/asistencia historial [dias:7]` - Consultar historial (1-15 días)

### Faltas

- `/faltas ver` - Ver faltas injustificadas

### Recuperación

- `/recuperación` - Registrar sesión de recuperación (2:30 PM - 8:00 PM)
- `/recuperación_historial [dias:15]` - Consultar historial (1-30 días)

## ⚙️ Configuración

### Horarios

Los horarios están definidos en `bot/config/constants.py`:

```python
HORARIO_ENTRADA_INICIO = time(7, 0)        # 7:00 AM
HORARIO_ENTRADA_FIN = time(14, 0)          # 2:00 PM
HORA_LIMITE_TARDANZA = time(8, 10, 59)     # 8:10:59 AM
HORARIO_RECUPERACION_INICIO = time(14, 30) # 2:30 PM
HORARIO_RECUPERACION_FIN = time(20, 0)     # 8:00 PM
```

### Días Permitidos

Por defecto, solo se permiten días laborables (Lunes-Viernes). Los fines de semana están bloqueados para el registro de entrada.

### Base de Datos

#### Tablas Principales

- **Practicante**: Información de los practicantes
- **Asistencia**: Registros de entrada/salida
- **Estado_Asistencia**: Estados posibles (Presente, Tardanza, Falta injustificada, etc.)
- **Recuperacion**: Registros de sesiones de recuperación

#### Script SQL

Ejecutar `scripts/sql/recuperacion_table.sql` para crear la tabla de recuperaciones:

```sql
CREATE TABLE IF NOT EXISTS Recuperacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    practicante_id INT NOT NULL,
    fecha DATE NOT NULL,
    hora_entrada TIME NOT NULL,
    hora_salida TIME NULL,
    motivo TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (practicante_id) REFERENCES Practicante(id) ON DELETE CASCADE,
    UNIQUE KEY unique_recuperacion_dia (practicante_id, fecha),
    INDEX idx_practicante_fecha (practicante_id, fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## 🏃 Ejecución

### Desarrollo

```bash
python bot.py
```

### Producción con Docker

```bash
docker-compose up -d
```

## 🔧 Desarrollo

### Utilizando la Nueva Arquitectura

El proyecto ha sido reestructurado con una arquitectura modular. Aquí algunos ejemplos:

#### Configuración

```python
from bot.config import get_settings, HORARIO_ENTRADA_INICIO

settings = get_settings()
hora_limite = HORARIO_ENTRADA_INICIO
```

#### Utilidades

```python
# Validaciones
from bot.core.utils.validators import validate_horario, validate_dias_historial

# Formateo
from bot.core.utils.formatters import format_time, format_date

# Embeds
from bot.core.utils.embeds import create_success_embed, create_error_embed

# Fechas
from bot.core.utils.datetime_utils import get_current_time, get_current_date, is_weekday

# Permisos
from bot.core.utils.permissions import check_channel_permission, check_role_permission
```

#### Excepciones

```python
from bot.core.exceptions import ValidationError, PermissionError, DatabaseError

try:
    # Código que puede fallar
    validate_horario(...)
except ValidationError as e:
    # Manejo específico
    embed = create_error_embed("Error", str(e))
```

#### Base de Datos

```python
from bot.core.database import get_database

db = get_database()
result = await db.fetch_one(query, params)
results = await db.fetch_all(query, params)
id = await db.execute(query, params)
```

### Estructura de Cogs

Los cogs están organizados por carpetas, cada módulo tiene su propia carpeta:

```
cogs/
├── asistencia/
│   ├── __init__.py        # Carga el cog
│   ├── commands.py        # Comandos de asistencia
│   └── modals.py          # Modales (salida anticipada)
├── faltas/
│   ├── __init__.py
│   └── commands.py
└── recuperacion/
    ├── __init__.py
    └── commands.py
```

**Ejemplo de un cog:**

```python
# cogs/asistencia/commands.py
from discord.ext import commands
from discord import app_commands
import discord

class Asistencia(commands.GroupCog, name="asistencia"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name='entrada', description="Descripción")
    async def entrada(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        # Lógica del comando
        await interaction.followup.send("Respuesta", ephemeral=True)

# cogs/asistencia/__init__.py
from .commands import Asistencia

async def setup(bot):
    await bot.add_cog(Asistencia(bot))
```

## 📊 Características Técnicas

### Arquitectura Modular

- **Separación de Responsabilidades**: Cada módulo tiene un propósito claro
- **Código Reutilizable**: Utilidades modulares en `bot/core/utils/`
- **Configuración Centralizada**: Toda la configuración en `bot/config/`
- **Type Hints**: Tipado completo para mejor desarrollo
- **Manejo de Errores**: Excepciones personalizadas y consistentes

### Mejores Prácticas

- ✅ **SOLID Principles**: Cada clase tiene una responsabilidad única
- ✅ **DRY**: No hay código duplicado
- ✅ **Clean Code**: Código legible y expresivo
- ✅ **Logging estructurado**: Sistema de logging profesional
- ✅ **Validaciones centralizadas**: Validaciones reutilizables

### Ventajas de la Nueva Estructura

1. **Mantenibilidad**: Código organizado y fácil de encontrar
2. **Escalabilidad**: Agregar nuevas funcionalidades es simple
3. **Testeable**: Cada componente puede probarse independientemente
4. **Profesional**: Sigue mejores prácticas de la industria
5. **Modular**: Responsabilidades claras y separadas

## 🐛 Troubleshooting

### El bot no se conecta

1. Verificar que `DISCORD_TOKEN` esté correcto en `.env`
2. Verificar permisos del bot en Discord Developer Portal
3. Revisar logs para errores específicos

### No se registran comandos

1. Verificar que los cogs estén cargados en `bot.py`:
   ```python
   await bot.load_extension('cogs.asistencia')
   await bot.load_extension('cogs.faltas')
   await bot.load_extension('cogs.recuperacion')
   ```
2. Esperar algunos minutos para sincronización de comandos
3. Verificar permisos del bot en el servidor (necesita permisos de aplicaciones de comandos)

### Errores de base de datos

1. Verificar variables de entorno de DB en `.env`
2. Verificar que la base de datos exista
3. Verificar que las tablas estén creadas
4. Revisar logs para errores específicos

### Comandos no funcionan en canales

1. Verificar configuración de `canales_permitidos` en `bot.py`
2. Verificar que el ID del canal sea correcto
3. Verificar que el ID del servidor coincida
4. Para obtener IDs: Activar "Modo Desarrollador" en Discord → Clic derecho → "Copiar ID"

### Horario no permitido

1. Verificar la zona horaria del servidor (configurada en `bot/config/settings.py`)
2. Verificar los horarios en `bot/config/constants.py`
3. Los comandos de entrada solo funcionan en días laborables (Lunes-Viernes)

### Recuperación no disponible

1. Verificar que esté dentro del horario permitido (2:30 PM - 8:00 PM)
2. Verificar que no haya registrado una recuperación el mismo día
3. Si hay restricción de roles, verificar que tengas el rol necesario

## 📚 Documentación y Estructura

### Archivos de Referencia

- **Constantes**: `bot/config/constants.py`
- **Configuración**: `bot/config/settings.py`
- **Utilidades**: `bot/core/utils/`
- **Base de Datos**: `bot/core/database/`
- **Excepciones**: `bot/core/exceptions/`

### Estructura de Carpetas

```
📁 Raíz
  ├── bot.py                    # Punto de entrada
  ├── requirements.txt          # Dependencias
  └── README.md                 # Este archivo

📁 bot/                         # Módulo principal
  ├── config/                   # Configuración
  └── core/                     # Núcleo reutilizable
      ├── database/            # Base de datos
      ├── utils/               # Utilidades
      └── exceptions/          # Excepciones

📁 cogs/                        # Comandos (por carpetas)
  ├── asistencia/
  ├── faltas/
  └── recuperacion/

📁 scripts/                     # Scripts SQL y herramientas
  └── sql/

📁 docs/                        # Documentación adicional
```

### Módulos del Sistema

- **`bot/config/`**: Configuración centralizada del sistema
- **`bot/core/utils/`**: Utilidades reutilizables (validaciones, formateo, embeds)
- **`bot/core/database/`**: Gestión de base de datos con pool de conexiones
- **`bot/core/exceptions/`**: Excepciones personalizadas para manejo de errores
- **`cogs/`**: Comandos del bot organizados por funcionalidad en carpetas
- **`scripts/sql/`**: Scripts SQL para migraciones y creación de tablas

## 🔄 Migración a Nueva Arquitectura

El proyecto está en proceso de migración a una arquitectura más modular. El código existente (`database.py`, `utils.py`) sigue funcionando, pero se recomienda migrar gradualmente a la nueva estructura:

### Ejemplo de Migración

**Antes:**
```python
from utils import obtener_practicante
from database import fetch_one
```

**Después:**
```python
from bot.core.database import get_database
# Usar repositorios cuando estén disponibles
```

La migración es opcional y puede hacerse gradualmente sin afectar la funcionalidad actual.

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es privado y propietario.

## 👥 Autores

- **RP Soft** - Desarrollo inicial y mantenimiento

## 🙏 Agradecimientos

- Discord.py por la excelente librería
- La comunidad de desarrolladores de bots de Discord

---

**Versión**: 2.0.0  
**Última actualización**: 2024
