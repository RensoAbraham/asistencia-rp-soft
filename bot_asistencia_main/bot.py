import os
import discord
from discord.ext import commands, tasks
import aiohttp
from dotenv import load_dotenv
# from database import init_db_pool, close_db_pool
import asyncio
import logging
import datetime as _datetime
from zoneinfo import ZoneInfo

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
BACKEND_API_KEY = os.getenv('BACKEND_API_KEY')
BACKEND_URL = os.getenv('BACKEND_URL')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(name)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S' 
)

# logging.Formatter.converter = lambda *args: datetime.datetime.now(ZoneInfo("America/Lima")).timetuple()

# Clase para métricas del bot
class BotMetrics:
    def __init__(self):
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        self.events_processed_today = 0
        self.last_reset_day = self.start_time.day

    def increment_event_count(self):
        """Incrementa el contador de eventos y lo resetea si es un nuevo día."""
        now = datetime.datetime.now(datetime.timezone.utc)
        if now.day != self.last_reset_day:
            self.events_processed_today = 0
            self.last_reset_day = now.day
        self.events_processed_today += 1

    def get_uptime(self):
        """Calcula el tiempo de actividad del bot."""
        return datetime.datetime.now(datetime.timezone.utc) - self.start_time

metrics = BotMetrics()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Diccionario de canales permitidos por servidor
bot.canales_permitidos = {
    # Servidor RP Soft (Producción)
    1389959112556679239: [
        1390353417079361607, 1390013888791183370, 1395093712832565339, 1400200650402431007, 1404466917002969128, 1412152264969162969, 1415770590975102986,
        1457747478592884878, # Canal Principal de Asistencia
        1457747701038059643  # Canal de Recuperación
    ],
    # Servidor Laboratorios (Pruebas)
    1405602519635202048: [
        1406544076534190110,
        1457802290093228093 # Canal Pruebas Actual
    ]
}

# Diccionario de roles permitidos para recuperación por servidor
# Agregar aquí los IDs de los roles que pueden usar el comando de recuperación
bot.roles_recuperacion = {
    1389959112556679239: [], # Servidor RP Soft - lista vacía significa que todos los practicantes pueden usar
    1405602519635202048: []  # Servidor Laboratorios - lista vacía significa que todos los practicantes pueden usar
    # Ejemplo con roles: 1389959112556679239: [123456789012345678, 987654321098765432]
}

# Función para actualizar el estado del bot en el backend
async def update_bot_status(status: str):
    """Envía una actualización de estado al backend."""
    if not BACKEND_URL or not BACKEND_API_KEY:
        return  # Skip if backend not configured
    
    headers = {"Authorization": f"Bearer {BACKEND_API_KEY}"}
    payload = {"status": status}
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.post(f"{BACKEND_URL}/status/", json=payload) as response:
                if response.status == 200:
                    logging.info(f"Estado del bot actualizado a '{status}' en el backend.")
                else:
                    logging.error(f"Error al actualizar el estado del bot: {response.status}")
        except aiohttp.ClientConnectorError as e:
            logging.error(f"No se pudo conectar al backend para actualizar estado: {e}")

# Eventos para Contar Métricas
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    metrics.increment_event_count()
    await bot.process_commands(message)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    metrics.increment_event_count()

# Tarea Periódica para Enviar Métricas
@tasks.loop(minutes=1)
async def send_metrics_to_backend():
    if not BACKEND_URL or not BACKEND_API_KEY:
        return  # Skip if backend not configured
    await bot.wait_until_ready()
    
    uptime_delta = metrics.get_uptime()
    now_lima = datetime.datetime.now()

    payload = {
        "resumen": {
            "servidores_conectados": len(bot.guilds),
            "eventos_procesados_hoy": metrics.events_processed_today,
            "uptime_porcentaje": 99.9,
            "ultima_sincronizacion": now_lima.isoformat()
        },
        "estado": {
            "status": "online",
            "uptime_dias": uptime_delta.days,
            "latencia_ms": round(bot.latency * 1000, 2),
            "ultima_conexion": now_lima.isoformat()
        },
        "servers": [
            {
                "server_id": guild.id,
                "server_name": guild.name,
                "miembros": guild.member_count,
                "canales": len(guild.channels),
                "status": "conectado"
            } for guild in bot.guilds
        ]
    }

    headers = {
        "Authorization": f"Bearer {BACKEND_API_KEY}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.post(f"{BACKEND_URL}/metrics/", json=payload) as response:
                if response.status == 200:
                    logging.info("Métricas enviadas exitosamente al backend.")
                else:
                    logging.error(f"Error al enviar métricas: {response.status} - {await response.text()}")
        except aiohttp.ClientConnectorError as e:
            logging.error(f"No se pudo conectar al backend para enviar métricas: {e}")
        except Exception as e:
            logging.error(f"Ocurrió un error inesperado al enviar métricas: {e}")

# Evento de inicio del bot
@bot.event
async def setup_hook():
    import database as db
    logging.info('Verificando y configurando base de datos...')
    await db.ensure_db_setup()
    
    logging.info('Cargando extensiones...')
    # Ajuste: Cargar explícitamente .commands ya que no usamos __init__.py en las subcarpetas
    await bot.load_extension('cogs.asistencia.commands')
    logging.info('...Asistencia cargada')
    
    # await bot.load_extension('cogs.faltas.commands') 
    
    await bot.load_extension('cogs.recuperacion.commands')
    logging.info('...Recuperación cargada')
    
    await bot.load_extension('cogs.reportes.commands')
    logging.info('...Reportes cargada')
    
    logging.info('Sincronizando comandos (tree.sync)...')
    await bot.tree.sync()
    logging.info('Comandos sincronizados.')
    # Nota: Los cogs ahora están organizados en carpetas (asistencia/, faltas/, recuperacion/)
    logging.info('Iniciando tarea de envío de métricas...')
    send_metrics_to_backend.start()
    logging.info(f'Bot conectado como {bot.user}')

# Manejo de errores globales
async def main():
    if not TOKEN:
        logging.error("Falta DISCORD_TOKEN. El bot no puede iniciar sin el token de Discord.")
        return
    
    if not all([BACKEND_API_KEY, BACKEND_URL]):
        logging.warning("BACKEND_API_KEY o BACKEND_URL no configurados. El bot funcionará sin enviar métricas al backend.")


    try:
        await bot.start(TOKEN)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logging.info("Bot detenido manualmente.")
    finally:
        logging.info("Bot apagándose...")
        if send_metrics_to_backend.is_running():
            send_metrics_to_backend.cancel()
        await update_bot_status("offline")
        await asyncio.sleep(1)
        # await close_db_pool()
        # logging.info("Conexión a la base de datos cerrada.")
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
