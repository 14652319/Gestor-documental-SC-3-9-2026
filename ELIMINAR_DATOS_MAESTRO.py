"""
Script para eliminar todos los datos de maestro_dian_vs_erp
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de PostgreSQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'gestor_documental'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

print("=" * 80)
print("🗑️  ELIMINAR DATOS DE maestro_dian_vs_erp")
print("=" * 80)

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Contar registros antes
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
    count_antes = cursor.fetchone()[0]
    print(f"\n📊 Registros actuales: {count_antes:,}")
    
    if count_antes == 0:
        print("✅ La tabla ya está vacía")
    else:
        # Confirmar
        respuesta = input(f"\n⚠️  ¿Confirmas eliminar {count_antes:,} registros? (si/no): ")
        
        if respuesta.lower() in ['si', 'sí', 's', 'yes', 'y']:
            print("\n🔄 Eliminando registros...")
            cursor.execute("DELETE FROM maestro_dian_vs_erp")
            conn.commit()
            
            # Verificar
            cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
            count_despues = cursor.fetchone()[0]
            
            print(f"✅ Eliminados: {count_antes:,} registros")
            print(f"📊 Registros actuales: {count_despues:,}")
        else:
            print("❌ Operación cancelada")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
