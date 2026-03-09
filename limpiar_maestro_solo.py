"""
Limpiar SOLO la tabla maestro_dian_vs_erp
Los archivos en uploads/ NO se tocan
"""
import psycopg2
from sqlalchemy import create_engine, text
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("🧹 LIMPIANDO TABLA MAESTRO")
print("=" * 80)

# Conexión
DATABASE_URL = "postgresql://gestor_user:G3st0r2024!@localhost:5432/gestor_documental"
engine = create_engine(DATABASE_URL)

try:
    with engine.begin() as conn:
        # Contar registros antes
        result = conn.execute(text("SELECT COUNT(*) FROM maestro_dian_vs_erp"))
        count_antes = result.scalar()
        print(f"\n📊 Registros en maestro ANTES: {count_antes:,}")
        
        # ELIMINAR todos los registros de maestro
        print(f"\n🗑️  Eliminando registros de maestro_dian_vs_erp...")
        conn.execute(text("DELETE FROM maestro_dian_vs_erp"))
        
        # Verificar que quedó vacío
        result = conn.execute(text("SELECT COUNT(*) FROM maestro_dian_vs_erp"))
        count_despues = result.scalar()
        print(f"✅ Registros en maestro DESPUÉS: {count_despues:,}")
        
        # Verificar que los archivos siguen ahí (DIAN, ERP, ACUSES)
        print(f"\n📋 Verificando otras tablas (NO se tocan):")
        
        result = conn.execute(text("SELECT COUNT(*) FROM dian"))
        count_dian = result.scalar()
        print(f"   ✅ DIAN: {count_dian:,} registros")
        
        result = conn.execute(text("SELECT COUNT(*) FROM erp_financiero"))
        count_fn = result.scalar()
        print(f"   ✅ ERP Financiero: {count_fn:,} registros")
        
        result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial"))
        count_cm = result.scalar()
        print(f"   ✅ ERP Comercial: {count_cm:,} registros")
        
        result = conn.execute(text("SELECT COUNT(*) FROM acuses"))
        count_acuses = result.scalar()
        print(f"   ✅ Acuses: {count_acuses:,} registros")
        
    print(f"\n" + "=" * 80)
    print("✅ MAESTRO LIMPIADO CORRECTAMENTE")
    print("=" * 80)
    print(f"\n🚀 SIGUIENTE PASO:")
    print(f"   1. Ve a la interfaz web (puerto 8099)")
    print(f"   2. Click en 'Procesar & Consolidar'")
    print(f"   3. El código corregido leerá CUFE correctamente")
    print(f"   4. Verifica 'Ver PDF' y 'Estado Aprobación' en Visor V2")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    print(traceback.format_exc())
