"""
VERIFICACIÓN RÁPIDA: ¿Por qué "No Registra" en maestro?
========================================================
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/gestor_documental')
engine = create_engine(DATABASE_URL)

print("=" * 80)
print("DIAGNÓSTICO RÁPIDO: ESTADO_APROBACION EN MAESTRO")
print("=" * 80)

with engine.connect() as conn:
    # 1. Total en maestro
    print(f"\n📊 TABLA MAESTRO_DIAN_VS_ERP:")
    result = conn.execute(text("SELECT COUNT(*) FROM maestro_dian_vs_erp"))
    total = result.fetchone()[0]
    print(f"   Total registros: {total:,}")
    
    # 2. Distribución de estados
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
    
    for row in result:
        estado, cantidad, porcentaje = row
        print(f"   {estado:30s} {cantidad:>10,} ({porcentaje:>5}%)")
    
    # 3. ¿Cuántos tienen CUFE?
    print(f"\n📊 REGISTROS CON CUFE:")
    result = conn.execute(text("""
        SELECT 
            COUNT(*) FILTER (WHERE cufe IS NOT NULL AND cufe != '') as con_cufe,
            COUNT(*) FILTER (WHERE cufe IS NULL OR cufe = '') as sin_cufe
        FROM maestro_dian_vs_erp
    """))
    row = result.fetchone()
    print(f"   Con CUFE: {row[0]:,}")
    print(f"   Sin CUFE: {row[1]:,}")
    
    # 4. De los que tienen CUFE, ¿cuántos tienen estado "No Registra"?
    print(f"\n📊 REGISTROS CON CUFE Y 'NO REGISTRA':")
    result = conn.execute(text("""
        SELECT COUNT(*)
        FROM maestro_dian_vs_erp
        WHERE (cufe IS NOT NULL AND cufe != '')
        AND estado_aprobacion = 'No Registra'
    """))
    con_cufe_sin_estado = result.fetchone()[0]
    print(f"   Total: {con_cufe_sin_estado:,}")
    
    # 5. Verificar si esos CUFEs existen en tabla acuses
    print(f"\n🔍 VERIFICANDO SI ESOS CUFEs EXISTEN EN TABLA ACUSES:")
    result = conn.execute(text("""
        SELECT COUNT(*)
        FROM maestro_dian_vs_erp m
        INNER JOIN acuses a ON m.cufe = a.cufe
        WHERE m.estado_aprobacion = 'No Registra'
        AND m.cufe IS NOT NULL
        AND m.cufe != ''
        LIMIT 1000
    """))
    tienen_match = result.fetchone()[0]
    print(f"   Registros con 'No Registra' que SÍ tienen acuse: {tienen_match:,}")
    
    if tienen_match > 0:
        print(f"\n   ❌ PROBLEMA CONFIRMADO:")
        print(f"      {tienen_match:,} registros tienen CUFE que existe en tabla acuses")
        print(f"      Pero muestran 'No Registra' en lugar del estado real")
        
        # Mostrar ejemplos
        print(f"\n   📝 EJEMPLOS DE REGISTROS AFECTADOS:")
        result = conn.execute(text("""
            SELECT 
                m.nit,
                m.razon_social,
                m.prefijo,
                m.folio,
                m.cufe,
                m.estado_aprobacion as estado_maestro,
                a.estado_docto as estado_acuses
            FROM maestro_dian_vs_erp m
            INNER JOIN acuses a ON m.cufe = a.cufe
            WHERE m.estado_aprobacion = 'No Registra'
            AND m.cufe IS NOT NULL
            LIMIT 5
        """))
        
        for i, row in enumerate(result, 1):
            nit, razon, prefijo, folio, cufe, estado_m, estado_a = row
            print(f"\n      {i}. NIT: {nit} - {razon}")
            print(f"         Factura: {prefijo}-{folio}")
            print(f"         CUFE: {cufe[:40]}...")
            print(f"         Estado en MAESTRO: '{estado_m}'")
            print(f"         Estado en ACUSES: '{estado_a}'")
            print(f"         ⚠️  DESAJUSTE: Debería ser '{estado_a}' pero muestra '{estado_m}'")
    
    # 6. Ejemplos de registros que SÍ tienen el estado correcto
    print(f"\n✅ EJEMPLOS DE REGISTROS CON ESTADO CORRECTO:")
    result = conn.execute(text("""
        SELECT 
            nit,
            razon_social,
            prefijo,
            folio,
            estado_aprobacion
        FROM maestro_dian_vs_erp
        WHERE estado_aprobacion != 'No Registra'
        AND estado_aprobacion IS NOT NULL
        LIMIT 5
    """))
    
    tiene_correctos = False
    for i, row in enumerate(result, 1):
        tiene_correctos = True
        nit, razon, prefijo, folio, estado = row
        print(f"      {i}. {nit} - {razon} | {prefijo}-{folio} → {estado}")
    
    if not tiene_correctos:
        print(f"      ❌ NO HAY REGISTROS con estado diferente a 'No Registra'")

print(f"\n" + "=" * 80)
print("CONCLUSIÓN:")
print("=" * 80)

if tienen_match > 0:
    print(f"""
❌ PROBLEMA CONFIRMADO: ESTADOS NO SE ESTÁN ACTUALIZANDO

Hay {tienen_match:,} registros que tienen CUFE válido en tabla acuses
pero siguen mostrando 'No Registra' en la tabla maestro.

CAUSA PROBABLE:
El problema está en el proceso de carga o en la consulta del Visor V2.

SOLUCIÓN:
1. Verificar línea 1600 de routes.py donde se hace el match
2. Verificar que acuses_por_cufe se esté poblando correctamente
3. Re-procesar archivos para actualizar tabla maestro

SIGUIENTE PASO:
Revisar logs de procesamiento para ver si acuses_por_cufe está vacío.
""")
elif total == 0:
    print(f"""
❌ NO HAY DATOS EN TABLA MAESTRO

La tabla maestro está vacía. Necesitas procesararchivos.
""")
else:
    print(f"""
✅ TODO CORRECTO

Los estados se están reflejando correctamente en la tabla maestro.
Si ves "No Registra" en el Visor V2, verifica:
1. Filtros aplicados en la vista
2. Que estés viendo la página correcta
""")

print("=" * 80)
