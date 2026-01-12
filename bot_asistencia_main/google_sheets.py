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
            # Correo es opcional en el Excel pero obligatorio en BD
            try:
                idx_correo = next(i for i, h in enumerate(headers) if 'correo' in h or 'mail' in h)
            except StopIteration:
                idx_correo = None
        except StopIteration:
            logging.error("❌ No se encontraron las columnas 'ID Discord' o 'Nombre' en el Excel.")
            return []

        for row in rows[1:]: # Saltar encabezado
            if len(row) <= max(idx_id, idx_nombre): continue
            
            raw_id = row[idx_id].strip()
            nombre_completo = row[idx_nombre].strip()
            correo = row[idx_correo].strip() if idx_correo is not None and len(row) > idx_correo else f"registro_{raw_id}@example.com"
            
            if not raw_id or not nombre_completo: continue
            
            try:
                # Limpiar ID (a veces Excel lo pone como científico 1.23E+17)
                discord_id = int(float(raw_id))
                
                # Dividir nombre
                partes = nombre_completo.split(' ', 1)
                nombre = partes[0]
                apellido = partes[1] if len(partes) > 1 else ''
                
                practicantes.append({
                    'id_discord': discord_id,
                    'nombre': nombre,
                    'apellido': apellido,
                    'correo': correo
                })
            except ValueError:
                logging.warning(f"⚠️ ID inválido ignorado: {raw_id} ({nombre_completo})")
                continue
                
        logging.info(f"✅ Leídos {len(practicantes)} practicantes de Google Sheets.")
        return practicantes

    except Exception as e:
        logging.error(f"❌ Error crítico en sync Google Sheets: {e}")
        return []

async def sync_practicantes_to_db():
    """
    Función principal para sincronizar datos de Sheets hacia la BD.
    """
    import database as db
    
    practicantes = get_practicantes_from_sheet()
    
    if not practicantes:
        return
    
    nuevos = 0
    for p in practicantes:
        # Insertar ignorando duplicados (ID Discord es UNIQUE)
        # Opcional: Podríamos usar ON DUPLICATE KEY UPDATE si quisiéramos actualizar nombres
        query = """
        INSERT IGNORE INTO practicante (id_discord, nombre, apellido, correo, estado)
        VALUES (%s, %s, %s, %s, 'activo')
        """
        id_gen = await db.execute_query(query, (p['id_discord'], p['nombre'], p['apellido'], p['correo']))
        
        # execute_query suele retornar el lastrowid, pero con INSERT IGNORE si no inserta puede variar.
        # Una forma mejor de contar es verificar si se insertó, pero por simplicidad:
        if id_gen: 
            nuevos += 1
            
    if nuevos > 0:
        logging.info(f"📥 Sincronización: Se registraron {nuevos} nuevos practicantes desde Sheets.")
    else:
        logging.info("↻ Sincronización: No hubo nuevos practicantes para agregar.")

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
        
        # 2. Obtener o crear la hoja de reporte
        try:
            worksheet = spreadsheet.worksheet("Reporte Asistencia")
        except gspread.WorksheetNotFound:
            # Crear si no existe, con 1000 filas de margen
            worksheet = spreadsheet.add_worksheet(title="Reporte Asistencia", rows="1000", cols="10")
        
        # 3. Formatear datos para gspread
        headers = ["Fecha", "Nombre", "Apellido", "Entrada", "Salida", "Estado", "Tardanza (min)", "Horas Totales"]
        rows_to_write = [headers]
        
        for row in data:
            rows_to_write.append([
                str(row['Fecha']),
                row['Nombre'],
                row['Apellido'],
                str(row['Entrada']) if row['Entrada'] else '-',
                str(row['Salida']) if row['Salida'] else '-',
                row['Estado'],
                str(row['Tardanza_Minutos']),
                str(row['Horas_Trabajadas'])
            ])
            
        # 4. Limpiar y actualizar
        worksheet.clear()
        worksheet.update('A1', rows_to_write)
        logging.info(f"📊 Reporte en Google Sheets actualizado ({len(data)} registros).")
        
    except Exception as e:
        logging.error(f"❌ Error al exportar reporte a Google Sheets: {e}")
