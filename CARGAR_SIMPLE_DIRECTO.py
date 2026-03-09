"""
CARGA DIRECTA Y SIMPLE - DIAN + ERP FINANCIERO
Sin Polars, solo pandas + PostgreSQL COPY
"""
import pandas as pd
import os
import io
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from unicodedata import normalize
import re

load_dotenv()

def normalizar_columna(nombre):
    nombre = str(nombre).strip()
    nombre = normalize('NFD', nombre)
    nombre = ''.join(c for c in nombre if c.isalnum() or c in ' _-')
    nombre = nombre.lower().replace(' ', '_').replace('-', '_')
    nombre = re.sub(r'_+', '_', nombre)
    return nombre.rstrip('.')

def extraer_prefijo(docto):
    if not docto or str(docto).strip() == '':
        return ''
    docto_str = str(docto).strip()
    docto_limpio = docto_str.replace('-', '').replace('.', '').replace(' ', '')
    prefijo = re.sub(r'\d', '', docto_limpio)
    return prefijo if prefijo else ''

def extraer_folio(docto):
    if not docto:
        return ''
    docto_str = str(docto).strip()
    digitos = re.sub(r'\D', '', docto_str)
    return digitos if digitos else ''

def ultimos_8_sin_ceros(folio_str):
    if not folio_str:
        return ''
    folio_str = str(folio_str).strip()
    ultimos = folio_str[-8:] if len(folio_str) >= 8 else folio_str
    sin_ceros = ultimos.lstrip('0')
    return sin_ceros if sin_ceros else '0'

def crear_clave_factura(nit, prefijo, folio):
    nit = str(nit).strip() if nit else ''
    prefijo = str(prefijo).strip() if prefijo else ''
    folio = str(folio).strip() if folio else ''
    return f"{nit}-{prefijo}-{folio}"

def format_value(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    if isinstance(value, str):
        value = value.replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
        return value
    return str(value)

print("\n" + "="*80)
print("CARGA DIRECTA Y SIMPLE")
print("="*80)
print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}\n")

database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)
raw_conn = engine.raw_connection()
cursor = raw_conn.cursor()

# ==============================================================================
# TABLA 1: ERP FINANCIERO (3K - PEQUEÑO, VA PRIMERO)
# ==============================================================================

print("-"*80)
print("1. ERP FINANCIERO (3K registros - archivo pequeño)")
print("-"*80)

archivo_erp_fn = r'uploads\erp_fn\erp_financiero_23022026.xlsx'

print("Leyendo Excel...")
inicio = datetime.now()
df_fn = pd.read_excel(archivo_erp_fn, engine='openpyxl')
print(f"✓ {len(df_fn):,} filas en {(datetime.now()-inicio).total_seconds():.1f}s")

df_fn.columns = [normalizar_columna(col) for col in df_fn.columns]

# Detectar (LÓGICA CORREGIDA)
cols = df_fn.columns.tolist()
proveedor_col = next((c for c in cols if "proveedor" in c.lower() and "razon" not in c.lower()), None)
razon_col = next((c for c in cols if "razon" in c.lower() and "social" in c.lower()), None)
docto_col = next((c for c in cols if "docto" in c.lower() and "proveedor" in c.lower()), None)
co_col = next((c for c in cols if c.upper() == "CO" or c.upper() == "C.O."), None)
nro_doc_col = next((c for c in cols if "nro" in c.lower() and "documento" in c.lower()), None)
usuario_col = next((c for c in cols if "usuario" in c.lower() and "creac" in c.lower()), None)
clase_col = next((c for c in cols if "clase" in c.lower() and "docto" in c.lower()), None)
fecha_col = next((c for c in cols if "fecha" in c.lower() and ("proveedor" in c.lower() or "docto" in c.lower())), None)
valor_col = next((c for c in cols if "valor" in c.lower() and ("subtotal" in c.lower() or "bruto" in c.lower())), None)

print(f"Procesando...")
registros = []
for _, row in df_fn.iterrows():
    proveedor = str(row.get(proveedor_col, '')).strip() if proveedor_col else ''
    razon_social = str(row.get(razon_col, '')).strip() if razon_col else ''
    docto_proveedor = str(row.get(docto_col, '')).strip() if docto_col else ''
    co = str(row.get(co_col, '')).strip() if co_col else ''
    nro_documento = str(row.get(nro_doc_col, '')).strip() if nro_doc_col else ''
    usuario_creacion = str(row.get(usuario_col, '')).strip() if usuario_col else ''
    clase_documento = str(row.get(clase_col, '')).strip() if clase_col else ''
    
    fecha_recibido = None
    if fecha_col:
        try:
            fecha_raw = row.get(fecha_col)
            if fecha_raw and not pd.isna(fecha_raw):
                fecha_recibido = pd.to_datetime(fecha_raw, errors='coerce').date() if isinstance(fecha_raw, str) else (fecha_raw.date() if hasattr(fecha_raw, 'date') else fecha_raw)
        except:
            pass
    
    valor = 0.0
    if valor_col:
        try:
            valor_raw = row.get(valor_col, 0)
            if valor_raw and not pd.isna(valor_raw):
                valor = float(valor_raw)
        except:
            pass
    
    prefijo = extraer_prefijo(docto_proveedor)
    folio_raw = extraer_folio(docto_proveedor)
    folio = ultimos_8_sin_ceros(folio_raw)
    clave = crear_clave_factura(proveedor, prefijo, folio_raw)
    doc_causado = f"{co} - {usuario_creacion} - {nro_documento}"
    
    registros.append((proveedor, razon_social, docto_proveedor, prefijo, folio, co, nro_documento, fecha_recibido, usuario_creacion, clase_documento, valor, clave, doc_causado, 'Financiero'))

