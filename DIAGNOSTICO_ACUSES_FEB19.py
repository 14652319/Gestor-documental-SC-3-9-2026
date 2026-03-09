"""
DIAGNÓSTICO DE ACUSES - 19 de Febrero de 2026
Valida por qué los CUFEs de ACUSES no coinciden con DIAN

Script completo de diagnóstico con análisis detallado
"""

import pandas as pd
import os
from pathlib import Path
from difflib import SequenceMatcher

# Rutas de archivos
BASE_DIR = Path(__file__).parent
UPLOADS_DIAN = BASE_DIR / "uploads" / "dian"
UPLOADS_ACUSES = BASE_DIR / "uploads" / "acuses"

def buscar_ultimo_archivo(carpeta):
    """Busca el archivo más reciente en la carpeta"""
    archivos = list(carpeta.glob("*.xlsx")) + list(carpeta.glob("*.csv"))
    if not archivos:
        return None
    return max(archivos, key=os.path.getmtime)

def normalizar_texto(texto):
    """Normaliza texto para comparación"""
    if pd.isna(texto) or texto is None:
        return ""
    return str(texto).strip().upper()

def similitud(a, b):
    """Calcula similitud entre dos strings (0-100%)"""
    return SequenceMatcher(None, a, b).ratio() * 100

print("="*80)
print("🔍 DIAGNÓSTICO DE ACUSES - Análisis de CUFEs")
print("="*80)

# 1️⃣ BUSCAR ARCHIVOS
print("\n📂 PASO 1: Buscando archivos...")
archivo_dian = buscar_ultimo_archivo(UPLOADS_DIAN)
archivo_acuses = buscar_ultimo_archivo(UPLOADS_ACUSES)

if not archivo_dian:
    print("❌ ERROR: No se encontró archivo DIAN en uploads/dian/")
    exit(1)
if not archivo_acuses:
    print("❌ ERROR: No se encontró archivo ACUSES en uploads/acuses/")
    exit(1)

print(f"✅ DIAN: {archivo_dian.name}")
print(f"✅ ACUSES: {archivo_acuses.name}")

# 2️⃣ LEER ARCHIVOS
print("\n📥 PASO 2: Leyendo archivos...")
try:
    dian_df = pd.read_excel(archivo_dian) if archivo_dian.suffix == '.xlsx' else pd.read_csv(archivo_dian)
    acuses_df = pd.read_excel(archivo_acuses) if archivo_acuses.suffix == '.xlsx' else pd.read_csv(archivo_acuses)
    print(f"✅ DIAN: {len(dian_df):,} registros")
    print(f"✅ ACUSES: {len(acuses_df):,} registros")
except Exception as e:
    print(f"❌ ERROR leyendo archivos: {e}")
    exit(1)

# 3️⃣ DETECTAR COLUMNAS
print("\n🔍 PASO 3: Detectando columnas...")

# DIAN - Buscar columna CUFE
print("\n📋 Columnas disponibles en DIAN:")
for idx, col in enumerate(dian_df.columns, 1):
    print(f"   {idx}. '{col}' (tipo: {dian_df[col].dtype})")

col_cufe_dian = None
for col in dian_df.columns:
    col_lower = str(col).lower().strip()
    if 'cufe' in col_lower or 'cude' in col_lower:
        col_cufe_dian = col
        print(f"\n✅ DIAN - Columna CUFE detectada: '{col}'")
        break

if not col_cufe_dian:
    print("\n❌ ERROR: No se encontró columna CUFE en DIAN")
    print("   Opciones disponibles:")
    for col in dian_df.columns:
        print(f"      - {col}")
    exit(1)

# ACUSES - Buscar columnas CUFE y Estado
print("\n📋 Columnas disponibles en ACUSES:")
for idx, col in enumerate(acuses_df.columns, 1):
    print(f"   {idx}. '{col}' (tipo: {acuses_df[col].dtype})")

col_cufe_acuses = None
col_estado_acuses = None

