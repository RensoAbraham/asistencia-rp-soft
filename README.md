# 🤖 Bot de Asistencia RP Soft

Bot de Discord corporativo para la gestión automatizada de asistencias, tardanzas y reportes sincronizados con Google Sheets.

## 📚 Documentación Oficial

Toda la documentación técnica se encuentra en la carpeta [`bot_asistencia_main/docs/`](./bot_asistencia_main/docs):

*   **[Visión General](./bot_asistencia_main/docs/overview.md):** Arquitectura y Flujo.
*   **[Guía de Despliegue VPS](./bot_asistencia_main/docs/deploy_vps.md):** Instalación en Servidor (Docker).
*   **[Guía de Configuración](./bot_asistencia_main/docs/guia_configuracion.md):** Excel, Horarios (08:20) y Reportes.
*   **[Testing](./bot_asistencia_main/docs/testing.md):** Pruebas de Calidad.

---

## 🚀 Guía de Instalación (Desde Cero)

### 1. Obtener Token de Discord
Si aún no tienes el bot creado:
1.  Ve al [Discord Developer Portal](https://discord.com/developers/applications).
2.  Crea una **"New Application"**.
3.  En **"Bot"**, activa los **Privileged Gateway Intents** (Presence, Server Members, Message Content).
4.  Haz clic en **"Reset Token"** y copia tu Token.

### 2. Configuración del Proyecto
1.  **Clonar:**
    ```bash
    git clone https://github.com/RensoAbraham/asistencia-rp-soft.git
    cd asistencia-rp-soft/bot_asistencia_main
    ```
2.  **Variables de Entorno:**
    Copia `.env.testing` a `.env` y editalo con tus claves reales:
    ```bash
    cp .env.testing .env
    nano .env
    ```
3.  **Google Sheets:**
    Coloca tu archivo `credentials.json` en la raíz de la carpeta `bot_asistencia_main`.

### 3. Iniciar (Docker)
Asegúrate de estar dentro de la carpeta `bot_asistencia_main`:
```bash
docker compose up -d --build
```

---

## 🧪 Comandos Disponibles para Usuarios
*   `/asistencia entrada`: Marcar ingreso (07:00 - 14:00).
*   `/asistencia salida`: Marcar salida.
*   `/asistencia estado`: Ver si ya marcaste hoy.
*   `/asistencia historial`: Ver tus últimos 7 días.
*   `/recuperacion`: Solicitar horas (debe ser aprobado por roles).
