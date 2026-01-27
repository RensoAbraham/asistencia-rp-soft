"""Módulo administrativo para gestión de asistencia"""

import discord
from discord import app_commands, Embed, Color
from discord.ext import commands
from datetime import datetime
from zoneinfo import ZoneInfo
import database as db
import logging
from utils import obtener_practicante, obtener_estado_asistencia

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
            entrada = res['hora_entrada'].strftime('%H:%M') if res['hora_entrada'] else "--:--"
            salida = res['hora_salida'].strftime('%H:%M') if res['hora_salida'] else "--:--"
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
               SEC_TO_TIME(SUM(TIME_TO_SEC(IFNULL(TIMEDIFF(a.hora_salida, a.hora_entrada), '00:00:00')))) as horas_trabajadas,
               p.horas_base
        FROM practicante p
        LEFT JOIN asistencia a ON p.id = a.practicante_id
        GROUP BY p.id
        ORDER BY p.nombre_completo ASC
        """
        resultados = await db.fetch_all(query)

        embed = Embed(
            title="📈 Resumen General de Horas",
            color=Color.green(),
            description="Acumulado total de horas trabajadas (incluyendo horas base)."
        )

        for res in resultados:
            trabajadas = str(res['horas_trabajadas']) if res['horas_trabajadas'] else "00:00:00"
            base = res['horas_base'] or "00:00:00"
            
            # Intentar sumar (formato simple para el reporte)
            embed.add_field(
                name=res['nombre_completo'],
                value=f"⏳ Trabajadas: `{trabajadas}`\n📅 Base: `{base}`",
                inline=True
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
