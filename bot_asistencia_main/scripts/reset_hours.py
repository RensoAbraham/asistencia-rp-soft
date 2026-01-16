import asyncio
import os
import sys

# Añadir directorio raíz al path para importar database.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
import database as db

async def reset_hours():
    # Cargar variables de entorno
    load_dotenv()
    
    print("⏳ Conectando a la base de datos...")
    await db.init_db_pool()
    
    print("⚠️  Iniciando vaciado de tablas de asistencia...")
    
    try:
        # 1. Limpiar tabla de Asistencia Diaria
        await db.execute_query("TRUNCATE TABLE asistencia;")
        print("✅ Tabla 'asistencia' vaciada.")
        
        # 2. Limpiar tabla de Recuperaciones
        await db.execute_query("TRUNCATE TABLE asistencia_recuperacion;")
        print("✅ Tabla 'asistencia_recuperacion' vaciada.")
        
        print("\n✨ ¡Limpieza completada! Todos los contadores de horas están a CERO.")
        print("   (La lista de practicantes y sus ID se ha mantenido intacta)")
        
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
    finally:
        await db.close_db_pool()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(reset_hours())
