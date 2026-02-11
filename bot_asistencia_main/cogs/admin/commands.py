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

@app_commands.default_permissions(administrator=True)
class Admin(commands.GroupCog, name="admin"):
    """Cog para comandos administrativos"""

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.AUTHORIZED_USERS = [615932763161362636, 824692049084678144]  # Renso - Wilber

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Verificar si el usuario tiene permisos (Respaldo -> BD -> Admin de Server)"""
        # 1. Respaldo por ID
        if interaction.user.id in self.AUTHORIZED_USERS:
            return True
            
        # 2. Base de datos
        try:
            if await es_admin_bot(interaction.user.id):
                return True
        except:
            pass

        # 3. Permisos de servidor
        if interaction.user.guild_permissions.administrator:
            return True
        
        await interaction.response.send_message("❌ No tienes permisos suficientes para acceder a este panel.", ephemeral=True)
        return False

class ConfirmacionEliminar(discord.ui.View):
    def __init__(self, admin_cog, interaction, id_discord, nombre_completo):
        super().__init__(timeout=60)
        self.admin_cog = admin_cog
        self.interaction = interaction
        self.id_discord = id_discord
        self.nombre_completo = nombre_completo
        self.confirmado = False

    @discord.ui.button(label="Confirmar Eliminación", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction.user.id:
            return await interaction.response.send_message("❌ Solo el administrador que inició el comando puede confirmar.", ephemeral=True)
        
        self.confirmado = True
        await interaction.response.defer()
        
        try:
            # Lógica de eliminación (movida aquí)
            query_check = "SELECT id FROM practicante WHERE id_discord = %s"
            practicante = await db.fetch_one(query_check, (self.id_discord,))
            
            if not practicante:
                await interaction.followup.send(f"❌ El practicante ya no existe.", ephemeral=True)
                return

            # Eliminar registros relacionados
            await db.execute_query("DELETE FROM asistencia WHERE practicante_id = %s", (practicante['id'],))
            await db.execute_query("DELETE FROM asistencia_recuperacion WHERE practicante_id = %s", (practicante['id'],))
            await db.execute_query("DELETE FROM practicante WHERE id = %s", (practicante['id'],))
            
            await interaction.followup.edit_message(
                message_id=self.interaction.message.id,
                content=f"✅ **{self.nombre_completo}** ha sido eliminado permanentemente de la base de datos.",
                view=None
            )
            logging.info(f"Admin {interaction.user.display_name} eliminó permanentemente a {self.nombre_completo}")

        except Exception as e:
            logging.error(f"Error al eliminar practicante: {e}")
            await interaction.followup.send(f"❌ Error al eliminar: {e}", ephemeral=True)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Acción cancelada. No se realizaron cambios.", view=None)
        self.stop()


    @app_commands.command(name='reporte_hoy', description="Ver el estado de todos los practicantes hoy")
    async def reporte_hoy(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        fecha_actual = datetime.now(LIMA_TZ).date()
        hora_actual = datetime.now(LIMA_TZ).time()
        
        # Horario de corte para considerar falta vs pendiente
        HORA_CORTE_FALTA = time(14, 30)

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
        first_field = True
        
        for res in resultados:
            nombre = res['nombre_completo']
            entrada = format_timedelta(res['hora_entrada'])
            salida = format_timedelta(res['hora_salida'])
            
            # Lógica de Estado
            if res['estado']:
                estado = res['estado']
            else:
                # Si no tiene estado registrado
                if hora_actual < HORA_CORTE_FALTA:
                    estado = "Pendiente"
                else:
                    estado = "Falta"
            
            emoji = "✅" if res['hora_entrada'] else "❌"
            
            if res['hora_entrada']: 
                presentes += 1
            else: 
                if estado == "Pendiente":
                    emoji = "🟡"
                faltan += 1

            linea = f"{emoji} **{nombre}** | {entrada} - {salida} | *{estado}*\n"
            
            # Evitar exceder el límite de caracteres de un solo field (1024 chars)
            if len(lista_practicantes) + len(linea) > 1000:
                name_field = "Practicantes" if first_field else "..."
                embed.add_field(name=name_field, value=lista_practicantes, inline=False)
                lista_practicantes = linea
                first_field = False
            else:
                lista_practicantes += linea

        if lista_practicantes:
            name_field = "Practicantes" if first_field else "..."
            embed.add_field(name=name_field, value=lista_practicantes, inline=False)

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
            
            # Validar que el estado existe en la base de datos
            if estado_id is None:
                await interaction.followup.send(f"❌ El estado '{estado or 'Presente'}' no existe en la base de datos. Estados válidos: Presente, Tardanza, Falta Injustificada, Falta Recuperada, Permiso.", ephemeral=True)
                return
            
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
                if estado_id is None:
                    await interaction.followup.send(f"❌ El estado '{estado}' no existe en la base de datos. Estados válidos: Presente, Tardanza, Falta Injustificada, Falta Recuperada, Permiso.", ephemeral=True)
                    return
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

        # Paginación: Discord permite max 25 fields por Embed.
        CHUNK_SIZE = 25
        chunks = [resultados[i:i + CHUNK_SIZE] for i in range(0, len(resultados), CHUNK_SIZE)]
        
        for i, chunk in enumerate(chunks):
            embed = Embed(
                title=f"📈 Resumen General de Horas (Parte {i+1}/{len(chunks)})",
                description="Acumulado total de horas trabajadas (Base + Bot).",
                color=Color.green()
            )

            for res in chunk:
                bot_str = format_timedelta_total(res['horas_bot_raw'])
                base_str = format_timedelta_total(res['horas_base'])
                
                # Cálculo de Total (sumando bot y base)
                try:
                    h1, m1, s1 = map(int, bot_str.split(':'))
                    h2, m2, s2 = map(int, base_str.split(':'))
                    
                    total_h = h1 + h2
                    total_m = m1 + m2
                    total_s = s1 + s2
                    
                    if total_s >= 60:
                        total_m += total_s // 60
                        total_s %= 60
                    if total_m >= 60:
                        total_h += total_m // 60
                        total_m %= 60
                    
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
            query_check = "SELECT nombre_completo FROM practicante WHERE id_discord = %s"
            practicante = await db.fetch_one(query_check, (id_discord,))
            
            if not practicante:
                await interaction.followup.send(f"❌ No se encontró ningún practicante con el ID: `{id_discord}`", ephemeral=True)
                return

            # Crear mensaje de confirmación
            nombre = practicante['nombre_completo']
            embed = Embed(
                title="⚠️ Confirmación de Eliminación",
                description=(
                    f"¿Estás seguro de que deseas eliminar a **{nombre}**?\n\n"
                    "🔴 **ATENCIÓN:** Esta acción borrará permanentemente:\n"
                    "• El registro del practicante.\n"
                    "• Todas sus asistencias históricas.\n"
                    "• Todas sus recuperaciones pendientes o completadas.\n\n"
                    "Esta acción **no se puede deshacer**."
                ),
                color=Color.red()
            )
            
            view = ConfirmacionEliminar(self, interaction, id_discord, nombre)
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        except Exception as e:
            logging.error(f"Error al iniciar eliminación de practicante: {e}")
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

    @app_commands.command(name='configurar', description="Panel de configuración y gestión del equipo")
    async def configurar(self, interaction: discord.Interaction):
        """Abre un menú interactivo para configurar canales y ver al equipo"""
        # Obtener equipo de desarrollo de la BD
        query_equipo = "SELECT nombre_referencia, rol, discord_id FROM bot_admins ORDER BY rol DESC"
        equipo = await db.fetch_all(query_equipo)
        
        texto_equipo = ""
        for mem in equipo:
            texto_equipo += f"• <@{mem['discord_id']}> (**{mem['rol']}**)\n"

        embed = discord.Embed(
            title="⚙️ Panel de Administración - RP Soft",
            description=(
                "### 👥 Equipo de Desarrollo\n"
                f"{texto_equipo}\n"
                "--- \n"
                "**Selecciona una opción abajo para configurar el servidor o gestionar el bot.**"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Gestión de Asistencia v2.0 • Sistema de Seguridad Activo")
        
        view = ConfigView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class ConfigSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Canal de Asistencia", description="Establece el canal donde se marcará asistencia", emoji="📝"),
            discord.SelectOption(label="Canal de Reportes", description="Establece el canal para reportes diarios", emoji="📊"),
            discord.SelectOption(label="Menciones de Reporte", description="Configura quiénes serán avisados en el reporte", emoji="🔔"),
            discord.SelectOption(label="Agregar Administrador del Bot", description="Dar permisos de Developer a un usuario", emoji="👨‍💻"),
            discord.SelectOption(label="Estado de Invitación", description="Ver link de invitación del bot", emoji="🔗"),
        ]
        super().__init__(placeholder="Selecciona una opción a configurar...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # ... (lógica anterior de canales)
        
        # 4. Agregar Administrador (NUEVO)
        if self.values[0] == "Agregar Administrador del Bot":
            await interaction.response.send_message(
                "Envía el **ID de Discord** del nuevo administrador (ej. 123456789):",
                ephemeral=True
            )
            def check(m): return m.author == interaction.user and m.channel == interaction.channel
            try:
                msg = await interaction.client.wait_for('message', check=check, timeout=30)
                new_id = int(msg.content) if msg.content.isdigit() else None
                await msg.delete()

                if new_id:
                    # Traer nombre del usuario para confirmar
                    user = await interaction.client.fetch_user(new_id)
                    view = ConfirmacionNuevoAdmin(new_id, user.name)
                    embed = discord.Embed(
                        title="⚠️ Doble Confirmación",
                        description=f"¿Estás seguro de que quieres darle permisos de **Developer** a **{user.name}** (ID: `{new_id}`)?\n\nPodrá acceder a este panel de configuración.",
                        color=discord.Color.gold()
                    )
                    await interaction.followup.send(embed=embed, view=view, ephemeral=True)
                else: await interaction.followup.send("❌ ID no válido.", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"❌ Error o tiempo agotado: {e}", ephemeral=True)

        elif self.values[0] == "Canal de Asistencia":
            # (Mantener lógica de Canal de Asistencia aquí...)
            pass

class ConfirmacionNuevoAdmin(discord.ui.View):
    def __init__(self, discord_id, nombre):
        super().__init__(timeout=60)
        self.discord_id = discord_id
        self.nombre = nombre

    @discord.ui.button(label="Sí, Agregar como Developer", style=discord.ButtonStyle.success, emoji="✅")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        query = "INSERT INTO bot_admins (discord_id, nombre_referencia, rol) VALUES (%s, %s, %s)"
        await db.execute_query(query, (self.discord_id, self.nombre, 'Developer'))
        await interaction.response.edit_message(content=f"✅ **{self.nombre}** ha sido añadido al equipo como **Developer**.", embed=None, view=None)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Acción cancelada.", embed=None, view=None)

class ConfigView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ConfigSelect())

async def setup(bot):
    # Añadir el comando configurar fuera del Cog por conveniencia o dentro si se desea
    # Lo añadiré dentro de la clase Admin para mantener el grupo
    pass

# Actualizar el Cog Admin para incluir el comando configurar
# Voy a añadirlo al final de la clase Admin antes del cierre
