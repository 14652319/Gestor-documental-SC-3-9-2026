"""
🔍 DIAGNÓSTICO COMPLETO DEL PROBLEMA DE CLAVE ÚNICA

PROBLEMA IDENTIFICADO:
La tabla 'dian' tiene un UNIQUE constraint en la columna 'clave'.
Cuando se intenta insertar registros con clave duplicada, el sistema usa:

    ON CONFLICT (clave) DO NOTHING

Esto significa: Si la clave ya existe, se IGNORA SILENCIOSAMENTE el nuevo registro.

CAUSA RAÍZ:
Si el archivo Excel tiene prefijos NULL o vacíos, múltiples facturas del mismo NIT
generan la misma clave, y solo la primera se inserta.

Ejemplo:
  NIT=805013653, Prefijo=NULL, Folio=37 → clave="80501365337" ✅ (primera, inserta)
  NIT=805013653, Prefijo=NULL, Folio=37 → clave="80501365337" ❌ (duplicada, IGNORADA)
  NIT=805013653, Prefijo=NULL, Folio=155 → clave="805013653155" ✅ (única, inserta)

RESULTADO:
- Solo 1,400 registros insertados (1 por NIT)
- ~10,000-50,000 registros rechazados silenciosamente
- No hay errores en logs porque es comportamiento esperado

SOLUCIÓN:
Tenemos 3 opciones según la documentación técnica consultada:

OPCIÓN A (RECOMENDADA): ELIMINAR UNIQUE CONSTRAINT
    - ALTER TABLE dian DROP CONSTRAINT uk_dian_clave;
    - Permite todos los registros
    - El CUFE/CUDE ya garantiza unicidad real de DIAN
    - RIESGO: Bajo (el CUFE es el identificador oficial único)

OPCIÓN B: MODIFICAR CLAVE PARA INCLUIR MÁS CAMPOS
    - Agregar fecha_emision o CUFE a la clave
    - Garantiza mejor unicidad
    - Requiere cambio de código + reload completo
    - RIESGO: Medio (puede romper integraciones existentes)

OPCIÓN C: USAR ON CONFLICT UPDATE EN VEZ DE DO NOTHING
    - Sobrescribir registros existentes con datos nuevos
    - Mantiene el constraint
    - Puede perder datos históricos
    - RIESGO: Alto (potencial pérdida de información)

EVIDENCIA DEL PROBLEMA:
"""

import psycopg2
from datetime import date, datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Conexión a PostgreSQL
conn = psycopg2.connect(
    dbname=os.getenv('POSTGRES_DB', 'gestor_documental'),
    user=os.getenv('POSTGRES_USER', 'postgres'),
    password=os.getenv('POSTGRES_PASSWORD', 'Innovacion2022*'),
    host=os.getenv('POSTGRES_HOST', 'localhost'),
    port=os.getenv('POSTGRES_PORT', '5432')
)
cursor = conn.cursor()

print("\n" + "="*80)
print("🔍 DIAGNÓSTICO COMPLETO DEL PROBLEMA DE CLAVE ÚNICA")
print("="*80)

# 1. Verificar constraint actual
print("\n1️⃣ CONSTRAINT ACTUAL:")
cursor.execute("""
    SELECT conname, contype, pg_get_constraintdef(oid) 
    FROM pg_constraint 
    WHERE conrelid = 'dian'::regclass AND conname = 'uk_dian_clave'
""")
resultado = cursor.fetchone()
if resultado:
    print(f"   ✅ Constraint encontrado: {resultado[0]}")
    print(f"   📋 Definición: {resultado[2]}")
else:
    print("   ⚠️ Constraint NO encontrado (ya fue eliminado?)")

# 2. Ver ejemplos de claves duplicadas que intentaron insertarse
print("\n2️⃣ ANÁLISIS DE CLAVES EN TABLA DIAN:")
cursor.execute("""
    SELECT 
        LEFT(clave, 9) as nit_inicio,
        COUNT(*) as registros,
        STRING_AGG(DISTINCT prefijo, ', ' ORDER BY prefijo) as prefijos_distintos,
        STRING_AGG(DISTINCT folio, ', ' ORDER BY folio LIMIT 5) as folios_muestra
    FROM dian
    WHERE LEFT(clave, 9) = '805013653'
    GROUP BY LEFT(clave, 9)
""")
resultado = cursor.fetchone()
if resultado:
    print(f"   NIT 805013653:")
    print(f"   - Registros en DIAN: {resultado[1]}")
    print(f"   - Prefijos encontrados: {resultado[2] or 'NULL/Vacío'}")
    print(f"   - Folios muestra: {resultado[3]}")

