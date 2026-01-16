# 🤖 Bot de Asistencia RP Soft

Bot de Discord corporativo para la gestión automatizada de asistencias, tardanzas y reportes sincronizados con Google Sheets.

## 📋 Características Principales

*   ✅ **Registro de Asistencia**: Comandos `/asistencia entrada` y `/asistencia salida`.
*   ✅ **Validación de Horarios**: Validación estricta (07:00 - 14:00) y detección de tardanzas (> 08:20 AM).
*   ✅ **Sincronización Bidireccional**: Lee practicantes desde Google Sheets y exporta reportes.
*   ✅ **Arquitectura Resiliente**: Dockerizado, con reconexión automática a BD y manejo de excepciones.
*   ✅ **Seguridad**: Gestión segura de credenciales y roles.

---

## 🏗️ Arquitectura del Proyecto

El proyecto ha sido diseñado siguiendo una **arquitectura modular** para facilitar el mantenimiento y la escalabilidad.

### Principios de Diseño
*   **SOLID & DRY**: Código limpio, sin redundancias y con responsabilidades únicas por clase.
*   **Configuración Centralizada**: Todo reside en `config/` y variables de entorno.
*   **Logging Estructurado**: Trazabilidad completa de acciones y errores.

### Estructura de Carpetas

```text
Bots discord/
├── README.md                   <-- TÚ ESTÁS AQUÍ (Guía Maestra)
└── bot_asistencia_main/        <-- CÓDIGO FUENTE
    ├── .env.testing            <-- Plantilla de variables de entorno
    ├── bot/
    │   ├── config/             # Configuración (settings, constants)
    │   ├── core/               # Núcleo (DB pool, utilidades)
    │   └── cogs/               # Módulos (Asistencia, Recuperación)
    ├── docs/                   # Documentación Detallada
    │   ├── overview.md
    │   ├── deploy_vps.md
    │   └── guia_configuracion.md
    ├── scripts/
    │   └── sql/                # Scripts SQL (init_db, etc.)
    ├── tests/                  # Tests funcionales (pytest)
    └── docker-compose.yml      # Orquestación de contenedores
```

---

## 🚀 Guía de Instalación (Desde Cero)

### 1. Preparación en Discord
1.  Ve al [Discord Developer Portal](https://discord.com/developers/applications).
2.  Crea una Application > Bot.
3.  **IMPORTANTE:** Activa los **Privileged Gateway Intents** (Presence, Server Members, Message Content).
4.  Copia el **Token** del bot.

### 2. Despliegue con Docker (Recomendado)

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/RensoAbraham/asistencia-rp-soft.git
    cd asistencia-rp-soft
    ```

2.  **Configurar Entorno:**
    Usa el archivo `.env.testing` como base.
    ```bash
    cd bot_asistencia_main
    cp .env.testing .env
    nano .env
    ```
    *Rellena `DISCORD_TOKEN`, credenciales de BD y `BACKEND_API_KEY`.*

3.  **Credenciales Google:**
    Coloca tu `credentials.json` en la carpeta `bot_asistencia_main/`.

4.  **Iniciar:**
    ```bash
    docker compose up -d --build
    ```

---

## 📘 Documentación Oficial

Para detalles profundos, consulta los manuales en `bot_asistencia_main/docs/`:

*   **[Visión General](./bot_asistencia_main/docs/overview.md):** Explicación profunda del flujo de datos.
*   **[Guía de Despliegue VPS](./bot_asistencia_main/docs/deploy_vps.md):** Paso a paso para servidores Linux (Hetzner).
*   **[Guía de Configuración](./bot_asistencia_main/docs/guia_configuracion.md):** Cómo configurar el Excel de practicantes y reglas de negocio.
*   **[Testing](./bot_asistencia_main/docs/testing.md):** Cómo correr los tests automatizados.

---

## 🧪 Comandos y Funcionalidades

### 🕒 Asistencia
*   `/asistencia entrada`: Registra ingreso. (Permitido: 07:00 - 14:00).
    *   *Tardanza:* Si marca después de las **08:20:59 AM**.
*   `/asistencia salida`: Registra salida.
    *   *Alerta:* Si marca antes de las 14:00, avisa al usuario.
*   `/asistencia estado`: Muestra si ya marcó hoy.
*   `/asistencia historial`: Muestra los últimos 7 días.

### 🔄 Recuperación
*   `/recuperacion`: Permite registrar horas extra (14:30 - 20:00).
*   Pueden requerir roles específicos según configuración.

### 📊 Reportes (Automático)
El bot actualiza un Google Sheet cada hora con:
1.  **Detalle Diario:** Asistencias del día.
2.  **Resumen General:** Suma de `Horas Base` (Excel) + `Horas Bot`.

---

## 🔧 Solución de Problemas Frecuentes

### ❌ El bot no responde
*   Verifica que el contenedor corra: `docker compose ps`
*   Revisa los logs: `docker compose logs -f bot`

### ❌ "Bot connected but interactions failed"
*   Asegúrate de haber hecho `tree.sync()` (el bot lo hace al inicio).
*   Verifica los **Intents** en el Developer Portal.

### ❌ Error de Base de Datos
*   Verifica que las credenciales en `.env` coincidan con las del contenedor `db`.
*   Si necesitas reiniciar de cero: `docker compose down -v`.

---

## 👥 Soporte
Desarrollado para **RP Soft**.
Para soporte técnico, contactar al equipo de desarrollo o revisar los logs en el VPS.
