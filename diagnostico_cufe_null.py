"""
VERIFICAR SI PROBLEMA ES DE REGISTROS ANTIGUOS
===============================================
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/gestor_documental')
engine = create_engine(DATABASE_URL)

print("=" * 80)
print("VERIFICACIÓN: ¿Los registros maestro son antiguos o nuevos?")
print("=" * 80)

with engine.connect() as conn:
    # 1. Ver fechas de los registros en maestro
    print(f"\n📅 FECHAS DE ÚLTIMA MODIFICACIÓN EN MAESTRO:")
    result = conn.execute(text("""
        SELECT 
            TO_CHAR(MIN(fecha_emision), 'DD-MM-YYYY') as fecha_mas_antigua,
            TO_CHAR(MAX(fecha_emision), 'DD-MM-YYYY') as fecha_mas_reciente,
            COUNT(*) as total
        FROM maestro_dian_vs_erp
        WHERE fecha_emision IS NOT NULL
    """))
    row = result.fetchone()
    if row:
        print(f"   Fecha más antigua: {row[0]}")
        print(f"   Fecha más reciente: {row[1]}")
        print(f"   Total con fecha: {row[2]:,}")
    
    # 2. Ver si existe el campo CUFE en maestro (columnas)
    print(f"\n🔍 VERIFICANDO EXISTENCIA DE COLUMNA 'cufe' EN MAESTRO:")
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'maestro_dian_vs_erp' 
        AND table_schema = 'public'
        AND column_name = 'cufe'
    """))
    
    row = result.fetchone()
    if row:
        print(f"   ✅ Columna 'cufe' existe:")
        print(f"      Tipo: {row[1]}")
        print(f"      Nullable: {row[2]}")
    else:
        print(f"   ❌ Columna 'cufe' NO existe en la tabla")
    
    # 3. Ver todas las columnas de maestro
    print(f"\n📋 TODAS LAS COLUMNAS EN MAESTRO:")
    result = conn.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns 
        WHERE table_name = 'maestro_dian_vs_erp' 
        AND table_schema = 'public'
        ORDER BY ordinal_position
    """))
    
    for row in result:
        col_name, col_type = row
        print(f"   {col_name:30s} {col_type}")
    
    # 4. Verificar primeros 5 registros de DIAN con CUFE
    print(f"\n📊 PRIMEROS 5 REGISTROS DE TABLA DIAN:")
    result = conn.execute(text("""
        SELECT 
            nit,
            razon_social,
            prefijo,
            folio,
            SUBSTRING(cufe_cude, 1, 40) as cufe_inicio
        FROM dian
        WHERE cufe_cude IS NOT NULL
        AND cufe_cude != ''
        LIMIT 5
    """))
    
    for i, row in enumerate(result, 1):
        nit, razon, prefijo, folio, cufe = row
        print(f"\n   {i}. NIT: {nit} - {razon}")
        print(f"      Factura: {prefijo}-{folio}")
        print(f"      CUFE: {cufe}...")
    
    # 5. Verificar si esos mismos registros existen en MAESTRO y tienen CUFE
    print(f"\n🔍 VERIFICANDO SI ESOS MISMOS REGISTROS EXISTEN EN MAESTRO:")
    result = conn.execute(text("""
        SELECT 
            d.nit as nit_dian,
            d.prefijo as prefijo_dian,
            d.folio as folio_dian,
            SUBSTRING(d.cufe_cude, 1, 40) as cufe_dian,
            m.nit_emisor as nit_maestro,
            m.prefijo as prefijo_maestro,
            m.folio as folio_maestro,
            COALESCE(SUBSTRING(m.cufe, 1, 40), 'NULL') as cufe_maestro
        FROM dian d
        LEFT JOIN maestro_dian_vs_erp m 
            ON d.nit = m.nit_emisor
            AND d.prefijo = m.prefijo
            AND d.folio = m.folio
        WHERE d.cufe_cude IS NOT NULL
        LIMIT 5
    """))
    
    tiene_null = False
    for i, row in enumerate(result, 1):
        nit_d, pref_d, folio_d, cufe_d, nit_m, pref_m, folio_m, cufe_m = row
        print(f"\n   {i}. Factura: {pref_d}-{folio_d}")
        print(f"      DIAN tiene CUFE: {cufe_d}...")
        if nit_m:
            print(f"      MAESTRO existe: Sí")
            print(f"      MAESTRO tiene CUFE: {cufe_m if cufe_m != 'NULL' else '❌ NULL'}")
            if cufe_m == 'NULL':
                tiene_null = True
        else:
            print(f"      MAESTRO existe: ❌ No")
    
    if tiene_null:
        print(f"\n   ⚠️  PROBLEMA CONFIRMADO:")
        print(f"      Las facturas en DIAN tienen CUFE")
        print(f"      Las facturas en MAESTRO tienen CUFE = NULL")
        print(f"      El campo NO se  está copiando correctamente")

print(f"\n" + "=" * 80)
print("DIAGNÓSTICO FINAL:")
print("=" * 80)

if row and cufe_m == 'NULL':
    print(f"""
❌ PROBLEMA CONFIRMADO: CUFE NO SE ESTÁ COPIANDO A MAESTRO

La columna `cufe` existe en maestro, pero está vacía (NULL).
Las facturas en DIAN sí tienen CUFE.
Pero al insertarse en MAESTRO, el CUFE se pierde.

CAUSAS POSIBLES:
1. Error en el procesamiento (COPY FROM)
2. El CUFE llega vacío por error en línea 1584
3. Problema con normalización de columnas

SOLUCIÓN:
1. RE-PROCESAR archivos (borrar maestro y volver a cargar)
2. Agregar logs en línea 1584 para ver si CUFE se lee correctamente
3. Verificar buffer.write en línea ~1720 que incluya el CUFE

SIGUIENTE PASO:
Eliminar datos de maestro y re-procesar archivos.
""")
else:
    print(f"""
✅ TODO CORRECTO

Si la columna no existe, necesitas agregarla con:
ALTER TABLE maestro_dian_vs_erp ADD COLUMN cufe VARCHAR(255);

Luego re-procesar archivos para poblarla.
""")

print("=" * 80)
