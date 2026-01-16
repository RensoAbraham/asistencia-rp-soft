import gspread
from google.oauth2.service_account import Credentials
import logging
import os

# Configuración
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
CREDENTIALS_FILE = '/app/credentials.json'  # Ruta en el contenedor Docker
# Si estás probando localmente fuera de Docker, podrías necesitar ajustar la ruta
# CREDENTIALS_FILE = 'credentials.json' 
SHEET_NAME_ENV = 'GOOGLE_SHEET_NAME' # Nombre de la hoja en .env

def get_practicantes_from_sheet():
    """
    Lee la lista de practicantes desde Google Sheets.
    Retorna una lista de diccionarios con 'id_discord', 'nombre', 'apellido'.
    """
    sheet_name = os.getenv(SHEET_NAME_ENV, 'Practicantes_RP_Soft')
    
    # Verificar si existe el archivo de credenciales
    if not os.path.exists(CREDENTIALS_FILE) and not os.path.exists('credentials.json'):
         # Fallback para pruebas locales si no está en /app
        if os.path.exists('credentials.json'):
            creds_path = 'credentials.json'
        else:
            logging.warning(f"⚠️ No se encontró {CREDENTIALS_FILE}. La sincronización con Google Sheets no funcionará.")
            return []
    else:
        creds_path = CREDENTIALS_FILE if os.path.exists(CREDENTIALS_FILE) else 'credentials.json'

    try:
        creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        # Abrir la hoja de cálculo
        try:
            sheet = client.open(sheet_name).sheet1
        except gspread.SpreadsheetNotFound:
            logging.error(f"❌ No se encontró la hoja de cálculo: '{sheet_name}'. Verifica el nombre.")
            return []
        
        # Obtener todos los registros (asumiendo fila 1 = encabezados)
        # Se espera: Timestamp, ID Discord, Nombre Completo
        # Indices (0-based): 0=Timestamp, 1=ID Discord, 2=Nombre Completo
        rows = sheet.get_all_values()
        
        if len(rows) < 2:
            return [] # Hoja vacía
            
        practicantes = []
        
        # Detectar índices de columnas por nombre (más robusto)
        headers = [h.lower() for h in rows[0]]
        try:
            # Buscar columnas clave (ajusta 'id' y 'nombre' según tus preguntas del Form)
            idx_id = next(i for i, h in enumerate(headers) if 'id' in h and 'discord' in h)
            idx_nombre = next(i for i, h in enumerate(headers) if 'nombre' in h)
            
            # Buscar columna opcional de Horas Base
            try:
                idx_horas_base = next(i for i, h in enumerate(headers) if 'base' in h or 'acumuladas' in h)
            except StopIteration:
                idx_horas_base = None
                
        except StopIteration:
            logging.error("❌ No se encontraron las columnas 'ID Discord' o 'Nombre' en el Excel.")
            return []

        for row in rows[1:]: # Saltar encabezado
            if len(row) <= max(idx_id, idx_nombre): continue
            
            raw_id = row[idx_id].strip()
            nombre_completo = row[idx_nombre].strip()
            # Correo eliminado por solicitud del usuario
            horas_base = row[idx_horas_base].strip() if idx_horas_base is not None and len(row) > idx_horas_base else "00:00:00"
            
            # Validar formato de horas base
            # 1. Si es solo números (ej: "10"), lo convertimos a "10:00:00"
            if horas_base and horas_base.isdigit():
                horas_base = f"{horas_base}:00:00"
            # 2. Si no tiene ':' y tampoco es número, o está vacío, poner 0
            elif not horas_base or ':' not in horas_base:
                horas_base = "00:00:00"
            # 3. Si tiene formato decimal (ej "10.5"), intentamos arreglarlo o lo dejamos en 0
            elif '.' in horas_base and ':' not in horas_base:
                 try:
                     h = int(float(horas_base))
                     horas_base = f"{h}:00:00"
                 except:
                     horas_base = "00:00:00"

            if not raw_id or not nombre_completo: continue
            
            try:
                # Limpiar ID (a veces Excel lo pone como científico 1.23E+17)
                # Usamos una forma más segura para no perder precisión con números grandes
                raw_id_clean = "".join(filter(str.isdigit, raw_id))
                if not raw_id_clean:
                    # Si no hay dígitos, intentamos float por si acaso, pero con cuidado
                    discord_id = int(float(raw_id))
                else:
                    discord_id = int(raw_id_clean)
                
                # Dividir nombre
                partes = nombre_completo.split(' ', 1)
                nombre = partes[0]
                apellido = partes[1] if len(partes) > 1 else ''
                
                practicantes.append({
                    'id_discord': discord_id,
                    'nombre': nombre,
                    'apellido': apellido,
                    'horas_base': horas_base
                })
            except ValueError:
                logging.warning(f"⚠️ ID inválido ignorado: {raw_id} ({nombre_completo})")
                continue
                
        logging.info(f"✅ Leídos {len(practicantes)} practicantes de Google Sheets (Sin correos).")
        return practicantes

    except Exception as e:
        logging.error(f"❌ Error crítico en sync Google Sheets: {e}")
        return []

