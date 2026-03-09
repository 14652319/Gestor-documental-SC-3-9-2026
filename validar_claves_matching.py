"""
VALIDACIÓN DE CLAVES: ¿Por qué NO coinciden DIAN vs ERP?

Verifica cómo se generan las claves en cada tabla y por qué no hay matching
"""

import psycopg2

# Conexión
conn = psycopg2.connect(
    dbname='gestor_documental',
    user='postgres',
    password='G3st0radm$2025.',
    host='localhost',
    port='5432'
)
cursor = conn.cursor()

print("\n" + "="*80)
print("🔍 VALIDACIÓN DE CLAVES - ¿Por qué no hay matching?")
print("="*80)

# 1. Verificar registros cargados
print("\n1️⃣ REGISTROS CARGADOS:")
cursor.execute("SELECT COUNT(*) FROM dian")
dian_count = cursor.fetchone()[0]
print(f"   DIAN: {dian_count:,} registros")

cursor.execute("SELECT COUNT(*) FROM erp_financiero")
erp_fn_count = cursor.fetchone()[0]
print(f"   ERP_FINANCIERO: {erp_fn_count:,} registros")

cursor.execute("SELECT COUNT(*) FROM erp_comercial")
erp_cm_count = cursor.fetchone()[0]
print(f"   ERP_COMERCIAL: {erp_cm_count:,} registros")

# 2. Ver ejemplos de claves en DIAN para NIT 805013653
print("\n2️⃣ CLAVES EN TABLA DIAN (NIT 805013653) - Primeras 10:")
cursor.execute("""
    SELECT 
        nit_emisor,
        prefijo,
        folio,
        clave,
        LEFT(cufe_cude, 20) as cufe_inicio
    FROM dian
    WHERE nit_emisor = '805013653'
    ORDER BY fecha_emision DESC
    LIMIT 10
""")
dian_rows = cursor.fetchall()
print("   NIT        | Prefijo | Folio | Clave                    | CUFE (inicio)")
print("   " + "-"*75)
for row in dian_rows:
    print(f"   {row[0]:10} | {row[1] or 'NULL':7} | {row[2] or 'NULL':5} | {row[3]:24} | {row[4] or 'NULL'}")

# 3. Ver ejemplos de claves en ERP_FINANCIERO para NIT 805013653
print("\n3️⃣ CLAVES EN TABLA ERP_FINANCIERO (NIT 805013653) - Primeras 10:")
cursor.execute("""
    SELECT 
        nit_proveedor,
        prefijo,
        folio,
        clave_erp_financiero
    FROM erp_financiero
    WHERE nit_proveedor = '805013653'
    ORDER BY fecha_documento DESC
    LIMIT 10
""")
erp_rows = cursor.fetchall()
print("   NIT        | Prefijo | Folio | Clave ERP")
print("   " + "-"*60)
for row in erp_rows:
    print(f"   {row[0]:10} | {row[1] or 'NULL':7} | {row[2] or 'NULL':5} | {row[3]:24}")

# 4. Ver si hay ALGUNA coincidencia
print("\n4️⃣ BUSCANDO COINCIDENCIAS (matching de claves):")
cursor.execute("""
    SELECT COUNT(*) 
    FROM dian d
    INNER JOIN erp_financiero ef ON d.clave = ef.clave_erp_financiero
    WHERE d.nit_emisor = '805013653'
""")
matches_fn = cursor.fetchone()[0]
print(f"   Matches DIAN ↔ ERP_FINANCIERO (NIT 805013653): {matches_fn}")

cursor.execute("""
    SELECT COUNT(*) 
    FROM dian d
    INNER JOIN erp_comercial ec ON d.clave = ec.clave_erp_comercial
    WHERE d.nit_emisor = '805013653'
""")
matches_cm = cursor.fetchone()[0]
print(f"   Matches DIAN ↔ ERP_COMERCIAL (NIT 805013653): {matches_cm}")

# 5. Comparar estructura de claves
print("\n5️⃣ ANÁLISIS DE ESTRUCTURA DE CLAVES:")
cursor.execute("""
    SELECT 
        'DIAN' as tabla,
        LENGTH(clave) as longitud_clave,
        LEFT(clave, 9) as inicio_clave,
        RIGHT(clave, 10) as final_clave,
        clave as clave_completa
    FROM dian
    WHERE nit_emisor = '805013653'
    LIMIT 3
""")
dian_structure = cursor.fetchall()

