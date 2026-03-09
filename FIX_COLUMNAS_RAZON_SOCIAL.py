"""
FIX: Renombrar columnas razon_social_proveedor a razon_social
====================================================================
El código routes.py usa 'razon_social' pero el schema tiene 'razon_social_proveedor'
Este script corrige el desajuste de nombres.
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def fix_columnas():
    """Renombra las columnas en las tablas ERP para coincidir con el código"""
    
    # Conectar a PostgreSQL
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    
    try:
        print("🔧 Renombrando columnas razon_social_proveedor → razon_social\n")
        
        # 1. Tabla erp_comercial
        print("📋 Tabla: erp_comercial")
        try:
            cursor.execute("""
                ALTER TABLE erp_comercial 
                RENAME COLUMN razon_social_proveedor TO razon_social
            """)
            print("   ✅ Columna renombrada exitosamente")
        except psycopg2.errors.UndefinedColumn:
            print("   ⚠️ La columna ya se llama 'razon_social' o no existe")
            conn.rollback()
        
        # 2. Tabla erp_financiero
        print("\n📋 Tabla: erp_financiero")
        try:
            cursor.execute("""
                ALTER TABLE erp_financiero 
                RENAME COLUMN razon_social_proveedor TO razon_social
            """)
            print("   ✅ Columna renombrada exitosamente")
        except psycopg2.errors.UndefinedColumn:
            print("   ⚠️ La columna ya se llama 'razon_social' o no existe")
            conn.rollback()
        
        # Commit cambios
        conn.commit()
        print("\n✅ CAMBIOS APLICADOS - Reinicia el servidor Flask para usar las tablas corregidas")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    fix_columnas()
