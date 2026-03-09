"""
Probar cómo Polars lee el archivo Excel DIAN
"""
import polars as pl
import pandas as pd
import unicodedata

archivo = r"C:\Users\Usuario\Downloads\Ricardo\Dian.xlsx"

print("\n" + "="*80)
print("🧪 PRUEBA: Lectura de Excel con Polars")
print("="*80)

# 1. Leer con Polars (como hace el código actual)
print("\n1️⃣ Lectura con Polars (calamine)...")
try:
    df_polars = pl.read_excel(archivo, engine='calamine', infer_schema_length=1000)
    print(f"✅ Polars leído: {len(df_polars):,} filas, {len(df_polars.columns)} columnas")
    
    print("\n📋 Columnas ORIGINALES de Polars:")
    for i, col in enumerate(df_polars.columns[:15], 1):
        print(f"   {i:2}. '{col}'")
    
    # Normalizar como hace la función read_csv()
    df_polars_norm = df_polars.rename({c: c.strip().lower() for c in df_polars.columns})
    print("\n📋 Columnas DESPUÉS de .lower():")
    for i, col in enumerate(df_polars_norm.columns[:15], 1):
        print(f"   {i:2}. '{col}'")
    
    # Función de normalización del código
    def normalizar_columna(nombre):
        sin_tildes = ''.join(
            c for c in unicodedata.normalize('NFD', str(nombre))
            if unicodedata.category(c) != 'Mn'
        )
        return sin_tildes.lower().strip().replace(' ', '_')
    
    # Crear diccionario como hace el código
    columnas_originales = {}
    d_pd = df_polars_norm.to_pandas()
    for col in d_pd.columns:
        col_norm = normalizar_columna(col)
        columnas_originales[col_norm] = col
        columnas_originales[col_norm.replace('_', '')] = col
    
    print("\n📋 Diccionario columnas_originales (Polars normalizado):")
    for key in list(columnas_originales.keys())[:20]:
        print(f"   '{key}' → '{columnas_originales[key]}'")
    
    # Buscar columnas críticas
    print("\n🔍 BÚSQUEDA en diccionario columnas_originales:")
    buscar = ['prefijo', 'folio', 'total', 'fecha_emision', 'fechaemision']
    for palabra in buscar:
        encontrado = columnas_originales.get(palabra)
        if encontrado:
            print(f"   ✅ '{palabra}' → '{encontrado}'")
        else:
            print(f"   ❌ '{palabra}' NO ENCONTRADO")
    
    # Ver primer registro
    print("\n📊 PRIMER REGISTRO de columnas críticas:")
    row_0 = d_pd.iloc[0]
    for col in ['folio', 'prefijo', 'fecha emisión', 'total', 'nit emisor']:
        if col in d_pd.columns:
            print(f"   '{col}': {row_0[col]}")
        else:
            print(f"   '{col}': ❌ NO EXISTE EN DATAFRAME")
    
except Exception as e:
    print(f"❌ ERROR con Polars: {e}")
    import traceback
    traceback.print_exc()

# 2. Comparar con Pandas
print("\n" + "="*80)
print("2️⃣ Lectura con Pandas (para comparar)...")
try:
    df_pandas = pd.read_excel(archivo, engine='openpyxl', nrows=5)
    print(f"✅ Pandas leído: {len(df_pandas):,} filas")
    
    print("\n📋 Columnas ORIGINALES de Pandas:")
    for i, col in enumerate(df_pandas.columns[:15], 1):
        print(f"   {i:2}. '{col}'")
    
    print("\n📊 PRIMER REGISTRO (Pandas):")
    print(df_pandas[['Folio', 'Prefijo', 'Fecha Emisión', 'Total', 'NIT Emisor']].head(1).to_string())
    
except Exception as e:
    print(f"❌ ERROR con Pandas: {e}")

print("\n" + "="*80)
print("✅ PRUEBA COMPLETADA")
print("="*80)
