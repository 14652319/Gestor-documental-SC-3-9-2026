"""
VERIFICACIÓN MANUAL DE COLUMNAS - 19 Feb 2026
Lee las primeras filas de DIAN y ACUSES para ver los nombres exactos de las columnas
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent
UPLOADS_DIAN = BASE_DIR / "uploads" / "dian"
UPLOADS_ACUSES = BASE_DIR / "uploads" / "acuses"

# Encontrar archivos
archivos_dian = list(UPLOADS_DIAN.glob("*.xlsx")) + list(UPLOADS_DIAN.glob("*.csv"))
archivos_acuses = list(UPLOADS_ACUSES.glob("*.xlsx")) + list(UPLOADS_ACUSES.glob("*.csv"))

if not archivos_dian:
    print("❌ No hay archivos en uploads/dian/")
    exit(1)
if not archivos_acuses:
    print("❌ No hay archivos en uploads/acuses/")
    exit(1)

archivo_dian = max(archivos_dian, key=lambda x: x.stat().st_mtime)
archivo_acuses = max(archivos_acuses, key=lambda x: x.stat().st_mtime)

print("="*100)
print("VERIFICACIÓN MANUAL DE COLUMNAS Y PRIMERAS FILAS")
print("="*100)

print(f"\n📁 Archivo DIAN: {archivo_dian.name}")
print(f"📁 Archivo ACUSES: {archivo_acuses.name}")

# Leer DIAN
print("\n" + "="*100)
print("ARCHIVO DIAN - COLUMNAS Y PRIMERAS 3 FILAS")
print("="*100)

try:
    dian = pd.read_excel(archivo_dian, nrows=3) if archivo_dian.suffix == '.xlsx' else pd.read_csv(archivo_dian, nrows=3)
    
    print(f"\n✅ Total de columnas: {len(dian.columns)}")
    print("\n📋 LISTA DE COLUMNAS:")
    for idx, col in enumerate(dian.columns, 1):
        print(f"   {idx:2d}. '{col}'")
    
    print("\n📊 PRIMERAS 3 FILAS:")
    for idx, row in dian.iterrows():
        print(f"\n   --- FILA {idx+1} ---")
        for col in dian.columns:
            valor = row[col]
            if pd.isna(valor):
                valor_str = "[VACÍO]"
            else:
                valor_str = str(valor)[:60]
            print(f"   {col}: {valor_str}")
    
    # Buscar columna CUFE
    print("\n🔍 BÚSQUEDA DE COLUMNA CUFE/CUDE EN DIAN:")
    col_cufe_dian = None
    for col in dian.columns:
        col_lower = str(col).lower()
        if 'cufe' in col_lower or 'cude' in col_lower:
            col_cufe_dian = col
            print(f"   ✅ ENCONTRADA: '{col}'")
            print(f"   Primeros 2 valores:")
            for idx, val in enumerate(dian[col].head(2)):
                print(f"      Fila {idx+1}: {str(val)[:80]}...")
            break
    
    if not col_cufe_dian:
        print("   ❌ NO SE ENCONTRÓ columna con 'CUFE' o 'CUDE'")
        print("   Columnas disponibles:")
        for col in dian.columns:
            print(f"      - {col}")

except Exception as e:
    print(f"❌ ERROR leyendo DIAN: {e}")

# Leer ACUSES
print("\n" + "="*100)
print("ARCHIVO ACUSES - COLUMNAS Y PRIMERAS 3 FILAS")
print("="*100)

try:
    acuses = pd.read_excel(archivo_acuses, nrows=3) if archivo_acuses.suffix == '.xlsx' else pd.read_csv(archivo_acuses, nrows=3)
    
    print(f"\n✅ Total de columnas: {len(acuses.columns)}")
    print("\n📋 LISTA DE COLUMNAS:")
    for idx, col in enumerate(acuses.columns, 1):
        print(f"   {idx:2d}. '{col}'")
    
    print("\n📊 PRIMERAS 3 FILAS:")
    for idx, row in acuses.iterrows():
        print(f"\n   --- FILA {idx+1} ---")
        for col in acuses.columns:
            valor = row[col]
            if pd.isna(valor):
                valor_str = "[VACÍO]"
            else:
                valor_str = str(valor)[:60]
            print(f"   {col}: {valor_str}")
    
    # Buscar columna CUFE
    print("\n🔍 BÚSQUEDA DE COLUMNA CUFE EN ACUSES:")
    col_cufe_acuses = None
    for col in acuses.columns:
        col_lower = str(col).lower()
        if 'cufe' in col_lower:
            col_cufe_acuses = col
            print(f"   ✅ ENCONTRADA: '{col}'")
            print(f"   Primeros 2 valores:")
            for idx, val in enumerate(acuses[col].head(2)):
                print(f"      Fila {idx+1}: {str(val)[:80]}...")
            break
    
    if not col_cufe_acuses:
        print("   ❌ NO SE ENCONTRÓ columna con 'CUFE'")
        print("   Columnas disponibles:")
        for col in acuses.columns:
            print(f"      - {col}")
    
    # Buscar columna ESTADO
    print("\n🔍 BÚSQUEDA DE COLUMNA ESTADO EN ACUSES:")
    col_estado_acuses = None
    for col in acuses.columns:
        col_lower = str(col).lower()
        if 'estado' in col_lower and ('docto' in col_lower or 'documento' in col_lower):
            col_estado_acuses = col
            print(f"   ✅ ENCONTRADA: '{col}'")
            print(f"   Primeros 2 valores:")
            for idx, val in enumerate(acuses[col].head(2)):
                print(f"      Fila {idx+1}: {val}")
            break
    
    if not col_estado_acuses:
        print("   ⚠️  NO SE ENCONTRÓ columna con 'estado' + 'docto'")
        print("   Buscando solo 'estado':")
        for col in acuses.columns:
            if 'estado' in str(col).lower():
                print(f"      Candidata: '{col}'")

except Exception as e:
    print(f"❌ ERROR leyendo ACUSES: {e}")

print("\n" + "="*100)
print("FIN DE LA VERIFICACIÓN")
print("="*100)
