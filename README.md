# 🤖 Guía de Configuración del Bot de Discord

Este documento te guiará paso a paso para configurar y encender tu bot de Asistencia.

## 🚀 Pasos Previos (Discord Developer Portal)

Para obtener el **TOKEN** que necesitas poner en el archivo `.env`, sigue estos pasos:

1.  Ve al [Discord Developer Portal](https://discord.com/developers/applications).
2.  Haz clic en **"New Application"** (arriba a la derecha).
3.  Ponle un nombre (ej: `Bot Asistencia`) y acepta los términos.
4.  En el menú de la izquierda, ve a **"Bot"**.
5.  **IMPORTANTE**: Baja hasta la sección **Privileged Gateway Intents** y activa estas 3 opciones (tienen que estar en azul):
    *   [x] **Presence Intent**
    *   [x] **Server Members Intent**
    *   [x] **Message Content Intent**
6.  Guarda los cambios (**Save Changes**).
7.  Sube de nuevo, busca la sección **Build-A-Bot** y haz clic en **"Reset Token"**.
8.  Copia ese código largo y extraño. **Ese es tu DISCORD_TOKEN**.

---

## ⚙️ Configuración del Proyecto

1.  Abre el archivo `.env` que está en esta carpeta.
2.  Busca la línea que dice `DISCORD_TOKEN=TU_TOKEN_AQUI_REEMPLAZAME`.
3.  Borra lo que está después del `=` y pega el Token que copiaste.

   Ejemplo:
   ```env
   DISCORD_TOKEN=MTEyMz... (y muchos más caracteres)
   ```

---

## ▶️ Iniciar el Bot

Una vez guardado el Token:

1.  Abre una terminal en esta carpeta.
2.  Ejecuta el siguiente comando:
   ```bash
   docker-compose up --build
   ```
3.  Espera unos minutos. Verás que se descargan cosas y luego textos de colores.
4.  Cuando veas `Bot conectado como...`, ¡tu bot estará vivo!

## 🧪 Comandos Disponibles

- `/entrada` - Marca entrada (7:00am - 2:00pm)
- `/salida` - Marca salida
- `/recuperacion` - Recuperación de horas (2:30pm - 8:00pm)
- `/historial` - Ver historial de asistencia.
