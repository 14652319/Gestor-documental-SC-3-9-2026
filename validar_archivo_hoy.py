"""
Probar carga del archivo REAL subido hoy (23/02/2026 13:25)
Ubicación CORRECTA: uploads\dian\Dian.xlsx
"""
import pandas as pd
import unicodedata
import re
import os

archivo_real = r"uploads\dian\Dian.xlsx"

print("="*80)
print("📂 VALIDACIÓN DE ARCHIVO REAL SUBIDO HOY")
print("="*80)

# Verificar existencia
if not os.path.exists(archivo_real):
    print(f"❌ ERROR: Archivo no encontrado en: {archivo_real}")
    print("\n🔍 Buscando en rutas alternativas...")
    
    # Buscar en otras ubicaciones posibles
    rutas = [
        r"D:\0.1. Backup Equipo Contablilidad\Gestor Documental\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059\uploads\dian\Dian.xlsx",
        r"uploads\dian\Dian.xlsx",
        r"modules\dian_vs_erp\uploads\dian\Dian.xlsx"
    ]
    
    for ruta in rutas:
        if os.path.exists(ruta):
            print(f"✅ Encontrado en: {ruta}")
            archivo_real = ruta
            break
    else:
        print("❌ No se encontró el archivo en ninguna ubicación")
        exit(1)

print(f"✅ Archivo: {archivo_real}")
print(f"📊 Tamaño: {os.path.getsize(archivo_real) / 1024:.2f} KB")
print(f"📅 Modificado: {pd.Timestamp.fromtimestamp(os.path.getmtime(archivo_real))}")

# PASO 1: Leer con pandas (primeras 3 filas para ser rápido)
print(f"\n{'='*80}")
print("PASO 1: Leer Excel con pandas")
print("="*80)
df = pd.read_excel(archivo_real, dtype=str, nrows=3)
print(f"✅ Leído: {len(df)} filas, {len(df.columns)} columnas")

# PASO 2: Normalizar a lowercase (como hace read_csv línea 288)
print(f"\nPASO 2: Normalizar a lowercase")
print("="*80)
df_lower = df.rename(columns={c: c.strip().lower() for c in df.columns})
print(f"Primeras columnas: {list(df_lower.columns[:8])}")

# PASO 3: Crear diccionario (como hace actualizar_maestro)
print(f"\nPASO 3: Crear diccionario columnas_originales")
print("="*80)

def normalizar_columna(nombre):
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

print("Mapeo para columnas críticas:")
for key in ['prefijo', 'folio', 'fecha_emision', 'total']:
    val = columnas_originales.get(key, 'NO ENCONTRADO')
    print(f"   '{key}' → '{val}'")

# PASO 4: Leer primera fila
print(f"\nPASO 4: Leer valores de primera fila")
print("="*80)
row = df_lower.iloc[0]

def extraer_prefijo(docto: str) -> str:
    if not docto:
        return ""
    prefijo = re.sub(r'[\-\.\s]', '', str(docto)).strip().upper()
    if len(prefijo) > 20:
        if re.match(r'^[A-F0-9]+$', prefijo) and len(prefijo) > 20:
            return ""
        return prefijo[:20]
    return prefijo

def extraer_folio(docto: str) -> str:
    if not docto:
        return ""
    return re.sub(r'[^0-9]', '', str(docto))

def ultimos_8_sin_ceros(folio: str) -> str:
    if not folio:
        return "0"
    numeros = re.sub(r'[^0-9]', '', str(folio))
    if not numeros:
        return "0"
    ultimos = numeros[-8:] if len(numeros) >= 8 else numeros
    return ultimos.lstrip('0') or '0'

# Prefijo
prefijo_col = columnas_originales.get('prefijo', 'Prefijo')
prefijo_raw = str(row.get(prefijo_col, ''))
prefijo_final = extraer_prefijo(prefijo_raw)
print(f"Prefijo:")
print(f"   Columna: '{prefijo_col}'")
print(f"   Valor raw: '{prefijo_raw}'")
print(f"   Valor final: '{prefijo_final}'")
print(f"   Estado: {'❌ NULL' if prefijo_final == '' else '✅ OK'}")

# Folio
folio_col = columnas_originales.get('folio', 'Folio')
folio_raw = str(row.get(folio_col, ''))
folio_temp = extraer_folio(folio_raw)
folio_final = ultimos_8_sin_ceros(folio_temp)
print(f"\nFolio:")
print(f"   Columna: '{folio_col}'")
print(f"   Valor raw: '{folio_raw}'")
print(f"   Valor temp: '{folio_temp}'")
print(f"   Valor final: '{folio_final}'")
print(f"   Estado: {'❌ CERO' if folio_final == '0' else '✅ OK'}")

# Total
total_col = columnas_originales.get('total')
if total_col and total_col in df_lower.columns:
    total_raw = row.get(total_col, '')
    print(f"\nTotal:")
    print(f"   Columna: '{total_col}'")
    print(f"   Valor raw: '{total_raw}'")
    print(f"   Estado: {'❌ VACÍO' if total_raw == '' else '✅ OK'}")
else:
    print(f"\nTotal:")
    print(f"   ❌ Columna NO encontrada en diccionario")

# Fecha Emisión
fecha_col = columnas_originales.get('fecha_emision')
if fecha_col and fecha_col in df_lower.columns:
    fecha_raw = row.get(fecha_col, '')
    print(f"\nFecha Emisión:")
    print(f"   Columna: '{fecha_col}'")
    print(f"   Valor raw: '{fecha_raw}'")
    print(f"   Estado: {'❌ VACÍO' if fecha_raw == '' else '✅ OK'}")
else:
    print(f"\nFecha Emisión:")
    print(f"   ❌ Columna NO encontrada en diccionario")

print(f"\n{'='*80}")
print("CONCLUSIÓN")
print("="*80)

if prefijo_final != '' and folio_final != '0':
    print("✅ LOS DATOS SE LEERÍAN CORRECTAMENTE")
    print(f"   Prefijo: {prefijo_final}")
    print(f"   Folio: {folio_final}")
else:
    print("❌ HAY UN PROBLEMA EN LA LECTURA")
    if prefijo_final == '':
        print("   - Prefijo está vacío")
    if folio_final == '0':
        print("   - Folio está en cero")
print("="*80)
