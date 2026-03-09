"""
CARGA OPTIMIZADA CON CHUNKS - TODAS LAS TABLAS
Procesa DIAN en bloques para evitar timeouts
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

def format_value_for_copy(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    if isinstance(value, str):
        value = value.replace('\\', '\\\\')
        value = value.replace('\t', '\\t')
        value = value.replace('\n', '\\n')
        value = value.replace('\r', '\\r')
        return value
    return str(value)

print("\n" + "="*80)
print("CARGA OPTIMIZADA CON CHUNKS")
print("="*80)
print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}\n")

database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)

# ==============================================================================
# TABLA 1: DIAN (66K registros) - EN CHUNKS
# ==============================================================================

print("-"*80)
print("CARGANDO DIAN (66K registros)")
print("-"*80)

archivo_dian = r'uploads\dian\Dian_23022026.xlsx'

print("Leyendo Excel completo (13.96 MB)... esto puede tomar 30-60 segundos...")
inicio_total = datetime.now()

df_dian = pd.read_excel(archivo_dian, engine='openpyxl')
tiempo_lectura = (datetime.now() - inicio_total).total_seconds()
print(f"✓ Leídas {len(df_dian):,} filas en {tiempo_lectura:.1f} segundos")

# Normalizar columnas
df_dian.columns = [normalizar_columna(col) for col in df_dian.columns]

chunk_size = 10000
total_insertados_dian = 0

raw_conn = engine.raw_connection()
cursor = raw_conn.cursor()

# Procesar en chunks (en memoria)
print(f"\nProcesando en bloques de {chunk_size:,} registros...")
for chunk_num in range(0, len(df_dian), chunk_size):
    df_chunk = df_dian[chunk_num:chunk_num + chunk_size]
    print(f"\n📦 BLOQUE {chunk_num//chunk_size + 1} - Filas {chunk_num+1:,} a {min(chunk_num+chunk_size, len(df_dian)):,}")
    
    # Detectar columnas
    cols = df_chunk.columns.tolist()
    nit_col = next((c for c in cols if "nit" in c.lower() and "adquir" in c.lower()), None)
    razon_col = next((c for c in cols if "razon" in c.lower() and "social" in c.lower()), None)
    numero_col = next((c for c in cols if "numero" in c.lower() and "documento" not in c.lower()), None)
    fecha_col = next((c for c in cols if "fecha" in c.lower() and ("factur" in c.lower() or "gener" in c.lower())), None)
    valor_col = next((c for c in cols if "total" in c.lower() and "documento" in c.lower()), None)
    
    # Procesar chunk
    registros = []
    for _, row in df_chunk.iterrows():
        nit_adquiriente = str(row.get(nit_col, '')).strip() if nit_col else ''
        razon_social = str(row.get(razon_col, '')).strip() if razon_col else ''
        numero_documento = str(row.get(numero_col, '')).strip() if numero_col else ''
        
        fecha_factura = None
        if fecha_col:
            try:
                fecha_raw = row.get(fecha_col)
                if fecha_raw and not pd.isna(fecha_raw):
                    if isinstance(fecha_raw, str):
                        fecha_factura = pd.to_datetime(fecha_raw, format='%d/%m/%Y', errors='coerce').date()
                    else:
                        fecha_factura = fecha_raw.date() if hasattr(fecha_raw, 'date') else fecha_raw
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
        
        prefijo = extraer_prefijo(numero_documento)
        folio_raw = extraer_folio(numero_documento)
        folio = ultimos_8_sin_ceros(folio_raw)
        clave_dian = crear_clave_factura(nit_adquiriente, prefijo, folio_raw)
        
        registros.append({
            'nit_adquiriente': nit_adquiriente,
            'razon_social': razon_social,
            'numero': numero_documento,
            'prefijo': prefijo,
            'folio': folio,
            'fecha_factura': fecha_factura,
            'valor': valor,
            'clave_dian': clave_dian
        })
    
    print(f"  ✓ Procesados {len(registros):,} registros")
    
    # Insertar chunk
    cursor.execute("CREATE TEMP TABLE temp_dian_chunk (LIKE dian INCLUDING DEFAULTS) ON COMMIT DROP")
    
    buffer = io.StringIO()
    for reg in registros:
        buffer.write(f"{format_value_for_copy(reg['nit_adquiriente'])}\t")
        buffer.write(f"{format_value_for_copy(reg['razon_social'])}\t")
        buffer.write(f"{format_value_for_copy(reg['numero'])}\t")
        buffer.write(f"{format_value_for_copy(reg['prefijo'])}\t")
        buffer.write(f"{format_value_for_copy(reg['folio'])}\t")
        buffer.write(f"{format_value_for_copy(reg['fecha_factura'])}\t")
        buffer.write(f"{format_value_for_copy(reg['valor'])}\t")
        buffer.write(f"{format_value_for_copy(reg['clave_dian'])}\n")
    
    buffer.seek(0)
    cursor.copy_from(buffer, 'temp_dian_chunk', sep='\t', null='',
                     columns=('nit_adquiriente', 'razon_social', 'numero', 'prefijo', 'folio', 
                             'fecha_factura', 'valor', 'clave_dian'))
    
    cursor.execute("""
        INSERT INTO dian (nit_adquiriente, razon_social, numero, prefijo, folio, fecha_factura, valor, clave_dian)
        SELECT * FROM temp_dian_chunk
        ON CONFLICT (clave_dian) DO NOTHING
    """)
    
    insertados = cursor.rowcount
    total_insertados_dian += insertados
    print(f"  ✓ {insertados:,} registros insertados (total acumulado: {total_insertados_dian:,})")
    
    raw_conn.commit()

tiempo_dian = (datetime.now() - inicio_total).total_seconds()
print(f"\n✅ DIAN COMPLETADO: {total_insertados_dian:,} registros en {tiempo_dian:.1f} segundos")

# ==============================================================================
# TABLA 2: ERP FINANCIERO (3K registros)
# ==============================================================================

print("\n" + "-"*80)
print("CARGANDO ERP FINANCIERO (3K registros)")
print("-"*80)

archivo_erp_fn = r'uploads\erp_fn\erp_financiero_23022026.xlsx'

print("Leyendo Excel...")
df_fn = pd.read_excel(archivo_erp_fn, engine='openpyxl')
df_fn.columns = [normalizar_columna(col) for col in df_fn.columns]

print(f"✓ Leídas {len(df_fn):,} filas")

# Detectar (CORREGIDO)
cols = df_fn.columns.tolist()
proveedor_col = next((c for c in cols if "proveedor" in c.lower() and "razon" not in c.lower()), None)
razon_col = next((c for c in cols if "razon" in c.lower() and "social" in c.lower()), None)
docto_col = next((c for c in cols if "docto" in c.lower() and "proveedor" in c.lower()), None)
co_col = next((c for c in cols if c.upper() == "CO" or c.upper() == "C.O."), None)
nro_doc_col = next((c for c in cols if "nro" in c.lower() and "documento" in c.lower()), None)
usuario_col = next((c for c in cols if "usuario" in c.lower() and "creac" in c.lower()), None)
clase_col = next((c for c in cols if "clase" in c.lower() and "docto" in c.lower()), None)  # ✅
fecha_col = next((c for c in cols if "fecha" in c.lower() and ("proveedor" in c.lower() or "docto" in c.lower())), None)  # ✅
valor_col = next((c for c in cols if "valor" in c.lower() and ("subtotal" in c.lower() or "bruto" in c.lower())), None)  # ✅

print(f"Procesando {len(df_fn):,} registros...")

registros_fn = []
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
                if isinstance(fecha_raw, str):
                    fecha_recibido = pd.to_datetime(fecha_raw, format='%d/%m/%Y', errors='coerce').date()
                else:
                    fecha_recibido = fecha_raw.date() if hasattr(fecha_raw, 'date') else fecha_raw
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
    clave_erp_financiero = crear_clave_factura(proveedor, prefijo, folio_raw)
    doc_causado_por = f"{co} - {usuario_creacion} - {nro_documento}"
    
    registros_fn.append({
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
        'clave_erp_financiero': clave_erp_financiero,
        'doc_causado_por': doc_causado_por,
        'modulo': 'Financiero'
    })

print(f"✓ Procesados {len(registros_fn):,}")

# Insertar
cursor.execute("CREATE TEMP TABLE temp_erp_fn_nuevos (LIKE erp_financiero INCLUDING DEFAULTS) ON COMMIT DROP")

buffer = io.StringIO()
for reg in registros_fn:
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
    buffer.write(f"{format_value_for_copy(reg['clave_erp_financiero'])}\t")
    buffer.write(f"{format_value_for_copy(reg['doc_causado_por'])}\t")
    buffer.write(f"{format_value_for_copy(reg['modulo'])}\n")

buffer.seek(0)
cursor.copy_from(buffer, 'temp_erp_fn_nuevos', sep='\t', null='',
                 columns=('proveedor', 'razon_social', 'docto_proveedor', 'prefijo', 'folio',
                         'co', 'nro_documento', 'fecha_recibido', 'usuario_creacion',
                         'clase_documento', 'valor', 'clave_erp_financiero', 'doc_causado_por', 'modulo'))

cursor.execute("""
    INSERT INTO erp_financiero (
        proveedor, razon_social, docto_proveedor, prefijo, folio,
        co, nro_documento, fecha_recibido, usuario_creacion,
        clase_documento, valor, clave_erp_financiero, doc_causado_por, modulo
    )
    SELECT * FROM temp_erp_fn_nuevos
    ON CONFLICT (clave_erp_financiero) DO NOTHING
""")

insertados_fn = cursor.rowcount
raw_conn.commit()
print(f"✓ {insertados_fn:,} registros insertados")

cursor.close()
raw_conn.close()

# ==============================================================================
# RESUMEN
# ==============================================================================

print("\n" + "="*80)
print("RESUMEN FINAL")
print("="*80)

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM dian"))
    total_dian = result.scalar()
    print(f"\n📊 DIAN: {total_dian:,} registros")
    
    result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial"))
    total_cm = result.scalar()
    print(f"📊 ERP Comercial: {total_cm:,} registros")
    
    result = conn.execute(text("SELECT COUNT(*) FROM erp_financiero"))
    total_fn = result.scalar()
    print(f"📊 ERP Financiero: {total_fn:,} registros")
    
    total_general = total_dian + total_cm + total_fn
    print(f"\n✅ TOTAL GENERAL: {total_general:,} registros")

tiempo_total = (datetime.now() - inicio_total).total_seconds()
print(f"\n⏱️  Tiempo total: {tiempo_total:.1f} segundos ({tiempo_total/60:.1f} minutos)")
print("="*80 + "\n")