async def sync_practicantes_to_db():
    """
    Función principal para sincronizar datos de Sheets hacia la BD.
    Sincroniza ID, Nombre, Apellido y Horas Base. Ignora correos.
    """
    import database as db
    
    practicantes = get_practicantes_from_sheet()
    
    if not practicantes:
        return
    
    nuevos = 0
    actualizados = 0
    
    for p in practicantes:
        # 1. Intentar Insertar (Nuevos) o Actualizar
        # Nota: El campo correo es obligatorio en la BD actual. Insertaremos un dummy vacío.
        query_insert = """
        INSERT INTO practicante (id_discord, nombre, apellido, correo, horas_base, estado)
        VALUES (%s, %s, %s, '', %s, 'activo')
        ON DUPLICATE KEY UPDATE 
            nombre = VALUES(nombre),
            apellido = VALUES(apellido),
            horas_base = VALUES(horas_base)
        """
        
        await db.execute_query(query_insert, (
            p['id_discord'], p['nombre'], p['apellido'], p['horas_base']
        ))
            
    logging.info(f"📥 Sincronización completa (Nuevos/Actualizados) desde Sheets.")

async def export_report_to_sheet():
    """
    Lee la vista reporte_asistencia de la BD y la exporta a una nueva pestaña en Google Sheets.
    """
    import database as db
    
    # 1. Obtener datos de la base de datos
    query = "SELECT * FROM reporte_asistencia ORDER BY Fecha DESC, Nombre ASC"
    data = await db.fetch_all(query)
    
    if not data:
        logging.info("↻ Reporte Sheets: No hay datos para exportar.")
        return

    sheet_name = os.getenv(SHEET_NAME_ENV, 'Practicantes_RP_Soft')
    
    # Verificar si existe el archivo de credenciales
    if not os.path.exists(CREDENTIALS_FILE) and not os.path.exists('credentials.json'):
        logging.warning("⚠️ No se encontraron credenciales para Google Sheets.")
        return
    
    creds_path = CREDENTIALS_FILE if os.path.exists(CREDENTIALS_FILE) else 'credentials.json'

    try:
        creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open(sheet_name)
        
        # 2. Obtener o crear la hoja de reporte detallado
        try:
            worksheet_det = spreadsheet.worksheet("Reporte Detallado")
        except gspread.WorksheetNotFound:
            worksheet_det = spreadsheet.add_worksheet(title="Reporte Detallado", rows="1000", cols="10")
        
        # 3. Formatear datos para gspread (Detallado)
        headers_det = ["Fecha", "Nombre", "Apellido", "Entrada", "Salida", "Horas Sesión", "Horas Acumuladas", "Estado"]
        rows_det = [headers_det]
        
        for row in data:
            rows_det.append([
                str(row['Fecha']),
                row['Nombre'],
                row['Apellido'],
                str(row['Entrada']) if row['Entrada'] else '-',
                str(row['Salida']) if row['Salida'] else '-',
                str(row['Horas_Sesion']) if row['Horas_Sesion'] else '00:00:00',
                str(row['Horas_Acumuladas_Hasta_Hoy']) if row['Horas_Acumuladas_Hasta_Hoy'] else '00:00:00',
                row['Estado']
            ])
            
        # 4. Limpiar y actualizar Detallado
        worksheet_det.clear()
        worksheet_det.update('A1', rows_det)

        # ---------------------------------------------------------
        # 5. Generar Hoja de "Resumen General" (Acumulado por alumno)
        # ---------------------------------------------------------
        try:
            worksheet_res = spreadsheet.worksheet("Resumen General")
        except gspread.WorksheetNotFound:
            worksheet_res = spreadsheet.add_worksheet(title="Resumen General", rows="100", cols="6")

        # Consulta agrupa por practicante para ver totales reales
        query_resumen = """
        SELECT 
            p.nombre, 
            p.apellido, 
            IFNULL(p.horas_base, '00:00:00') as Horas_Base,
            -- Suma de horas trabajadas (diferencia salida - entrada)
            SEC_TO_TIME(SUM(IFNULL(TIME_TO_SEC(TIMEDIFF(a.hora_salida, a.hora_entrada)), 0))) as Horas_Trabajadas_Bot,
            -- Total (Base + Bot)
            ADDTIME(
                IFNULL(p.horas_base, '00:00:00'),
                SEC_TO_TIME(SUM(IFNULL(TIME_TO_SEC(TIMEDIFF(a.hora_salida, a.hora_entrada)), 0)))
            ) as Total_Acumulado,
            -- Meta (Ejemplo 480h)
            '480:00:00' as Meta
        FROM practicante p
        LEFT JOIN asistencia a ON p.id = a.practicante_id AND a.hora_salida IS NOT NULL
        GROUP BY p.id, p.nombre, p.apellido, p.horas_base
        ORDER BY Total_Acumulado DESC
        """
        data_resumen = await db.fetch_all(query_resumen)
        
        headers_res = ["Nombre", "Apellido", "Horas Base (Anteriores)", "Horas Bot (Nuevas)", "TOTAL ACUMULADO", "Meta (480h)"]
        rows_res = [headers_res]
        
        for row in data_resumen:
            rows_res.append([
                row['nombre'],
                row['apellido'],
                str(row['Horas_Base']),
                str(row['Horas_Trabajadas_Bot']),
                str(row['Total_Acumulado']),
                row['Meta']
            ])

        worksheet_res.clear()
        worksheet_res.update('A1', rows_res)
        
        logging.info(f"📊 Reportes actualizados: 'Reporte Detallado' ({len(data)} filas) y 'Resumen General' ({len(data_resumen)} filas).")
        
    except Exception as e:
        logging.error(f"❌ Error al exportar reporte a Google Sheets: {e}")
