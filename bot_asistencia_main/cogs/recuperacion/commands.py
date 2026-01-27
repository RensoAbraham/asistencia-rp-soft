"""Comandos del módulo de recuperación"""

import discord
from discord import app_commands, Embed, Color
from discord.ext import commands
from utils import obtener_practicante, canal_permitido, verificar_rol_permitido, verificar_recuperacion
from datetime import datetime, time, timedelta
import database as db
import logging


class Recuperacion(commands.Cog):
    """Cog para gestionar comandos de recuperación"""
    
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @app_commands.command(name='recuperación', description="Registrar una sesión de recuperación")
    async def recuperacion(self, interaction: discord.Interaction):
        from utils import es_domingo, LIMA_TZ
        await interaction.response.defer(ephemeral=True)
        
        # Bloquear domingos
        if es_domingo():
            await interaction.followup.send(
                "⛔ **Día Domingo, No laboral**\nLos comandos de asistencia están deshabilitados los domingos.",
                ephemeral=True
            )
            return

        if not await canal_permitido(interaction):
            logging.warning(f'Canal no permitido para el usuario {interaction.user.display_name}.')
            return
        
        # Verificar roles permitidos para recuperación (antes de defer)
        servidor_id = interaction.guild.id
        bot = interaction.client
        roles_permitidos = bot.roles_recuperacion.get(servidor_id, [])
        
        # Si hay roles configurados, verificar permisos
        if roles_permitidos:
            if not await verificar_rol_permitido(interaction, roles_permitidos, usar_followup=True):
                logging.warning(f'Usuario {interaction.user.display_name} no tiene los roles necesarios para recuperación.')
                return
        

        discord_id = interaction.user.id
        nombre_usuario = interaction.user.mention
        logging.info(f'Usuario {interaction.user.display_name} está intentando registrar recuperación.')
        
        practicante_id = await obtener_practicante(interaction, discord_id)
        if not practicante_id:
            logging.warning(f'Practicante no encontrado para el usuario {interaction.user.display_name}.')
            return

        fecha_actual = datetime.now(LIMA_TZ).date()
        hora_actual = datetime.now(LIMA_TZ).time()
        hora_inicio_permitida = time(14, 30)  # 2:30 PM
        hora_fin_permitida = time(20, 0)      # 8:00 PM

        # Verificar si la hora actual está dentro del rango permitido
        if not (hora_inicio_permitida <= hora_actual <= hora_fin_permitida):
            embed = Embed(
                title="⏰ Horario no permitido",
                description=f"{nombre_usuario}, las recuperaciones solo pueden registrarse entre las 2:30 PM y las 8:00 PM.",
                color=Color.red()
            )
            embed.set_footer(text="Horario permitido: 2:30 PM - 8:00 PM")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Verificar si ya existe una recuperación para hoy
        recuperacion_existente = await verificar_recuperacion(practicante_id, fecha_actual)
        
        if recuperacion_existente:
            embed = Embed(
                title="⚠️ Recuperación ya registrada",
                description=f"{nombre_usuario}, ya has registrado una recuperación el día de hoy.",
                color=Color.orange()
            )
            embed.set_footer(text="Solo se permite una recuperación por día.")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Insertar la recuperación en la base de datos
        query_insert_recuperacion = """
        INSERT INTO asistencia_recuperacion (practicante_id, fecha_recuperacion, hora_entrada)
        VALUES (%s, %s, %s)
        """
        await db.execute_query(query_insert_recuperacion, (practicante_id, fecha_actual, hora_actual))
        logging.info(f'Recuperación registrada para el usuario {interaction.user.display_name}.')

        # Crear embed de confirmación
        embed = Embed(
            title="✅ Recuperación Registrada",
            description=f"{nombre_usuario}, se ha registrado tu recuperación correctamente.",
            color=Color.green()
        )
        embed.add_field(name="🕒 Hora de Entrada", value=f"{hora_actual.strftime('%H:%M')}", inline=False)
        embed.add_field(name="📅 Fecha", value=f"{fecha_actual.strftime('%d/%m/%Y')}", inline=False)
        embed.set_footer(text="Si tienes dudas, contacta con el administrador.")

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name='recuperacion_salida', description="Registrar salida de recuperación")
    async def recuperacion_salida(self, interaction: discord.Interaction):
        from utils import es_domingo, LIMA_TZ
        
        if es_domingo():
            await interaction.response.send_message("⛔ **Día Domingo, No laboral**", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        practicante_id = await obtener_practicante(interaction, interaction.user.id)
        if not practicante_id: return

        fecha_actual = datetime.now(LIMA_TZ).date()
        hora_actual = datetime.now(LIMA_TZ).time()
        
        # Buscar recuperación activa (sin salida)
        query = "SELECT id, hora_entrada FROM asistencia_recuperacion WHERE practicante_id=%s AND fecha_recuperacion=%s AND hora_salida IS NULL"
        rec = await db.fetch_one(query, (practicante_id, fecha_actual))
        
        if not rec:
            await interaction.followup.send("⚠️ No tienes una sesión de recuperación activa hoy.", ephemeral=True)
            return

        # Actualizar salida
        await db.execute_query("UPDATE asistencia_recuperacion SET hora_salida=%s WHERE id=%s", (hora_actual, rec['id']))
        
        # Calcular duración
        inicio = datetime.combine(fecha_actual, (datetime.min + rec['hora_entrada']).time())
        fin = datetime.combine(fecha_actual, hora_actual)
        duracion = fin - inicio
        horas = duracion.seconds // 3600
        minutos = (duracion.seconds % 3600) // 60
        
        embed = Embed(title="✅ Salida de Recuperación", color=Color.blue())
        embed.add_field(name="Duración", value=f"{horas}h {minutos}m")
        embed.add_field(name="Hora Salida", value=hora_actual.strftime('%H:%M'))
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name='recuperación_historial', description="Consultar tu historial de recuperaciones")
    @app_commands.describe(dias="Cantidad de días a mostrar (1-30)")
    async def historial_recuperaciones(self, interaction: discord.Interaction, dias: int = 15):
        if not await canal_permitido(interaction):
            logging.warning(f'Canal no permitido para el usuario {interaction.user.display_name}.')
            return
        
        await interaction.response.defer(ephemeral=True)

        discord_id = interaction.user.id
        nombre_usuario = interaction.user.mention
        logging.info(f'Usuario {interaction.user.display_name} está consultando su historial de recuperaciones.')
        
        practicante_id = await obtener_practicante(interaction, discord_id)
        if not practicante_id:
            logging.warning(f'Practicante no encontrado para el usuario {interaction.user.display_name}.')
            return
        
        # Validar el rango de días
        if dias < 1 or dias > 30:
            await interaction.followup.send(
                f"{nombre_usuario}, el número de días debe estar entre 1 y 30.",
                ephemeral=True
            )
            return
        
        fecha_actual = datetime.now().date()
        fecha_inicio = fecha_actual - timedelta(days=dias)

        query_historial = """
            SELECT date_format(fecha_recuperacion, '%%m-%%d') as fecha, hora_entrada, hora_salida
            FROM asistencia_recuperacion
            WHERE practicante_id = %s AND fecha_recuperacion >= %s
            ORDER BY fecha_recuperacion DESC
        """

        resultados = await db.fetch_all(query_historial, (practicante_id, fecha_inicio))

        if not resultados:
            embed = Embed(
                title="📋 Historial de Recuperaciones",
                description=f"{nombre_usuario}, no se encontraron recuperaciones en los últimos {dias} días.",
                color=Color.blue()
            )
            embed.set_footer(text="Si tienes dudas, contacta con el administrador.")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Crear el Embed para el historial
        embed = Embed(
            title=f"📋 Historial de Recuperaciones - Últimos {dias} días",
            description=f"**{interaction.user.display_name}**, aquí está tu historial de recuperaciones para los últimos {dias} días:",
            color=Color.blue()
        )

        # Recorrer los resultados y añadirlos al Embed
        for resultado in resultados:
            fecha = resultado['fecha']
            entrada = resultado['hora_entrada'] or 'No registrada'
            salida = resultado['hora_salida'] or 'No registrada'

            # Añadir cada recuperación al Embed
            embed.add_field(
                name=f"📅 Fecha: **{fecha}**",
                value=f"**Hora de Entrada**: {entrada} | **Hora de Salida**: {salida}",
                inline=False
            )
        
        embed.set_footer(text="Si tienes dudas, contacta con el administrador.")

        await interaction.followup.send(embed=embed, ephemeral=True)



async def setup(bot):
    await bot.add_cog(Recuperacion(bot))
