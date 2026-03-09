"""
Script para simular la carga de archivo DIAN desde el navegador
Reproduce la lógica de actualizar_maestro() de routes.py
DIAGNÓSTICO DE FECHAS
"""
import polars as pl
import pandas as pd
import psycopg2
from datetime import datetime, date
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'gestor_documental'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

ARCHIVO_CSV = Path(__file__).parent / 'uploads' / 'dian' / 'Desde_01-01-2025_Hasta_28-02-2025_ea77100881.csv'

print("=" * 80)
print("🚀 SIMULACIÓN DE CARGA DESDE NAVEGADOR - DIAGNÓSTICO FECHAS")
print("=" * 80)
print(f"📁 Archivo: {ARCHIVO_CSV.name}")
print(f"📅 Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

def extraer_folio(docto: str) -> str:
    """Extrae solo DÍGITOS del documento"""
    if not docto:
        return ""
    import re
    return re.sub(r'[^0-9]', '', str(docto))

def extraer_prefijo(docto: str) -> str:
    """Extrae solo LETRAS del documento"""
    if not docto:
        return ""
    import re
    return re.sub(r'[0-9\-\.]', '', str(docto)).strip().upper()

def ultimos_8_sin_ceros(folio: str) -> str:
    """Últimos 8 dígitos sin ceros a la izquierda"""
    if not folio:
        return "0"
    import re
    numeros = re.sub(r'[^0-9]', '', str(folio))
    if not numeros:
        return "0"
    ultimos = numeros[-8:] if len(numeros) >= 8 else numeros
    return str(int(ultimos))

# Verificar que existe el archivo
if not ARCHIVO_CSV.exists():
    print(f"❌ ERROR: No se encontró el archivo: {ARCHIVO_CSV}")
    exit(1)

print(f"\n✅ Archivo encontrado: {ARCHIVO_CSV.name}")

# Leer CSV con Polars (como lo hace el código original)
print("\n🔄 Leyendo CSV con Polars...")
try:
    d = pl.read_csv(str(ARCHIVO_CSV), infer_schema_length=0, ignore_errors=True, null_values=["", " "])
    print(f"✅ CSV leído: {d.height:,} registros")
    
    # Normalizar nombres de columnas (minúsculas y sin espacios extra)
    d = d.rename({c: c.strip().lower() for c in d.columns})
    
    print(f"\n📊 Columnas detectadas ({len(d.columns)} total):")
    for i, col in enumerate(d.columns, 1):
        print(f"   {i:2d}. '{col}'")
    
    # Buscar columnas de fecha
    columnas_fecha = [c for c in d.columns if 'fecha' in c.lower() or 'emis' in c.lower()]
    print(f"\n🔍 Columnas relacionadas con fecha:")
    for col in columnas_fecha:
        print(f"   - '{col}'")
    
except Exception as e:
    print(f"❌ Error leyendo CSV: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Convertir a Pandas (como hace el código original)
print("\n🔄 Convirtiendo a Pandas...")
d_pd = d.to_pandas()

# Procesar primeras 5 filas para ver qué detecta
print("\n" + "=" * 80)
print("📋 PROCESANDO PRIMERAS 5 FILAS")
print("=" * 80)

errores_fecha = 0
registros_procesados = 0

for idx in range(min(5, len(d_pd))):
    row = d_pd.iloc[idx]
    print(f"\n--- FILA {idx + 1} ---")
    
    # Buscar fecha emisión (múltiples variantes)
    fecha_emision_raw = None
    col_encontrada = None
    for col_variante in ['fecha emisión', 'fecha emision', 'fecha_emision', 'fecha emisiã³n', 'fechaemision', 'fecha']:
        if col_variante in row:
            fecha_emision_raw = row[col_variante]
            if fecha_emision_raw is not None and not pd.isna(fecha_emision_raw):
                col_encontrada = col_variante
                print(f"✅ Columna encontrada: '{col_encontrada}'")
                print(f"   Valor raw: {repr(fecha_emision_raw)} (tipo: {type(fecha_emision_raw).__name__})")
                break
    
    if fecha_emision_raw is None or pd.isna(fecha_emision_raw):
        print(f"❌ NO se encontró fecha de emisión")
        print(f"   Columnas con 'fecha': {[c for c in row.keys() if 'fecha' in c.lower()]}")
        print(f"   ⚠️  USANDO FALLBACK: {date.today()}")
        errores_fecha += 1
        fecha_emision = date.today()
    elif isinstance(fecha_emision_raw, str):
        fecha_str = fecha_emision_raw.strip()
        print(f"   Parseando string: '{fecha_str}'")
        try:
            if '-' in fecha_str:
                partes = fecha_str.split('-')
                if len(partes[0]) == 4:  # YYYY-MM-DD
                    fecha_emision = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                    print(f"   ✅ Formato YYYY-MM-DD detectado: {fecha_emision}")
                else:  # DD-MM-YYYY
                    fecha_emision = datetime.strptime(fecha_str, '%d-%m-%Y').date()
                    print(f"   ✅ Formato DD-MM-YYYY detectado: {fecha_emision}")
            else:
                print(f"   ❌ Fecha sin guiones, usando fallback")
                fecha_emision = date.today()
        except Exception as e:
            print(f"   ❌ Error parseando: {e}")
            fecha_emision = date.today()
            errores_fecha += 1
    else:
        print(f"   Tipo inesperado: {type(fecha_emision_raw)}")
        if isinstance(fecha_emision_raw, datetime):
            fecha_emision = fecha_emision_raw.date()
        elif isinstance(fecha_emision_raw, date):
            fecha_emision = fecha_emision_raw
        else:
            fecha_emision = date.today()
    
    print(f"   📅 Fecha final guardada: {fecha_emision}")
    
    # Mostrar otros campos clave
    nit = str(row.get('nit emisor', row.get('nit_emisor', ''))).strip()
    prefijo = str(row.get('prefijo', ''))
    folio = str(row.get('folio', row.get('numero', '')))
    
    print(f"   NIT: {nit}")
    print(f"   Prefijo: {prefijo}")
    print(f"   Folio: {folio}")
    
    registros_procesados += 1

print("\n" + "=" * 80)
print("📊 RESUMEN")
print("=" * 80)
print(f"Total registros en CSV: {len(d_pd):,}")
print(f"Registros procesados (muestra): {registros_procesados}")
print(f"❌ Errores de fecha detectados: {errores_fecha}")

if errores_fecha > 0:
    print(f"\n⚠️  PROBLEMA CRÍTICO:")
    print(f"   {errores_fecha} registros NO pudieron parsear la fecha")
    print(f"   Se guardará con fecha actual: {date.today()}")
    print(f"\n💡 CAUSA PROBABLE:")
    print(f"   - La columna 'Fecha Emisión' del CSV no se detectó correctamente")
    print(f"   - El formato de fecha no coincide con los esperados (DD-MM-YYYY o YYYY-MM-DD)")
else:
    print(f"\n✅ Todas las fechas se detectaron correctamente")

print("\n" + "=" * 80)
