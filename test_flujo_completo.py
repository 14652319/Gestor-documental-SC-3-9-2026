"""
Test COMPLETO del flujo: Excel → DataFrame → Diccionario → Extracción
"""
import pandas as pd
import unicodedata
import re

archivo = r"C:\Users\Usuario\Downloads\Ricardo\Dian.xlsx"

# PASO 1: Leer Excel (como hace routes.py línea 265)
print("="*80)
print("PASO 1: Leer Excel con pandas + fallback")
print("="*80)
df = pd.read_excel(archivo, dtype=str, nrows=3)
print(f"✅ Leído: {len(df)} filas")

# PASO 2: Normalizar a lowercase (como hace read_csv línea 288)
print("\nPASO 2: Normalizar columnas a lowercase")
print("="*80)
df_lower = df.rename(columns={c: c.strip().lower() for c in df.columns})
print(f"Primeras columnas: {list(df_lower.columns[:10])}")

# PASO 3: Crear diccionario columnas_originales (como hace actualizar_maestro línea 2150)
print("\nPASO 3: Crear diccionario columnas_originales")
print("="*80)

def normalizar_columna(nombre):
    """Normaliza nombre: lowercase, sin tildes, espacios→guion bajo"""
    sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', str(nombre))
        if unicodedata.category(c) != 'Mn'
    )
    return sin_tildes.lower().strip().replace(' ', '_')

columnas_originales = {}
for col in df_lower.columns:
    col_norm = normalizar_columna(col)
    columnas_originales[col_norm] = col
    columnas_originales[col_norm.replace('_', '')] = col

print(f"Entradas para columnas críticas:")
for key in ['prefijo', 'folio', 'fecha_emision', 'total']:
    val = columnas_originales.get(key)
    print(f"   columnas_originales['{key}'] = '{val}'")

# PASO 4: Simular lectura de primera fila (como hace línea 2262-2265)
print("\nPASO 4: Simular lectura de primera fila")
print("="*80)
row = df_lower.iloc[0]

# Prefijo
print("\n🔍 PREFIJO:")
key_prefijo = columnas_originales.get('prefijo', 'Prefijo')
print(f"   1. columnas_originales.get('prefijo', 'Prefijo') = '{key_prefijo}'")
val_prefijo = row.get(key_prefijo, '')
print(f"   2. row.get('{key_prefijo}', '') = '{val_prefijo}'")
prefijo_raw = str(val_prefijo)
print(f"   3. str(val) = '{prefijo_raw}'")

# Folio  
print("\n🔍 FOLIO:")
key_folio = columnas_originales.get('folio', 'Folio')
print(f"   1. columnas_originales.get('folio', 'Folio') = '{key_folio}'")
val_folio = row.get(key_folio, '')
print(f"   2. row.get('{key_folio}', '') = '{val_folio}'")
folio_raw = str(val_folio)
print(f"   3. str(val) = '{folio_raw}'")

# PASO 5: Aplicar funciones de extracción (como hace línea 2263-2266)
print("\nPASO 5: Aplicar funciones extraer_prefijo() y extraer_folio()")
print("="*80)

def extraer_prefijo(docto: str) -> str:
    """Extrae prefijo alfanumérico (letras Y números), limpiando solo guiones y puntos"""
    if not docto:
        return ""
    import re
    prefijo = re.sub(r'[\-\.\s]', '', str(docto)).strip().upper()
    if len(prefijo) > 20:
        if re.match(r'^[A-F0-9]+$', prefijo) and len(prefijo) > 20:
            return ""
        return prefijo[:20]
    return prefijo

def extraer_folio(docto: str) -> str:
    """Extrae solo DÍGITOS del documento"""
    if not docto:
        return ""
    import re
    return re.sub(r'[^0-9]', '', str(docto))

def ultimos_8_sin_ceros(folio: str) -> str:
    """Últimos 8 dígitos sin ceros a la izquierda"""
    if not folio:
        return "0"
    import re
    numeros = re.sub(r'[^0-9]', '', str(folio))
    if not numeros:
        return "0"
    ultimos = numeros[-8:] if len(numeros) >= 8 else numeros
    return ultimos.lstrip('0') or '0'

# Aplicar
prefijo_final = extraer_prefijo(prefijo_raw)
print(f"\n   extraer_prefijo('{prefijo_raw}') = '{prefijo_final}'")
if prefijo_final == '':
    print(f"   ❌ VACÍO - se guardará como NULL en BD")
else:
    print(f"   ✅ Tiene valor - se guardará en BD")

folio_temp = extraer_folio(folio_raw)
folio_final = ultimos_8_sin_ceros(folio_temp)
print(f"\n   extraer_folio('{folio_raw}') = '{folio_temp}'")
print(f"   ultimos_8_sin_ceros('{folio_temp}') = '{folio_final}'")
if folio_final == '0':
    print(f"   ❌ Es '0' - se guardará como '0' en BD")
else:
    print(f"   ✅ Tiene valor - se guardará en BD")

# RESULTADO FINAL
print("\n" + "="*80)
print("RESULTADO FINAL (lo que se insertaría en BD):")
print("="*80)
print(f"   Prefijo: '{prefijo_final}' {'❌ NULL' if prefijo_final == '' else '✅ OK'}")
print(f"   Folio: '{folio_final}' {'❌ CERO' if folio_final == '0' else '✅ OK'}")
print("="*80)
