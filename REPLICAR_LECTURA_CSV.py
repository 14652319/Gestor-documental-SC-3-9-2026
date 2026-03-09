"""
Replicar EXACTAMENTE el proceso de lectura del CSV
"""
import polars as pl
import pandas as pd
from datetime import date, datetime
from pathlib import Path

print("=" * 80)
print("🔍 REPLICANDO LECTURA EXACTA DEL CSV")
print("=" * 80)

# Ruta al CSV
csv_path = Path("uploads/dian/Dian_922e8ffff1.csv")

print(f"\n📁 Archivo: {csv_path}")
print(f"   Existe: {csv_path.exists()}")
print()

# 1. Leer con Polars (como hace read_csv)
print("📖 PASO 1: Leer con Polars...")
d = pl.read_csv(str(csv_path), infer_schema_length=0, ignore_errors=True, null_values=["", " "])
print(f"   ✅ Columnas: {len(d.columns)}")
print(f"   ✅ Filas: {d.height}")

# 2. Normalizar columnas (como hace read_csv)
print("\n⚙️ PASO 2: Normalizar columnas...")
d_norm = d.rename({c: c.strip().lower() for c in d.columns})
print(f"   ✅ Primeras 10 columnas normalizadas:")
for i, col in enumerate(d_norm.columns[:10], 1):
    print(f"      {i:2d}. {repr(col)}")

# 3. Verificar si 'fecha emisión' existe
print("\n🔍 PASO 3: Verificar columna de fecha...")
fecha_col_exists = 'fecha emisión' in d_norm.columns
print(f"   'fecha emisión' existe: {fecha_col_exists}")

if not fecha_col_exists:
    print("\n   🔍 Buscando columnas que contengan 'fecha' o 'emis':")
    for col in d_norm.columns:
        if 'fecha' in col or 'emis' in col:
            print(f"      → {repr(col)}")

# 4. Convertir a Pandas
print("\n⚙️ PASO 4: Convertir a Pandas...")
d_pd = d_norm.to_pandas()

# 5. Procesar primeras 5 filas
print("\n📊 PASO 5: Procesando primeras 5 filas like routes.py hace...\n")

for idx, row in d_pd.head(5).iterrows():
    print(f"   FILA {idx + 1}:")
    
    # Extraer fecha EXACTAMENTE como lo hace el código
    fecha_emision_raw = row.get('fecha emisión', row.get('fecha emisiã³n', row.get('fecha emision', row.get('fecha_emision', date.today()))))
    
    print(f"      fecha_emision_raw = {repr(fecha_emision_raw)} (tipo: {type(fecha_emision_raw).__name__})")
    
    if isinstance(fecha_emision_raw, str):
        print(f"      Es string, procesando...")
        try:
            # Lógica del código arreglado
            if '-' in fecha_emision_raw:
                partes = fecha_emision_raw.split('-')
                if len(partes[0]) == 4:  # año-mes-día
                    fecha_emision = datetime.strptime(fecha_emision_raw, '%Y-%m-%d').date()
                    print(f"      → Formato año-mes-día: {fecha_emision}")
                else:  # día-mes-año
                    fecha_emision = datetime.strptime(fecha_emision_raw, '%d-%m-%Y').date()
                    print(f"      → Formato día-mes-año: {fecha_emision}")
            else:
                fecha_emision = date.today()
                print(f"      → Sin guiones, usando hoy: {fecha_emision}")
        except Exception as e:
            fecha_emision = date.today()
            print(f"      → ERROR: {e}, usando hoy: {fecha_emision}")
    else:
        fecha_emision = fecha_emision_raw
        print(f"      → Ya es date: {fecha_emision}")
    
    print()

print("=" * 80)
