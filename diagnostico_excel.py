"""
Script para diagnosticar por qué NO se están leyendo las columnas del Excel
"""
import pandas as pd
import sys
from datetime import date, datetime

if len(sys.argv) < 2:
    print("❌ Uso: python diagnostico_excel.py <ruta_archivo.xlsx>")
    sys.exit(1)

archivo_excel = sys.argv[1]

print("=" * 100)
print("🔍 DIAGNÓSTICO DEL ARCHIVO EXCEL")
print("=" * 100)

# 1. Leer Excel completo
df_pd = pd.read_excel(archivo_excel, engine='openpyxl')
print(f"\n📊 Total de registros en Excel: {len(df_pd):,}")

# 2. Mostrar columnas ORIGINALES (antes de normalizar)
print(f"\n📋 COLUMNAS ORIGINALES ({len(df_pd.columns)}):")
for i, col in enumerate(df_pd.columns, 1):
    print(f"   {i}. '{col}' (tipo: {df_pd[col].dtype})")

# 3. Normalizar columnas (como hace el script)
df_pd.columns = [c.strip().lower() for c in df_pd.columns]

print(f"\n🔄 COLUMNAS DESPUÉS DE NORMALIZAR ({len(df_pd.columns)}):")
for i, col in enumerate(df_pd.columns, 1):
    print(f"   {i}. '{col}'")

# 4. Buscar columnas específicas
print(f"\n🔍 BÚSQUEDA DE COLUMNAS CRÍTICAS:")

# Fecha emisión
fecha_cols = ['fecha emisión', 'fecha emision', 'fecha_emision']
fecha_encontrada = None
for col in fecha_cols:
    if col in df_pd.columns:
        fecha_encontrada = col
        break

if fecha_encontrada:
    print(f"   ✅ Fecha encontrada: '{fecha_encontrada}'")
    print(f"      Primeros 3 valores:")
    for i, val in enumerate(df_pd[fecha_encontrada].head(3), 1):
        print(f"         {i}. {val} (tipo: {type(val).__name__})")
else:
    print(f"   ❌ NO se encontró columna de fecha con nombres: {fecha_cols}")
    print(f"      Columnas similares:")
    for col in df_pd.columns:
        if 'fecha' in col or 'emis' in col:
            print(f"         • '{col}'")

# Valor/Total
valor_cols = ['total', 'valor']
valor_encontrada = None
for col in valor_cols:
    if col in df_pd.columns:
        valor_encontrada = col
        break

if valor_encontrada:
    print(f"\n   ✅ Valor encontrado: '{valor_encontrada}'")
    print(f"      Primeros 3 valores:")
    for i, val in enumerate(df_pd[valor_encontrada].head(3), 1):
        print(f"         {i}. {val} (tipo: {type(val).__name__})")
else:
    print(f"\n   ❌ NO se encontró columna de valor con nombres: {valor_cols}")
    print(f"      Columnas similares:")
    for col in df_pd.columns:
        if 'valor' in col or 'total' in col or 'precio' in col:
            print(f"         • '{col}'")

# Forma de pago
forma_cols = ['forma de pago', 'forma pago', 'forma_pago']
forma_encontrada = None
for col in forma_cols:
    if col in df_pd.columns:
        forma_encontrada = col
        break

if forma_encontrada:
    print(f"\n   ✅ Forma de pago encontrada: '{forma_encontrada}'")
    print(f"      Primeros 3 valores:")
    for i, val in enumerate(df_pd[forma_encontrada].head(3), 1):
        print(f"         {i}. {val} (tipo: {type(val).__name__})")
else:
    print(f"\n   ❌ NO se encontró forma de pago con nombres: {forma_cols}")

# 5. Mostrar primer registro completo
print(f"\n📄 PRIMER REGISTRO COMPLETO (después de normalización):")
if len(df_pd) > 0:
    primer_registro = df_pd.iloc[0]
    for col in df_pd.columns:
        val = primer_registro[col]
        print(f"   {col}: {val} ({type(val).__name__})")

# 6. Simular extracción como hace el script
print(f"\n🧪 SIMULACIÓN DE EXTRACCIÓN (como hace CARGA_DIRECTA_SIMPLE.py):")
if len(df_pd) > 0:
    row = df_pd.iloc[0]
    
    # Fecha
    fecha_raw = row.get('fecha emisión', row.get('fecha emision', row.get('fecha_emision', date.today())))
    print(f"\n   fecha_raw = {fecha_raw} (tipo: {type(fecha_raw).__name__})")
    
    if isinstance(fecha_raw, str):
        try:
            fecha = datetime.strptime(fecha_raw, '%Y-%m-%d').date()
            print(f"   ✅ Fecha parseada: {fecha}")
        except:
            print(f"   ❌ Error parseando fecha con formato '%Y-%m-%d'")
            print(f"      Intentando otros formatos...")
            for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    fecha = datetime.strptime(fecha_raw, fmt).date()
                    print(f"      ✅ Fecha parseada con formato '{fmt}': {fecha}")
                    break
                except:
                    print(f"      ❌ No funciona con formato '{fmt}'")
            else:
                fecha = date.today()
                print(f"      ⚠️  Usando fecha actual: {fecha}")
    else:
        fecha = fecha_raw
        print(f"   ℹ️  Fecha ya es tipo fecha: {fecha}")
    
    # Valor
    valor_raw = row.get('total', row.get('valor', 0))
    print(f"\n   valor_raw = {valor_raw} (tipo: {type(valor_raw).__name__})")
    valor = float(valor_raw) if valor_raw and str(valor_raw).strip() != '' else 0.0
    print(f"   valor final = {valor}")
    
    # Forma de pago
    forma_pago = str(row.get('forma de pago', row.get('forma pago', row.get('forma_pago', '2')))).strip()
    print(f"\n   forma_pago = '{forma_pago}'")

print("\n" + "=" * 100)
print("🎯 DIAGNÓSTICO COMPLETO")
print("=" * 100)
