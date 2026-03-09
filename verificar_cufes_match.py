"""
Script MEJORADO para verificar si los CUFEs de DIAN coinciden con los CUFEs de Acuses
Versión: 2.0 - 18 Febrero 2026
Mejoras: Normalización de CUFEs, trim de espacios, validación de formatos
"""
import pandas as pd
import os
from pathlib import Path

# Rutas de archivos
dian_path = r"uploads\dian\Dian.xlsx"
acuses_path = r"uploads\acuses\acuses.xlsx"

# Verificar que existan los archivos
print("=" * 80)
print("🔍 VERIFICACIÓN DE MATCH ENTRE DIAN Y ACUSES - v2.0")
print("=" * 80)

# Verificar archivos
if not os.path.exists(dian_path):
    print(f"❌ ERROR: Archivo DIAN no encontrado: {dian_path}")
    print(f"   Ruta absoluta: {os.path.abspath(dian_path)}")
    exit(1)

if not os.path.exists(acuses_path):
    print(f"❌ ERROR: Archivo ACUSES no encontrado: {acuses_path}")
    print(f"   Ruta absoluta: {os.path.abspath(acuses_path)}")
    print(f"\n💡 SOLUCIÓN:")
    print(f"   1. Verifica que el archivo exista en la carpeta uploads/acuses/")
    print(f"   2. Si es .xls, conviértelo a .xlsx en Excel")
    print(f"   3. Guárdalo como 'acuses.xlsx'")
    exit(1)

print(f"✅ Archivos encontrados:")
print(f"   - DIAN: {dian_path}")
print(f"   - ACUSES: {acuses_path}")

