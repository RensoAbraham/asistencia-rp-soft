import database as db
import discord
from discord import TextStyle, ui
import datetime
from zoneinfo import ZoneInfo

# Zona horaria de Perú
LIMA_TZ = ZoneInfo("America/Lima")

def format_timedelta(td):
    """Convierte un timedelta o time a string HH:MM:SS"""
    if td is None:
        return "--:--"
    if isinstance(td, datetime.time):
        return td.strftime("%H:%M")
    
    # Si es timedelta (común en MySQL TIME)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}"

def format_timedelta_total(td_val):
    """
    Convierte un valor de tiempo de la BD (timedelta, string o None) 
    en un formato de horas totales [HH]:MM:SS.
    Ejemplo: timedelta de 47 horas -> '47:00:00'
    """
    if td_val is None:
        return "00:00:00"
    
    if isinstance(td_val, datetime.timedelta):
        total_seconds = int(td_val.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    
    # Si ya es un string, intentamos normalizarlo (por si viene con 'days')
    td_str = str(td_val)
    if 'day' in td_str:
        # Reutilizamos lógica de format_duration de google_sheets o la replicamos aquí
        try:
            parts = td_str.split(',')
            days_part = parts[0].strip()
            time_part = parts[1].strip()
            days = int(days_part.split(' ')[0])
            h, m, s = map(int, time_part.split(':'))
            total_hours = (days * 24) + h
            return f"{total_hours:02}:{m:02}:{s:02}"
        except:
            return td_str
    return td_str

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
        # ID oficial del canal de asistencia
        canal_asistencia_id = 1457747478592884878
        
        if interaction.response.is_done():
            await interaction.followup.send(
                f"🚫 **Canal Incorrecto**\nEste comando solo está habilitado en el canal de asistencia.\n👉 Por favor, ve a <#{canal_asistencia_id}> para registrar tu asistencia.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"🚫 **Canal Incorrecto**\nEste comando solo está habilitado en el canal de asistencia.\n👉 Por favor, ve a <#{canal_asistencia_id}> para registrar tu asistencia.",
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

async def validar_dispositivo_pc(interaction: discord.Interaction) -> bool:
    """
    Verifica si el usuario está en PC/Web y no en modo Invisible.
    Retorna True si es válido, False y envía mensaje si es inválido.
    """
    member = interaction.guild.get_member(interaction.user.id)
    if not member:
        return True # Si no podemos obtener el member, permitimos por seguridad
        
    # El estado 'offline' significa que está Invisible (o realmente desconectado, pero interactuando)
    if member.status == discord.Status.offline:
        await interaction.followup.send(
            "⚠️ **Estado Invisible detectado**\n"
            "Por políticas de la empresa, debes estar en modo **Conectado**, **Inactivo** o **No Molestar** "
            "para que el sistema pueda verificar que estás usando una PC.",
            ephemeral=True
        )
        return False

    # Verificar si está en móvil
    # member.is_on_mobile es confiable si los intents están activos
    if member.is_on_mobile:
        await interaction.followup.send(
            "🚫 **Acceso restringido: Solo PC**\n"
            "Se ha detectado que estás intentando registrar asistencia desde un dispositivo móvil. "
            "Por seguridad y normativa interna, las marcas de asistencia deben realizarse únicamente desde una computadora.",
            ephemeral=True
        )
        return False

    # Verificación adicional por plataformas específicas
    # member.mobile_status, member.desktop_status, member.web_status
    if member.mobile_status != discord.Status.offline:
        await interaction.followup.send(
            "🚫 **Dispositivo Móvil detectado**\n"
            "Tu cuenta de Discord registra una sesión activa en móvil. Por favor, cierra la sesión en tu celular "
            "o asegúrate de estar operando exclusivamente desde tu PC para marcar asistencia.",
            ephemeral=True
        )
        return False

    return True

async def verificar_recuperacion(practicante_id, fecha_actual):
    """Verifica si ya existe una recuperación para el practicante en la fecha dada"""
    query_recuperacion = "SELECT id FROM asistencia_recuperacion WHERE practicante_id = %s AND fecha_recuperacion = %s"
    recuperacion_existente = await db.fetch_one(query_recuperacion, (practicante_id, fecha_actual))
    return recuperacion_existente
