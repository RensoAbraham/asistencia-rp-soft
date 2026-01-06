import database as db
import discord
from discord import TextStyle, ui


async def obtener_practicante(interaction, discord_id):
    nombre_usuario = interaction.user.mention
    query_practicante = "SELECT id FROM practicante WHERE id_discord = %s"
    practicante = await db.fetch_one(query_practicante, (discord_id,))
    
    # Si no se encuentra el practicante, informar al usuario
    if not practicante:
        await interaction.followup.send(
            f"{nombre_usuario}, no estás registrado como practicante.",
            ephemeral=True
        )
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
    
    # Excepción temporal para pruebas (Canal solicitado por usuario)
    if interaction.channel.id == 1457802290093228093:
        return True

    canales_permitidos = bot.canales_permitidos.get(servidor_id, [])

    # Verificar si el canal es permitido
    if interaction.channel.id not in canales_permitidos:
        await interaction.response.send_message(
            "Este comando no está habilitado en este canal.",
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
