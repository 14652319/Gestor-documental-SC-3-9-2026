"""
VERIFICAR_ESTADO_RAPIDO.py
==========================
Verificación rápida del estado actual
"""

import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="gestor_documental",
        user="postgres",
        password="G3st0radm$2025."
    )
    cursor = conn.cursor()
    
    print("="*80)
    print("🔍 ESTADO ACTUAL DE LAS TABLAS")
    print("="*80)
    print()
    
    # Conteos
    cursor.execute("SELECT COUNT(*) FROM dian")
    count_dian = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM erp_comercial")
    count_erp_cm = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM erp_financiero")
    count_erp_fn = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM acuses")
    count_acuses = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
    count_maestro = cursor.fetchone()[0]
    
    print("📊 TABLAS INDIVIDUALES:")
    print(f"   dian:             {count_dian:>10,}")
    print(f"   erp_comercial:    {count_erp_cm:>10,}")
    print(f"   erp_financiero:   {count_erp_fn:>10,}")
    print(f"   acuses:           {count_acuses:>10,}")
    print()
    print(f"📊 TABLA MAESTRO:")
    print(f"   maestro_dian_vs_erp: {count_maestro:>10,}")
    print()
    
    if count_maestro == 0:
        print("❌ MAESTRO VACÍO - El proceso NO ha terminado o falló")
        print("   → Espera a que el script termine")
        print()
    elif count_maestro > 100000:
        print("✅ CONSOLIDACIÓN COMPLETADA EXITOSAMENTE")
        print()
        
        # Verificar campos críticos
        cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE ver_pdf IS NOT NULL")
        count_pdf = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE estado_aprobacion IS NOT NULL")
        count_estado = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE tipo_fuente = 'ERP_FINANCIERO') as erp_fn,
                COUNT(*) FILTER (WHERE tipo_fuente = 'ERP_COMERCIAL') as erp_cm
            FROM maestro_dian_vs_erp
        """)
        fuentes = cursor.fetchone()
        
        print("   📋 VERIFICACIÓN:")
        print(f"      ver_pdf:            {count_pdf:>10,} ({'✅' if count_pdf > 0 else '❌'})")
        print(f"      estado_aprobacion:  {count_estado:>10,} ({'✅' if count_estado > 0 else '❌'})")
        print(f"      ERP_FINANCIERO:     {fuentes[0]:>10,} ({'✅' if fuentes[0] > 0 else '❌'})")
        print(f"      ERP_COMERCIAL:      {fuentes[1]:>10,} ({'✅' if fuentes[1] > 0 else '❌'})")
        print()
        print("🌐 ABRIR EN NAVEGADOR:")
        print("   http://localhost:8099/dian_vs_erp/visor_v2")
        print()
    else:
        print("⚠️  Maestro tiene datos pero pocos registros")
        print("   → Puede estar procesando aún")
        print()
    
    cursor.close()
    conn.close()
    
    print("="*80)
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

