"""
VERIFICACIÓN POST-PROCESAMIENTO
================================
Ejecutar DESPUÉS de que termine el procesamiento
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/gestor_documental')
engine = create_engine(DATABASE_URL)

print("=" * 80)
print("VERIFICACIÓN DE RESULTADOS POST-PROCESAMIENTO")
print("=" * 80)

with engine.connect() as conn:
    # 1. Total de registros
    print(f"\n📊 REGISTROS PROCESADOS:")
    result = conn.execute(text("""
        SELECT 
            'DIAN' as tabla,
            COUNT(*) as registros
        FROM dian
        UNION ALL
        SELECT 'ERP Financiero', COUNT(*) FROM erp_financiero
        UNION ALL
        SELECT 'ERP Comercial', COUNT(*) FROM erp_comercial
        UNION ALL
        SELECT 'Acuses', COUNT(*) FROM acuses
        UNION ALL
        SELECT 'Maestro', COUNT(*) FROM maestro_dian_vs_erp
    """))
    
    for row in result:
        tabla, registros = row
        print(f"   {tabla:20s} {registros:>10,} registros")
    
    # 2. CUFEs en maestro
    print(f"\n✅ VERIFICACIÓN DE CUFEs EN MAESTRO:")
    result = conn.execute(text("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE cufe IS NOT NULL AND cufe != '') as con_cufe,
            COUNT(*) FILTER (WHERE cufe IS NULL OR cufe = '') as sin_cufe
        FROM maestro_dian_vs_erp
    """))
    
    row = result.fetchone()
    total, con_cufe, sin_cufe = row
    porcentaje_cufe = (con_cufe / total * 100) if total > 0 else 0
    
    print(f"   Total registros: {total:,}")
    print(f"   Con CUFE: {con_cufe:,} ({porcentaje_cufe:.1f}%)")
    print(f"   Sin CUFE: {sin_cufe:,}")
    
    if con_cufe == 0:
        print(f"\n   ❌ PROBLEMA: No hay CUFEs en maestro")
    elif con_cufe == total:
        print(f"\n   ✅ PERFECTO: Todos los registros tienen CUFE")
    else:
        print(f"\n   ⚠️  PARCIAL: {con_cufe:,} de {total:,} tienen CUFE")
    
    # 3. Distribución de estados de aprobación
    print(f"\n📊 DISTRIBUCIÓN DE ESTADOS DE APROBACIÓN:")
    result = conn.execute(text("""
        SELECT 
            COALESCE(estado_aprobacion, 'NULL') as estado,
            COUNT(*) as cantidad,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as porcentaje
        FROM maestro_dian_vs_erp
        GROUP BY estado_aprobacion
        ORDER BY cantidad DESC
    """))
    
    estados_validos = 0
    no_registra = 0
    
    for row in result:
        estado, cantidad, porcentaje = row
        if estado == 'No Registra':
            no_registra = cantidad
            print(f"   ⚠️  {estado:30s} {cantidad:>10,} ({porcentaje:>5}%)")
        else:
            estados_validos += cantidad
            print(f"   ✅ {estado:30s} {cantidad:>10,} ({porcentaje:>5}%)")
    
    # 4. Resumen de éxito
    print(f"\n📈 RESUMEN DE ÉXITO:")
    if estados_validos > 0:
        exito_rate = (estados_validos / (estados_validos + no_registra) * 100)
        print(f"   Registros con estado válido: {estados_validos:,}")
        print(f"   Registros sin acuse: {no_registra:,}")
        print(f"   Tasa de éxito: {exito_rate:.1f}%")
        
        if exito_rate > 80:
            print(f"\n   ✅ EXCELENTE: {exito_rate:.1f}% de los registros tienen acuse")
        elif exito_rate > 50:
            print(f"\n   ⚠️  BUENO: {exito_rate:.1f}% de los registros tienen acuse")
        else:
            print(f"\n   ❌ PROBLEMA: Solo {exito_rate:.1f}% tienen acuse")
    else:
        print(f"\n   ❌ PROBLEMA: NO hay registros con estado válido")
    
    # 5. Verificar matches entre maestro y acuses
    print(f"\n🔍 VERIFICANDO MATCHES CON ACUSES:")
    result = conn.execute(text("""
        SELECT COUNT(*) as matches
        FROM maestro_dian_vs_erp m
        INNER JOIN acuses a ON m.cufe = a.cufe
        WHERE m.cufe IS NOT NULL
    """))
    
    matches = result.fetchone()[0]
    print(f"   Matches encontrados: {matches:,}")
    
    if matches == 0:
        print(f"\n   ❌ NO hay matches entre maestro y acuses")
        print(f"   Posibles causas:")
        print(f"      1. Los CUFEs no coinciden (formato diferente)")
        print(f"      2. Los archivos son de períodos diferentes")
    elif matches > 50000:
        print(f"\n   ✅ PERFECTO: {matches:,} facturas con acuse")
    else:
        print(f"\n   ⚠️  PARCIAL: {matches:,} facturas con acuse")
    
    # 6. Ejemplos de registros exitosos
    print(f"\n📝 EJEMPLOS DE REGISTROS CON ACUSE:")
    result = conn.execute(text("""
        SELECT 
            nit_emisor,
            razon_social,
            prefijo,
            folio,
            SUBSTRING(cufe, 1, 30) as cufe_inicio,
            estado_aprobacion,
            acuses_recibidos
        FROM maestro_dian_vs_erp
        WHERE estado_aprobacion != 'No Registra'
        AND cufe IS NOT NULL
        LIMIT 5
    """))
    
    tiene_ejemplos = False
    for i, row in enumerate(result, 1):
        tiene_ejemplos = True
        nit, razon, prefijo, folio, cufe, estado, acuses_num = row
        print(f"\n   {i}. {razon[:40]}")
        print(f"      NIT: {nit} | Factura: {prefijo}-{folio}")
        print(f"      CUFE: {cufe}...")
        print(f"      Estado: {estado}")
    
    if not tiene_ejemplos:
        print(f"   ❌ NO hay ejemplos (todos son 'No Registra')")
    
    # 7. Verificar si necesita restaurar causación
    print(f"\n💾 VERIFICAR BACKUP DE CAUSACIÓN:")
    try:
        result = conn.execute(text("SELECT COUNT(*) FROM backup_causacion_temp"))
        backup_count = result.fetchone()[0]
        
        if backup_count > 0:
            print(f"   ⚠️  Hay {backup_count:,} registros en backup")
            print(f"   ⚠️  DEBES ejecutar el script de restauración:")
            print(f"\n   UPDATE maestro_dian_vs_erp m")
            print(f"   SET causada = b.causada, ...")
            print(f"   FROM backup_causacion_temp b")
            print(f"   WHERE m.nit_emisor = b.nit_emisor...")
        else:
            print(f"   ✅ No hay datos de causación para restaurar")
    except:
        print(f"   ℹ️  No hay tabla de backup (normal)")

print(f"\n" + "=" * 80)
print("CONCLUSIÓN:")
print("=" * 80)

if con_cufe > 0 and estados_validos > 0:
    print(f"""
✅ PROCESAMIENTO EXITOSO

• {con_cufe:,} registros con CUFE
• {estados_validos:,} registros con estado de acuse válido
• {matches:,} matches con tabla acuses

TODO FUNCIONÓ CORRECTAMENTE ✅
Los estados de aprobación deberían verse en el Visor V2.
""")
elif con_cufe > 0 and estados_validos == 0:
    print(f"""
⚠️ CUFEs SÍ se cargaron pero NO hay estados

• Registros con CUFE: {con_cufe:,} ✅
• Registros con estado válido: 0 ❌

PROBLEMA: Los CUFEs se guardaron pero no hicieron match con acuses.
Verifica que los archivos DIAN y ACUSES sean del mismo período.
""")
else:
    print(f"""
❌ PROBLEMA EN EL PROCESAMIENTO

• Registros con CUFE: {con_cufe:,}
• Registros con estado válido: {estados_validos:,}

El procesamiento no funcionó como esperado.
Revisa los logs de la consola donde corre Flask.
""")

print("=" * 80)
