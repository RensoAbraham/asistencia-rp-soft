"""Comandos del módulo de faltas"""

import discord
from discord import app_commands, Embed, Color
from discord.ext import commands
from utils import obtener_practicante, obtener_estado_asistencia, canal_permitido
import database as db
import logging


class Faltas(commands.GroupCog, name="faltas"):
    """Cog para gestionar comandos de faltas"""
    
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @app_commands.command(name='ver', description="Ver tus faltas injustificadas")
    async def ver_faltas(self, interaction: discord.Interaction):
        if not await canal_permitido(interaction):
            logging.warning(f'Canal no permitido para el usuario {interaction.user.display_name}.')
            return

        discord_id = interaction.user.id
        nombre_usuario = interaction.user.mention
        logging.info(f'Usuario {interaction.user.display_name} ha solicitado ver sus faltas injustificadas.')
        practicante_id = await obtener_practicante(interaction, discord_id)
        if not practicante_id:
            logging.warning(f'Practicante no encontrado para el usuario {interaction.user.display_name}.')
            return

        # Consultar las faltas injustificadas del practicante
        query_faltas = """
            SELECT date_format(fecha, '%%m-%%d') as fecha, motivo
            FROM asistencia
            WHERE practicante_id = %s AND estado_id = %s
            ORDER BY fecha DESC
            LIMIT 5
        """
        estado_falta_injustificada_id = await obtener_estado_asistencia('Falta injustificada')
        faltas = await db.fetch_all(query_faltas, (practicante_id, estado_falta_injustificada_id))

        if not faltas:
            await interaction.response.send_message(
                f"{nombre_usuario}, no tienes faltas injustificadas registradas.",
                ephemeral=True
            )
            return

        # Crear el Embed para mostrar las faltas
        embed = Embed(
            title="🚫 Faltas Injustificadas Registradas",
            description=f"**{interaction.user.display_name}**, aquí están tus últimas 5 faltas injustificadas:",
            color=Color.red()
        )

        # Agregar las faltas al embed
        for falta in faltas:
            fecha = falta['fecha']
            motivo = falta['motivo'] or "No especificado"
            embed.add_field(
                name=f"Fecha: {fecha}",
                value=f"**Motivo**: {motivo}",
                inline=False
            )

        embed.set_footer(text="Si tienes dudas, contacta con el administrador.")

        await interaction.response.send_message(embed=embed, ephemeral=True)


