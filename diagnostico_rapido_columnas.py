"""
Diagnóstico RÁPIDO: Solo primeras 100 filas
"""
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("DIAGNÓSTICO RÁPIDO - COLUMNAS DIAN")
print("=" * 80)

# Leer SOLO 100 filas
archivo = r'uploads\dian\Dian.xlsx'
print(f"\n📂 Leyendo primeras 100 filas de: {archivo}")

df = pd.read_excel(archivo, nrows=100, engine='openpyxl')

print(f"✅ Archivo leído: {len(df)} filas, {len(df.columns)} columnas\n")

# Mostrar columnas
print("📋 COLUMNAS EN EL EXCEL:")
for i, col in enumerate(df.columns, 1):
    print(f"   {i:2d}. '{col}'")

# Buscar CUFE
print(f"\n🔍 BÚSQUEDA DE CUFE:")
cufe_col = None
for col in df.columns:
    if 'cufe' in str(col).lower() or 'cude' in str(col).lower():
        cufe_col = col
        print(f"   ✅ Encontrada: '{col}'")
        
        # Mostrar 3 valores de ejemplo
        print(f"\n📖 Ejemplos de valores en '{col}':")
        for i in range(min(3, len(df))):
            val = df[col].iloc[i]
            if pd.notna(val) and str(val) != 'nan':
                print(f"      Fila {i+1}: {str(val)[:80]}... (longitud: {len(str(val))})")
            else:
                print(f"      Fila {i+1}: VACÍO/NaN")
        break

if not cufe_col:
    print(f"   ❌ NO se encontró columna CUFE/CUDE")

# Normalización
print(f"\n🔄 NORMALIZACIÓN:")

def normalizar(nombre):
    if nombre is None:
        return ''
    nombre_str = str(nombre).strip()
    nombre_norm = ' '.join(nombre_str.split()).lower()
    nombre_norm = nombre_norm.replace(' ', '_').replace('/', '_').replace('-', '_')
    return nombre_norm

if cufe_col:
    original = cufe_col
    normalizado = normalizar(cufe_col)
    print(f"   Original: '{original}'")
    print(f"   Normalizado: '{normalizado}'")
    
    # El código busca en routes.py línea 1584:
    # cufe = str(row.get(columnas_originales.get('cufe_cude', 'CUFE/CUDE'), ''))
    print(f"\n❓ PROBLEMA POTENCIAL:")
    print(f"   El código busca: 'cufe_cude' o 'CUFE/CUDE'")
    print(f"   Pero la columna es: '{original}'")
    print(f"   Y normalizada es: '{normalizado}'")
    
    if normalizado != 'cufe_cude' and original != 'CUFE/CUDE':
        print(f"\n   ⚠️  ¡HAY UN MISMATCH!")
        print(f"   El código NO va a encontrar la columna con esta lógica")

print("=" * 80)
