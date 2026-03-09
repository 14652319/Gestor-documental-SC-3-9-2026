"""
Diagnóstico rápido: ¿Por qué Prefijo y Folio salen NULL/0?
Basado en el mapeo del usuario
"""
import polars as pl
import pandas as pd
import unicodedata

archivo = r"C:\Users\Usuario\Downloads\Ricardo\Dian.xlsx"

print("\n" + "="*80)
print("🔍 DIAGNÓSTICO: Lectura de columnas DIAN")
print("="*80)

# Leer solo 3 filas para ser rápido
print("\n1️⃣ Leyendo Excel (primeras 3 filas)...")
try:
    df_polars = pl.read_excel(archivo, engine='calamine', read_options={'n_rows': 3})
    print("   Método: Polars con calamine")
except Exception as e:
    print(f"   ⚠️  Calamine falló, usando pandas como fallback...")
    # Fallback a pandas (como hace routes.py línea 265)
    pdf = pd.read_excel(archivo, dtype=str, nrows=3)
    df_polars = pl.from_pandas(pdf)
    print("   Método: Pandas → Polars")

print(f"\n✅ Leído: {len(df_polars)} filas")
print(f"📋 Columnas ORIGINALES (sin normalizar):")
for i, col in enumerate(df_polars.columns[:15], 1):
    print(f"   {i:2}. '{col}' (tipo: {df_polars[col].dtype})")

# PASO 1: Normalizar a lowercase (como hace read_csv línea 288)
print(f"\n{'='*80}")
print("PASO 1: Normalizar a lowercase (strip + lower)")
print("="*80)
df_lower = df_polars.rename({c: c.strip().lower() for c in df_polars.columns})
print(f"\n📋 Columnas DESPUÉS de .lower():")
for i, col in enumerate(df_lower.columns[:15], 1):
    print(f"   {i:2}. '{col}'")

# PASO 2: Convertir a Pandas y crear diccionario (como hace actualizar_maestro línea 2150)
print(f"\n{'='*80}")
print("PASO 2: Crear diccionario columnas_originales")
print("="*80)

d_pd = df_lower.to_pandas()

def normalizar_columna(nombre):
    """Normaliza nombre: lowercase, sin tildes, espacios→guion bajo"""
    sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', str(nombre))
        if unicodedata.category(c) != 'Mn'
    )
    return sin_tildes.lower().strip().replace(' ', '_')

columnas_originales = {}
for col in d_pd.columns:
    col_norm = normalizar_columna(col)
    columnas_originales[col_norm] = col
    columnas_originales[col_norm.replace('_', '')] = col

print(f"\n📋 Diccionario columnas_originales (primeras 20 entradas):")
for i, (key, val) in enumerate(columnas_originales.items(), 1):
    print(f"   {i:2}. '{key}' → '{val}'")
    if i >= 20:
        break

# PASO 3: Buscar columnas críticas (como hace el código línea 2263-2264)
print(f"\n{'='*80}")
print("PASO 3: Buscar columnas críticas en diccionario")
print("="*80)

buscar = {
    'prefijo': 'Prefijo',
    'folio': 'Folio', 
    'fecha_emision': 'Fecha Emisión',
    'total': 'Total'
}

for clave, esperado in buscar.items():
    col_encontrada = columnas_originales.get(clave, 'Prefijo' if clave == 'prefijo' else 'Folio' if clave == 'folio' else None)
    print(f"\n🔎 Buscando '{clave}' (debería ser '{esperado}'):")
    print(f"   columnas_originales.get('{clave}') = '{col_encontrada}'")
    
    if col_encontrada and col_encontrada in d_pd.columns:
        print(f"   ✅ Columna existe en DataFrame")
        print(f"   📊 Primer valor: {d_pd[col_encontrada].iloc[0]}")
    elif col_encontrada:
        print(f"   ❌ Columna NO existe en DataFrame")
        print(f"   📋 Columnas disponibles: {list(d_pd.columns[:10])}")
    else:
        print(f"   ❌ NO encontrado en diccionario")

# PASO 4: Simular la lectura como hace el código (línea 2263-2264)
print(f"\n{'='*80}")
print("PASO 4: Simular lectura como hace routes.py")
print("="*80)

row = d_pd.iloc[0]  # Primera fila
print(f"\n📊 Primera fila del DataFrame:")

# Prefijo
prefijo_raw = str(row.get(columnas_originales.get('prefijo', 'Prefijo'), ''))
print(f"\n   prefijo_raw = str(row.get(columnas_originales.get('prefijo', 'Prefijo'), ''))")
print(f"   prefijo_raw = '{prefijo_raw}'")
if prefijo_raw == '':
    print(f"   ❌ VACÍO - Por eso sale NULL en la base de datos")
else:
    print(f"   ✅ Tiene valor")

# Folio
folio_raw = str(row.get(columnas_originales.get('folio', 'Folio'), ''))
print(f"\n   folio_raw = str(row.get(columnas_originales.get('folio', 'Folio'), ''))")
print(f"   folio_raw = '{folio_raw}'")
if folio_raw == '':
    print(f"   ❌ VACÍO - Por eso sale '0' en la base de datos")
else:
    print(f"   ✅ Tiene valor")

# Fecha Emisión
fecha_key = columnas_originales.get('fecha_emision')
if fecha_key:
    fecha_raw = row.get(fecha_key)
    print(f"\n   fecha_emision_raw = row.get('{fecha_key}')")
    print(f"   fecha_emision_raw = '{fecha_raw}'")
else:
    print(f"\n   ❌ 'fecha_emision' NO encontrado en diccionario")

print("\n" + "="*80)
print("✅ DIAGNÓSTICO COMPLETADO")
print("="*80)
