"""
COMPARACIÓN DE VALORES CUFE ENTRE DIAN Y ACUSES
================================================
Verifica si los CUFEs en los archivos coinciden
"""

import pandas as pd
from pathlib import Path

print("=" * 80)
print("COMPARACIÓN DE VALORES CUFE")
print("=" * 80)

# Rutas de archivos
dian_file = Path("uploads/dian/Dian.xlsx")
acuses_file = Path("uploads/acuses/acuses_2.xlsx")

print(f"\n📂 Archivos:")
print(f"   DIAN: {dian_file}")
print(f"   ACUSES: {acuses_file}")

# Leer solo las primeras 1000 filas para velocidad
print(f"\n📊 Leyendo primeras 1000 filas de cada archivo...")
dian_df = pd.read_excel(dian_file, nrows=1000)
acuses_df = pd.read_excel(acuses_file, nrows=1000)

print(f"   DIAN: {len(dian_df)} filas, {len(dian_df.columns)} columnas")
print(f"   ACUSES: {len(acuses_df)} filas, {len(acuses_df.columns)} columnas")

# Detectar columnas de CUFE
print(f"\n🔍 Detectando columnas de CUFE...")

# DIAN: buscar "CUFE/CUDE" o similares
cufe_dian_col = None
for col in dian_df.columns:
    col_lower = col.lower().strip()
    if 'cufe' in col_lower or 'cude' in col_lower:
        cufe_dian_col = col
        print(f"   ✅ DIAN: '{col}'")
        break

# ACUSES: buscar "CUFE"
cufe_acuses_col = None
for col in acuses_df.columns:
    col_lower = col.lower().strip()
    if 'cufe' in col_lower or 'cude' in col_lower:
        cufe_acuses_col = col
        print(f"   ✅ ACUSES: '{col}'")
        break

if not cufe_dian_col or not cufe_acuses_col:
    print(f"\n❌ ERROR: No se encontraron columnas de CUFE")
    exit(1)

# Extraer CUFEs
print(f"\n📋 Extrayendo CUFEs...")
cufes_dian = set()
for cufe in dian_df[cufe_dian_col]:
    cufe_str = str(cufe).strip().upper()
    if cufe_str and cufe_str != 'NAN' and len(cufe_str) > 10:
        cufes_dian.add(cufe_str)

cufes_acuses = set()
for cufe in acuses_df[cufe_acuses_col]:
    cufe_str = str(cufe).strip().upper()
    if cufe_str and cufe_str != 'NAN' and len(cufe_str) > 10:
        cufes_acuses.add(cufe_str)

print(f"   DIAN: {len(cufes_dian):,} CUFEs únicos")
print(f"   ACUSES: {len(cufes_acuses):,} CUFEs únicos")

# Comparar
coincidencias = cufes_dian.intersection(cufes_acuses)
solo_dian = cufes_dian - cufes_acuses
solo_acuses = cufes_acuses - cufes_dian

print(f"\n🎯 RESULTADOS:")
print(f"   Coincidencias: {len(coincidencias):,}")
print(f"   Solo en DIAN: {len(solo_dian):,}")
print(f"   Solo en ACUSES: {len(solo_acuses):,}")

if len(coincidencias) > 0:
    porcentaje_dian = (len(coincidencias) / len(cufes_dian)) * 100
    porcentaje_acuses = (len(coincidencias) / len(cufes_acuses)) * 100
    print(f"\n📊 PORCENTAJES:")
    print(f"   {porcentaje_dian:.1f}% de DIAN tiene match en ACUSES")
    print(f"   {porcentaje_acuses:.1f}% de ACUSES tiene match en DIAN")

# Mostrar ejemplos
print(f"\n📝 EJEMPLOS:")

if len(coincidencias) > 0:
    print(f"\n✅ CUFE con coincidencia (primeros 3):")
    for i, cufe in enumerate(list(coincidencias)[:3], 1):
        print(f"   {i}. {cufe[:60]}...")

if len(solo_dian) > 0:
    print(f"\n❌ CUFE solo en DIAN (primeros 3):")
    for i, cufe in enumerate(list(solo_dian)[:3], 1):
        print(f"   {i}. {cufe[:60]}...")

if len(solo_acuses) > 0:
    print(f"\n❌ CUFE solo en ACUSES (primeros 3):")
    for i, cufe in enumerate(list(solo_acuses)[:3], 1):
        print(f"   {i}. {cufe[:60]}...")

# Verificar normalización
print(f"\n🔧 VERIFICANDO NORMALIZACIÓN:")
print(f"   Extrayendo primera muestra de cada archivo...")

# Primera muestra de DIAN
primer_cufe_dian = None
for cufe in dian_df[cufe_dian_col]:
    if str(cufe).strip() and str(cufe).strip().upper() != 'NAN':
        primer_cufe_dian = cufe
        break

# Primera muestra de ACUSES
primer_cufe_acuses = None
for cufe in acuses_df[cufe_acuses_col]:
    if str(cufe).strip() and str(cufe).strip().upper() != 'NAN':
        primer_cufe_acuses = cufe
        break

if primer_cufe_dian:
    original = str(primer_cufe_dian)
    normalizado = original.strip().upper()
    print(f"\n   DIAN - Primer CUFE:")
    print(f"      Original: '{original}'")
    print(f"      Longitud original: {len(original)}")
    print(f"      Normalizado: '{normalizado}'")
    print(f"      Longitud normalizado: {len(normalizado)}")
    print(f"      Tiene espacios: {' ' in original}")
    print(f"      Tiene saltos línea: {'\\n' in original or '\\r' in original}")

if primer_cufe_acuses:
    original = str(primer_cufe_acuses)
    normalizado = original.strip().upper()
    print(f"\n   ACUSES - Primer CUFE:")
    print(f"      Original: '{original}'")
    print(f"      Longitud original: {len(original)}")
    print(f"      Normalizado: '{normalizado}'")
    print(f"      Longitud normalizado: {len(normalizado)}")
    print(f"      Tiene espacios: {' ' in original}")
    print(f"      Tiene saltos línea: {'\\n' in original or '\\r' in original}")

print(f"\n" + "=" * 80)
print("DIAGNÓSTICO:")
print("=" * 80)

if len(coincidencias) == 0:
    print("""
❌ NO HAY COINCIDENCIAS EN LAS PRIMERAS 1000 FILAS

Causas posibles:
1. Los archivos son de DIFERENTES PERÍODOS O EMPRESAS
2. Los CUFEs están en formato diferente (case, espacios)
3. Los archivos no corresponden entre sí

SOLUCIÓN:
- Verificar que ambos archivos sean del mismo período
- Verificar que sean de la misma empresa (NIT)
- Revisar si hay normalización de mayúsculas/minúsculas
""")
elif len(coincidencias) < len(cufes_acuses) * 0.5:
    print(f"""
⚠️ COINCIDENCIAS BAJAS ({len(coincidencias):,} de {len(cufes_acuses):,})

Los archivos tienen ALGUNA superposición pero no mucha.

SOLUCIÓN:
- Verificar períodos de los archivos
- Puede ser normal si acuses cubre período más amplio
""")
else:
    print(f"""
✅ BUENAS COINCIDENCIAS ({len(coincidencias):,} de {len(cufes_acuses):,})

Los archivos SÍ corresponden. Si el sistema muestra "No Registra",
el problema está en el código de matching (línea 1600 de routes.py).

SOLUCIÓN:
- Verificar normalización en línea 1600
- Verificar que se use .strip() y .upper() consistentemente
""")

print("=" * 80)