for col in acuses_df.columns:
    col_lower = str(col).lower().strip()
    if 'cufe' in col_lower or 'cude' in col_lower:
        col_cufe_acuses = col
        print(f"\n✅ ACUSES - Columna CUFE detectada: '{col}'")
    if 'estado' in col_lower and ('docto' in col_lower or 'documento' in col_lower):
        col_estado_acuses = col
        print(f"✅ ACUSES - Columna ESTADO detectada: '{col}'")

if not col_cufe_acuses:
    print("\n❌ ERROR: No se encontró columna CUFE en ACUSES")
    exit(1)
if not col_estado_acuses:
    print("\n⚠️  WARNING: No se encontró columna ESTADO en ACUSES")

# 4️⃣ ANÁLISIS DE CUFES
print("\n🔬 PASO 4: Analizando CUFEs...")

# Extraer CUFEs de DIAN (solo no vacíos)
cufes_dian = set()
for cufe in dian_df[col_cufe_dian].dropna():
    cufe_limpio = normalizar_texto(cufe)
    if cufe_limpio:
        cufes_dian.add(cufe_limpio)

# Extraer CUFEs de ACUSES (solo no vacíos)
acuses_dict = {}
for _, row in acuses_df.iterrows():
    cufe = row.get(col_cufe_acuses)
    estado = row.get(col_estado_acuses, 'Pendiente') if col_estado_acuses else 'Pendiente'
    
    cufe_limpio = normalizar_texto(cufe)
    if cufe_limpio:
        acuses_dict[cufe_limpio] = str(estado).strip()

cufes_acuses = set(acuses_dict.keys())

print(f"\n✅ CUFEs únicos en DIAN: {len(cufes_dian):,}")
print(f"✅ CUFEs únicos en ACUSES: {len(cufes_acuses):,}")

# 5️⃣ CALCULAR COINCIDENCIAS
print("\n🎯 PASO 5: Calculando coincidencias...")

coincidencias = cufes_dian.intersection(cufes_acuses)
solo_dian = cufes_dian - cufes_acuses
solo_acuses = cufes_acuses - cufes_dian

print(f"\n🔗 COINCIDENCIAS: {len(coincidencias):,} CUFEs coinciden")
print(f"   Porcentaje de match: {len(coincidencias)/len(cufes_dian)*100:.2f}%")

print(f"\n📊 SOLO EN DIAN: {len(solo_dian):,} CUFEs no tienen acuse")
print(f"   Porcentaje: {len(solo_dian)/len(cufes_dian)*100:.2f}%")

print(f"\n📊 SOLO EN ACUSES: {len(solo_acuses):,} CUFEs no están en DIAN")
print(f"   Porcentaje: {len(solo_acuses)/len(cufes_acuses)*100:.2f}%")

# 6️⃣ MUESTRAS
print("\n📋 PASO 6: Muestras de CUFEs...")

print("\n✅ PRIMEROS 5 CUFES QUE COINCIDEN:")
for idx, cufe in enumerate(list(coincidencias)[:5], 1):
    estado = acuses_dict.get(cufe, 'N/A')
    print(f"   {idx}. {cufe[:80]}...")
    print(f"      Estado: {estado}")

print("\n❌ PRIMEROS 5 CUFES SOLO EN DIAN (sin acuse):")
for idx, cufe in enumerate(list(solo_dian)[:5], 1):
    print(f"   {idx}. {cufe[:80]}...")

print("\n⚠️  PRIMEROS 5 CUFES SOLO EN ACUSES (no en DIAN):")
for idx, cufe in enumerate(list(solo_acuses)[:5], 1):
    estado = acuses_dict.get(cufe, 'N/A')
    print(f"   {idx}. {cufe[:80]}...")
    print(f"      Estado: {estado}")

# 7️⃣ ANÁLISIS DE SIMILITUD
print("\n🔍 PASO 7: Análisis de similitud (CUFEs parecidos)...")
print("   Buscando CUFEs que puedan ser el mismo pero con diferencias mínimas...")

