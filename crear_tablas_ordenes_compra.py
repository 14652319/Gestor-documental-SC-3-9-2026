"""
Script para crear tablas de Órdenes de Compra
Ejecuta el schema SQL en la base de datos
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def ejecutar_schema():
    """Ejecuta el schema de órdenes de compra"""
    
    # Obtener URL de la base de datos
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: No se encontró DATABASE_URL en .env")
        return False
    
    try:
        # Conectar a la base de datos
        print("📊 Conectando a la base de datos...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Leer el archivo SQL
        schema_path = os.path.join('sql', 'ordenes_compra_schema.sql')
        print(f"📄 Leyendo schema: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Ejecutar el script SQL
        print("⚙️ Ejecutando script SQL...")
        cursor.execute(sql_script)
        conn.commit()
        
        print("✅ Schema de Órdenes de Compra creado exitosamente!")
        
        # Verificar tablas creadas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('ordenes_compra', 'ordenes_compra_detalle', 'unidades_negocio', 'centros_costo', 'consecutivos_ordenes_compra')
            ORDER BY table_name
        """)
        
        tablas = cursor.fetchall()
        print(f"\n📋 Tablas creadas ({len(tablas)}):")
        for tabla in tablas:
            print(f"   ✓ {tabla[0]}")
        
        # Verificar consecutivo inicial
        cursor.execute("SELECT prefijo, ultimo_numero FROM consecutivos_ordenes_compra WHERE prefijo = 'OCR'")
        consecutivo = cursor.fetchone()
        if consecutivo:
            print(f"\n🔢 Consecutivo inicial: {consecutivo[0]}-{consecutivo[1]:09d}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("CREACIÓN DE TABLAS DE ÓRDENES DE COMPRA")
    print("=" * 60)
    print()
    
    exitoso = ejecutar_schema()
    
    if exitoso:
        print("\n✅ Proceso completado exitosamente!")
        print("🚀 Ahora puedes usar el módulo de Órdenes de Compra")
    else:
        print("\n❌ Hubo errores durante la ejecución")
    
    input("\nPresiona Enter para salir...")
