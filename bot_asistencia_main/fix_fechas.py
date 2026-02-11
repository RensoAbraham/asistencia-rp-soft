import asyncio
import database as db
import logging
from datetime import date

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def fix_fechas():
    logging.info("Iniciando corrección de fechas...")
    
    fecha_incorrecta = date(2026, 1, 6)
    fecha_correcta = date(2026, 2, 6)

    try:
        # Verificar cuántos registros hay en la fecha incorrecta
        query_check = "SELECT id, practicante_id FROM asistencia WHERE fecha = %s"
        registros_erroneos = await db.fetch_all(query_check, (fecha_incorrecta,))
        
        if not registros_erroneos:
            logging.info("✅ No se encontraron registros con la fecha 2026-01-06.")
            return

        logging.info(f"⚠️ Se encontraron {len(registros_erroneos)} registros con fecha {fecha_incorrecta}. Procesando...")

        for reg in registros_erroneos:
            p_id = reg['practicante_id']
            id_erroneo = reg['id']
            
            # Verificar si ya existe registro en la fecha correcta
            query_existente = "SELECT id FROM asistencia WHERE practicante_id = %s AND fecha = %s"
            coincidencia = await db.fetch_one(query_existente, (p_id, fecha_correcta))
            
            if coincidencia:
                # Si existe, ELIMINAMOS el registro existente en la fecha correcta para que prevalezca el corregido
                # (Asumiendo que el del Enero 6 es el que tiene la info valiosa que el usuario editó manualmente)
                logging.info(f"   ⚠️ Encontrado conflicto para practicante {p_id}. Eliminando registro vacio/incorrecto de {fecha_correcta} (ID: {coincidencia['id']})...")
                await db.execute_query("DELETE FROM asistencia WHERE id = %s", (coincidencia['id'],))
            
            # Ahora movemos el registro de Enero a Febrero
            await db.execute_query("UPDATE asistencia SET fecha = %s WHERE id = %s", (fecha_correcta, id_erroneo))
            logging.info(f"   ✅ Registro {id_erroneo} movido a {fecha_correcta}.")
        
        logging.info("✅ Corrección completada exitosamente.")
        
    except Exception as e:
        logging.error(f"❌ Error al corregir fechas: {e}")
    finally:
        await db.close_db_pool()

if __name__ == "__main__":
    asyncio.run(fix_fechas())
