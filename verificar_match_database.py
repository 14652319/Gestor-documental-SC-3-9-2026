"""
VERIFICACIÓN DE MATCH DE CUFEs EN BASE DE DATOS
================================================
Verifica si hay coincidencias entre tabla DIAN y tabla ACUSES
directamente en PostgreSQL
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno
load_dotenv()

# Conectar a PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/gestor_documental')
engine = create_engine(DATABASE_URL)

print("=" * 80)
print("VERIFICACIÓN DE MATCH DE CUFEs EN BASE DE DATOS")
print("=" * 80)

with engine.connect() as conn:
    # 1. Verificar registros en tabla DIAN
    print(f"\n📊 TABLA DIAN:")
    result = conn.execute(text("SELECT COUNT(*) as total FROM dian"))
    total_dian = result.fetchone()[0]
    print(f"   Total registros: {total_dian:,}")
    
    # Verificar CUFEs no nulos
    result = conn.execute(text("""
        SELECT COUNT(*) as total 
        FROM dian 
        WHERE cufe_cude IS NOT NULL 
        AND cufe_cude != ''
    """))
    dian_con_cufe = result.fetchone()[0]
    print(f"   Con CUFE no nulo: {dian_con_cufe:,}")
    
    # Muestra de CUFEs
    result = conn.execute(text("""
        SELECT cufe_cude 
        FROM dian 
        WHERE cufe_cude IS NOT NULL 
        AND cufe_cude != ''
        LIMIT 5
    """))
    print(f"\n   Ejemplos de CUFEs en DIAN:")
    for i, row in enumerate(result, 1):
        cufe = row[0]
        print(f"      {i}. {cufe[:60]}...")
    
    # 2. Verificar registros en tabla ACUSES
    print(f"\n📊 TABLA ACUSES:")
    result = conn.execute(text("SELECT COUNT(*) as total FROM acuses"))
    total_acuses = result.fetchone()[0]
    print(f"   Total registros: {total_acuses:,}")
    
    # Verificar CUFEs no nulos
    result = conn.execute(text("""
        SELECT COUNT(*) as total 
        FROM acuses 
        WHERE cufe IS NOT NULL 
        AND cufe != ''
    """))
    acuses_con_cufe = result.fetchone()[0]
    print(f"   Con CUFE no nulo: {acuses_con_cufe:,}")
    
    # Muestra de CUFEs
    result = conn.execute(text("""
        SELECT cufe, estado_docto
        FROM acuses 
        WHERE cufe IS NOT NULL 
        AND cufe != ''
        LIMIT 5
    """))
    print(f"\n   Ejemplos de CUFEs en ACUSES:")
    for i, row in enumerate(result, 1):
        cufe, estado = row[0], row[1]
        print(f"      {i}. {cufe[:60]}... → Estado: {estado}")
    
    # 3. VERIFICAR MATCH ENTRE DIAN Y ACUSES
    print(f"\n🎯 VERIFICANDO MATCH ENTRE TABLAS:")
    
    # Match directo
    result = conn.execute(text("""
        SELECT COUNT(*) as coincidencias
        FROM dian d
        INNER JOIN acuses a ON d.cufe_cude = a.cufe
        WHERE d.cufe_cude IS NOT NULL 
        AND d.cufe_cude != ''
        AND a.cufe IS NOT NULL
        AND a.cufe != ''
    """))
    coincidencias = result.fetchone()[0]
    print(f"   ✅ Coincidencias EXACTAS: {coincidencias:,}")
    
    # Match con normalización (UPPER, TRIM)
    result = conn.execute(text("""
        SELECT COUNT(*) as coincidencias
        FROM dian d
        INNER JOIN acuses a ON UPPER(TRIM(d.cufe_cude)) = UPPER(TRIM(a.cufe))
        WHERE d.cufe_cude IS NOT NULL 
        AND d.cufe_cude != ''
        AND a.cufe IS NOT NULL
        AND a.cufe != ''
    """))
    coincidencias_norm = result.fetchone()[0]
    print(f"   ✅ Coincidencias con normalización: {coincidencias_norm:,}")
    
    if coincidencias > 0:
        # Mostrar ejemplos de match
        result = conn.execute(text("""
            SELECT 
                d.nit,
                d.razon_social,
                d.prefijo,
                d.folio,
                d.cufe_cude,
                a.estado_docto
            FROM dian d
            INNER JOIN acuses a ON d.cufe_cude = a.cufe
            WHERE d.cufe_cude IS NOT NULL 
            AND d.cufe_cude != ''
            LIMIT 5
        """))
        print(f"\n   📝 Ejemplos de facturas con match:")
        for i, row in enumerate(result, 1):
            nit, razon, prefijo, folio, cufe, estado = row
            print(f"\n      {i}. NIT: {nit} - {razon}")
            print(f"         Factura: {prefijo}-{folio}")
            print(f"         CUFE: {cufe[:40]}...")
            print(f"         Estado Acuse: {estado}")
    
    # 4. VERIFICAR TABLA MAESTRO
    print(f"\n📊 TABLA MAESTRO_DIAN_VS_ERP:")
    result = conn.execute(text("SELECT COUNT(*) as total FROM maestro_dian_vs_erp"))
    total_maestro = result.fetchone()[0]
    print(f"   Total registros: {total_maestro:,}")
    
    # Verificar estados de aprobación
    result = conn.execute(text("""
        SELECT 
            estado_aprobacion,
            COUNT(*) as cantidad
        FROM maestro_dian_vs_erp
        GROUP BY estado_aprobacion
        ORDER BY cantidad DESC
    """))
    print(f"\n   Estados de aprobación:")
    for row in result:
        estado, cantidad = row
        print(f"      {estado}: {cantidad:,}")
    
    # Verificar si hay registros con estado diferente a "No Registra"
    result = conn.execute(text("""
        SELECT COUNT(*) as total
        FROM maestro_dian_vs_erp
        WHERE estado_aprobacion != 'No Registra'
        AND estado_aprobacion IS NOT NULL
    """))
    con_estado = result.fetchone()[0]
    print(f"\n   ✅ Registros CON estado de acuse: {con_estado:,}")
    
    if con_estado > 0:
        # Mostrar ejemplos
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
        print(f"\n   📝 Ejemplos de registros con estado:")
        for i, row in enumerate(result, 1):
            nit, razon, prefijo, folio, estado = row
            print(f"      {i}. {nit} - {razon} | {prefijo}-{folio} → {estado}")

print(f"\n" + "=" * 80)
print("DIAGNÓSTICO:")
print("=" * 80)

if total_dian == 0 or total_acuses == 0:
    print("""
