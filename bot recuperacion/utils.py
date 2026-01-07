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
    canales_permitidos = bot.canales_permitidos.get(servidor_id, [])

    # Verificar si el canal es permitido
    if interaction.channel.id not in canales_permitidos:
        await interaction.response.send_message(
            "Este comando no está habilitado en este canal.",
            ephemeral=True
        )
        return False
    return True

class manejar_salida_anticipada(ui.Modal, title="Salida Anticipada"):
    motivo = ui.TextInput(
        label="Motivo de la salida anticipada",
        style=TextStyle.paragraph,
        placeholder="Escribe tu motivo aquí...",
        required=True,
        max_length=255
    )

    # Inicializar con parámetros necesarios
    def __init__(self, hora_actual, asistencia, nombre_usuario):
        super().__init__()
        self.hora_actual = hora_actual
        self.asistencia = asistencia
        self.nombre_usuario = nombre_usuario

    async def on_submit(self, interaction: discord.Interaction):
        motivo_guardado = self.motivo.value

        # Actualizar la DB con la salida anticipada
        estado_id = await obtener_estado_asistencia('Salida Anticipada')
        query_update_salida = """
            UPDATE asistencia 
            SET hora_salida = %s, estado_id = %s, motivo = %s 
            WHERE id = %s
        """
        await db.execute_query(query_update_salida, (self.hora_actual, estado_id, motivo_guardado, self.asistencia['id']))

        await interaction.response.send_message(
            f"{self.nombre_usuario}, tu salida anticipada ha sido registrada con éxito.",
            ephemeral=True
        )
