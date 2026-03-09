"""
Leer el CSV procesado y mostrar columnas y primeras filas
"""
import polars as pl
import pandas as pd

archivo_csv = r"uploads\dian\Dian_bc63e290ca.csv"

print("=" * 80)
print("🔍 ANÁLISIS DEL ARCHIVO CSV GUARDADO")
print("=" * 80)

# 1. Leer CSV con Polars (como lo hace read_csv)
print("\n📖 PASO 1: Leer CSV con Polars...")
df = pl.read_csv(archivo_csv, infer_schema_length=0, ignore_errors=True, null_values=["", " "])
print(f"✅ Total de columnas: {len(df.columns)}")
print(f"✅ Total de filas: {df.height}")

print("\n📋 COLUMNAS ORIGINALES (Polars):")
for i, col in enumerate(df.columns[:15], 1):  # Primeras 15 columnas
    print(f"  {i:2d}. [{repr(col)}]")

# 2. Normalizar columnas (como hace read_csv)
print("\n⚙️ PASO 2: Normalizar columnas (strip + lower)...")
df_norm = df.rename({c: c.strip().lower() for c in df.columns})

print("\n📋 COLUMNAS NORMALIZADAS (Polars):")
for i, col in enumerate(df_norm.columns[:15], 1):  # Primeras 15 columnas
    print(f"  {i:2d}. [{repr(col)}]")

# 3. Verificar si 'fecha emisión' y 'total' existen
print("\n🔍 VERIFICANDO COLUMNAS CLAVE:")
print(f"  ✓ 'fecha emisión' (CON  ACENTO) existe: {'fecha emisión' in df_norm.columns}")
print(f"  ✓ 'fecha emision' (SIN ACENTO) existe: {'fecha emision' in df_norm.columns}")
print(f"  ✓ 'total' existe: {'total' in df_norm.columns}")
print(f"  ✓ 'valor' existe: {'valor' in df_norm.columns}")

# 4. Buscar columnas que contengan "fecha" o "emis"
print("\n🔍 TODAS LAS COLUMNAS QUE CONTIENEN 'fecha' o 'emis':")
for col in df_norm.columns:
    if 'fecha' in col.lower() or 'emis' in col.lower():
        print(f"  → {repr(col)}")

print("\n🔍 TODAS LAS COLUMNAS QUE CONTIENEN 'total' o 'valor':")
for col in df_norm.columns:
    if 'total' in col.lower() or 'valor' in col.lower():
        print(f"  → {repr(col)}")

# 5. Convertir a Pandas y mostrar primeras filas
print("\n⚙️ PASO 3: Convertir a Pandas...")
df_pd = df_norm.to_pandas()

print("\n📄 PRIMERAS 3 FILAS (columnas de interés):")
for idx, row in df_pd.head(3).iterrows():
    print(f"\n  FILA {idx + 1}:")
    print(f"    NIT: {row.get('nit emisor', 'NO_ENCONTRADO')}")
    print(f"    Prefijo: {row.get('prefijo', 'NO_ENCONTRADO')}")
    print(f"    Folio: {row.get('numero', row.get('folio', 'NO_ENCONTRADO'))}")
    print(f"    row.get('fecha emisión'): {row.get('fecha emisión', 'NO_ENCONTRADO')}")
    print(f"    row.get('fecha emision'): {row.get('fecha emision', 'NO_ENCONTRADO')}")
    print(f"    row.get('total'): {row.get('total', 'NO_ENCONTRADO')}")
    print(f"    row.get('valor'): {row.get('valor', 'NO_ENCONTRADO')}")

print("\n" + "=" * 80)
print("✅ ANÁLISIS COMPLETADO")
print("=" * 80)
