"""
LIMPIEZA COMPLETA Y VERIFICADA DE TABLAS
Febrero 23, 2026
"""
import psycopg2

print("=" * 80)
print("LIMPIEZA COMPLETA DE TABLA maestro_dian_vs_erp")
print("=" * 80)

# Conectar
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="gestor_documental",
        user="postgres",
        password="G3st0radm$2025."
    )
    cursor = conn.cursor()
    print("✅ Conexión exitosa\n")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit(1)

try:
    # 1. Verificar cuántos registros hay ANTES de borrar
    print("🔍 Verificando tabla ANTES de limpiar...")
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
    total_antes = cursor.fetchone()[0]
    print(f"   Registros actuales: {total_antes:,}")
    
    if total_antes == 0:
        print("\n✅ Tabla ya está vacía - Lista para cargar\n")
    else:
        print(f"\n⚠️  Tabla tiene {total_antes:,} registros - ELIMINANDO...\n")
        
        # 2. BORRAR TODO
        cursor.execute("DELETE FROM maestro_dian_vs_erp")
        conn.commit()
        print(f"✅ {total_antes:,} registros eliminados")
        
        # 3. VERIFICAR que quedó en 0
        cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
        total_despues = cursor.fetchone()[0]
        
        if total_despues == 0:
            print(f"✅ Verificación: Tabla vacía (0 registros)")
        else:
            print(f"❌ ERROR: Aún hay {total_despues:,} registros")
            print("   Intentando con TRUNCATE...")
            cursor.execute("TRUNCATE TABLE maestro_dian_vs_erp CASCADE")
            conn.commit()
            
            cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
            total_final = cursor.fetchone()[0]
            
            if total_final == 0:
                print("✅ TRUNCATE exitoso - Tabla vacía")
            else:
                print(f"❌ CRÍTICO: No se pudo limpiar la tabla")
                exit(1)
    
    # 4. VERIFICAR CONSTRAINTS (por si hay problema con el UNIQUE)
    print("\n🔍 Verificando constraints UNIQUE...")
    cursor.execute("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints
        WHERE table_name = 'maestro_dian_vs_erp'
        AND constraint_type = 'UNIQUE'
    """)
    
    constraints = cursor.fetchall()
    if constraints:
        print(f"   Constraints UNIQUE encontrados: {len(constraints)}")
        for constraint in constraints:
            print(f"      • {constraint[0]}")
    else:
        print("   ⚠️  No hay constraints UNIQUE (puede causar duplicados)")
    
    print("\n" + "=" * 80)
    print("✅✅✅ TABLA LISTA PARA CARGAR ✅✅✅")
    print("=" * 80)
    print("\nAhora puedes cargar los archivos por navegador:")
    print("http://localhost:8099/dian_vs_erp/")
    print("\n" + "=" * 80)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    conn.rollback()
    exit(1)

finally:
    cursor.close()
    conn.close()
