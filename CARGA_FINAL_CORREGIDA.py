"""
CARGA FINAL CON DETECCIÓN DINÁMICA CORREGIDA
Usa exactamente la misma lógica que routes.py CORREGIDO
"""
import polars as pl
import pandas as pd
import os
import io
from datetime import datetime
from sqlalchemy import create_engine
from dotenv import load_dotenv
from unicodedata import normalize
import re

load_dotenv()

# ==============================================================================
# FUNCIONES (copiadas de routes.py)
# ==============================================================================

def normalizar_columna(nombre):
    """Normaliza nombres de columnas"""
    nombre = str(nombre).strip()
    nombre = normalize('NFD', nombre)
    nombre = ''.join(c for c in nombre if c.isalnum() or c in ' _-')
    nombre = nombre.lower().replace(' ', '_').replace('-', '_')
    nombre = re.sub(r'_+', '_', nombre)
    return nombre.rstrip('.')

def extraer_prefijo(docto):
    """Extrae prefijo manteniendo letras Y números"""
    if not docto or str(docto).strip() == '':
        return ''
    docto_str = str(docto).strip()
    docto_limpio = docto_str.replace('-', '').replace('.', '').replace(' ', '')
    prefijo = re.sub(r'\d', '', docto_limpio)
    return prefijo if prefijo else ''

def extraer_folio(docto):
    """Extrae solo los dígitos"""
    if not docto:
        return ''
    docto_str = str(docto).strip()
    digitos = re.sub(r'\D', '', docto_str)
    return digitos if digitos else ''

def ultimos_8_sin_ceros(folio_str):
    """Últimos 8 caracteres sin ceros a la izquierda"""
    if not folio_str:
        return ''
    folio_str = str(folio_str).strip()
    ultimos = folio_str[-8:] if len(folio_str) >= 8 else folio_str
    sin_ceros = ultimos.lstrip('0')
    return sin_ceros if sin_ceros else '0'

def crear_clave_factura(nit, prefijo, folio):
    """Crea clave única: NIT-PREFIJO-FOLIO"""
    nit = str(nit).strip() if nit else ''
    prefijo = str(prefijo).strip() if prefijo else ''
    folio = str(folio).strip() if folio else ''
    return f"{nit}-{prefijo}-{folio}"

