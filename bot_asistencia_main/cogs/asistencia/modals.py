"""Modales para el módulo de asistencia"""

import database as db
import discord
from discord import TextStyle, ui
from utils import obtener_estado_asistencia


class SalidaAnticipadaModal(ui.Modal, title="Salida Anticipada"):
    """Modal para registrar salida anticipada con motivo"""
    
    motivo = ui.TextInput(
        label="Motivo de la salida anticipada",
        style=TextStyle.paragraph,
        placeholder="Escribe tu motivo aquí...",
        required=True,
        max_length=255
    )

    def __init__(self, hora_actual, asistencia, nombre_usuario):
        super().__init__()
        self.hora_actual = hora_actual
        self.asistencia = asistencia
        self.nombre_usuario = nombre_usuario

    async def on_submit(self, interaction: discord.Interaction):
        """Maneja el envío del modal"""
        motivo_guardado = self.motivo.value

        # Actualizar la DB con la salida anticipada
        estado_id = await obtener_estado_asistencia('Salida Anticipada')
        query_update_salida = """
            UPDATE asistencia 
            SET hora_salida = %s, estado_id = %s, motivo = %s 
            WHERE id = %s
        """
        await db.execute_query(
            query_update_salida,
            (self.hora_actual, estado_id, motivo_guardado, self.asistencia['id'])
        )

        await interaction.response.send_message(
            f"{self.nombre_usuario}, tu salida anticipada ha sido registrada con éxito.",
            ephemeral=True
        )