print(f"✓ {len(registros):,} procesados")

cursor.execute("CREATE TEMP TABLE temp_fn (LIKE erp_financiero INCLUDING DEFAULTS) ON COMMIT DROP")

buffer = io.StringIO()
for r in registros:
    buffer.write('\t'.join([format_value(v) for v in r]) + '\n')

buffer.seek(0)
cursor.copy_from(buffer, 'temp_fn', sep='\t', null='', columns=('proveedor', 'razon_social', 'docto_proveedor', 'prefijo', 'folio', 'co', 'nro_documento', 'fecha_recibido', 'usuario_creacion', 'clase_documento', 'valor', 'clave_erp_financiero', 'doc_causado_por', 'modulo'))

cursor.execute("INSERT INTO erp_financiero SELECT * FROM temp_fn ON CONFLICT (clave_erp_financiero) DO NOTHING")
insertados_fn = cursor.rowcount
raw_conn.commit()
print(f"✅ {insertados_fn:,} insertados\n")

# ==============================================================================
# TABLA 2: DIAN (66K - GRANDE)
# ==============================================================================

print("-"*80)
print("2. DIAN (66K registros - archivo grande 13.96 MB)")
print("-"*80)

archivo_dian = r'uploads\dian\Dian_23022026.xlsx'

print("Leyendo Excel (puede tomar 60-90 segundos)...")
inicio = datetime.now()
df_dian = pd.read_excel(archivo_dian, engine='openpyxl')
print(f"✓ {len(df_dian):,} filas en {(datetime.now()-inicio).total_seconds():.1f}s")

df_dian.columns = [normalizar_columna(col) for col in df_dian.columns]

# Detectar
cols = df_dian.columns.tolist()
nit_col = next((c for c in cols if "nit" in c.lower() and "adquir" in c.lower()), None)
razon_col = next((c for c in cols if "razon" in c.lower() and "social" in c.lower()), None)
numero_col = next((c for c in cols if "numero" in c.lower() and "documento" not in c.lower()), None)
fecha_col = next((c for c in cols if "fecha" in c.lower() and ("factur" in c.lower() or "gener" in c.lower())), None)
valor_col = next((c for c in cols if "total" in c.lower() and "documento" in c.lower()), None)

print(f"Procesando {len(df_dian):,} registros...")
inicio_proc = datetime.now()

registros_dian = []
for idx, (_, row) in enumerate(df_dian.iterrows()):
    nit = str(row.get(nit_col, '')).strip() if nit_col else ''
    razon = str(row.get(razon_col, '')).strip() if razon_col else ''
    numero = str(row.get(numero_col, '')).strip() if numero_col else ''
    
    fecha_factura = None
    if fecha_col:
        try:
            fecha_raw = row.get(fecha_col)
            if fecha_raw and not pd.isna(fecha_raw):
                fecha_factura = pd.to_datetime(fecha_raw, errors='coerce').date() if isinstance(fecha_raw, str) else (fecha_raw.date() if hasattr(fecha_raw, 'date') else fecha_raw)
        except:
            pass
    
    valor = 0.0
    if valor_col:
        try:
            valor_raw = row.get(valor_col, 0)
            if valor_raw and not pd.isna(valor_raw):
                valor = float(valor_raw)
        except:
            pass
    
    prefijo = extraer_prefijo(numero)
    folio_raw = extraer_folio(numero)
    folio = ultimos_8_sin_ceros(folio_raw)
    clave = crear_clave_factura(nit, prefijo, folio_raw)
    
    registros_dian.append((nit, razon, numero, prefijo, folio, fecha_factura, valor, clave))
    
    if (idx + 1) % 10000 == 0:
        print(f"  {idx+1:,} registros...")

print(f"✓ {len(registros_dian):,} procesados en {(datetime.now()-inicio_proc).total_seconds():.1f}s")

print("Insertando en PostgreSQL...")
inicio_ins = datetime.now()

cursor.execute("CREATE TEMP TABLE temp_dian (LIKE dian INCLUDING DEFAULTS) ON COMMIT DROP")

buffer = io.StringIO()
for r in registros_dian:
    buffer.write('\t'.join([format_value(v) for v in r]) + '\n')

buffer.seek(0)
cursor.copy_from(buffer, 'temp_dian', sep='\t', null='', columns=('nit_adquiriente', 'razon_social', 'numero', 'prefijo', 'folio', 'fecha_factura', 'valor', 'clave_dian'))

cursor.execute("INSERT INTO dian SELECT * FROM temp_dian ON CONFLICT (clave_dian) DO NOTHING")
insertados_dian = cursor.rowcount
raw_conn.commit()
print(f"✅ {insertados_dian:,} insertados en {(datetime.now()-inicio_ins).total_seconds():.1f}s\n")

cursor.close()
raw_conn.close()

# RESUMEN
print("="*80)
print("RESUMEN FINAL")
print("="*80)

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM dian"))
    print(f"\n📊 DIAN: {result.scalar():,} registros")
    
    result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial"))
    print(f"📊 ERP Comercial: {result.scalar():,} registros")
    
    result = conn.execute(text("SELECT COUNT(*) FROM erp_financiero"))
    print(f"📊 ERP Financiero: {result.scalar():,} registros")
    
    result = conn.execute(text("SELECT COUNT(*) FROM dian"))
    total_dian = result.scalar()
    result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial"))
    total_cm = result.scalar()
    result = conn.execute(text("SELECT COUNT(*) FROM erp_financiero"))
    total_fn = result.scalar()
    
    total = total_dian + total_cm + total_fn
    print(f"\n✅ TOTAL: {total:,} registros")

print("\n" + "="*80 + "\n")
