"""
VERIFICAR_Y_LIMPIAR_MAESTRO.py
===============================
Verifica registros y limpia la tabla maestro_dian_vs_erp usando SQL directo
"""

import psycopg2
from datetime import datetime

print("="*80)
print("🔍 VERIFICAR Y LIMPIAR maestro_dian_vs_erp")
print("="*80)
print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'gestor_documental',
    'user': 'postgres',
    'password': 'Vimer2024*'
}

try:
    # Conectar a PostgreSQL
    print("\n🔌 Conectando a PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("✅ Conectado exitosamente")
    
    # PASO 1: Verificar registros actuales
    print("\n" + "="*80)
    print("📊 PASO 1: VERIFICAR REGISTROS ACTUALES")
    print("="*80)
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp;")
    count_total = cursor.fetchone()[0]
    print(f"Total registros: {count_total:,}")
    
    if count_total > 0:
        # Mostrar distribución de fechas
        cursor.execute("""
            SELECT fecha_emision, COUNT(*) as cantidad
            FROM maestro_dian_vs_erp
            GROUP BY fecha_emision
            ORDER BY cantidad DESC
            LIMIT 10;
        """)
        
        print(f"\n📅 Distribución de fechas (top 10):")
        for fecha, cantidad in cursor.fetchall():
            print(f"   {fecha}: {cantidad:,} registros")
    
    if count_total == 0:
        print("\n✅ La tabla ya está vacía, lista para cargar datos nuevos")
        conn.close()
        exit(0)
    
    # PASO 2: Solicitar confirmación para eliminar
    print("\n" + "="*80)
    print("⚠️  CONFIRMAR ELIMINACIÓN")
    print("="*80)
    print(f"Se eliminarán {count_total:,} registros de maestro_dian_vs_erp")
    print("\n¿Deseas continuar? (escribe 'si' para confirmar)")
    
    respuesta = input("→ ").strip().lower()
    
    if respuesta != 'si':
        print("❌ Operación cancelada por el usuario")
        conn.close()
        exit(0)
    
    # PASO 3: Eliminar todos los registros
    print("\n" + "="*80)
    print("🗑️  PASO 2: ELIMINANDO REGISTROS")
    print("="*80)
    
    print(f"Ejecutando: DELETE FROM maestro_dian_vs_erp...")
    cursor.execute("DELETE FROM maestro_dian_vs_erp;")
    conn.commit()
    print("✅ DELETE ejecutado")
    
    # PASO 4: Verificar eliminación
    print("\n" + "="*80)
    print("📊 PASO 3: VERIFICAR ELIMINACIÓN")
    print("="*80)
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp;")
    count_final = cursor.fetchone()[0]
    
    print(f"Registros antes: {count_total:,}")
    print(f"Registros después: {count_final:,}")
    print(f"Registros eliminados: {count_total - count_final:,}")
    
    if count_final == 0:
        print("\n" + "="*80)
        print("✅ ¡TABLA LIMPIADA EXITOSAMENTE!")
        print("="*80)
        print("\nAhora puedes ejecutar:")
        print("   python CARGAR_TODOS_LOS_CSVS.py")
        print("="*80)
    else:
        print(f"\n⚠️  ADVERTENCIA: Quedaron {count_final:,} registros")
    
    # Cerrar conexión
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
