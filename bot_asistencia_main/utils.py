import database as db
import discord
from discord import TextStyle, ui
import datetime
from zoneinfo import ZoneInfo

# Zona horaria de Perú
LIMA_TZ = ZoneInfo("America/Lima")

def es_domingo() -> bool:
    """Verifica si hoy es domingo en hora de Perú"""
    return datetime.datetime.now(LIMA_TZ).weekday() == 6


async def obtener_practicante(interaction, discord_id):
    import logging
    nombre_usuario = interaction.user.mention
    logging.info(f"🔍 Buscando practicante en BD para: {interaction.user} (ID: {discord_id})")
    query_practicante = "SELECT id FROM practicante WHERE id_discord = %s"
    practicante = await db.fetch_one(query_practicante, (discord_id,))
    
    # Si no se encuentra el practicante, informar al usuario
    if not practicante:
        msg = f"{nombre_usuario}, no estás registrado como practicante en este servidor. Por favor, completa el formulario de registro."
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
        return None
    return practicante['id']

async def verificar_entrada(practicante_id, fecha_actual):
    query_asistencia_existente = "SELECT id FROM asistencia WHERE practicante_id = %s AND fecha = %s"
    asistencia_existente = await db.fetch_one(query_asistencia_existente, (practicante_id, fecha_actual))
    return asistencia_existente

async def obtener_estado_asistencia(estado_nombre):
    query_estado = "SELECT id FROM estado_asistencia WHERE estado = %s"
    estado = await db.fetch_one(query_estado, (estado_nombre,))
    return estado['id'] if estado else None

async def canal_permitido(interaction: discord.Interaction) -> bool:
    servidor_id = interaction.guild.id
    bot = interaction.client
    canal_id = interaction.channel.id
    
    # Lista global de canales oficiales (Asistencia, Recuperación, Tests)
    # Estos siempre están permitidos sin importar el servidor
    canales_oficiales = [
        1457747478592884878, # Canal Principal Asistencia
        1457747701038059643, # Canal Recuperación
        1457802290093228093  # Canal de Tests
    ]
    
    if canal_id in canales_oficiales:
        return True

    canales_permitidos = bot.canales_permitidos.get(servidor_id, [])

    # Verificar si el canal es permitido según configuración de bot.py
    if canal_id not in canales_permitidos:
        import logging
        logging.warning(f"🚫 Canal denegado en Servidor {servidor_id} (Canal ID: {canal_id})")
        await interaction.response.send_message(
            f"Este comando no está habilitado en este canal (ID: {canal_id}). Por favor, usa los canales oficiales.",
            ephemeral=True
        )
        return False
    return True

async def verificar_rol_permitido(interaction: discord.Interaction, roles_permitidos: list, usar_followup: bool = False) -> bool:
    """
    Verifica si el usuario tiene alguno de los roles permitidos.
    roles_permitidos: Lista de IDs de roles permitidos
    usar_followup: Si es True, usa followup en lugar de response (para cuando ya se hizo defer)
    """
    if not roles_permitidos:
        return True
    
    usuario = interaction.user
    roles_usuario = [role.id for role in usuario.roles]
    
    # Verificar si tiene alguno de los roles permitidos
    tiene_rol = any(role_id in roles_usuario for role_id in roles_permitidos)
    
    if not tiene_rol:
        mensaje = "No tienes los permisos necesarios para usar este comando."
        if usar_followup:
            await interaction.followup.send(mensaje, ephemeral=True)
        else:
            await interaction.response.send_message(mensaje, ephemeral=True)
        return False
    return True

async def verificar_recuperacion(practicante_id, fecha_actual):
    """Verifica si ya existe una recuperación para el practicante en la fecha dada"""
    query_recuperacion = "SELECT id FROM asistencia_recuperacion WHERE practicante_id = %s AND fecha_recuperacion = %s"
    recuperacion_existente = await db.fetch_one(query_recuperacion, (practicante_id, fecha_actual))
    return recuperacion_existente
