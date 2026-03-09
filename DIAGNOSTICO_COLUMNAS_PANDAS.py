"""
DIAGNOSTICO_COLUMNAS_PANDAS.py
================================
Simula EXACTAMENTE el flujo de routes.py para diagnosticar
qué columnas quedan después de la conversión Polars -> Pandas
"""

import os
import sys
from pathlib import Path
import polars as pl
import pandas as pd
from datetime import datetime, date

print("="*80)
print("🔍 DIAGNÓSTICO: POLARS → PANDAS → DETECCIÓN DE COLUMNAS")
print("="*80)
print(f"📅 Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# Archivo CSV
csv_path = Path("uploads/dian/Desde_01-01-2025_Hasta_28-02-2025_ea77100881.csv")

if not csv_path.exists():
    print(f"❌ ERROR: No se encontró el archivo")
    sys.exit(1)

print(f"✅ Archivo: {csv_path.name}")
print(f"📊 Tamaño: {csv_path.stat().st_size / 1024:.2f} KB")

# PASO 1: Leer con Polars (exactamente como routes.py)
print("\n" + "="*80)
print("📖 PASO 1: LEER CSV CON POLARS")
print("="*80)

def norm_cols(df: pl.DataFrame) -> pl.DataFrame:
    """Normalizar columnas (exactamente como routes.py línea 260)"""
    return df.rename({c: c.strip().lower() for c in df.columns})

try:
    # Leer exactamente como routes.py línea 262
    df_polars = pl.read_csv(
        str(csv_path),
        infer_schema_length=0,
        ignore_errors=True,
        null_values=["", " "]
    )
    print(f"✅ CSV leído con Polars: {df_polars.height:,} registros")
    
    # Mostrar columnas ANTES de normalizar
    print(f"\n📊 Columnas ANTES de normalizar ({len(df_polars.columns)} total):")
    for i, col in enumerate(df_polars.columns[:10], 1):  # Primeras 10
        print(f"   {i:2}. '{col}'")
    if len(df_polars.columns) > 10:
        print(f"   ... y {len(df_polars.columns) - 10} más")
    
    # Normalizar columnas
    df_polars = norm_cols(df_polars)
    print(f"\n✅ Columnas normalizadas (lowercase + strip)")
    
    # Mostrar columnas DESPUÉS de normalizar
    print(f"\n📊 Columnas DESPUÉS de normalizar ({len(df_polars.columns)} total):")
    for i, col in enumerate(df_polars.columns[:15], 1):  # Primeras 15
        print(f"   {i:2}. '{col}'")
    if len(df_polars.columns) > 15:
        print(f"   ... y {len(df_polars.columns) - 15} más")
    
    # Mostrar columnas relevantes
    print(f"\n🔍 Columnas CRÍTICAS detectadas:")
    columnas_criticas = [
        'fecha emisión', 'fecha emision', 'fecha_emision',
        'forma de pago', 'forma pago', 'forma_pago',
        'total', 'valor',
        'prefijo', 'folio', 'nit emisor', 'nombre emisor'
    ]
    
    for col_buscar in columnas_criticas:
        if col_buscar in df_polars.columns:
            print(f"   ✅ '{col_buscar}' encontrada")
        else:
            print(f"   ❌ '{col_buscar}' NO encontrada")
    
except Exception as e:
    print(f"❌ ERROR leyendo CSV con Polars: {e}")
    sys.exit(1)

# PASO 2: Convertir a Pandas (exactamente como routes.py línea 1297)
print("\n" + "="*80)
print("🔄 PASO 2: CONVERTIR A PANDAS")
print("="*80)

try:
    df_pandas = df_polars.to_pandas()
    print(f"✅ Convertido a Pandas: {len(df_pandas):,} registros")
    
    # Mostrar columnas en Pandas
    print(f"\n📊 Columnas en Pandas ({len(df_pandas.columns)} total):")
    for i, col in enumerate(df_pandas.columns[:15], 1):
        print(f"   {i:2}. '{col}' (dtype: {df_pandas[col].dtype})")
    if len(df_pandas.columns) > 15:
        print(f"   ... y {len(df_pandas.columns) - 15} más")
    
    # Verificar columnas críticas en Pandas
    print(f"\n🔍 Columnas CRÍTICAS en Pandas:")
    for col_buscar in columnas_criticas:
        if col_buscar in df_pandas.columns:
            print(f"   ✅ '{col_buscar}' presente (dtype: {df_pandas[col_buscar].dtype})")
        else:
            print(f"   ❌ '{col_buscar}' AUSENTE")
    
except Exception as e:
    print(f"❌ ERROR convirtiendo a Pandas: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# PASO 3: Analizar primera fila (exactamente como routes.py)
print("\n" + "="*80)
print("📋 PASO 3: ANALIZAR PRIMERA FILA")
print("="*80)

try:
    first_row = df_pandas.iloc[0]
    
    print(f"\n🔍 Valores de columnas CRÍTICAS en primera fila:")
    
    # Fecha emisión
    for col_var in ['fecha emisión', 'fecha emision', 'fecha_emision']:
        if col_var in first_row.index:
            val = first_row[col_var]
            print(f"   '{col_var}': {repr(val)} (tipo: {type(val).__name__}, es NaN: {pd.isna(val)})")
    
    # Forma de pago
    for col_var in ['forma de pago', 'forma pago', 'forma_pago']:
        if col_var in first_row.index:
            val = first_row[col_var]
            print(f"   '{col_var}': {repr(val)} (tipo: {type(val).__name__}, es NaN: {pd.isna(val)})")
    
    # Valor/Total
    for col_var in ['total', 'valor']:
        if col_var in first_row.index:
            val = first_row[col_var]
            print(f"   '{col_var}': {repr(val)} (tipo: {type(val).__name__}, es NaN: {pd.isna(val)})")
    
    # NIT, Prefijo, Folio
    for col_var in ['nit emisor', 'prefijo', 'folio']:
        if col_var in first_row.index:
            val = first_row[col_var]
            print(f"   '{col_var}': {repr(val)} (tipo: {type(val).__name__})")
    
except Exception as e:
    print(f"❌ ERROR analizando primera fila: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# PASO 4: Simular detección como routes.py
print("\n" + "="*80)
print("🎯 PASO 4: SIMULAR DETECCIÓN COMO ROUTES.PY")
print("="*80)

try:
    row = first_row
    
    # Buscar fecha_emision con múltiples variantes
    print("\n🔍 Buscando 'fecha emisión':")
    fecha_emision_raw = None
    for col_variante in ['fecha emisión', 'fecha emision', 'fecha_emision', 'fecha emisiã³n', 'fechaemision', 'fecha']:
        if col_variante in row.index:
            fecha_emision_raw = row[col_variante]
            if fecha_emision_raw is not None and not pd.isna(fecha_emision_raw):
                print(f"   ✅ Encontrada columna '{col_variante}' con valor: {repr(fecha_emision_raw)}")
                break
            else:
                print(f"   ⚠️  Columna '{col_variante}' existe pero valor es None/NaN: {repr(fecha_emision_raw)}")
    
    if fecha_emision_raw is None or pd.isna(fecha_emision_raw):
        print(f"   ❌ NO se encontró fecha de emisión válida")
        print(f"   📋 Columnas con 'fecha': {[c for c in row.index if 'fecha' in c.lower()]}")
        print(f"   ⚠️  USARÍA date.today() = {date.today()}")
    else:
        print(f"   ✅ Fecha encontrada: {repr(fecha_emision_raw)}")
        if isinstance(fecha_emision_raw, str):
            fecha_str = fecha_emision_raw.strip()
            print(f"   🔄 Intentando parsear: '{fecha_str}'")
            try:
                if '-' in fecha_str:
                    partes = fecha_str.split('-')
                    if len(partes[0]) == 4:
                        fecha_final = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                        print(f"   ✅ Parseado como YYYY-MM-DD: {fecha_final}")
                    else:
                        fecha_final = datetime.strptime(fecha_str, '%d-%m-%Y').date()
                        print(f"   ✅ Parseado como DD-MM-YYYY: {fecha_final}")
            except Exception as e:
                print(f"   ❌ Error parseando: {e}")
    
    # Buscar forma_pago
    print("\n🔍 Buscando 'forma de pago':")
    forma_pago_val = None
    for col_var in ['forma de pago', 'forma pago', 'forma_pago']:
        if col_var in row.index:
            forma_pago_val = row[col_var]
            print(f"   ✅ Encontrada columna '{col_var}' con valor: {repr(forma_pago_val)}")
            break
    
    if forma_pago_val is None:
        print(f"   ❌ NO se encontró 'forma de pago'")
        print(f"   📋 Columnas con 'forma': {[c for c in row.index if 'forma' in c.lower()]}")
    
    # Buscar total/valor
    print("\n🔍 Buscando 'total' o 'valor':")
    valor_val = None
    for col_var in ['total', 'valor']:
        if col_var in row.index:
            valor_val = row[col_var]
            print(f"   ✅ Encontrada columna '{col_var}' con valor: {repr(valor_val)}")
            if valor_val is not None and not pd.isna(valor_val):
                break
    
    if valor_val is None or pd.isna(valor_val):
        print(f"   ❌ NO se encontró valor válido")
        print(f"   📋 Columnas con 'total' o 'valor': {[c for c in row.index if 'total' in c.lower() or 'valor' in c.lower()]}")
    
except Exception as e:
    print(f"❌ ERROR en simulación: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("✅ DIAGNÓSTICO COMPLETADO")
print("="*80)
