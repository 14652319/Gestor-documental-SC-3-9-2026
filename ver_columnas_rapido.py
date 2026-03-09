"""
Script rápido para ver solo las columnas del Excel (primeras 5 filas)
"""
import pandas as pd

archivo = r"C:\Users\Usuario\Downloads\Ricardo\Dian.xlsx"

print(f"\n📂 Leyendo: {archivo}\n")

# Leer solo primeras 5 filas para ser más rápido
df = pd.read_excel(archivo, engine='openpyxl', nrows=5)

print(f"✅ Total columnas: {len(df.columns)}\n")
print("="*80)
print("📋 COLUMNAS EXACTAS:")
print("="*80 + "\n")

for i, col in enumerate(df.columns, 1):
    print(f"{i:3}. '{col}'")

print(f"\n{'='*80}")
print("🔍 BÚSQUEDA DE COLUMNAS CRÍTICAS:")
print("="*80 + "\n")

# Buscar específicamente
buscar = ['folio', 'prefijo', 'total', 'fecha emis', 'nit emis', 'nombre emis']

for palabra in buscar:
    print(f"🔎 '{palabra}':")
    encontradas = [col for col in df.columns if palabra.lower() in col.lower()]
    if encontradas:
        for col in encontradas:
            print(f"   ✅ '{col}'")
    else:
        print(f"   ❌ NO ENCONTRADA")
    print()

print("="*80)
print("📊 PRIMERA FILA DE DATOS (muestra):")
print("="*80 + "\n")

# Mostrar primera fila de algunas columnas clave
cols_mostrar = [col for col in df.columns if any(palabra in col.lower() for palabra in ['folio', 'prefijo', 'total', 'nit', 'nombre'])][:6]
if cols_mostrar:
    print(df[cols_mostrar].head(1).to_string())

print("\n✅ Listo!")
