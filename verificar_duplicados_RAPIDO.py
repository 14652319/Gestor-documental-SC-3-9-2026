"""
VERIFICAR DUPLICADOS EN EXCEL - VERSIÓN RÁPIDA (solo columna CUFE)
"""
import pandas as pd
import os
from collections import Counter

archivo = r'uploads\dian\Dian_23022026.xlsx'

print("\n" + "="*80)
print("VERIFICANDO DUPLICADOS EN EXCEL DIAN (SOLO COLUMNA CUFE)")
print("="*80)

if not os.path.exists(archivo):
    print(f"\n❌ Archivo no encontrado: {archivo}")
    exit()

print(f"\n📂 Leyendo columnas del Excel...")

# Primero leer solo los headers
df_headers = pd.read_excel(archivo, nrows=0)
columnas = [c.strip().lower().replace(' ', '_').replace('ó', 'o').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ú', 'u') for c in df_headers.columns]

print(f"✅ Columnas detectadas: {len(columnas)}")

# Buscar la columna CUFE
col_cufe_idx = None
col_cufe_name = None
for idx, col in enumerate(columnas):
    if 'cufe' in col or 'cude' in col:
        col_cufe_idx = idx
        col_cufe_name = col
        break

if col_cufe_idx is None:
    print("\n❌ No se encontró columna CUFE/CUDE")
    exit()

print(f"🔍 Columna CUFE encontrada: '{col_cufe_name}' (índice {col_cufe_idx})")
print(f"\n📖 Leyendo SOLO la columna CUFE (más rápido)...")

# Leer SOLO la columna CUFE
df_cufe = pd.read_excel(archivo, usecols=[col_cufe_idx])
col_real = df_cufe.columns[0]

print(f"✅ Leídos {len(df_cufe):,} registros")

# Contar duplicados
cufes = df_cufe[col_real].dropna().astype(str).str.strip()
total_cufes = len(cufes)
cufes_unicos = cufes.nunique()
duplicados = total_cufes - cufes_unicos

print(f"\n📊 RESULTADO:")
print(f"   Total CUFEs: {total_cufes:,}")
print(f"   CUFEs únicos: {cufes_unicos:,}")
print(f"   Duplicados: {duplicados:,}")

if duplicados > 0:
    print(f"\n❌ ¡HAY {duplicados:,} CUFEs DUPLICADOS EN EL EXCEL!")
    
    # Contar repeticiones
    contador = Counter(cufes)
    duplicados_list = [(cufe, count) for cufe, count in contador.items() if count > 1]
    duplicados_list.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n🔍 Primeros 10 CUFEs más repetidos:")
    cufe_error = "929f7761de9ff5fd92865b32d3aabbd4e056589f9cb854c0cfc15a570564f657aba35f6131872b4523c43152f393c793"
    
    for i, (cufe, count) in enumerate(duplicados_list[:10]):
        marca = ""
        if cufe == cufe_error:
            marca = " ⚠️ ¡ESTE ES EL CUFE DEL ERROR!"
        print(f"   {i+1}. {cufe[:50]}... → {count} veces{marca}")
    
    print("\n" + "="*80)
    print("❌ PROBLEMA IDENTIFICADO:")
    print("="*80)
    print("El archivo Excel tiene CUFEs duplicados.")
    print("No puedes cargar este archivo sin limpiarlo primero.")
    print("\n✅ SOLUCIONES:")
    print("1. Eliminar manualmente las facturas duplicadas del Excel")
    print("2. Ejecutar: python limpiar_duplicados_excel.py (próximo script)")
    print("="*80)
    
else:
    print(f"\n✅ PERFECTO: No hay CUFEs duplicados")
    print("\n🤔 Si las tablas están vacías Y el Excel no tiene duplicados,")
    print("   entonces el problema está en el CÓDIGO que inserta los datos.")
    print("\n🔍 Posible causa:")
    print("   - El código está insertando cada registro DOS VECES")
    print("   - O hay un loop que repite la inserción")
    
print("\n")