# Leer archivo DIAN
print(f"\n📂 Leyendo archivo DIAN: {dian_path}")
try:
    dian_df = pd.read_excel(dian_path, engine='openpyxl')
    print(f"✅ DIAN leído: {len(dian_df):,} registros")
    print(f"   Columnas: {list(dian_df.columns[:10])}")
    
    # Normalizar nombres de columnas
    dian_df.columns = [str(c).strip().lower() for c in dian_df.columns]
    print(f"\n🔄 Columnas normalizadas:")
    print(f"   Total: {len(dian_df.columns)} columnas")
    print(f"   Primeras 10:")
    for col in list(dian_df.columns[:10]):
        print(f"      • {col}")
    
    # Buscar columna CUFE
    cufe_col_dian = None
    for col in dian_df.columns:
        if 'cufe' in str(col).lower() or 'cude' in str(col).lower():
            cufe_col_dian = col
            print(f"\n✅ Columna CUFE encontrada en DIAN: '{col}'")
            break
    
    if not cufe_col_dian:
        print("❌ ERROR: No se encontró columna CUFE en DIAN")
        exit(1)
    
    # Mostrar primeros CUFEs de DIAN
    print(f"\n📝 Primeros 5 CUFEs en DIAN:")
    cufes_dian = dian_df[cufe_col_dian].tolist()
    for i, cufe in enumerate(cufes_dian[:5]):
        print(f"   {i+1}. {str(cufe)[:60]}...")
     and str(c).lower() != 'nan']
    cufes_dian_unicos = set(cufes_dian_validos)
    
    # Análisis de longitudes de CUFEs DIAN
    longitudes_dian = [len(c) for c in cufes_dian_validos[:100]]
    longitud_promedio_dian = sum(longitudes_dian) / len(longitudes_dian) if longitudes_dian else 0
    
    print(f"\n📊 CUFEs en DIAN:")
    print(f"   - Total registros: {len(cufes_dian):,}")
    print(f"   - CUFEs válidos: {len(cufes_dian_validos):,}")
    print(f"   - CUFEs únicos: {len(cufes_dian_unicos):,}")
    print(f"   - Longitud promedio: {longitud_promedio_dian:.0f} caracteres
    print(f"   - CUFEs válidos: {len(cufes_dian_validos):,}")
    print(f"   - CUFEs únicos: {len(cufes_dian_unicos):,}")
    
except Exception as e:
    print(f"❌ ERROR leyendo DIAN: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Leer archivo ACUSES
print(f"\n📂 Leyendo archivo ACUSES: {acuses_path}")
try:str(c).strip().lower() for c in acuses_df.columns]
    print(f"\n🔄 Columnas normalizadas:")
    print(f"   Total: {len(acuses_df.columns)} columnas")
    for idx, col in enumerate(acuses_df.columns, 1):
        tipo_dato = acuses_df[col].dtype
        print(f"      {idx:2d}. {col:40s} (tipo: {tipo_dato})iginales:")
    for col in acuses_df.columns:
        print(f"      - '{col}'")
    
    # Normalizar nombres de columnas
    acuses_df.columns = [c.strip().lower() for c in acuses_df.columns]
    print(f"\n🔄 Columnas normalizadas:")
    for col in acuses_df.columns:
        print(f"   - {col}")
    
    # Buscar columna CUFE
    cufe_col_acuses = None
    for col in acuses_df.columns:
        if 'cufe' in str(col).lower() or 'cude' in str(col).lower():
            cufe_col_acuses = col
            print(f"\n✅ Columna CUFE encontrada en ACUSES: '{col}'")
            break
    
    if not cufe_col_acuses:
        print("❌ ERROR: No se encontró columna CUFE en ACUSES")
        exit(1)
    
    # Buscar columna ESTADO
    estado_col = None
    for col in acuses_df.columns:
        col_lower = str(col).lower().strip()
        if 'estado' in col_lower and ('docto' in col_lower or 'documento' in col_lower):
            estado_col = col
            print(f"✅ Columna ESTADO encontrada en ACUSES: '{col}'")
            break
    
    # Mostrar primeros CUFEs de ACUSES
    print(f"\n📝 Primeros 5 CUFEs en ACUSES:") and str(c).lower() != 'nan']
    cufes_acuses_unicos = set(cufes_acuses_validos)
    
    # Análisis de longitudes de CUFEs ACUSES
    longitudes_acuses = [len(c) for c in cufes_acuses_validos[:100]]
    longitud_promedio_acuses = sum(longitudes_acuses) / len(longitudes_acuses) if longitudes_acuses else 0
    
    print(f"\n📊 CUFEs en ACUSES:")
    print(f"   - Total registros: {len(cufes_acuses):,}")
    print(f"   - CUFEs válidos: {len(cufes_acuses_validos):,}")
    print(f"   - CUFEs únicos: {len(cufes_acuses_unicos):,}")
    print(f"   - Longitud promedio: {longitud_promedio_acuses:.0f} caracteres
        estado = estados_acuses[i] if estados_acuses else 'N/A'
        print(f"   {i+1}. CUFE: {str(cufe)[:60]}... → Estado: {estado}")
    
    # Contar CUFEs únicos no vacíos
    cufes_acuses_validos = [str(c).strip() for c in cufes_acuses if pd.notna(c) and str(c).strip()]
    cufes_acuses_unicos = set(cufes_acuses_validos)
    print(f"\n📊 CUFEs en ACUSES:")
    print(f"   - Total registros: {len(cufes_acuses):,}")
    print(f"   - CUFEs válidos: {len(cufes_acuses_validos):,}")
    print(f"   - CUFEs únicos: {len(cufes_acuses_unicos):,}")
    
except Exception as e:
    print(f"❌ ERROR leyendo ACUSES: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# COMPARAR
print("\n" + "=" * 80)
print("🔍 ANÁLIS¡HAY COINCIDENCIAS! Ejemplos:")
    for i, cufe in enumerate(list(coincidencias)[:5]):
        # Buscar el estado en acuses
        estado = acuses_df[acuses_df[cufe_col_acuses] == cufe][estado_col].iloc[0] if estado_col else 'N/A'
        print(f"   {i+1}. CUFE: {cufe[:50]}...")
        print(f"      Estado: {estado}")
    
    # Porcentaje de cobertura
    porcentaje_dian = (len(coincidencias) / len(cufes_dian_unicos)) * 100 if len(cufes_dian_unicos) > 0 else 0
    porcentaje_acuses = (len(coincidencias) / len(cufes_acuses_unicos)) * 100 if len(cufes_acuses_unicos) > 0 else 0
    
    print(f"\n📈 COBERTURA:")
    print(f"   • {porcentaje_dian:.2f}% de facturas DIAN tienen acuse")
    print(f"   • {porcentaje_acuses:.2f}% de acuses están en DIAN")
    
    print(f"\n💡 RECOMENDACIÓN:")
    if porcentaje_dian < 50:
        print(f"   ⚠️  Cobertura baja ({porcentaje_dian:.1f}%)")
        print(f"   → Verifica que el archivo acuses esté completo")
        print(f"   → Considera actualizar el archivo acuses")
    else:
        print(f"   ✅ Cobertura aceptable ({porcentaje_dian:.1f}%)")
        print(f"   → El sistema debería mostrar estados correctamente")
else:
    print("\n❌ NO HAY COINCIDENCIAS - ANÁLISIS DETALLADO:")
    print("\n🔍 Comparando primeros 3 CUFEs de cada archivo:")
    
    print("\n   📄 DIAN:")
    for i, cufe in enumerate(list(cufes_dian_unicos)[:3]):
        print(f"      {i+1}. Longitud: {len(cufe):3d} chars")
        print(f"         Primeros 40: '{cufe[:40]}'")
        print(f"         Últimos 40:  '{cufe[-40:]}'")
    
    print("\n   📋 ACUSES:")
    for i, cufe in enumerate(list(cufes_acuses_unicos)[:3]):
        print(f"      {i+1}. Longitud: {len(cufe):3d} chars")
        print(f"         Primeros 40: '{cufe[:40]}'")
        print(f"         Últimos 40:  '{cufe[-40:]}'")
    
    print(f"\n💡 POSIBLES CAUSAS:")
    print(f"   1. ❌ CUFEs con formato diferente (mayúsculas/minúsculas)")
    print(f"   2. ❌ Espacios o caracteres invisibles")
    print(f"   3. ❌ Archivo de acuses no corresponde al periodo de DIAN")
    print(f"   4. ❌ Columnas CUFE detectadas incorrectamente")
    print(f"   5. ❌ Archivo .xls no procesado correctamente")
    
    print(f"\n🔧 SOLUCIONES:")
    print(f"   1. Convierte el archivo acuses a .xlsx si es .xls")
    print(f"   2. Abre ambos archivos en Excel y compara un CUFE manualmente")
    print(f"   3. Verifica que sean del mismo periodo (mismas fechas)")
    print(f"   4. Re-descarga el archivo acuses del sistema fuente")

print("\n" + "=" * 80)
print("📊 RESUMEN FINAL")
print("=" * 80)
print(f"   DIAN:")
print(f"     - Total: {len(cufes_dian_unicos):,} CUFEs únicos")
print(f"     - Promedio: {longitud_promedio_dian:.0f} caracteres")
print(f"   ACUSES:")
print(f"     - Total: {len(cufes_acuses_unicos):,} CUFEs únicos")
print(f"     - Promedio: {longitud_promedio_acuses:.0f} caracteres")
print(f"   MATCH:")
if len(coincidencias) > 0:
    print(f"     - ✅ {len(coincidencias):,} coincidencias ({porcentaje_dian:.1f}%)")
else:
    print(f"     - ❌ 0 coincidencias - REQUIERE ATENCIÓNoincidencias) / len(cufes_dian_unicos)) * 100
    print(f"\n📈 Cobertura: {porcentaje:.2f}% de facturas DIAN tienen acuse")
else:
    print("\n❌ NO HAY COINCIDENCIAS")
    print("\n🔍 Comparando primeros 3 CUFEs de cada archivo:")
    print("\n   DIAN:")
    for i, cufe in enumerate(list(cufes_dian_unicos)[:3]):
        print(f"      {i+1}. Longitud: {len(cufe)}, Valor: {cufe[:80]}")
    
    print("\n   ACUSES:")
    for i, cufe in enumerate(list(cufes_acuses_unicos)[:3]):
        print(f"      {i+1}. Longitud: {len(cufe)}, Valor: {cufe[:80]}")

print("\n" + "=" * 80)
print("FIN DEL ANÁLISIS")
print("=" * 80)
