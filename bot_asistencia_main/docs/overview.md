# 🤖 Bot de Asistencia RP Soft - Visión General

Este proyecto es un bot de Discord diseñado para gestionar y registrar automáticamente la asistencia de los practicantes de **RP Soft**.

## 🎯 Objetivo Principal
Liberar la carga administrativa de llevar registros manuales de entradas, salidas y tardanzas, automatizando el proceso mediante comandos simples en Discord y sincronización en tiempo real con Google Sheets.

## 🏗️ Arquitectura del Sistema

El sistema está construido con tecnologías robustas y desacopladas para facilitar (como has visto) su mantenimiento y despliegue:

*   **Lenguaje:** Python 3.10+ (Librería `discord.py` para el bot).
*   **Base de Datos:** MySQL/MariaDB (Alojada en contenedor Docker).
*   **Gestión de Datos:** Google Sheets API (Sincronización bidireccional de practicantes y reportes).
*   **Despliegue:** Docker & Docker Compose (Contenerización completa para cualquier VPS).

## 🔄 Flujo de Datos

1.  **Entrada de Practicantes:** El administrador (Tú) llena un Excel (`Practicantes_RP_Soft`) con IDs y Horas Base.
2.  **Sincronización:** Cada hora, el bot lee ese Excel y actualiza su base de datos local.
3.  **Registro Diario:** Los practicantes usan comandos (`/asistencia entrada`, `/salida`) en Discord.
4.  **Cálculo:** El bot calcula tiempos, tardanzas y suma las horas acumuladas.
5.  **Reporte:** El bot genera/actualiza la pestaña "Resumen General" y "Reporte Detallado" en el mismo Excel automáticamente.

## 🛠️ Tecnologías Clave
*   **discord.py**: Interacción con usuarios.
*   **aiomysql**: Conexión asíncrona a la base de datos (para no bloquear al bot).
*   **gspread**: Conexión con Google Sheets.
*   **Pandas**: (Opcional) Procesamiento de datos para reportes complejos.

Este proyecto está diseñado para ser:
1.  **Resiliente:** Si se cae el VPS, al reiniciar se recupera solo.
2.  **Seguro:** Credenciales en `.env` y separadas del código.
3.  **Escalable:** Soporta múltiples servidores de Discord (configurado en `bot.py`).
