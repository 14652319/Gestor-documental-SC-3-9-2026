"""
LIMPIAR TODAS LAS TABLAS PARA RECARGA COMPLETA
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
    print("🗑️ LIMPIANDO TABLAS PARA RECARGA")
    print("="*80)
    
    # Ver totales actuales
    print("\n📊 ANTES DE LIMPIAR:")
    cursor.execute("SELECT COUNT(*) FROM dian")
    print(f"   DIAN: {cursor.fetchone()[0]:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM erp_financiero")
    print(f"   ERP Financiero: {cursor.fetchone()[0]:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM erp_comercial")
    print(f"   ERP Comercial: {cursor.fetchone()[0]:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM acuses")
    print(f"   Acuses: {cursor.fetchone()[0]:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
    print(f"   Maestro: {cursor.fetchone()[0]:,} registros")
    
    # CONFIRMAR
    print("\n⚠️  ¿ESTÁS SEGURO? Esta operación NO se puede deshacer.")
    confirmacion = input("   Escribe 'SI' para continuar: ")
    
    if confirmacion.upper() != 'SI':
        print("\n❌ Operación cancelada")
        cursor.close()
        conn.close()
        exit()
    
    # TRUNCAR TABLAS
    print("\n🗑️ Limpiando tablas...")
    
    cursor.execute("TRUNCATE TABLE maestro_dian_vs_erp CASCADE")
    print("   ✅ maestro_dian_vs_erp limpiado")
    
    cursor.execute("TRUNCATE TABLE dian CASCADE")
    print("   ✅ dian limpiado")
    
    cursor.execute("TRUNCATE TABLE erp_financiero CASCADE")
    print("   ✅ erp_financiero limpiado")
    
    cursor.execute("TRUNCATE TABLE erp_comercial CASCADE")
    print("   ✅ erp_comercial limpiado")
    
    cursor.execute("TRUNCATE TABLE acuses CASCADE")
    print("   ✅ acuses limpiado")
    
    conn.commit()
    
    # Verificar
    print("\n📊 DESPUÉS DE LIMPIAR:")
    cursor.execute("SELECT COUNT(*) FROM dian")
    print(f"   DIAN: {cursor.fetchone()[0]:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM erp_financiero")
    print(f"   ERP Financiero: {cursor.fetchone()[0]:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM erp_comercial")
    print(f"   ERP Comercial: {cursor.fetchone()[0]:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM acuses")
    print(f"   Acuses: {cursor.fetchone()[0]:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
    print(f"   Maestro: {cursor.fetchone()[0]:,} registros")
    
    print("\n" + "="*80)
    print("✅ TABLAS LIMPIAS - LISTO PARA RECARGAR")
    print("="*80)
    print("""
    PRÓXIMOS PASOS:
    1. Ir al visor: http://localhost:8099/dian_vs_erp/visor_v2
    2. Cargar los 4 archivos Excel:
       - Dian.xlsx
       - ERP_financiero.xlsx
       - ERP_comercial.xlsx
       - Acuses.xlsx
    3. El sistema:
       ✅ Usará la función correcta crear_clave_factura()
       ✅ Aplicará regla de últimos 8 dígitos del folio
       ✅ Generará maestro con estados contables correctos
    """)
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ ERROR: {str(e)}")
    raise

finally:
    cursor.close()
    conn.close()