similares_encontrados = 0
for cufe_dian in list(solo_dian)[:10]:  # Analizar solo 10 para no saturar
    mejor_match = None
    mejor_similitud = 0
    
    for cufe_acuses in list(solo_acuses)[:100]:  # Comparar con 100 de acuses
        sim = similitud(cufe_dian, cufe_acuses)
        if sim > mejor_similitud and sim >= 90:  # Solo si similitud >= 90%
            mejor_similitud = sim
            mejor_match = cufe_acuses
    
    if mejor_match:
        similares_encontrados += 1
        print(f"\n   ⚠️  POSIBLE MATCH ({mejor_similitud:.1f}% similar):")
        print(f"      DIAN:   {cufe_dian[:80]}...")
        print(f"      ACUSES: {mejor_match[:80]}...")
        estado = acuses_dict.get(mejor_match, 'N/A')
        print(f"      Estado: {estado}")

if similares_encontrados == 0:
    print("   ✅ No se encontraron CUFEs similares (>90%)")

# 8️⃣ VERIFICACIÓN DE FORMATOS
print("\n🔬 PASO 8: Verificación de formatos de CUFE...")

print("\n📏 Longitud de CUFEs en DIAN (primeros 5):")
for idx, cufe in enumerate(list(cufes_dian)[:5], 1):
    print(f"   {idx}. Longitud: {len(cufe)} caracteres")
    print(f"      {cufe[:80]}...")

print("\n📏 Longitud de CUFEs en ACUSES (primeros 5):")
for idx, cufe in enumerate(list(cufes_acuses)[:5], 1):
    print(f"   {idx}. Longitud: {len(cufe)} caracteres")
    print(f"      {cufe[:80]}...")

# 9️⃣ VERIFICACIÓN DE ESPACIOS OCULTOS
print("\n🔍 PASO 9: Verificación de espacios ocultos...")

espacios_dian = 0
espacios_acuses = 0

for cufe in list(cufes_dian)[:100]:
    if cufe != cufe.strip():
        espacios_dian += 1

for cufe in list(cufes_acuses)[:100]:
    if cufe != cufe.strip():
        espacios_acuses += 1

print(f"   DIAN: {espacios_dian}/100 CUFEs con espacios")
print(f"   ACUSES: {espacios_acuses}/100 CUFEs con espacios")

# 🔟 ESTADÍSTICAS DE ESTADOS (si hay columna estado)
if col_estado_acuses:
    print("\n📊 PASO 10: Distribución de estados en ACUSES...")
    estados = acuses_df[col_estado_acuses].value_counts()
    print("\n   Estados encontrados:")
    for estado, cantidad in estados.items():
        print(f"      {estado}: {cantidad:,} ({cantidad/len(acuses_df)*100:.2f}%)")

# ✅ CONCLUSIONES
print("\n" + "="*80)
print("📝 CONCLUSIONES")
print("="*80)

if len(coincidencias) == 0:
    print("\n❌ PROBLEMA CRÍTICO: NO HAY COINCIDENCIAS")
    print("   Posibles causas:")
    print("   1. Columnas incorrectas detectadas")
    print("   2. Formato de CUFE completamente diferente entre archivos")
    print("   3. Archivos de diferentes períodos/empresas")
    print("\n   Recomendación: Verificar manualmente los archivos Excel")
    
elif len(coincidencias) < len(cufes_dian) * 0.5:
    print(f"\n⚠️  PROBLEMA: POCAS COINCIDENCIAS ({len(coincidencias)/len(cufes_dian)*100:.1f}%)")
    print("   Posibles causas:")
    print("   1. Archivo de acuses incompleto")
    print("   2. Archivos de diferentes períodos")
    print("   3. Formato de CUFE diferente (prefijos, sufijos)")
    
else:
    print(f"\n✅ MATCH CORRECTO: {len(coincidencias)/len(cufes_dian)*100:.1f}% de coincidencias")
    print("   El sistema debería estar funcionando correctamente")
    print("   Si sigues viendo 'No Registra', puede ser un problema de:")
    print("   1. Cache del navegador (recargar con Ctrl+F5)")
    print("   2. Filtro en el visor que oculta registros con acuses")

print("\n" + "="*80)
print("✅ DIAGNÓSTICO COMPLETADO")
print("="*80)