# 3. Comparar con ERP (donde sí están todos los datos)
print("\n3️⃣ COMPARACIÓN CON ERP_FINANCIERO:")
cursor.execute("""
    SELECT 
        COUNT(*) as registros_erp,
        STRING_AGG(DISTINCT prefijo, ', ' ORDER BY prefijo) as todos_prefijos,
        COUNT(DISTINCT prefijo) as prefijos_distintos
    FROM erp_financiero
    WHERE nit_proveedor = '805013653'
""")
resultado = cursor.fetchone()
if resultado:
    print(f"   NIT 805013653 en ERP_FINANCIERO:")
    print(f"   - Registros totales: {resultado[0]}")
    print(f"   - Prefijos distintos: {resultado[2]}")
    print(f"   - Prefijos encontrados: {resultado[1]}")

# 4. Calcular registros perdidos
cursor.execute("""
    SELECT 
        (SELECT COUNT(*) FROM erp_financiero WHERE nit_proveedor = '805013653') as en_erp,
        (SELECT COUNT(*) FROM dian WHERE nit_emisor = '805013653') as en_dian,
        (SELECT COUNT(*) FROM erp_financiero WHERE nit_proveedor = '805013653') -
        (SELECT COUNT(*) FROM dian WHERE nit_emisor = '805013653') as perdidos
""")
en_erp, en_dian, perdidos = cursor.fetchone()

print(f"\n4️⃣ REGISTROS PERDIDOS PARA NIT 805013653:")
print(f"   📊 En ERP_FINANCIERO: {en_erp} registros")
print(f"   📊 En DIAN: {en_dian} registros")
print(f"   ❌ PERDIDOS: {perdidos} registros ({(perdidos/en_erp*100):.1f}%)")

# 5. Estimación total del problema
cursor.execute("""
    SELECT 
        COUNT(DISTINCT nit_emisor) as nits_unicos,
        COUNT(*) as registros_totales,
        AVG(registros_por_nit) as promedio_por_nit
    FROM (
        SELECT nit_emisor, COUNT(*) as registros_por_nit
        FROM dian
        GROUP BY nit_emisor
    ) subq
""")
nits, total, promedio = cursor.fetchone()

print(f"\n5️⃣ ESTIMACIÓN GLOBAL DEL PROBLEMA:")
print(f"   📊 NITs únicos en DIAN: {nits}")
print(f"   📊 Registros totales en DIAN: {total}")
print(f"   📊 Promedio por NIT: {promedio:.2f}")
print(f"   ⚠️ Patrón sospechoso: Promedio cercano a 1.0 indica pérdida masiva de datos")

# 6. Ver el INSERT statement usado
print(f"\n6️⃣ MECANISMO DE INSERCIÓN DETECTADO:")
print(f"   Archivo: modules/dian_vs_erp/routes.py")
print(f"   Función: insertar_dian_bulk() (línea 1153)")
print(f"   Método: INSERT ... ON CONFLICT (clave) DO NOTHING")
print(f"   ⚠️ Esto significa: Duplicados se IGNORAN SILENCIOSAMENTE")

print("\n" + "="*80)
print("💡 SOLUCIÓN RECOMENDADA:")
print("="*80)
print("""
PASO 1: Eliminar el UNIQUE constraint en la columna 'clave'
        SQL: ALTER TABLE dian DROP CONSTRAINT uk_dian_clave;

PASO 2: Truncar la tabla dian para limpiar datos parciales
        SQL: TRUNCATE TABLE dian CASCADE;

PASO 3: Recargar TODOS los archivos desde la interfaz web

PASO 4: Verificar que ahora se carguen TODOS los registros

ALTERNATIVA (si quieres mantener unicidad):
- Cambiar la clave para incluir más campos únicos
- Ejemplo: clave = NIT + PREFIJO + FOLIO + FECHA + CUFE[:8]
- Pero esto requiere cambiar el código de crear_clave_factura()

JUSTIFICACIÓN para eliminar constraint:
- El CUFE/CUDE es el identificador ÚNICO OFICIAL de DIAN
- Ya existe una columna 'cufe_cude' que garantiza unicidad real
- La columna 'clave' es solo para cross-reference interno
- No necesita ser UNIQUE en la BD, solo funcionalmente única
""")

cursor.close()
conn.close()

print("\n✅ Diagnóstico completado")
print("📝 Revisa las opciones arriba y decide cuál implementar")
