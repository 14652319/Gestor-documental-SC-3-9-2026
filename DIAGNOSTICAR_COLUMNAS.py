"""
Script para diagnosticar columnas del CSV/Excel cargado
"""
import os
import polars as pl

# Buscar archivo más reciente en uploads/dian
uploads_dir = "uploads/dian"
archivos = [f for f in os.listdir(uploads_dir) if f.endswith(('.csv', '.xlsx', '.xlsm'))]
if not archivos:
    print("❌ No hay archivos en uploads_postgres/dian")
    exit()

archivo_mas_reciente = max(
    [os.path.join(uploads_dir, f) for f in archivos],
    key=os.path.getctime
)

print(f"📁 Archivo: {os.path.basename(archivo_mas_reciente)}")
print(f"📏 Tamaño: {os.path.getsize(archivo_mas_reciente):,} bytes")

# Intentar leer con Polars
ext = os.path.splitext(archivo_mas_reciente)[1].lower()

if ext in ['.xlsx', '.xlsm']:
    print("\n⚡ Leyendo Excel con Polars...")
    try:
        df = pl.read_excel(archivo_mas_reciente, engine='calamine')
        print("✅ Leído con calamine")
    except:
        import pandas as pd
        df_pd = pd.read_excel(archivo_mas_reciente)
        df = pl.from_pandas(df_pd)
        print("✅ Leído con pandas (fallback)")
else:
    print("\n⚡ Leyendo CSV con Polars...")
    df = pl.read_csv(archivo_mas_reciente)

print(f"\n📊 Registros: {df.height:,}")
print(f"📊 Columnas: {df.width}")

print("\n🔍 COLUMNAS DISPONIBLES:")
for i, col in enumerate(df.columns, 1):
    print(f"   {i:2d}. '{col}'")

# Buscar columnas específicas
print("\n🔍 BUSCANDO COLUMNAS CLAVE:")

# Buscar Total/Valor
total_cols = [c for c in df.columns if 'total' in c.lower() or 'valor' in c.lower()]
if total_cols:
    print(f"   💰 Columnas de monto: {total_cols}")
    for col in total_cols:
        print(f"      - Primeros 3 valores de '{col}': {df[col].head(3).to_list()}")
else:
    print("   ❌ NO encontrada columna de Total/Valor")

# Buscar Fecha Emisión
fecha_cols = [c for c in df.columns if 'fecha' in c.lower() and 'emis' in c.lower()]
if fecha_cols:
    print(f"   📅 Columnas de fecha: {fecha_cols}")
    for col in fecha_cols:
        print(f"      - Primeros 3 valores de '{col}': {df[col].head(3).to_list()}")
else:
    print("   ❌ NO encontrada columna de Fecha Emisión")

print("\n✅ Diagnóstico completo")