cursor.execute("""
    SELECT 
        'ERP_FN' as tabla,
        LENGTH(clave_erp_financiero) as longitud_clave,
        LEFT(clave_erp_financiero, 9) as inicio_clave,
        RIGHT(clave_erp_financiero, 10) as final_clave,
        clave_erp_financiero as clave_completa
    FROM erp_financiero
    WHERE nit_proveedor = '805013653'
    LIMIT 3
""")
erp_structure = cursor.fetchall()

print("\n   📊 DIAN:")
for row in dian_structure:
    print(f"      {row[0]:8} | Long: {row[1]:2} | Inicio: {row[2]:9} | Final: {row[3]:10} | Completa: {row[4]}")

print("\n   📊 ERP_FINANCIERO:")
for row in erp_structure:
    print(f"      {row[0]:8} | Long: {row[1]:2} | Inicio: {row[2]:9} | Final: {row[3]:10} | Completa: {row[4]}")

# 6. Ver si el problema es solo en prefijos NULL
print("\n6️⃣ PREFIJOS NULL EN DIAN:")
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN prefijo IS NULL OR prefijo = '' THEN 1 END) as prefijo_null,
        COUNT(CASE WHEN prefijo IS NOT NULL AND prefijo != '' THEN 1 END) as prefijo_ok
    FROM dian
""")
prefijo_stats = cursor.fetchone()
total, null_count, ok_count = prefijo_stats
print(f"   Total registros: {total:,}")
print(f"   Prefijo NULL/vacío: {null_count:,} ({null_count/total*100:.1f}%)")
print(f"   Prefijo OK: {ok_count:,} ({ok_count/total*100:.1f}%)")

# 7. Buscar MISMO NIT+PREFIJO+FOLIO en ambas tablas
print("\n7️⃣ BUSCAR MISMO NIT+PREFIJO+FOLIO en DIAN y ERP:")
cursor.execute("""
    SELECT 
        d.nit_emisor as nit_dian,
        d.prefijo as prefijo_dian,
        d.folio as folio_dian,
        d.clave as clave_dian,
        ef.prefijo as prefijo_erp,
        ef.folio as folio_erp,
        ef.clave_erp_financiero as clave_erp
    FROM dian d
    FULL OUTER JOIN erp_financiero ef 
        ON d.nit_emisor = ef.nit_proveedor
        AND d.prefijo = ef.prefijo
        AND d.folio = ef.folio
    WHERE d.nit_emisor = '805013653' OR ef.nit_proveedor = '805013653'
    LIMIT 5
""")
matches = cursor.fetchall()
if matches:
    print("   NIT DIAN   | Pr DIAN | Fo DIAN | Clave DIAN           | Pr ERP  | Fo ERP | Clave ERP")
    print("   " + "-"*90)
    for row in matches:
        print(f"   {row[0] or 'NULL':10} | {row[1] or 'NULL':7} | {row[2] or 'NULL':7} | {row[3] or 'NULL':20} | {row[4] or 'NULL':7} | {row[5] or 'NULL':6} | {row[6] or 'NULL'}")
else:
    print("   ❌ No hay registros con mismo NIT+PREFIJO+FOLIO")

print("\n" + "="*80)
print("💡 DIAGNÓSTICO:")
print("="*80)
print("""
Si las claves NO coinciden puede ser por:

1. PREFIJOS DIFERENTES:
   - DIAN tiene prefijos NULL/vacíos
   - ERP tiene prefijos (1FEA, 2FEA, etc.)
   - Solución: Usar CUFE como clave principal

2. FORMATO DE FOLIO DIFERENTE:
   - DIAN: Folio completo (ej: "000000037")
   - ERP: Folio sin ceros (ej: "37")
   - Solución: Normalizar formato

3. NIT CON/SIN DÍGITO DE VERIFICACIÓN:
   - DIAN: NIT con DV (ej: "805013653-1")
   - ERP: NIT sin DV (ej: "805013653")
   - Solución: Limpiar ambos

4. COLUMNAS MAL MAPEADAS:
   - Los nombres de columnas en Excel son diferentes
   - Los datos se leen de la columna equivocada
   - Solución: Verificar mapeo de columnas
""")

cursor.close()
conn.close()

print("\n✅ Validación completada")
