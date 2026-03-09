"""
Simulación EXACTA del proceso de routes.py para detectar el bug
"""
import polars as pl
import pandas as pd
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("SIMULACIÓN EXACTA DEL PROCESO DE ROUTES.PY")
print("=" * 80)

# 1. Leer archivo como POLARS (igual que routes.py)
archivo = r'uploads\dian\Dian.xlsx'
print(f"\n📂 PASO 1: Leer con Polars")
print(f"   Archivo: {archivo}")

try:
    d = pl.read_excel(archivo, read_csv_options={'n_rows': 100})
    print(f"   ✅ Polars: {d.shape[0]} filas, {d.shape[1]} columnas")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# 2. Convertir a Pandas (línea 1415 de routes.py)
print(f"\n📂 PASO 2: Convertir a Pandas")
d_pd = d.to_pandas()
print(f"   ✅ Pandas: {len(d_pd)} filas, {len(d_pd.columns)} columnas")

# 3. Mostrar columnas después de conversión
print(f"\n📋 PASO 3: Columnas en Pandas después de Polars:")
for i, col in enumerate(d_pd.columns, 1):
    print(f"   {i:2d}. '{col}' (tipo: {type(col).__name__})")

# 4. Normalizar columnas (líneas 1421-1451 de routes.py)
print(f"\n🔄 PASO 4: Normalización")

def normalizar_columna(nombre):
    """EXACTAMENTE como routes.py línea 1423"""
    # Quitar tildes
    sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', str(nombre))
        if unicodedata.category(c) != 'Mn'
    )
    # Lowercase y espacios→guion bajo
    return sin_tildes.lower().strip().replace(' ', '_')

columnas_originales = {}
for col in d_pd.columns:
    col_norm = normalizar_columna(col)
    columnas_originales[col_norm] = col
    # Agregar variante sin guion bajo (línea 1451)
    columnas_originales[col_norm.replace('_', '')] = col
    
    if 'cufe' in col_norm or 'cude' in col_norm:
        print(f"   ✅ '{col}' → '{col_norm}'")
        print(f"      columnas_originales['{col_norm}'] = '{col}'")
        print(f"      columnas_originales['{col_norm.replace('_', '')}'] = '{col}'")

# 5. Buscar CUFE (EXACTAMENTE como línea 1584)
print(f"\n🔍 PASO 5: Buscar CUFE (línea 1584)")
print(f"   Código: cufe = str(row.get(columnas_originales.get('cufe_cude', 'CUFE/CUDE'), ''))")

# ¿Qué devuelve columnas_originales.get('cufe_cude', 'CUFE/CUDE')?
col_a_buscar = columnas_originales.get('cufe_cude', 'CUFE/CUDE')
print(f"\n   ➡️  columnas_originales.get('cufe_cude', 'CUFE/CUDE') = '{col_a_buscar}'")

# ¿Existe esa columna en el DataFrame?
if col_a_buscar in d_pd.columns:
    print(f"   ✅ La columna '{col_a_buscar}' SÍ existe en el DataFrame")
else:
    print(f"   ❌ La columna '{col_a_buscar}' NO existe en el DataFrame")
    print(f"   ⚠️  Columnas disponibles:")
    for col in d_pd.columns:
        if 'cufe' in col.lower() or 'cude' in col.lower():
            print(f"      - '{col}'")

# 6. Intentar leer valores (EXACTAMENTE como el código)
print(f"\n📖 PASO 6: Leer valores de las primeras 3 filas")
for idx, row in d_pd.head(3).iterrows():
    # EXACTAMENTE como línea 1584
    cufe = str(row.get(columnas_originales.get('cufe_cude', 'CUFE/CUDE'), ''))
    
    if cufe and cufe != '' and cufe != 'nan':
        print(f"   ✅ Fila {idx}: '{cufe[:50]}...' (len={len(cufe)})")
    else:
        print(f"   ❌ Fila {idx}: VACÍO o NaN")
        
        # Diagnóstico adicional
        print(f"      → row.get('{col_a_buscar}', '') = {repr(row.get(col_a_buscar, ''))}")
        print(f"      → Valor directo row['{col_a_buscar}'] = {repr(row[col_a_buscar]) if col_a_buscar in row else 'NO EXISTE'}")

# 7. Diagnóstico final
print(f"\n" + "=" * 80)
print("DIAGNÓSTICO FINAL:")
print("=" * 80)

if col_a_buscar not in d_pd.columns:
    print("❌ PROBLEMA: La columna buscada NO existe en el DataFrame después de Polars → Pandas")
    print("\n   POSIBLE CAUSA: Polars está renombrando las columnas durante la conversión")
    print("\n   SOLUCIÓN: Buscar la columna directamente en d_pd.columns por 'CUFE' en lugar de usar columnas_originales")
else:
    # Ver si el valor viene vacío
    valores_vacios = d_pd[col_a_buscar].isna().sum()
    valores_totales = len(d_pd)
    print(f"✅ La columna existe")
    print(f"   Valores vacíos/NaN: {valores_vacios}/{valores_totales}")
    
    if valores_vacios == valores_totales:
        print(f"\n   ❌ PROBLEMA: TODOS los valores en '{col_a_buscar}' son NaN")
        print(f"   Esto significa que Polars no está leyendo correctamente los valores")
    else:
        print(f"\n   ✅ Hay valores válidos en la columna")

print("=" * 80)