def format_value_for_copy(value):
    """Formatea valor para COPY FROM"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    if isinstance(value, str):
        value = value.replace('\\', '\\\\')
        value = value.replace('\t', '\\t')
        value = value.replace('\n', '\\n')
        value = value.replace('\r', '\\r')
        return value
    return str(value)

# ==============================================================================
# PASO 1: LEER ARCHIVOS
# ==============================================================================

print("\n" + "="*80)
print("CARGA FINAL CON DETECCIÓN DINÁMICA CORREGIDA")
print("="*80)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

archivo_erp_cm = r'uploads\erp_cm\ERP_comercial_23022026.xlsx'

print("Leyendo ERP Comercial con Polars...")
df_polars = pl.read_excel(archivo_erp_cm, engine='calamine')
df_polars.columns = [normalizar_columna(col) for col in df_polars.columns]
df = df_polars.to_pandas()

print(f"✓ Leídas {len(df):,} filas")
print(f"  Columnas: {list(df.columns)}")

# ==============================================================================
# PASO 2: DETECTAR COLUMNAS (LÓGICA CORREGIDA)
# ==============================================================================

print("\nDetectando columnas dinámicamente...")

cols = df.columns.tolist()
proveedor_col = next((c for c in cols if "proveedor" in c.lower() and "razon" not in c.lower()), None)
razon_col = next((c for c in cols if "razon" in c.lower() and "social" in c.lower()), None)
docto_col = next((c for c in cols if "docto" in c.lower() and "proveedor" in c.lower()), None)
co_col = next((c for c in cols if c.upper() == "CO" or c.upper() == "C.O."), None)
nro_doc_col = next((c for c in cols if "nro" in c.lower() and "documento" in c.lower()), None)
usuario_col = next((c for c in cols if "usuario" in c.lower() and "creac" in c.lower()), None)
clase_col = next((c for c in cols if "clase" in c.lower() and "docto" in c.lower()), None)  # ✅ CORREGIDO
fecha_col = next((c for c in cols if "fecha" in c.lower() and "docto" in c.lower()), None)  # ✅ CORREGIDO
valor_col = next((c for c in cols if "valor" in c.lower() and "bruto" in c.lower()), None)  # ✅ CORREGIDO

print(f"  proveedor: '{proveedor_col}'")
print(f"  razon_social: '{razon_col}'")
print(f"  docto_proveedor: '{docto_col}'")
print(f"  co: '{co_col}'")
print(f"  nro_documento: '{nro_doc_col}'")
print(f"  usuario_creacion: '{usuario_col}'")
print(f"  clase_documento: '{clase_col}'")
print(f"  fecha_recibido: '{fecha_col}'")
print(f"  valor: '{valor_col}'")

if not all([proveedor_col, docto_col]):
    print(f"\n✗ ERROR: Columnas requeridas no encontradas")
    exit(1)

# ==============================================================================
# PASO 3: PROCESAR REGISTROS
# ==============================================================================

print(f"\nProcesando {len(df):,} registros...")

registros = []
for idx, (_, row) in enumerate(df.iterrows()):
    proveedor = str(row.get(proveedor_col, '')).strip() if proveedor_col else ''
    razon_social = str(row.get(razon_col, '')).strip() if razon_col else ''
    docto_proveedor = str(row.get(docto_col, '')).strip() if docto_col else ''
    co = str(row.get(co_col, '')).strip() if co_col else ''
    nro_documento = str(row.get(nro_doc_col, '')).strip() if nro_doc_col else ''
    usuario_creacion = str(row.get(usuario_col, '')).strip() if usuario_col else ''
    clase_documento = str(row.get(clase_col, '')).strip() if clase_col else ''
    
    # Fecha
    fecha_recibido = None
    if fecha_col:
        try:
            fecha_raw = row.get(fecha_col)
            if fecha_raw and not pd.isna(fecha_raw):
                if isinstance(fecha_raw, str):
                    fecha_recibido = pd.to_datetime(fecha_raw, format='%d/%m/%Y', errors='coerce').date()
                else:
                    fecha_recibido = fecha_raw.date() if hasattr(fecha_raw, 'date') else fecha_raw
        except:
            pass
    
    # Valor
    valor = 0.0
    if valor_col:
        try:
            valor_raw = row.get(valor_col, 0)
            if valor_raw and not pd.isna(valor_raw):
                if isinstance(valor_raw, str):
                    valor = float(valor_raw.strip().replace('.', '').replace(',', '.'))
                else:
                    valor = float(valor_raw)
        except:
            pass
    
    # Calculados
    prefijo = extraer_prefijo(docto_proveedor)
    folio_raw = extraer_folio(docto_proveedor)
    folio = ultimos_8_sin_ceros(folio_raw)
    clave_erp_comercial = crear_clave_factura(proveedor, prefijo, folio_raw)
    doc_causado_por = f"{co} - {usuario_creacion} - {nro_documento}"
    modulo = 'Comercial'
    
    registros.append({
        'proveedor': proveedor,
        'razon_social': razon_social,
        'docto_proveedor': docto_proveedor,
        'prefijo': prefijo,
        'folio': folio,
        'co': co,
        'nro_documento': nro_documento,
        'fecha_recibido': fecha_recibido,
        'usuario_creacion': usuario_creacion,
        'clase_documento': clase_documento,
        'valor': valor,
        'clave_erp_comercial': clave_erp_comercial,
        'doc_causado_por': doc_causado_por,
        'modulo': modulo
    })
    
    if (idx + 1) % 10000 == 0:
        print(f"  Procesados {idx+1:,} registros...")

print(f"✓ {len(registros):,} registros procesados")

# Mostrar muestra
if len(registros) > 0:
    print(f"\nMuestra del primer registro:")
    for key, value in list(registros[0].items())[:8]:
        print(f"  {key}: {value}")

# ==============================================================================
# PASO 4: INSERTAR EN POSTGRESQL
# ==============================================================================

print(f"\nConectando a PostgreSQL...")

database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)
raw_conn = engine.raw_connection()
cursor = raw_conn.cursor()

print("✓ Conectado")

# Crear tabla temporal
cursor.execute("""
    CREATE TEMP TABLE temp_erp_comercial_nuevos (LIKE erp_comercial INCLUDING DEFAULTS) ON COMMIT DROP
