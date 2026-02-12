"""Módulo administrativo para gestión de asistencia"""

import discord
from discord import app_commands, Embed, Color
from discord.ext import commands
from typing import Optional
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
        self.AUTHORIZED_USERS = [615932763161362636, 824692049084678144] # Renso - Wilber

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

    @app_commands.command(name='editar_asistencia', description="Edita o crea un registro de asistencia manualmente")
    @app_commands.describe(
        usuario="El practicante a editar",
        fecha="Fecha en formato YYYY-MM-DD (ej. 2024-03-20)",
        entrada="Hora de entrada HH:MM (ej. 08:00)",
        salida="Hora de salida HH:MM (ej. 14:00)",
        estado="Estado: Presente, Tardanza, Falta Injustificada, Falta Recuperada, Permiso"
    )
    async def editar_asistencia(
        self, 
        interaction: discord.Interaction, 
        usuario: discord.User,
        fecha: Optional[str] = None,
        entrada: Optional[str] = None,
        salida: Optional[str] = None,
        estado: Optional[str] = None
    ):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # 1. Obtener ID del practicante
            query_p = "SELECT id FROM practicante WHERE id_discord = %s"
            p = await db.fetch_one(query_p, (usuario.id,))
            if not p:
                return await interaction.followup.send(f"❌ {usuario.mention} no está registrado.", ephemeral=True)
            
            p_id = p['id']
            fecha_final = fecha if fecha else datetime.now(LIMA_TZ).strftime('%Y-%m-%d')
            
            # 2. Obtener estado_id si se proporcionó
            estado_id = None
            if estado:
                estado_id = await obtener_estado_asistencia(estado)
                if not estado_id:
                    return await interaction.followup.send(f"❌ Estado '{estado}' no válido.", ephemeral=True)

            # 3. Comprobar si ya existe el registro
            query_check = "SELECT id FROM asistencia WHERE practicante_id = %s AND fecha = %s"
            existente = await db.fetch_one(query_check, (p_id, fecha_final))

            if existente:
                # Actualizar (crear lista de campos a actualizar)
                updates = []
                params = []
                if entrada: updates.append("hora_entrada = %s"); params.append(entrada)
                if salida: updates.append("hora_salida = %s"); params.append(salida)
                if estado_id: updates.append("estado_id = %s"); params.append(estado_id)
                
                if not updates:
                    return await interaction.followup.send("⚠️ No se proporcionaron campos para actualizar.", ephemeral=True)
                
                query_upd = f"UPDATE asistencia SET {', '.join(updates)} WHERE id = %s"
                params.append(existente['id'])
                await db.execute_query(query_upd, tuple(params))
                await interaction.followup.send(f"✅ Asistencia de {usuario.mention} para el {fecha_final} actualizada.", ephemeral=True)
            else:
                # Crear nuevo registro (requiere estado o asumimos Presente)
                if not estado_id: estado_id = await obtener_estado_asistencia('Presente')
                query_ins = "INSERT INTO asistencia (practicante_id, fecha, hora_entrada, hora_salida, estado_id) VALUES (%s, %s, %s, %s, %s)"
                await db.execute_query(query_ins, (p_id, fecha_final, entrada, salida, estado_id))
                await interaction.followup.send(f"✅ Nuevo registro creado para {usuario.mention} el {fecha_final}.", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ Error al editar asistencia: {e}", ephemeral=True)

    @app_commands.command(name='resumen_general', description="Muestra el resumen de horas de todos los practicantes")
    async def resumen_general(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        query = "SELECT * FROM resumen_practicantes ORDER BY nombre_completo ASC"
        res = await db.fetch_all(query)
        
        if not res: return await interaction.followup.send("No hay datos.", ephemeral=True)
        
        embed = Embed(title="📋 Resumen General de Horas", color=Color.green())
        for r in res:
            prev = format_timedelta_total(r['horas_base'])
            bot = format_timedelta_total(r['horas_bot'])
            total = format_timedelta_total(r['total_acumulado'])
            embed.add_field(
                name=r['nombre_completo'], 
                value=f"Base: `{prev}` | Bot: `{bot}`\n**Total: `{total}`**", 
                inline=False
            )
            
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name='sincronizar', description="Fuerza la sincronización con Google Sheets")
    async def sincronizar(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        from google_sheets import sync_practicantes_to_db, export_report_to_sheet
        try:
            await sync_practicantes_to_db()
            await export_report_to_sheet()
            await interaction.followup.send("✅ Sincronización con Google Sheets completada.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

    @app_commands.command(name='agregar_equipo', description="Agrega a un miembro al equipo de desarrollo")
    async def agregar_equipo(self, interaction: discord.Interaction, usuario: discord.User, rol: str = "Developer"):
        await interaction.response.defer(ephemeral=True)
        query = "INSERT INTO bot_admins (discord_id, nombre_referencia, rol) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE rol = %s"
        await db.execute_query(query, (usuario.id, usuario.name, rol, rol))
        await interaction.followup.send(f"✅ **{usuario.name}** agregado como **{rol}**.", ephemeral=True)

    @app_commands.command(name='equipo', description="Muestra el equipo de desarrollo")
    async def ver_equipo(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True) # Evita el error 10062
        # Ordenamos: Wilber primero, Renso segundo, los demás después
        query = """
        SELECT * FROM bot_admins 
        ORDER BY 
            CASE 
                WHEN discord_id = 824692049084678144 THEN 1 -- Wilber
                WHEN discord_id = 615932763161362636 THEN 2 -- Renso
                ELSE 3 
            END ASC, 
            rol DESC
        """
        admins = await db.fetch_all(query)
        texto = "\n".join([f"• <@{a['discord_id']}> - **{a['rol']}**" for a in admins])
        embed = Embed(title="👥 Equipo de Desarrollo", description=texto, color=Color.gold())
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def admin_autocomplete(self, interaction: discord.Interaction, current: str):
        """Autocompletado para mostrar solo administradores actuales"""
        query = "SELECT nombre_referencia, discord_id FROM bot_admins WHERE nombre_referencia LIKE %s"
        admins = await db.fetch_all(query, (f"%{current}%",))
        return [
            app_commands.Choice(name=a['nombre_referencia'], value=str(a['discord_id']))
            for a in admins 
            if a['discord_id'] not in [824692049084678144, 615932763161362636] # No permitimos elegir a los fundadores
        ]

    @app_commands.command(name='eliminar_equipo', description="Quita a un miembro del equipo de desarrollo")
    @app_commands.autocomplete(usuario_id=admin_autocomplete)
    async def eliminar_equipo(self, interaction: discord.Interaction, usuario_id: str):
        await interaction.response.defer(ephemeral=True)
        
        id_int = int(usuario_id)
        # Protegemos a Wilber y a Renso (aunque el autocomplete ya los filtra, por seguridad extra)
        if id_int in [824692049084678144, 615932763161362636]:
            return await interaction.followup.send("❌ No puedes eliminar a los fundadores del equipo.", ephemeral=True)
            
        query = "DELETE FROM bot_admins WHERE discord_id = %s"
        await db.execute_query(query, (id_int,))
        await interaction.followup.send(f"✅ Usuario eliminado del equipo.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
