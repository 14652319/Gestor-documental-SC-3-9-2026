"""
COMPARACIÓN EXACTA DE CUFEs - 19 Feb 2026
Compara los CUFEs de DIAN vs ACUSES para encontrar coincidencias
"""

import pandas as pd
from pathlib import Path
import os

BASE_DIR = Path(__file__).parent
UPLOADS_DIAN = BASE_DIR / "uploads" / "dian"
UPLOADS_ACUSES = BASE_DIR / "uploads" / "acuses"

# Encontrar archivos más recientes
archivos_dian = list(UPLOADS_DIAN.glob("*.xlsx")) + list(UPLOADS_DIAN.glob("*.csv"))
archivos_acuses = list(UPLOADS_ACUSES.glob("*.xlsx")) + list(UPLOADS_ACUSES.glob("*.csv"))

archivo_dian = max(archivos_dian, key=lambda x: x.stat().st_mtime)
archivo_acuses = max(archivos_acuses, key=lambda x: x.stat().st_mtime)

print("="*100)
print("COMPARACIÓN DE CUFEs ENTRE DIAN Y ACUSES")
print("="*100)
print(f"\nArchivo DIAN: {archivo_dian.name}")
print(f"Archivo ACUSES: {archivo_acuses.name}")

# Leer archivos completos
print("\nLeyendo archivos completos...")
dian = pd.read_excel(archivo_dian) if archivo_dian.suffix == '.xlsx' else pd.read_csv(archivo_dian)
acuses = pd.read_excel(archivo_acuses) if archivo_acuses.suffix == '.xlsx' else pd.read_csv(archivo_acuses)

print(f"✅ DIAN: {len(dian):,} registros")
print(f"✅ ACUSES: {len(acuses):,} registros")

# Detectar columnas CUFE
col_cufe_dian = 'CUFE/CUDE'  # Ya sabemos que es este
col_cufe_acuses = 'CUFE'     # Ya sabemos que es este
col_estado_acuses = 'Estado Docto.'  # Ya sabemos que es este

print(f"\n📋 Columna DIAN: '{col_cufe_dian}'")
print(f"📋 Columna ACUSES CUFE: '{col_cufe_acuses}'")
print(f"📋 Columna ACUSES ESTADO: '{col_estado_acuses}'")

# Extraer y normalizar CUFEs de DIAN
print("\n🔄 Procesando CUFEs de DIAN...")
cufes_dian = set()
cufes_dian_vacios = 0

for idx, cufe in enumerate(dian[col_cufe_dian]):
    if pd.isna(cufe) or str(cufe).strip() == '':
        cufes_dian_vacios += 1
        continue
    
    cufe_limpio = str(cufe).strip().upper()
    cufes_dian.add(cufe_limpio)
    
    if idx < 3:
        print(f"   Fila {idx+1}: {cufe_limpio[:80]}...")

print(f"\n✅ CUFEs únicos en DIAN: {len(cufes_dian):,}")
print(f"⚠️  CUFEs vacíos en DIAN: {cufes_dian_vacios:,}")

# Extraer y normalizar CUFEs de ACUSES
print("\n🔄 Procesando CUFEs de ACUSES...")
acuses_dict = {}
cufes_acuses_vacios = 0

for idx, row in acuses.iterrows():
    cufe = row[col_cufe_acuses]
    estado = row[col_estado_acuses]
    
    if pd.isna(cufe) or str(cufe).strip() == '':
        cufes_acuses_vacios += 1
        continue
    
    cufe_limpio = str(cufe).strip().upper()
    estado_limpio = str(estado).strip() if not pd.isna(estado) else 'Pendiente'
    
    acuses_dict[cufe_limpio] = estado_limpio
    
    if idx < 3:
        print(f"   Fila {idx+1}: {cufe_limpio[:80]}... → {estado_limpio}")

cufes_acuses = set(acuses_dict.keys())

print(f"\n✅ CUFEs únicos en ACUSES: {len(cufes_acuses):,}")
print(f"⚠️  CUFEs vacíos en ACUSES: {cufes_acuses_vacios:,}")

# Calcular coincidencias
print("\n" + "="*100)
print("🎯 ANÁLISIS DE COINCIDENCIAS")
print("="*100)

coincidencias = cufes_dian.intersection(cufes_acuses)
solo_dian = cufes_dian - cufes_acuses
solo_acuses = cufes_acuses - cufes_dian

porcentaje_match = (len(coincidencias) / len(cufes_dian) * 100) if len(cufes_dian) > 0 else 0

print(f"\n✅ COINCIDEN: {len(coincidencias):,} CUFEs")
print(f"   Porcentaje: {porcentaje_match:.2f}%")