""")

# COPY FROM
print(f"\nInsertando {len(registros):,} registros...")

buffer = io.StringIO()
for reg in registros:
    buffer.write(f"{format_value_for_copy(reg['proveedor'])}\t")
    buffer.write(f"{format_value_for_copy(reg['razon_social'])}\t")
    buffer.write(f"{format_value_for_copy(reg['docto_proveedor'])}\t")
    buffer.write(f"{format_value_for_copy(reg['prefijo'])}\t")
    buffer.write(f"{format_value_for_copy(reg['folio'])}\t")
    buffer.write(f"{format_value_for_copy(reg['co'])}\t")
    buffer.write(f"{format_value_for_copy(reg['nro_documento'])}\t")
    buffer.write(f"{format_value_for_copy(reg['fecha_recibido'])}\t")
    buffer.write(f"{format_value_for_copy(reg['usuario_creacion'])}\t")
    buffer.write(f"{format_value_for_copy(reg['clase_documento'])}\t")
    buffer.write(f"{format_value_for_copy(reg['valor'])}\t")
    buffer.write(f"{format_value_for_copy(reg['clave_erp_comercial'])}\t")
    buffer.write(f"{format_value_for_copy(reg['doc_causado_por'])}\t")
    buffer.write(f"{format_value_for_copy(reg['modulo'])}\n")

buffer.seek(0)
cursor.copy_from(
    buffer,
    'temp_erp_comercial_nuevos',
    sep='\t',
    null='',
    columns=(
        'proveedor', 'razon_social', 'docto_proveedor', 'prefijo', 'folio',
        'co', 'nro_documento', 'fecha_recibido', 'usuario_creacion',
        'clase_documento', 'valor', 'clave_erp_comercial', 'doc_causado_por', 'modulo'
    )
)

print("  Datos copiados a tabla temporal")

# INSERT con ON CONFLICT
cursor.execute("""
    INSERT INTO erp_comercial (
        proveedor, razon_social, docto_proveedor, prefijo, folio,
        co, nro_documento, fecha_recibido, usuario_creacion,
        clase_documento, valor, clave_erp_comercial, doc_causado_por, modulo
    )
    SELECT 
        proveedor, razon_social, docto_proveedor, prefijo, folio,
        co, nro_documento, fecha_recibido, usuario_creacion,
        clase_documento, valor, clave_erp_comercial, doc_causado_por, modulo
    FROM temp_erp_comercial_nuevos
    ON CONFLICT (clave_erp_comercial) DO NOTHING
""")

insertados = cursor.rowcount
print(f"✓ {insertados:,} registros NUEVOS insertados (duplicados ignorados)")

# COMMIT
raw_conn.commit()
print("✓ Transacción confirmada")

# Verificar
cursor.execute("SELECT COUNT(*) FROM erp_comercial")
total = cursor.fetchone()[0]
print(f"✓ Total en tabla: {total:,} registros")

cursor.close()
raw_conn.close()

print("\n" + "="*80)
print("✓✓✓ CARGA COMPLETADA EXITOSAMENTE ✓✓✓")
print("="*80)
print()
