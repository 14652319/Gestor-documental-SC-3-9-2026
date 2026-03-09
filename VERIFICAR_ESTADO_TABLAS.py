"""
SCRIPT SIMPLE: Verificar estado de tablas individuales
Fecha: 19 de Febrero de 2026

Script directo para verificar el estado de las tablas sin ejecutar procesamiento.
"""

import psycopg2
from datetime import datetime

print("="*80)
print("🔍 VERIFICACIÓN RÁPIDA: Estado de Tablas Individuales")
print("="*80)

# Conectar a PostgreSQL
try:
    conn = psycopg2.connect(
        host="localhost",
        database="gestor_documental",
        user="postgres",
        password="G3st0radm$2025."
    )
    cursor = conn.cursor()
    print("\n✅ Conexión exitosa a PostgreSQL")
except Exception as e:
    print(f"\n❌ ERROR de conexión: {e}")
    exit(1)

print("\n📊 CONTEO ACTUAL DE REGISTROS:")
print("-"*80)

tablas = [
    ("dian", "Tabla DIAN (facturas electrónicas)"),
    ("erp_comercial", "ERP Comercial"),
    ("erp_financiero", "ERP Financiero"),
    ("acuses", "Acuses Recibidos"),
    ("maestro_dian_vs_erp", "Maestro Consolidado"),
]

for tabla, descripcion in tablas:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
        count = cursor.fetchone()[0]
        simbolo = "✅" if count > 0 else "❌"
        print(f"{simbolo} {descripcion:40s}: {count:>10,} registros")
    except Exception as e:
        print(f"❌ {descripcion:40s}: ERROR - {e}")

# Verificar campos calculados en DIAN

if count > 0:
    print("\n📋 VERIFICACIÓN DE CAMPOS CALCULADOS EN DIAN (3 muestras):")
    print("-"*80)
    
    cursor.execute("""
        SELECT 
            nit_emisor,
            prefijo,
            folio,
            clave,
            LENGTH(cufe_cude) AS cufe_length,
            tipo_tercero,
            n_dias
        FROM dian 
        LIMIT 3
    """)
    
    rows = cursor.fetchall()
    for i, row in enumerate(rows, 1):
        print(f"\n   Registro {i}:")
        print(f"      NIT: {row[0]}")
        print(f"      Prefijo: {row[1]}, Folio: {row[2]}")
        print(f"      Clave: {row[3]}")
        print(f"      CUFE Length: {row[4]} {'✅ (correcto)' if row[4] == 96 else '❌ (debe ser 96)'}")
        print(f"      Tipo Tercero: {row[5]}")
        print(f"      Días: {row[6]}")

# Verificar ERP Comercial
cursor.execute("SELECT COUNT(*) FROM erp_comercial")
count_erp = cursor.fetchone()[0]

if count_erp > 0:
    print("\n📋 VERIFICACIÓN DE EXTRACCIÓN EN ERP COMERCIAL (3 muestras):")
    print("-"*80)
    
    cursor.execute("""
        SELECT 
            proveedor,
            docto_proveedor,
            prefijo,
            folio,
            doc_causado_por
        FROM erp_comercial 
        WHERE prefijo IS NOT NULL
        LIMIT 3
    """)
    
    rows = cursor.fetchall()
    for i, row in enumerate(rows, 1):
        print(f"\n   Registro {i}:")
        print(f"      Proveedor: {row[0]}")
        print(f"      Docto Original: {row[1]}")
        print(f"      Prefijo Extraído: {row[2]}")
        print(f"      Folio Extraído: {row[3]}")
        print(f"      Doc Causado Por: {row[4]}")

# Verificar matching CUFE
cursor.execute("""
    SELECT COUNT(DISTINCT d.clave_acuse) 
    FROM dian d
    INNER JOIN acuses a ON d.clave_acuse = a.clave_acuse
""")
count_match = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM dian WHERE clave_acuse IS NOT NULL AND clave_acuse != ''")
count_total_dian = cursor.fetchone()[0]

print(f"\n🔗 MATCHING DIAN ↔ ACUSES:")
print("-"*80)
print(f"   Total DIAN con CUFE: {count_total_dian:,}")
print(f"   Matches encontrados:  {count_match:,}")
if count_total_dian > 0:
    porcentaje = (count_match / count_total_dian) * 100
    print(f"   Porcentaje match:    {porcentaje:.2f}%")

# Mostrar muestra de matching
cursor.execute("""
    SELECT 
        d.nit_emisor,
        d.prefijo || '-' || d.folio AS factura,
        SUBSTRING(d.cufe_cude, 1, 30) || '...' AS cufe_corto,
        a.estado_docto,
        CASE WHEN a.clave_acuse IS NOT NULL THEN 'SI' ELSE 'NO' END AS tiene_acuse
    FROM dian d
    LEFT JOIN acuses a ON d.clave_acuse = a.clave_acuse
    LIMIT 5
""")

print(f"\n   Muestra de 5 registros:")
for row in cursor.fetchall():
    print(f"      • {row[0]} | {row[1]} | {row[2]}")
    print(f"        Estado: {row[3] or 'Sin acuse'} | Match: {row[4]}")

# Cerrar conexión
cursor.close()
conn.close()

print("\n" + "="*80)
print("✅ VERIFICACIÓN COMPLETADA")
print("="*80)

print("\n💡 PRÓXIMOS PASOS:")
print("   1. Si las tablas están vacías: Cargar archivos desde la interfaz web")
print("   2. Si las tablas tienen datos: Verificar Visor V2 en el navegador")
print("   3. Verificar que 'Ver PDF' y 'Estado Aprobación' muestren datos")
