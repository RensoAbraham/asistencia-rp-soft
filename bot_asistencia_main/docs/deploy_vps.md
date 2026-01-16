# ☁️ Guía de Despliegue en VPS (Hetzner/Ubuntu)

Esta guía detalla los pasos para desplegar el bot en un entorno de producción (VPS), enfocado en servidores Linux como los de Hetzner.

## 📋 Requisitos Previos
*   Acceso SSH al servidor (`root@ip`).
*   Docker y Docker Compose instalados en el servidor.
*   Archivo de credenciales de Google (`credentials.json`).

## 1. Instalación Inicial (Solo primera vez)

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/RensoAbraham/asistencia-rp-soft.git
    cd asistencia-rp-soft
    ```

2.  **Crear archivo de entorno (.env):**
    ```bash
    nano .env
    ```
    *(Ver sección de seguridad abajo para el contenido)*.

3.  **Subir credenciales de Google:**
    Debes crear o subir el archivo `credentials.json` en la carpeta raíz del proyecto en el VPS.
    ```bash
    nano credentials.json
    # Pega el contenido de tu JSON de Google Service Account
    ```

4.  **Iniciar el servicio:**
    ```bash
    docker compose up -d --build
    ```

---

## 🔒 Seguridad: Configuración del .env

El archivo `.env` es crítico. Debe contener variables con claves seguras.
Puedes usar el archivo `.env.testing` incluido en el repositorio como plantilla, pero **CAMBIA LAS CONTRASEÑAS**.

```ini
DISCORD_TOKEN=TU_TOKEN_REAL_AQUI
BACKEND_API_KEY=CLAVE_DEL_BACKEND_AQUI
# Base de Datos (Usa contraseñas largas y alfanuméricas)
DB_HOST=db
DB_PORT=3306
DB_NAME=bot_asistencia
DB_USER=usuario_seguro
DB_PASSWORD=password_super_secreta
DB_ROOT_PASSWORD=password_root_super_secreta
GOOGLE_SHEET_NAME=Practicantes_RP_Soft
```

---

## 🔄 Actualización (Mantenimiento Diario)

Si realizas cambios en el código y quieres aplicarlos en el VPS:

1.  **Descargar cambios:**
    ```bash
    git pull origin feat-unificado
    ```

2.  **Reconstruir contenedores:**
    ```bash
    docker compose up -d --build
    ```

**(El bot se reiniciará automáticamente con los nuevos cambios).**

---

## 🧹 Reset de Fábrica (Limpieza de Datos)

Si necesitas borrar todas las asistencias para empezar un nuevo ciclo (pero manteniendo a los practicantes), usa estos comandos:

**Opción A (Script Automático):**
```bash
docker compose run --rm bot python scripts/reset_hours.py
```

**Opción B (Comando Manual SQL):**
```bash
docker compose exec db mysql -u[USUARIO_ENV] -p[PASS_ENV] bot_asistencia -e "TRUNCATE TABLE asistencia; TRUNCATE TABLE asistencia_recuperacion;"
```

## 🐛 Logs y Depuración
Para ver qué está haciendo el bot en tiempo real:
```bash
docker compose logs -f bot
```
