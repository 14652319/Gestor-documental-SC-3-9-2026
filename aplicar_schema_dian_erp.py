"""
Script para aplicar el esquema de tablas DIAN VS ERP a PostgreSQL

Fecha: 30 de Diciembre de 2025
"""

import os
import sys
import psycopg2

# Configuración de base de datos
# postgresql://postgres:G3st0radm$2025.@localhost:5432/gestor_documental
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'gestor_documental',
    'user': 'postgres',
    'password': 'G3st0radm$2025.'
}

def aplicar_esquema():
    """Aplica el esquema SQL a la base de datos"""
    print("="*80)
    print("APLICANDO ESQUEMA DIAN VS ERP A POSTGRESQL")
    print("="*80)
    
    # Verificar que existe el archivo SQL
    archivo_sql = os.path.join('sql', 'schema_dian_vs_erp.sql')
    if not os.path.exists(archivo_sql):
        print(f"❌ Error: No se encuentra el archivo {archivo_sql}")
        sys.exit(1)
    
    print(f"\n📄 Archivo SQL: {archivo_sql}")
    
    try:
        # Conectar a PostgreSQL
        print("\n🔌 Conectando a PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        print("✅ Conexión exitosa")
        
        # Leer y ejecutar el archivo SQL
        print("\n📋 Leyendo archivo SQL...")
        with open(archivo_sql, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print("⚙️  Ejecutando script SQL...")
        cursor.execute(sql_script)
        
        print("\n✅ Esquema aplicado exitosamente!")
        
        # Verificar que las tablas se crearon
        print("\n📊 Verificando tablas creadas...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('dian', 'erp_comercial', 'erp_financiero', 'acuses')
            ORDER BY table_name
        """)
        
        tablas = cursor.fetchall()
        if tablas:
            print("✅ Tablas creadas correctamente:")
            for tabla in tablas:
                print(f"   - {tabla[0]}")
        else:
            print("⚠️  No se encontraron las tablas esperadas")
        
        # Verificar triggers
        print("\n🔧 Verificando triggers...")
        cursor.execute("""
            SELECT trigger_name, event_object_table
            FROM information_schema.triggers
            WHERE event_object_table IN ('dian', 'erp_comercial', 'erp_financiero', 'acuses')
            ORDER BY event_object_table, trigger_name
        """)
        
        triggers = cursor.fetchall()
        if triggers:
            print("✅ Triggers creados correctamente:")
            for trigger in triggers:
                print(f"   - {trigger[0]} en tabla {trigger[1]}")
        
        # Verificar vistas
        print("\n👁️  Verificando vistas...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'v_%'
            ORDER BY table_name
        """)
        
        vistas = cursor.fetchall()
        if vistas:
            print("✅ Vistas creadas correctamente:")
            for vista in vistas:
                print(f"   - {vista[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*80)
        print("✅ ESQUEMA APLICADO EXITOSAMENTE")
        print("="*80)
        print("\nAhora puedes ejecutar: python cargar_archivos_dian_erp.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error al aplicar esquema: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = aplicar_esquema()
    sys.exit(0 if success else 1)
