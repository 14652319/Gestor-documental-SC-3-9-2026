"""
LIMPIAR TODAS LAS TABLAS DIAN VS ERP
=====================================
Script directo para truncar todas las tablas y recargar desde cero
"""
import psycopg2

conn = psycopg2.connect(
    dbname='gestor_documental',
    user='postgres',
    password='G3st0radm$2025.',
    host='localhost'
)
conn.autocommit = False
cursor = conn.cursor()

try:
    print("\n" + "="*80)
    print("🗑️  LIMPIANDO TODAS LAS TABLAS DIAN VS ERP")
    print("="*80 + "\n")
    
    # Ver totales actuales
    print("📊 ANTES DE LIMPIAR:")
    cursor.execute("SELECT COUNT(*) FROM dian")
    dian_antes = cursor.fetchone()[0]
    print(f"   DIAN:            {dian_antes:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM erp_financiero")
    fn_antes = cursor.fetchone()[0]
    print(f"   ERP Financiero:  {fn_antes:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM erp_comercial")
    cm_antes = cursor.fetchone()[0]
    print(f"   ERP Comercial:   {cm_antes:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM acuses")
    acuses_antes = cursor.fetchone()[0]
    print(f"   Acuses:          {acuses_antes:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
    maestro_antes = cursor.fetchone()[0]
    print(f"   Maestro:         {maestro_antes:,} registros")
    
    print(f"\n   📍 TOTAL A ELIMINAR: {dian_antes + fn_antes + cm_antes + acuses_antes + maestro_antes:,} registros")
    
    # TRUNCAR TABLAS
    print("\n🗑️  Ejecutando TRUNCATE CASCADE...\n")
    
    cursor.execute("TRUNCATE TABLE maestro_dian_vs_erp CASCADE")
    print("   ✅ maestro_dian_vs_erp")
    
    cursor.execute("TRUNCATE TABLE dian CASCADE")
    print("   ✅ dian")
    
    cursor.execute("TRUNCATE TABLE erp_financiero CASCADE")
    print("   ✅ erp_financiero")
    
    cursor.execute("TRUNCATE TABLE erp_comercial CASCADE")
    print("   ✅ erp_comercial")
    
    cursor.execute("TRUNCATE TABLE acuses CASCADE")
    print("   ✅ acuses")
    
    conn.commit()
    
    # Verificar
    print("\n📊 DESPUÉS DE LIMPIAR:")
    cursor.execute("SELECT COUNT(*) FROM dian")
    print(f"   DIAN:            {cursor.fetchone()[0]:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM erp_financiero")
    print(f"   ERP Financiero:  {cursor.fetchone()[0]:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM erp_comercial")
    print(f"   ERP Comercial:   {cursor.fetchone()[0]:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM acuses")
    print(f"   Acuses:          {cursor.fetchone()[0]:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
    print(f"   Maestro:         {cursor.fetchone()[0]:,} registros")
    
    print("\n" + "="*80)
    print("✅ TABLAS LIMPIADAS EXITOSAMENTE")
    print("="*80 + "\n")
    
    print("📋 PRÓXIMOS PASOS:")
    print("   1. Ve al visor: http://localhost:8099/dian_vs_erp/visor_v2")
    print("   2. Carga los 4 archivos Excel EN ORDEN:")
    print("      • Dian.xlsx")
    print("      • ERP_financiero.xlsx")
    print("      • ERP_comercial.xlsx")
    print("      • Acuses.xlsx")
    print("")
    print("   3. El sistema generará:")
    print("      ✅ Claves correctas (NIT + PREFIJO + últimos 8 del FOLIO)")
    print("      ✅ Maestro con Estados Contables")
    print("      ✅ Matches DIAN ↔ ERP")
    print("\n" + "="*80 + "\n")
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    raise

finally:
    cursor.close()
    conn.close()

print("✅ Script completado\n")
