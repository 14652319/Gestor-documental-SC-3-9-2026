"""
Script simple para depurar nombres de columnas del Excel
"""
import polars as pl
import pandas as pd
from pathlib import Path

# Путь al archivo del usuario
archivo = r"C:\Users\Usuario\Downloads\Ricardo\Dian.xlsx"

print("=" * 80)
print("🔍 DEPURACIÓN DE COLUMNAS DEL EXCEL")
print("=" * 80)

# 1. Leer con Polars
print("\n📖 PASO 1: Leer con Polars...")
df_polars = pl.read_excel(archivo, infer_schema_length=0)
print(f"✅ Total de columnas: {len(df_polars.columns)}")
print(f"✅ Total de filas: {df_polars.height}")

print("\n📋 COLUMNAS ORIGINALES (Polars):")
for i, col in enumerate(df_polars.columns, 1):
    print(f"  {i:2d}. [{repr(col)}] - Tipo: {df_polars[col].dtype}")

# 2. Normalizar columnas (como hace read_csv)
print("\n⚙️ PASO 2: Normalizar columnas (strip + lower)...")
df_norm = df_polars.rename({c: c.strip().lower() for c in df_polars.columns})

print("\n📋 COLUMNAS NORMALIZADAS (Polars):")
for i, col in enumerate(df_norm.columns, 1):
    print(f"  {i:2d}. [{repr(col)}]")

# 3. Convertir a Pandas
print("\n⚙️ PASO 3: Convertir a Pandas...")
df_pandas = df_norm.to_pandas()

print("\n📋 COLUMNAS EN PANDAS:")
for i, col in enumerate(df_pandas.columns, 1):
    print(f"  {i:2d}. [{repr(col)}]")

# 4. Verificar si 'fecha emisión' (CON ACENTO) existe
print("\n🔍 VERIFICANDO BÚSQUEDAS DE COLUMNAS:")
print(f"  ✓ 'fecha emisión' (CON ACENTO) en Pandas columns: {'fecha emisión' in df_pandas.columns}")
print(f"  ✓ 'fecha emision' (SIN ACENTO) en Pandas columns: {'fecha emision' in df_pandas.columns}")
print(f"  ✓ 'total' en Pandas columns: {'total' in df_pandas.columns}")
print(f"  ✓ 'valor' en Pandas columns: {'valor' in df_pandas.columns}")

# 5. Buscar columnas que contengan "fecha" o "emis"
print("\n🔍 COLUMNAS QUE CONTIENEN 'fecha' o 'emis':")
for col in df_pandas.columns:
    if 'fecha' in col.lower() or 'emis' in col.lower():
        print(f"  → {repr(col)}")

print("\n🔍 COLUMNAS QUE CONTIENEN 'total' o 'valor':")
for col in df_pandas.columns:
    if 'total' in col.lower() or 'valor' in col.lower():
        print(f"  → {repr(col)}")

# 6. Probar acceso a primera fila
if len(df_pandas) > 0:
    print("\n📄 MUESTRA DE PRIMERA FILA:")
    row = df_pandas.iloc[0]
    
    print("\n  Intentando leer con row.get():")
    fecha_con_acento = row.get('fecha emisión', 'NO_ENCONTRADO')
    fecha_sin_acento = row.get('fecha emision', 'NO_ENCONTRADO')
    total_val = row.get('total', 'NO_ENCONTRADO')
    valor_val = row.get('valor', 'NO_ENCONTRADO')
    
    print(f"    row.get('fecha emisión'): {fecha_con_acento}")
    print(f"    row.get('fecha emision'): {fecha_sin_acento}")
    print(f"    row.get('total'): {total_val}")
    print(f"    row.get('valor'): {valor_val}")

print("\n" + "=" * 80)
print("✅ DEPURACIÓN COMPLETADA")
print("=" * 80)
