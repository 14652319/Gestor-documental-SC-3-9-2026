"""
Script para verificar coincidencias entre CUFEs de DIAN y ACUSES
Versión 2.0 - Febrero 18, 2026
"""
import pandas as pd
import os

print("="* 80)
print("🔍 VERIFICACIÓN DE COINCIDENCIAS CUFE - DIAN vs ACUSES")
print("=" * 80)

# Rutas
dian_path = "uploads/dian/Dian.xlsx"
acuses_path = "uploads/acuses/acuses.xlsx"

# Verificar archivos
print(f"\n📂 Verificando archivos...")
if not os.path.exists(dian_path):
    print(f"❌ Archivo DIAN no encontrado: {dian_path}")
    exit(1)

if not os.path.exists(acuses_path):
    print(f"❌ Archivo ACUSES no encontrado: {acuses_path}")
    print(f"\n💡 Buscar archivos .xls y convertir a .xlsx")
    # Buscar archivos .xls
    acuses_dir = "uploads/acuses/"
    if os.path.exists(acuses_dir):
        archivos = [f for f in os.listdir(acuses_dir) if f.endswith('.xls')]
        if archivos:
            print(f"\n⚠️  Se encontraron archivos .xls (NO válidos):")
            for f in archivos:
                print(f"   - {f}")
            print(f"\n🔧 SOLUCIÓN:")
            print(f"   1. Abre estos archivos en Excel")
            print(f"   2. Guarda como 'Libro de Excel (.xlsx)'")
            print(f"   3. Renombra a 'acuses.xlsx'")
    exit(1)

print(f"✅ Archivos encontrados")

# Leer DIAN
print(f"\n📄 Leyendo DIAN: {dian_path}")
try:
    dian = pd.read_excel(dian_path, engine='openpyxl')
    print(f"✅ {len(dian):,} registros leídos")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Leer ACUSES
print(f"\n📄 Leyendo ACUSES: {acuses_path}")
try:
    acuses = pd.read_excel(acuses_path, engine='openpyxl')
    print(f"✅ {len(acuses):,} registros leídos")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Buscar columnas CUFE
print(f"\n🔍 Buscando columnas CUFE...")

# DIAN
cufe_dian = None
for c in dian.columns:
    if 'cufe' in str(c).lower() or 'cude' in str(c).lower():
        cufe_dian = c
        break

if not cufe_dian:
    print(f"❌ No se encontró columna CUFE en DIAN")
    print(f"   Columnas: {list(dian.columns[:10])}")
    exit(1)

print(f"✅ DIAN - Columna CUFE: '{cufe_dian}'")

# ACUSES
cufe_acuses = None
estado_acuses = None

for c in acuses.columns:
    c_lower = str(c).lower()
    if 'cufe' in c_lower or 'cude' in c_lower:
        cufe_acuses = c
    if 'estado' in c_lower and ('docto' in c_lower or 'documento' in c_lower):
        estado_acuses = c

if not cufe_acuses:
    print(f"❌ No se encontró columna CUFE en ACUSES")
    print(f"   Columnas disponibles:")
    for c in acuses.columns:
        print(f"      - {c}")
    exit(1)

print(f"✅ ACUSES - Columna CUFE: '{cufe_acuses}'")
if estado_acuses:
    print(f"✅ ACUSES - Columna ESTADO: '{estado_acuses}'")

# Extraer CUFEs
print(f"\n📊 Extrayendo CUFEs...")

# DIAN - limpiar y normalizar
cufes_dian = set()
for val in dian[cufe_dian]:
    if pd.notna(val):
        v = str(val).strip()
        if v and v.lower() != 'nan':
            cufes_dian.add(v)

print(f"   DIAN: {len(cufes_dian):,} CUFEs únicos")

# Mostrar primeros 3
print(f"\n   Primeros 3 CUFEs de DIAN:")
for i, cufe in enumerate(list(cufes_dian)[:3], 1):
    print(f"      {i}. [{len(cufe):3d} chars] {cufe[:50]}...")

# ACUSES - limpiar y normalizar
cufes_acuses = set()
for val in acuses[cufe_acuses]:
    if pd.notna(val):
        v = str(val).strip()
        if v and v.lower() != 'nan':
            cufes_acuses.add(v)

print(f"\n   ACUSES: {len(cufes_acuses):,} CUFEs únicos")

# Mostrar primeros 3
print(f"\n   Primeros 3 CUFEs de ACUSES:")
for i, cufe in enumerate(list(cufes_acuses)[:3], 1):
    print(f"      {i}. [{len(cufe):3d} chars] {cufe[:50]}...")

# Comparar
print(f"\n" + "=" * 80)
print(f"🎯 ANÁLISIS DE COINCIDENCIAS")
print(f"=" * 80)

coincidencias = cufes_dian.intersection(cufes_acuses)
solo_dian = cufes_dian - cufes_acuses
solo_acuses = cufes_acuses - cufes_dian

print(f"\n📊 RESULTADOS:")
print(f"   ✅ Coincidencias: {len(coincidencias):,}")
print(f"   📄 Solo en DIAN: {len(solo_dian):,}")
print(f"   📋 Solo en ACUSES: {len(solo_acuses):,}")

if len(coincidencias) > 0:
    porcentaje = (len(coincidencias) / len(cufes_dian)) * 100
    print(f"\n📈 Cobertura: {porcentaje:.2f}% de facturas DIAN tienen acuse")
    
    print(f"\n✅ Ejemplos de coincidencias:")
    for i, cufe in enumerate(list(coincidencias)[:3], 1):
        print(f"   {i}. {cufe[:60]}...")
else:
    print(f"\n❌ NO HAY COINCIDENCIAS")
    print(f"\n💡 POSIBLES CAUSAS:")
    print(f"   1. Archivos de diferentes periodos")
    print(f"   2. Formato de CUFE diferente")
    print(f"   3. Archivo .xls mal procesado")

print(f"\n" + "=" * 80)
print(f"FIN DEL ANÁLISIS")
print(f"=" * 80)
