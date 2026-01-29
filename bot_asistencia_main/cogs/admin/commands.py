"""Módulo administrativo para gestión de asistencia"""

import discord
from discord import app_commands, Embed, Color
from discord.ext import commands
from datetime import datetime
from zoneinfo import ZoneInfo
import database as db
import logging
from utils import obtener_practicante, obtener_estado_asistencia, format_timedelta, format_timedelta_total

LIMA_TZ = ZoneInfo("America/Lima")

class Admin(commands.GroupCog, name="admin"):
    """Cog para comandos administrativos"""

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.AUTHORIZED_USERS = [615932763161362636]  # Tu ID de admin

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Verificar si el usuario tiene permisos"""
        if interaction.user.id in self.AUTHORIZED_USERS or interaction.user.guild_permissions.administrator:
            return True
        
        await interaction.response.send_message(
            "❌ No tienes permisos suficientes para acceder a este panel.",
            ephemeral=True
        )
        return False

    @app_commands.command(name='reporte_hoy', description="Ver el estado de todos los practicantes hoy")
    async def reporte_hoy(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        fecha_actual = datetime.now(LIMA_TZ).date()

        # Consulta para obtener a todos los practicantes y sus marcas de hoy
        query = """
        SELECT p.nombre_completo, a.hora_entrada, a.hora_salida, ea.estado
        FROM practicante p
        LEFT JOIN asistencia a ON p.id = a.practicante_id AND a.fecha = %s
        LEFT JOIN estado_asistencia ea ON a.estado_id = ea.id
        ORDER BY p.nombre_completo ASC
        """
        resultados = await db.fetch_all(query, (fecha_actual,))

        if not resultados:
            await interaction.followup.send("No hay practicantes registrados en la base de datos.", ephemeral=True)
            return

        embed = Embed(
            title=f"📊 Reporte de Asistencia - {fecha_actual.strftime('%d/%m/%Y')}",
            color=Color.blue(),
            timestamp=datetime.now()
        )

        presentes = 0
        faltan = 0
        total = len(resultados)

        # Construir la lista de estados
        lista_practicantes = ""
        for res in resultados:
            nombre = res['nombre_completo']
            entrada = format_timedelta(res['hora_entrada'])
            salida = format_timedelta(res['hora_salida'])
            estado = res['estado'] or "Falta"
            
            emoji = "✅" if res['hora_entrada'] else "❌"
            if res['hora_entrada']: presentes += 1
            else: faltan += 1

            linea = f"{emoji} **{nombre}** | {entrada} - {salida} | *{estado}*\n"
            
            # Evitar exceder el límite de caracteres de un solo field
            if len(lista_practicantes) + len(linea) > 1000:
                embed.add_field(name="Practicantes", value=lista_practicantes, inline=False)
                lista_practicantes = linea
            else:
                lista_practicantes += linea

        if lista_practicantes:
            embed.add_field(name="Practicantes", value=lista_practicantes, inline=False)

        embed.add_field(name="Resumen", value=f"👥 Total: {total} | ✅ Presentes: {presentes} | ❌ Faltan: {faltan}", inline=False)
        embed.set_footer(text="Panel Administrativo RP Soft")

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name='editar_asistencia', description="Editar o registrar manualmente una salida/entrada de un usuario")
    @app_commands.describe(
        usuario="El usuario a editar",
        fecha="Fecha en formato YYYY-MM-DD (opcional, hoy por defecto)",
        entrada="Hora de entrada en formato HH:MM (opcional)",
        salida="Hora de salida en formato HH:MM (opcional)",
        estado="Estado (Presente, Tardanza, etc. opcional)"
    )
    async def editar_asistencia(
        self, 
        interaction: discord.Interaction, 
        usuario: discord.Member, 
        fecha: str = None,
        entrada: str = None,
        salida: str = None,
        estado: str = None
    ):
        await interaction.response.defer(ephemeral=True)
        
        try:
            fecha_valida = datetime.strptime(fecha, "%Y-%m-%d").date() if fecha else datetime.now(LIMA_TZ).date()
            hora_entrada = datetime.strptime(entrada, "%H:%M").time() if entrada else None
            hora_salida = datetime.strptime(salida, "%H:%M").time() if salida else None
        except ValueError:
            await interaction.followup.send("❌ Formato de fecha (YYYY-MM-DD) o hora (HH:MM) inválido.", ephemeral=True)
            return

        practicante_id = await obtener_practicante(interaction, usuario.id)
        if not practicante_id:
            await interaction.followup.send(f"❌ El usuario {usuario.mention} no está registrado como practicante.", ephemeral=True)
            return

        # Buscar si ya existe el registro
        query_check = "SELECT id FROM asistencia WHERE practicante_id = %s AND fecha = %s"
        asistencia = await db.fetch_one(query_check, (practicante_id, fecha_valida))

        if not asistencia:
            # Crear registro nuevo si no existe
            if not hora_entrada:
                await interaction.followup.send("❌ El usuario no tiene entrada hoy. Debes especificar una hora de entrada para crear el registro.", ephemeral=True)
                return
            
            estado_id = await obtener_estado_asistencia(estado or 'Presente')
            query_insert = """
            INSERT INTO asistencia (practicante_id, fecha, hora_entrada, hora_salida, estado_id)
            VALUES (%s, %s, %s, %s, %s)
            """
            await db.execute_query(query_insert, (practicante_id, fecha_valida, hora_entrada, hora_salida, estado_id))
            msg = f"✅ Nuevo registro creado para {usuario.mention} el {fecha_valida}."
        else:
            # Actualizar registro existente
            updates = []
            params = []
            if hora_entrada:
                updates.append("hora_entrada = %s")
                params.append(hora_entrada)
            if hora_salida:
                updates.append("hora_salida = %s")
                params.append(hora_salida)
            if estado:
                estado_id = await obtener_estado_asistencia(estado)
                updates.append("estado_id = %s")
                params.append(estado_id)
            
            if not updates:
                await interaction.followup.send("ℹ️ No se especificaron cambios.", ephemeral=True)
                return
                
            params.append(asistencia['id'])
            query_update = f"UPDATE asistencia SET {', '.join(updates)} WHERE id = %s"
            await db.execute_query(query_update, tuple(params))
            msg = f"✅ Registro de {usuario.mention} actualizado para el día {fecha_valida}."

        await interaction.followup.send(msg, ephemeral=True)
        logging.info(f"Admin {interaction.user.display_name} editó asistencia de {usuario.display_name}")

    @app_commands.command(name='resumen_general', description="Ver acumulado de horas de todos los practicantes")
    async def resumen_general(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Esta vista ya existe en database.py o podemos consultar directamente
        query = """
        SELECT p.nombre_completo, 
               SEC_TO_TIME(SUM(TIME_TO_SEC(IFNULL(TIMEDIFF(a.hora_salida, a.hora_entrada), '00:00:00')))) as horas_bot_raw,
               p.horas_base
        FROM practicante p
        LEFT JOIN asistencia a ON p.id = a.practicante_id
        GROUP BY p.id
        ORDER BY p.nombre_completo ASC
        """
        resultados = await db.fetch_all(query)

        embed = Embed(
            title="📈 Resumen General de Horas",
            description="Acumulado total de horas trabajadas (Base + Bot).",
            color=Color.green()
        )

        for res in resultados:
            bot_str = format_timedelta_total(res['horas_bot_raw'])
            base_str = format_timedelta_total(res['horas_base'])
            
            # Cálculo de Total (sumando bot y base)
            try:
                # Bot
                h1, m1, s1 = map(int, bot_str.split(':'))
                # Base
                h2, m2, s2 = map(int, base_str.split(':'))
                
                total_h = h1 + h2
                total_m = m1 + m2
                total_s = s1 + s2
                
                # Ajustar desbordamientos
                if total_s >= 60:
                    total_m += total_s // 60
                    total_s = total_s % 60
                if total_m >= 60:
                    total_h += total_m // 60
                    total_m = total_m % 60
                
                total_final = f"{total_h:02d}:{total_m:02d}:{total_s:02d}"
            except:
                total_final = "Error"

            embed.add_field(
                name=res['nombre_completo'],
                value=f"✅ Total: **{total_final}**\n*(Bot: {bot_str} | Base: {base_str})*",
                inline=True
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name='sincronizar', description="Forzar sincronización inmediata con Google Sheets")
    async def sincronizar(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            from google_sheets import sync_practicantes_to_db, export_report_to_sheet
            
            await interaction.followup.send("🔄 Iniciando sincronización forzada...", ephemeral=True)
            
            # 1. Sincronizar practicantes y horas base
            await sync_practicantes_to_db()
            
            # 2. Exportar reportes actualizados
            await export_report_to_sheet()
            
            await interaction.followup.send("✅ Sincronización completada exitosamente.", ephemeral=True)
            logging.info(f"Admin {interaction.user.display_name} forzó una sincronización manual.")
            
        except Exception as e:
            logging.error(f"Error en sincronización forzada: {e}")
            await interaction.followup.send(f"❌ Error durante la sincronización: {e}", ephemeral=True)

    @app_commands.command(name='eliminar_practicante', description="Elimina un practicante de la base de datos por su ID de Discord")
    @app_commands.describe(id_discord="El ID de Discord del registro a eliminar")
    async def eliminar_practicante(self, interaction: discord.Interaction, id_discord: str):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # 1. Verificar si existe
            query_check = "SELECT id, nombre_completo FROM practicante WHERE id_discord = %s"
            practicante = await db.fetch_one(query_check, (id_discord,))
            
            if not practicante:
                await interaction.followup.send(f"❌ No se encontró ningún practicante con el ID: `{id_discord}`", ephemeral=True)
                return

            # 2. Eliminar asistencias relacionadas (por integridad referencial)
            query_del_asistencia = "DELETE FROM asistencia WHERE practicante_id = %s"
            await db.execute_query(query_del_asistencia, (practicante['id'],))
            
            # 3. Eliminar recuperaciones (si existen)
            query_del_recup = "DELETE FROM asistencia_recuperacion WHERE practicante_id = %s"
            await db.execute_query(query_del_recup, (practicante['id'],))

            # 4. Eliminar practicante
            query_del_practicante = "DELETE FROM practicante WHERE id = %s"
            await db.execute_query(query_del_practicante, (practicante['id'],))
            
            await interaction.followup.send(f"✅ Se ha eliminado a **{practicante['nombre_completo']}** (ID: `{id_discord}`) y todos sus registros de la base de datos.", ephemeral=True)
            logging.info(f"Admin {interaction.user.display_name} eliminó permanentemente al practicante {practicante['nombre_completo']}")

        except Exception as e:
            logging.error(f"Error al eliminar practicante: {e}")
            await interaction.followup.send(f"❌ Error al eliminar: {e}", ephemeral=True)



async def setup(bot):
    await bot.add_cog(Admin(bot))
