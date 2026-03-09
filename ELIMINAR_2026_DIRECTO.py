"""
Script DIRECTO: Eliminar datos 2026 usando PostgreSQL directamente
"""
import psycopg2
from datetime import date

print("=" * 80)
print("🗑️  ELIMINANDO DATOS DE 2026 - Método Directo PostgreSQL")
print("=" * 80)
print()

# Conexión a PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="gestor_documental",
    user="gestor_user",
    password="GestDoc2024"
)

try:
    cursor = conn.cursor()
    
    # 1. Contar registros
    print("📊 Consultando registros de 2026...")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM maestro_dian_vs_erp 
        WHERE fecha_emision >= '2026-01-01'
    """)
    total = cursor.fetchone()[0]
    print(f"   Encontrados: {total:,} registros")
    print()
    
    if total == 0:
        print("✅ No hay registros de 2026 para elimimar")
    else:
        # 2. Eliminar
        print(f"🗑️  Eliminando {total:,} registros...")
        cursor.execute("""
            DELETE FROM maestro_dian_vs_erp 
            WHERE fecha_emision >= '2026-01-01'
        """)
        conn.commit()
        print(f"✅ Eliminados exitosamente")
        print()
        
        # 3. Verificar
        cursor.execute("""
            SELECT COUNT(*) 
            FROM maestro_dian_vs_erp 
            WHERE fecha_emision >= '2026-01-01'
        """)
        restantes = cursor.fetchone()[0]
        print(f"✅ Registros restantes de 2026: {restantes:,}")
        print()
        
        print("✅" * 40)
        print("✅✅✅ ELIMINACIÓN COMPLETADA ✅✅✅")
        print("✅" * 40)
        print()
        
        print("📋 AHORA SIGUE ESTOS PASOS:")
        print()
        print("   1️⃣  Abre tu navegador (Chrome, Edge, Firefox)")
        print()
        print("   2️⃣  Ve a esta URL:")
        print("       http://127.0.0.1:8099/dian_vs_erp/cargar_archivos")
        print()
        print("   3️⃣  Arrastra el archivo:")
        print("       C:\\Users\\Usuario\\Downloads\\Ricardo\\Dian.xlsx")
        print()
        print("   4️⃣  Haz clic en 'Subir Archivos'")
        print()
        print("   5️⃣  Espera 8-10 segundos (65,000+ registros)")
        print()
        print("   6️⃣  Verifica en el visor:")
        print("       http://127.0.0.1:8099/dian_vs_erp/visor_v2")
        print()
        print("   ✅ AHORA las fechas se cargarán correctamente")
        print("      (el código YA tiene el fix para 'fecha emisiã³n')")
        print()
        
    cursor.close()
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
    
finally:
    conn.close()

print("=" * 80)
