import discord
from discord import app_commands
from discord.ext import commands
import logging
import pandas as pd
import io
import database as db
from datetime import datetime

class Reportes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    # Decorador personalizado para verificar admin
    def es_admin_check():
        def predicate(interaction: discord.Interaction) -> bool:
            # IDs de administradores permitidos (Renso, Joel)
            admin_ids = [
                615932763161362636, 
                501948181538668546
            ]
            if interaction.user.id not in admin_ids:
                return False
            return True
        return app_commands.check(predicate)

    @app_commands.command(name='reporte_admin', description="Generar reporte Excel completo (Solo Admins)")
    @es_admin_check()
    async def reporte_admin(self, interaction: discord.Interaction):
        # Verificar canal permitido (opcional, por ahora lo dejamos libre o restringido a admin)
        
        await interaction.response.defer(ephemeral=True)
        logging.info(f"Admin {interaction.user.display_name} solicitó reporte general.")

        try:
            # 1. Obtener Datos Semanales (Detalle)
            query_semanal = """
                SELECT 
                    p.nombre AS Nombre, 
                    p.apellido AS Apellido, 
                    a.fecha AS Fecha, 
                    a.hora_entrada AS Entrada, 
                    a.hora_salida AS Salida, 
                    ea.estado AS Estado,
                    TIMEDIFF(a.hora_salida, a.hora_entrada) AS Horas_Sesion
                FROM asistencia a
                JOIN practicante p ON a.practicante_id = p.id
                JOIN estado_asistencia ea ON a.estado_id = ea.id
                WHERE a.fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                ORDER BY a.fecha DESC, p.apellido ASC
            """
            
            # 2. Obtener Datos Acumulados (Resumen Global)
            query_acumulado = """
                SELECT 
                    p.nombre AS Nombre, 
                    p.apellido AS Apellido,
                    COUNT(a.id) as Dias_Asistidos,
                    SEC_TO_TIME(SUM(TIME_TO_SEC(IFNULL(TIMEDIFF(a.hora_salida, a.hora_entrada), '00:00:00')))) as Tiempo_Total_Trabajado
                FROM practicante p
                LEFT JOIN asistencia a ON p.id = a.practicante_id
                GROUP BY p.id
                ORDER BY p.apellido ASC
            """

            # Ejecutar queries
            data_semanal = await db.fetch_all(query_semanal)
            data_acumulado = await db.fetch_all(query_acumulado)

            if not data_semanal and not data_acumulado:
                await interaction.followup.send("No hay datos para generar el reporte.", ephemeral=True)
                return

            # Crear DataFrames con Pandas
            df_semanal = pd.DataFrame(data_semanal)
            df_acumulado = pd.DataFrame(data_acumulado)

            # Generar el archivo Excel en memoria
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                if not df_semanal.empty:
                    df_semanal.to_excel(writer, index=False, sheet_name='Semana Actual')
                if not df_acumulado.empty:
                    df_acumulado.to_excel(writer, index=False, sheet_name='Resumen Acumulado')
            
            buffer.seek(0)
            archivo = discord.File(buffer, filename=f"Reporte_General_{datetime.now().strftime('%Y-%m-%d')}.xlsx")

            await interaction.followup.send(
                content=f"✅ **Reporte Generado Exitosamente**\nAquí tienes el reporte con el detalle semanal y el acumulado total.", 
                file=archivo, 
                ephemeral=True
            )

        except Exception as e:
            logging.error(f"Error generando reporte: {e}")
            await interaction.followup.send(f"❌ Ocurrió un error al generar el reporte: {e}", ephemeral=True)

    @reporte_admin.error
    async def reporte_admin_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("⛔ **Acceso Denegado**: No tienes permisos de administrador para usar este comando.", ephemeral=True)
        else:
            logging.error(f"Error en comando reporte_admin: {error}")

async def setup(bot):
    await bot.add_cog(Reportes(bot))
