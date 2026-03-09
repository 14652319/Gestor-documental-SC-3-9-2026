"""
VERIFICAR_CONSOLIDACION.py
===========================
Verificación rápida del estado de maestro_dian_vs_erp después de consolidar
"""

import psycopg2
from datetime import datetime

print("="*80)
print("🔍 VERIFICACIÓN RÁPIDA - MAESTRO DIAN VS ERP")
print("="*80)
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
print()

try:
    # Conectar con parámetros separados para evitar problemas de encoding
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="gestor_documental",
        user="postgres",
        password="Vimer2024*"
    )
    cursor = conn.cursor()
    
    # Conteo total
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
    total = cursor.fetchone()[0]
    print(f"📊 TOTAL maestro_dian_vs_erp: {total:,} registros")
    print()
    
    if total == 0:
        print("❌ La tabla maestro está VACÍA")
        print("   ⚠️  La consolidación no se ejecutó o falló")
        conn.close()
        exit(1)
    
    # Verificar campos críticos
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE ver_pdf IS NOT NULL AND ver_pdf != ''")
    con_pdf = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE estado_aprobacion IS NOT NULL AND estado_aprobacion != ''")
    con_estado = cursor.fetchone()[0]
    
    print("✅ VERIFICACIÓN DE CAMPOS:")
    print(f"   ver_pdf poblado:         {con_pdf:>10,} / {total:,} ({con_pdf/total*100:.1f}%)")
    print(f"   estado_aprobacion poblado: {con_estado:>10,} / {total:,} ({con_estado/total*100:.1f}%)")
    print()
    
    # Verificar fuentes de datos
    cursor.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE tipo_fuente = 'ERP_COMERCIAL') as erp_cm,
            COUNT(*) FILTER (WHERE tipo_fuente = 'ERP_FINANCIERO') as erp_fn,
            COUNT(*) FILTER (WHERE tipo_fuente = 'DIAN') as dian_solo,
            COUNT(*) FILTER (WHERE tipo_fuente IS NULL OR tipo_fuente = '') as sin_fuente
        FROM maestro_dian_vs_erp
    """)
    fuentes = cursor.fetchone()
    
    print("📊 DISTRIBUCIÓN POR FUENTE:")
    print(f"   ERP_COMERCIAL:  {fuentes[0]:>10,}")
    print(f"   ERP_FINANCIERO: {fuentes[1]:>10,}")
    print(f"   DIAN solo:      {fuentes[2]:>10,}")
    print(f"   Sin fuente:     {fuentes[3]:>10,}")
    print()
    
    # Verificar estados de aprobación
    cursor.execute("""
        SELECT estado_aprobacion, COUNT(*) 
        FROM maestro_dian_vs_erp 
        WHERE estado_aprobacion IS NOT NULL
        GROUP BY estado_aprobacion 
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """)
    estados = cursor.fetchall()
    
    if estados:
        print("📋 DISTRIBUCIÓN DE ESTADOS:")
        for estado, count in estados:
            print(f"   {estado[:40]:40} {count:>10,}")
        print()
    
    # Verificar acuses
    cursor.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE acuses_recibidos > 0) as con_acuses,
            SUM(acuses_recibidos) as total_acuses
        FROM maestro_dian_vs_erp
    """)
    acuses = cursor.fetchone()
    
    print("📮 ACUSES RECIBIDOS:")
    print(f"   Facturas con acuses: {acuses[0]:>10,}")
    print(f"   Total acuses:        {acuses[1]:>10,}")
    print()
    
    # Validación final
    print("="*80)
    print("✅ RESULTADO:")
    print("="*80)
    
    exito = True
    
    if total < 100000:
        print(f"   ⚠️  ADVERTENCIA: Solo {total:,} registros (esperado ~170,000)")
        exito = False
    else:
        print(f"   ✅ Cantidad de registros adecuada: {total:,}")
    
    if con_pdf == 0:
        print(f"   ❌ Campo ver_pdf VACÍO - Falta generación de enlaces PDF")
        exito = False
    else:
        print(f"   ✅ Campo ver_pdf poblado: {con_pdf:,} registros")
    
    if con_estado == 0:
        print(f"   ❌ Campo estado_aprobacion VACÍO")
        exito = False
    else:
        print(f"   ✅ Campo estado_aprobacion poblado: {con_estado:,} registros")
    
    if fuentes[1] == 0:  # ERP_FINANCIERO
        print(f"   ❌ ERP_FINANCIERO no consolidado (0 registros)")
        exito = False
    else:
        print(f"   ✅ ERP_FINANCIERO consolidado: {fuentes[1]:,} registros")
    
    print()
    
    if exito:
        print("🎉 CONSOLIDACIÓN EXITOSA")
        print("   Todos los campos críticos están poblados correctamente")
    else:
        print("⚠️  CONSOLIDACIÓN INCOMPLETA")
        print("   Revisar logs y ejecutar nuevamente si es necesario")
    
    print()
    print("="*80)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