print(f"\n❌ SOLO EN DIAN (sin acuse): {len(solo_dian):,} CUFEs")
print(f"   Porcentaje: {(len(solo_dian)/len(cufes_dian)*100):.2f}%")

print(f"\n❌ SOLO EN ACUSES (no en DIAN): {len(solo_acuses):,} CUFEs")

# Mostrar muestras
print("\n" + "="*100)
print("📋 MUESTRAS DE CUFEs")
print("="*100)

if len(coincidencias) > 0:
    print("\n✅ PRIMEROS 5 CUFEs QUE COINCIDEN:")
    for idx, cufe in enumerate(list(coincidencias)[:5], 1):
        estado = acuses_dict.get(cufe, 'N/A')
        print(f"   {idx}. CUFE: {cufe[:70]}...")
        print(f"      Estado: {estado}")
else:
    print("\n❌ NO HAY COINCIDENCIAS")

if len(solo_dian) > 0:
    print("\n❌ PRIMEROS 5 CUFEs SOLO EN DIAN:")
    for idx, cufe in enumerate(list(solo_dian)[:5], 1):
        print(f"   {idx}. {cufe[:70]}...")

if len(solo_acuses) > 0:
    print("\n⚠️  PRIMEROS 5 CUFEs SOLO EN ACUSES:")
    for idx, cufe in enumerate(list(solo_acuses)[:5], 1):
        estado = acuses_dict.get(cufe, 'N/A')
        print(f"   {idx}. CUFE: {cufe[:70]}...")
        print(f"      Estado: {estado}")

# Verificación de longitud de CUFEs
print("\n" + "="*100)
print("📏 ANÁLISIS DE LONGITUD DE CUFEs")
print("="*100)

longitudes_dian = {}
for cufe in list(cufes_dian)[:100]:
    lon = len(cufe)
    longitudes_dian[lon] = longitudes_dian.get(lon, 0) + 1

longitudes_acuses = {}
for cufe in list(cufes_acuses)[:100]:
    lon = len(cufe)
    longitudes_acuses[lon] = longitudes_acuses.get(lon, 0) + 1

print("\nLONGITUDES en DIAN (primeros 100):")
for lon in sorted(longitudes_dian.keys()):
    print(f"   {lon} caracteres: {longitudes_dian[lon]} CUFEs")

print("\nLONGITUDES en ACUSES (primeros 100):")
for lon in sorted(longitudes_acuses.keys()):
    print(f"   {lon} caracteres: {longitudes_acuses[lon]} CUFEs")

# Distribución de estados en acuses
print("\n" + "="*100)
print("📊 DISTRIBUCIÓN DE ESTADOS en ACUSES")
print("="*100)

estados_count = {}
for estado in acuses_dict.values():
    estados_count[estado] = estados_count.get(estado, 0) + 1

print("\nEstados encontrados:")
for estado in sorted(estados_count.keys()):
    count = estados_count[estado]
    porcentaje = (count / len(acuses_dict) * 100) if len(acuses_dict) > 0 else 0
    print(f"   {estado}: {count:,} ({porcentaje:.2f}%)")

# Conclusión
print("\n" + "="*100)
print("📝 CONCLUSIÓN")
print("="*100)

if len(coincidencias) == 0:
    print("\n❌ PROBLEMA CRÍTICO: NO HAY COINCIDENCIAS ENTRE DIAN Y ACUSES")
    print("\nPosibles causas:")
    print("   1. Los archivos son de diferentes períodos/empresas")
    print("   2. El formato de CUFE es diferente (completo vs truncado)")
    print("   3. Hay un problema en la normalización de los CUFEs")
    print("\n⚠️  RECOMENDACIÓN:")
    print("   Comparar manualmente un CUFE de DIAN con uno de ACUSES")
    print("   para ver si son iguales o tienen alguna diferencia")

elif porcentaje_match < 50:
    print(f"\n⚠️  PROBLEMA: POCAS COINCIDENCIAS ({porcentaje_match:.1f}%)")
    print("\nPosibles causas:")
    print("   1. Archivo de acuses incompleto o parcial")
    print("   2. Archivos de diferentes períodos")
    print("   3. CUFEs truncados en alguno de los archivos")

else:
    print(f"\n✅ MATCH BUENO: {porcentaje_match:.1f}% de coincidencias")
    print("\nEl sistema debería estar funcionando correctamente.")
    print("Si sigues viendo 'No Registra', puede ser:")
    print("   1. Cache del navegador (recargar con Ctrl+F5)")
    print("   2. Filtro activo en el visor")
    print("   3. Problema en el código de procesamiento")

print("\n" + "="*100)
