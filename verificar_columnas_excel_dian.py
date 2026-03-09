"""
VERIFICAR COLUMNAS DEL ARCHIVO EXCEL DIAN
==========================================
Lee el archivo Excel y muestra sus columnas reales
"""
import polars as pl
import sys

# Ruta al archivo Excel DIAN (ajustar según tu ubicación)
archivo_excel = input("\n📂 Ingresa la ruta completa del archivo Excel DIAN: ").strip()

print(f"\n🔍 Leyendo archivo: {archivo_excel}")
print("="*80 + "\n")

try:
    # Leer Excel con Polars
    df = pl.read_excel(archivo_excel)
    
    print(f"✅ Archivo leído correctamente")
    print(f"📊 Total de filas: {len(df):,}")
    print(f"📊 Total de columnas: {len(df.columns)}")
    
    print("\n" + "="*80)
    print("📋 COLUMNAS DEL EXCEL (nombres exactos)")
    print("="*80 + "\n")
    
    for idx, col in enumerate(df.columns, 1):
        print(f"  {idx:2}. '{col}'")
    
    # Buscar prefijo y folio
    print("\n" + "="*80)
    print("🔍 BUSCANDO COLUMNAS CRÍTICAS")
    print("="*80 + "\n")
    
    prefijo_col = None
    folio_col = None
    total_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'prefijo' in col_lower:
            prefijo_col = col
            print(f"  ✅ Prefijo encontrado: '{col}'")
        if 'folio' in col_lower:
            folio_col = col
            print(f"  ✅ Folio encontrado: '{col}'")
        if 'total' in col_lower and 'subtotal' not in col_lower:
            total_col = col
            print(f"  ✅ Total encontrado: '{col}'")
    
    if not prefijo_col:
        print(f"  ❌ NO se encontró columna 'Prefijo'")
    if not folio_col:
        print(f"  ❌ NO se encontró columna 'Folio'")
    if not total_col:
        print(f"  ❌ NO se encontró columna 'Total'")
    
    # Mostrar primeras 3 filas
    if prefijo_col and folio_col:
        print("\n" + "="*80)
        print("📊 PRIMERAS 3 FILAS")
        print("="*80 + "\n")
        
        for i in range(min(3, len(df))):
            print(f"  Fila {i+1}:")
            if prefijo_col:
                print(f"    Prefijo: '{df[prefijo_col][i]}'")
            if folio_col:
                print(f"    Folio: '{df[folio_col][i]}'")
            if total_col:
                print(f"    Total: '{df[total_col][i]}'")
            print()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
