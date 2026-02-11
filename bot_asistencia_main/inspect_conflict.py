import asyncio
import database as db
import logging
from datetime import date

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def inspect():
    fecha_erronea = date(2026, 1, 6)
    fecha_correcta = date(2026, 2, 6)
    
    # Obtener IDs de practicantes con registro en fecha errónea
    query = """
    SELECT p.id, p.nombre_completo 
    FROM asistencia a
    JOIN practicante p ON a.practicante_id = p.id
    WHERE a.fecha = %s
    """
    practicantes_erroneos = await db.fetch_all(query, (fecha_erronea,))
    
    if not practicantes_erroneos:
        logging.info("No hay registros en la fecha errónea.")
        return

    logging.info(f"Encontrados {len(practicantes_erroneos)} registros en fecha errónea {fecha_erronea}:")
    for p in practicantes_erroneos:
        logging.info(f" - {p['nombre_completo']} (ID: {p['id']})")
        
        # Verificar si existe en fecha correcta
        query_check = "SELECT * FROM asistencia WHERE practicante_id = %s AND fecha = %s"
        coincidencia = await db.fetch_one(query_check, (p['id'], fecha_correcta))
        
        if coincidencia:
            logging.warning(f"   ⚠️ YA EXISTE registro para {fecha_correcta}: {coincidencia}")
        else:
            logging.info(f"   ✅ No existe registro para {fecha_correcta}. Se puede mover sin problemas.")

    await db.close_db_pool()

if __name__ == "__main__":
    asyncio.run(inspect())
