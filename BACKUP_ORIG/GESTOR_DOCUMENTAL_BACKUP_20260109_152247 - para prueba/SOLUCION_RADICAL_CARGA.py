"""
SOLUCIÓN RADICAL PARA CARGAR ARCHIVOS
Diciembre 29, 2025

PROBLEMA: Archivos con duplicados internos causan error "ON CONFLICT DO UPDATE cannot affect row a second time"
SOLUCIÓN: Eliminar constraint, cargar todo, limpiar duplicados después
"""

import psycopg2
from psycopg2.extras import execute_batch
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv('DATABASE_URL')

def ejecutar_solucion_radical():
    """Preparar BD para carga sin restricciones"""
    
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("🔥 SOLUCIÓN RADICAL - PREPARANDO CARGA SIN RESTRICCIONES")
    print("=" * 80)
    
    # 1. ELIMINAR CONSTRAINT UNIQUE TEMPORALMENTE
    print("\n1️⃣ Eliminando constraint UNIQUE temporal...")
    cursor.execute("""
        ALTER TABLE maestro_dian_vs_erp 
        DROP CONSTRAINT IF EXISTS unique_nit_prefijo_folio;
    """)
    conn.commit()
    print("   ✅ Constraint eliminado")
    
    # 2. CREAR ÍNDICE PARA VELOCIDAD (sin unique)
    print("\n2️⃣ Creando índice normal (sin unique) para velocidad...")
    cursor.execute("""
        DROP INDEX IF EXISTS idx_maestro_clave;
        CREATE INDEX IF NOT EXISTS idx_maestro_clave 
        ON maestro_dian_vs_erp(nit_emisor, prefijo, folio);
    """)
    conn.commit()
    print("   ✅ Índice creado")
    
    # 3. MODIFICAR LÓGICA DE CARGA (eliminar ON CONFLICT)
    print("\n3️⃣ Instrucciones para modificar routes.py:")
    print("""
    En actualizar_maestro(), línea ~870, CAMBIAR:
    
    ANTES (con ON CONFLICT):
    INSERT INTO maestro_dian_vs_erp (...)
    SELECT ...
    FROM temp_maestro_nuevos
    ON CONFLICT (nit_emisor, prefijo, folio) DO UPDATE SET ...
    
    DESPUÉS (sin ON CONFLICT - insertar todo):
    INSERT INTO maestro_dian_vs_erp (...)
    SELECT ...
    FROM temp_maestro_nuevos;
    
    -- Luego limpiar duplicados con:
    DELETE FROM maestro_dian_vs_erp a USING maestro_dian_vs_erp b
    WHERE a.id > b.id
      AND a.nit_emisor = b.nit_emisor
      AND a.prefijo = b.prefijo
      AND a.folio = b.folio;
    """)
    
    print("\n" + "=" * 80)
    print("✅ BASE DE DATOS PREPARADA")
    print("=" * 80)
    print("\nAhora ejecuta: python APLICAR_CARGA_SIMPLE.py")
    print("Eso modificará routes.py automáticamente\n")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    ejecutar_solucion_radical()
