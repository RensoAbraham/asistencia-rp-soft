"""Módulo de pruebas administrativas sin restricciones"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from zoneinfo import ZoneInfo
import database as db
import logging
from utils import obtener_practicante, obtener_estado_asistencia, LIMA_TZ

@app_commands.default_permissions(administrator=True)
class Test(commands.GroupCog, name="test"):
    """Comandos de prueba exclusivos para admins (sin restricciones de horario)"""
    
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @app_commands.command(name='asistencia', description="Forzar entrada/salida de prueba (Admins solo, 24/7)")
    @app_commands.describe(
        accion="Entrada o Salida",
        id_discord="ID de Discord del practicante (opcional, por defecto tú)",
        estado="Estado manual (Presente, Tardanza, etc.)",
        validar_dispositivo="Si es True, aplicará las reglas de Móvil/Invisible"
    )
    @app_commands.choices(accion=[
        app_commands.Choice(name="Entrada", value="entrada"),
        app_commands.Choice(name="Salida", value="salida")
    ])
    async def test_asistencia(self, interaction: discord.Interaction, accion: str, id_discord: str = None, estado: str = "Presente", validar_dispositivo: bool = False):
        await interaction.response.defer(ephemeral=True)
        
        from utils import validar_dispositivo_pc
        
        # Si el admin quiere probar la restricción
        if validar_dispositivo:
            if not await validar_dispositivo_pc(interaction):
                return

        target_id = int(id_discord) if id_discord else interaction.user.id
        ahora = datetime.now(LIMA_TZ)
        fecha_actual = ahora.date()
        hora_actual = ahora.time()

        practicante_id = await obtener_practicante(interaction, target_id)
        if not practicante_id:
            return

        if accion == "entrada":
            estado_id = await obtener_estado_asistencia(estado)
            query = "INSERT INTO asistencia (practicante_id, fecha, hora_entrada, estado_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE hora_entrada = VALUES(hora_entrada), estado_id = VALUES(estado_id)"
            await db.execute_query(query, (practicante_id, fecha_actual, hora_actual, estado_id))
            await interaction.followup.send(f"✅ [TEST] Entrada registrada para <@{target_id}> a las {hora_actual.strftime('%H:%M')}.", ephemeral=True)
        
        else: # salida
            query = "UPDATE asistencia SET hora_salida = %s WHERE practicante_id = %s AND fecha = %s AND hora_salida IS NULL"
            result = await db.execute_query(query, (hora_actual, practicante_id, fecha_actual))
            await interaction.followup.send(f"✅ [TEST] Salida registrada para <@{target_id}> a las {hora_actual.strftime('%H:%M')}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Test(bot))
