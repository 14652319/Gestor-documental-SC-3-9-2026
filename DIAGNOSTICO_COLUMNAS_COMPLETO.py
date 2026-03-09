"""
==================================================================================
DIAGNÓSTICO COMPLETO: VALIDAR COLUMNAS EXCEL → CÓDIGO → BASE DE DATOS
==================================================================================

Este script valida:
1. Qué columnas tiene el Excel
2. Qué columnas espera el código de routes.py
3. Qué columnas existen en la tabla PostgreSQL
4. Dónde hay desajustes
"""
import polars as pl
from sqlalchemy import create_engine, inspect
import os
from dotenv import load_dotenv
from unicodedata import normalize
import re

load_dotenv()

def normalizar_columna(nombre):
    """Normaliza nombres de columnas (igual que routes.py)"""
    nombre = str(nombre).strip()
    nombre = normalize('NFD', nombre)
    nombre = ''.join(c for c in nombre if c.isalnum() or c in ' _-')
    nombre = nombre.lower().replace(' ', '_').replace('-', '_')
    nombre = re.sub(r'_+', '_', nombre)
    return nombre.rstrip('.')

print("\n" + "="*80)
print("DIAGNÓSTICO COMPLETO - COLUMNAS EXCEL vs CÓDIGO vs BASE DE DATOS")
print("="*80)

# ============================================================================
# 1. LEER COLUMNAS DEL EXCEL
# ============================================================================

print("\n" + "="*80)
print("PASO 1: COLUMNAS EN EXCEL ERP COMERCIAL")
print("="*80)

archivo_erp_cm = r'uploads\erp_cm\ERP_comercial_23022026.xlsx'
if os.path.exists(archivo_erp_cm):
    df_erp_cm = pl.read_excel(archivo_erp_cm, engine='calamine')
    columnas_excel = df_erp_cm.columns
    print(f"\n✓ Archivo encontrado: {archivo_erp_cm}")
    print(f"  Total columnas: {len(columnas_excel)}")
    print("\n  Columnas originales en Excel:")
    for i, col in enumerate(columnas_excel, 1):
        normalizada = normalizar_columna(col)
        print(f"    {i:2d}. '{col}' → normalizada: '{normalizada}'")
    
    # Columnas normalizadas (como las ve el código)
    df_erp_cm.columns = [normalizar_columna(col) for col in df_erp_cm.columns]
    columnas_normalizadas = df_erp_cm.columns
    print(f"\n  Columnas normalizadas (como las ve routes.py):")
    for i, col in enumerate(columnas_normalizadas, 1):
        print(f"    {i:2d}. '{col}'")
else:
    print(f"\n✗ Archivo NO encontrado: {archivo_erp_cm}")
    columnas_normalizadas = []

# ============================================================================
# 2. COLUMNAS QUE ESPERA EL CÓDIGO DE ROUTES.PY
# ============================================================================

print("\n" + "="*80)
print("PASO 2: COLUMNAS QUE ESPERA ROUTES.PY (erp_comercial)")
print("="*80)

columnas_esperadas_routes = {
    'proveedor': 'Detecta con: "proveedor" in c.lower() and "razon" not in c.lower()',
    'razon_social': 'Detecta con: "razon" in c.lower() and "social" in c.lower()',
    'docto_proveedor': 'Detecta con: "docto" in c.lower() and "proveedor" in c.lower()',
    'co': 'Detecta con: c.upper() == "CO" or c.upper() == "C.O."',
    'nro_documento': 'Detecta con: "nro" in c.lower() and "documento" in c.lower()',
    'usuario_creacion': 'Detecta con: "usuario" in c.lower() and "creac" in c.lower()',
    'clase_documento': 'Detecta con: "clase" in c.lower() and "documento" in c.lower()',
    'fecha_recibido': 'Detecta con: "fecha" in c.lower() and "recib" in c.lower()',
    'valor': 'Detecta con: "total" in c.lower() and "bruto" in c.lower()',
}

print("\n  Columnas que routes.py busca en el Excel (detectadas dinámicamente):")
for col, deteccion in columnas_esperadas_routes.items():
    print(f"    - '{col}': {deteccion}")

# ============================================================================
# 3. COLUMNAS EN LA TABLA POSTGRESQL
# ============================================================================

print("\n" + "="*80)
print("PASO 3: COLUMNAS EN TABLA POSTGRESQL (erp_comercial)")
print("="*80)

