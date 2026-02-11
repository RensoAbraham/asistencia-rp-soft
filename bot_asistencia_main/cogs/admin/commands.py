"""Módulo administrativo para gestión de asistencia"""

import discord
from discord import app_commands, Embed, Color
from discord.ext import commands
from datetime import datetime, time
from zoneinfo import ZoneInfo
import database as db
import logging
import utils
from utils import obtener_practicante, obtener_estado_asistencia, format_timedelta, format_timedelta_total, es_admin_bot

LIMA_TZ = ZoneInfo("America/Lima")

class ConfirmacionEliminar(discord.ui.View):
    def __init__(self, interaction, id_discord, nombre_completo):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.id_discord = id_discord
        self.nombre_completo = nombre_completo

    @discord.ui.button(label="Confirmar Eliminación", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction.user.id:
            return await interaction.response.send_message("❌ Solo quien inició el comando puede confirmar.", ephemeral=True)
        
        await interaction.response.defer()
        try:
            query_check = "SELECT id FROM practicante WHERE id_discord = %s"
            practicante = await db.fetch_one(query_check, (self.id_discord,))
            if practicante:
                await db.execute_query("DELETE FROM asistencia WHERE practicante_id = %s", (practicante['id'],))
                await db.execute_query("DELETE FROM asistencia_recuperacion WHERE practicante_id = %s", (practicante['id'],))
                await db.execute_query("DELETE FROM practicante WHERE id = %s", (practicante['id'],))
                await interaction.followup.edit_message(message_id=interaction.message.id, content=f"✅ **{self.nombre_completo}** eliminado.", view=None)
            else:
                await interaction.followup.send("❌ No encontrado.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Cancelado.", view=None)

class Admin(commands.GroupCog, name="admin"):
    """Cog para comandos administrativos"""

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.AUTHORIZED_USERS = [615932763161362636, 824692049084678144]

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id in self.AUTHORIZED_USERS: return True
        try:
            if await es_admin_bot(interaction.user.id): return True
        except: pass
        if interaction.user.guild_permissions.administrator: return True
        await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)
        return False

    @app_commands.command(name='reporte_hoy', description="Ver el estado de todos los practicantes hoy")
    async def reporte_hoy(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        fecha_actual = datetime.now(LIMA_TZ).date()
        query = """
        SELECT p.nombre_completo, a.hora_entrada, a.hora_salida, ea.estado
        FROM practicante p
        LEFT JOIN asistencia a ON p.id = a.practicante_id AND a.fecha = %s
        LEFT JOIN estado_asistencia ea ON a.estado_id = ea.id
        ORDER BY p.nombre_completo ASC
        """
        resultados = await db.fetch_all(query, (fecha_actual,))
        embed = Embed(title=f"📊 Reporte de Asistencia - {fecha_actual}", color=Color.blue())
        for res in resultados:
            entrada = res['hora_entrada'] or "---"
            salida = res['hora_salida'] or "---"
            estado = res['estado'] or "⚠️ Pendiente"
            embed.add_field(name=res['nombre_completo'], value=f"E: {entrada} | S: {salida}\nEst: {estado}", inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name='eliminar_practicante', description="Elimina a un practicante")
    async def eliminar_practicante(self, interaction: discord.Interaction, id_discord: str):
        await interaction.response.defer(ephemeral=True)
        query = "SELECT nombre_completo FROM practicante WHERE id_discord = %s"
        p = await db.fetch_one(query, (id_discord,))
        if not p: return await interaction.followup.send("❌ No encontrado.", ephemeral=True)
        
        embed = Embed(title="⚠️ Confirmación", description=f"¿Eliminar a **{p['nombre_completo']}**?", color=Color.red())
        view = ConfirmacionEliminar(interaction, id_discord, p['nombre_completo'])
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name='agregar_equipo', description="Agrega a un miembro al equipo de desarrollo")
    async def agregar_equipo(self, interaction: discord.Interaction, usuario: discord.User, rol: str = "Developer"):
        await interaction.response.defer(ephemeral=True)
        query = "INSERT INTO bot_admins (discord_id, nombre_referencia, rol) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE rol = %s"
        await db.execute_query(query, (usuario.id, usuario.name, rol, rol))
        await interaction.followup.send(f"✅ **{usuario.name}** agregado como **{rol}**.", ephemeral=True)

    @app_commands.command(name='equipo', description="Muestra el equipo de desarrollo")
    async def ver_equipo(self, interaction: discord.Interaction):
        query = "SELECT * FROM bot_admins ORDER BY rol DESC"
        admins = await db.fetch_all(query)
        texto = "\n".join([f"• <@{a['discord_id']}> - **{a['rol']}**" for a in admins])
        embed = Embed(title="👥 Equipo de Desarrollo", description=texto, color=Color.gold())
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