❌ NO HAY DATOS EN LAS TABLAS

Las tablas están vacías. Necesitas:
1. Cargar archivo DIAN
2. Cargar archivo ACUSES
3. El sistema procesará automáticamente
""")
elif coincidencias == 0:
    print(f"""
❌ NO HAY COINCIDENCIAS DE CUFEs

Tabla DIAN: {total_dian:,} registros ({dian_con_cufe:,} con CUFE)
Tabla ACUSES: {total_acuses:,} registros ({acuses_con_cufe:,} con CUFE)
Coincidencias: 0

CAUSAS POSIBLES:
1. Los archivos son de DIFERENTES PERÍODOS
2. Los CUFEs no están en el mismo formato
3. Los archivos no corresponden a las mismas facturas

SOLUCIÓN:
- Verificar que el archivo ACUSES contenga acuses de las facturas en DIAN
- Los CUFEs deben ser exactamente iguales (mismo hash)
""")
elif con_estado == 0:
    print(f"""
⚠️ HAY COINCIDENCIAS PERO NO SE REFLEJAN EN MAESTRO

Coincidencias entre DIAN y ACUSES: {coincidencias:,}
Registros en maestro con estado: {con_estado:,}

PROBLEMA:
Las tablas DIAN y ACUSES tienen matches, pero la tabla maestro
no refleja los estados de aprobación correctamente.

SOLUCIÓN:
1. Verificar proceso de consolidación (procesar_archivos)
2. Verificar que el JOIN en línea 1600 de routes.py esté correcto
3. Re-procesar archivos para actualizar tabla maestro
""")
else:
    print(f"""
✅ SISTEMA FUNCIONANDO CORRECTAMENTE

Tabla DIAN: {total_dian:,} registros
Tabla ACUSES: {total_acuses:,} registros
Coincidencias: {coincidencias:,}
Registros maestro con estado: {con_estado:,}

El sistema está procesando correctamente los acuses.
Si ves "No Registra" en el Visor V2, puede ser:
1. Filtro aplicado en la vista
2. Los registros que estás viendo no tienen acuse
3. Problema en la consulta del Visor V2
""")

print("=" * 80)