database_url = os.getenv('DATABASE_URL')
if database_url:
    engine = create_engine(database_url)
    inspector = inspect(engine)
    
    try:
        columnas_bd = inspector.get_columns('erp_comercial')
        if len(columnas_bd) > 0:
            print(f"\n✓ Tabla erp_comercial existe con {len(columnas_bd)} columnas:")
            for col in columnas_bd:
                print(f"    - {col['name']:40s} {col['type']}")
        else:
            print("\n✗ Tabla erp_comercial NO existe o está vacía")
            columnas_bd = []
    except Exception as e:
        print(f"\n✗ Error al consultar tabla: {str(e)[:200]}")
        columnas_bd = []
else:
    print("\n✗ DATABASE_URL no configurada")
    columnas_bd = []

# ============================================================================
# 4. VALIDAR DESAJUSTES
# ============================================================================

print("\n" + "="*80)
print("PASO 4: VALIDAR DESAJUSTES")
print("="*80)

if len(columnas_normalizadas) > 0 and len(columnas_bd) > 0:
    print("\n🔍 COMPARACIÓN:")
    
    # Columnas que routes.py intenta insertar
    columnas_routes_inserta = [
        'proveedor', 'razon_social', 'docto_proveedor', 'prefijo', 'folio',
        'co', 'nro_documento', 'fecha_recibido', 'usuario_creacion',
        'clase_documento', 'valor', 'clave_erp_comercial', 'doc_causado_por', 'modulo'
    ]
    
    columnas_bd_nombres = [col['name'] for col in columnas_bd]
    
    print(f"\n  Columnas que routes.py intenta INSERTAR:")
    for col_routes in columnas_routes_inserta:
        existe = col_routes in columnas_bd_nombres
        simbolo = "✓" if existe else "✗"
        print(f"    {simbolo} {col_routes:30s} {'(EXISTE EN BD)' if existe else '(❌ NO EXISTE EN BD)'}")
    
    print(f"\n  Columnas que FALTAN en BD (routes.py las necesita pero no existen):")
    faltantes = [col for col in columnas_routes_inserta if col not in columnas_bd_nombres]
    if len(faltantes) > 0:
        for col in faltantes:
            print(f"    ❌ {col}")
    else:
        print("    ✓ Todas las columnas necesarias existen")
    
    print(f"\n  Columnas EXTRA en BD (existen pero routes.py NO las usa):")
    extras = [col for col in columnas_bd_nombres if col not in columnas_routes_inserta and col != 'id' and not col.startswith('fecha_carga') and not col.startswith('fecha_actualizacion')]
    if len(extras) > 0:
        for col in extras:
            print(f"    ⚠️  {col}")
    else:
        print("   ✓ No hay columnas extras")

# ============================================================================
# 5. RECOMENDACIONES
# ============================================================================

print("\n" + "="*80)
print("PASO 5: RECOMENDACIONES")
print("="*80)

if len(columnas_normalizadas) > 0 and len(columnas_bd) > 0:
    faltantes = [col for col in columnas_routes_inserta if col not in columnas_bd_nombres]
    
    if len(faltantes) > 0:
        print(f"\n⚠️  HAY {len(faltantes)} COLUMNAS FALTANTES EN LA BASE DE DATOS")
        print(f"\nOPCIÓN 1: Actualizar el esquema SQL para usar los nombres que routes.py espera")
        print(f"  ALTER TABLE:")
        for col in faltantes:
            tipo = "VARCHAR(255)" if "razon" in col or "clase" in col or "docto" in col or "usuario" in col or "doc_causado" in col or "clave" in col or "modulo" in col else \
                   "VARCHAR(100)" if "nro" in col else \
                   "VARCHAR(50)" if "proveedor" in col or "co" in col or "prefijo" in col or "folio" in col else \
                   "DATE" if "fecha" in col else \
                   "NUMERIC(15,2)" if "valor" in col else \
                   "VARCHAR(100)"
            print(f"    ALTER TABLE erp_comercial ADD COLUMN IF NOT EXISTS {col} {tipo};")
        
        print(f"\nOPCIÓN 2: Modificar routes.py para usar los nombres del esquema SQL actual")
        print(f"  (NO RECOMENDADO - más cambios de código)")
    else:
        print(f"\n✓ TODAS LAS COLUMNAS COINCIDEN - El sistema debería funcionar correctamente")

print("\n" + "="*80)
print("FIN DEL DIAGNÓSTICO")
print("="*80)
print()
