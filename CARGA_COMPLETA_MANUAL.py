"""
CARGA COMPLETA MANUAL DE ARCHIVOS DIAN VS ERP
Este script replica EXACTAMENTE el proceso del navegador
"""
import polars as pl
import psycopg2
import io
from datetime import date, datetime
import pandas as pd
import unicodedata
import os
import sys

# FORZAR ENCODING UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print("\n" + "="*80)
print("CARGA COMPLETA MANUAL - DIAN VS ERP")
print("="*80)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================================================
# FUNCIONES AUXILIARES (copiadas de routes.py)
# ============================================================================

def normalizar_columna(nombre):
    """Normaliza nombre: lowercase, sin tildes, espacios→guion bajo, sin puntos"""
    sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', str(nombre))
        if unicodedata.category(c) != 'Mn'
    )
    # Lowercase, espacios→guion bajo, quitar puntos finales
    resultado = sin_tildes.lower().strip().replace(' ', '_')
    resultado = resultado.rstrip('.')  # Quitar puntos al final
    return resultado

def extraer_prefijo(docto):
    """Extrae prefijo de documento (letras Y números, sin guiones/puntos/espacios)"""
    import re
    s = str(docto).strip()
    prefijo = re.sub(r'[\-\.\s]', '', s)
    return prefijo if prefijo else ''

def extraer_folio(docto):
    """Extrae solo dígitos del documento"""
    s = str(docto).strip()
    digitos = ''.join(c for c in s if c.isdigit())
    return digitos if digitos else '0'

def ultimos_8_sin_ceros(folio_str):
    """Retorna últimos 8 caracteres sin ceros a la izquierda"""
    s = str(folio_str).strip()
    if len(s) > 8:
        s = s[-8:]
    return s.lstrip('0') or '0'

def crear_clave_factura(nit, prefijo, folio):
    """Crea clave única: NIT-PREFIJO-FOLIO"""
    return f"{nit}-{prefijo}-{folio}"

def format_value_for_copy(value):
    """Formatea valor para COPY FROM"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    if isinstance(value, str):
        return value.replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
    return str(value)

# ============================================================================
# PASO 1: VERIFICAR ARCHIVOS
# ============================================================================

archivos = {
    'DIAN': r'uploads\dian\Dian_23022026.xlsx',
    'ERP_FN': r'uploads\erp_fn\erp_financiero_23022026.xlsx',
    'ERP_CM': r'uploads\erp_cm\ERP_comercial_23022026.xlsx',
    'ACUSES': r'uploads\acuses\acuses_23022026.xlsx'
}

print("\n" + "="*80)
print("PASO 1: VERIFICAR ARCHIVOS")
print("="*80)

for nombre, ruta in archivos.items():
    if os.path.exists(ruta):
        size_mb = os.path.getsize(ruta) / (1024*1024)
        print(f"✅ {nombre}: {ruta} ({size_mb:.2f} MB)")
    else:
        print(f"❌ {nombre}: NO ENCONTRADO - {ruta}")
        exit()

# ============================================================================
# PASO 2: LEER ARCHIVOS CON POLARS
# ============================================================================

print("\n" + "="*80)
print("PASO 2: LEER ARCHIVOS CON POLARS")
print("="*80)

print("\n📂 Leyendo DIAN...")
d = pl.read_excel(archivos['DIAN'], engine='calamine')
print(f"✅ DIAN: {d.height:,} filas, {d.width} columnas")

# Normalizar columnas DIAN
columnas_dian = [normalizar_columna(c) for c in d.columns]
d.columns = columnas_dian
print(f"   Columnas: {', '.join(columnas_dian[:5])}...")

print("\n📂 Leyendo ERP Financiero...")
erp_fn = pl.read_excel(archivos['ERP_FN'], engine='calamine')
print(f"✅ ERP Financiero: {erp_fn.height:,} filas, {erp_fn.width} columnas")

# Normalizar columnas ERP FN
columnas_fn = [normalizar_columna(c) for c in erp_fn.columns]
erp_fn.columns = columnas_fn

print("\n📂 Leyendo ERP Comercial...")
erp_cm = pl.read_excel(archivos['ERP_CM'], engine='calamine')
print(f"✅ ERP Comercial: {erp_cm.height:,} filas, {erp_cm.width} columnas")

# Normalizar columnas ERP CM
columnas_cm = [normalizar_columna(c) for c in erp_cm.columns]
erp_cm.columns = columnas_cm

print("\n📂 Leyendo ACUSES...")
acuses_df = pl.read_excel(archivos['ACUSES'], engine='calamine')
print(f"✅ ACUSES: {acuses_df.height:,} filas, {acuses_df.width} columnas")

# Normalizar columnas ACUSES
columnas_acuses = [normalizar_columna(c) for c in acuses_df.columns]
acuses_df.columns = columnas_acuses
print(f"   Columnas: {', '.join(columnas_acuses[:8])}...")

# Procesar acuses a diccionario (CUFE → Estado)
acuses_por_cufe = {}
if 'cufe' in columnas_acuses and 'estado_docto' in columnas_acuses:
    df_ac = acuses_df.to_pandas()
    for _, row in df_ac.iterrows():
        cufe = str(row.get('cufe', ''))
        estado = str(row.get('estado_docto', ''))
        if cufe and cufe != 'nan':
            acuses_por_cufe[cufe.strip()] = estado.strip()
    print(f"✅ {len(acuses_por_cufe):,} acuses procesados (CUFE → Estado)")
else:
    print("⚠️ No se encontraron columnas CUFE o ESTADO en acuses")

# ============================================================================
# PASO 3: CONSOLIDAR TIPOS DE TERCERO
# ============================================================================

print("\n" + "="*80)
print("PASO 3: CONSOLIDAR TIPOS DE TERCERO")
print("="*80)

tipo_tercero_por_nit = {}

# De DIAN
df_dian = d.to_pandas()
for col in df_dian.columns:
    if 'nit' in col and 'emisor' in col:
        for nit in df_dian[col].dropna().unique():
            nit_str = str(nit).strip()
            if nit_str and nit_str != 'nan':
                nit_limpio = extraer_folio(nit_str)
                if nit_limpio not in tipo_tercero_por_nit:
                    tipo_tercero_por_nit[nit_limpio] = set()
                tipo_tercero_por_nit[nit_limpio].add('PROVEEDOR')
        break

# De ERP Financiero
df_fn = erp_fn.to_pandas()
for col in df_fn.columns:
    if 'proveedor' in col and 'razon' not in col.lower():
        for nit in df_fn[col].dropna().unique():
            nit_str = str(nit).strip()
            if nit_str and nit_str != 'nan':
                nit_limpio = extraer_folio(nit_str)
                if nit_limpio not in tipo_tercero_por_nit:
                    tipo_tercero_por_nit[nit_limpio] = set()
                tipo_tercero_por_nit[nit_limpio].add('ACREEDOR')
        break

# De ERP Comercial
df_cm = erp_cm.to_pandas()
for col in df_cm.columns:
    if 'proveedor' in col and 'razon' not in col.lower():
        for nit in df_cm[col].dropna().unique():
            nit_str = str(nit).strip()
            if nit_str and nit_str != 'nan':
                nit_limpio = extraer_folio(nit_str)
                if nit_limpio not in tipo_tercero_por_nit:
                    tipo_tercero_por_nit[nit_limpio] = set()
                tipo_tercero_por_nit[nit_limpio].add('PROVEEDOR')
        break

# Consolidar tipos
tipo_tercero_final = {}
for nit, tipos in tipo_tercero_por_nit.items():
    if 'PROVEEDOR' in tipos and 'ACREEDOR' in tipos:
        tipo_tercero_final[nit] = 'PROVEEDOR Y ACREEDOR'
    elif 'PROVEEDOR' in tipos:
        tipo_tercero_final[nit] = 'PROVEEDOR'
    elif 'ACREEDOR' in tipos:
        tipo_tercero_final[nit] = 'ACREEDOR'

print(f"✅ {len(tipo_tercero_final):,} terceros clasificados")
print(f"   Primeros 5: {list(tipo_tercero_final.items())[:5]}")

# ============================================================================
# PASO 4: CONECTAR A BASE DE DATOS
# ============================================================================

print("\n" + "="*80)
print("PASO 4: CONECTAR A POSTGRESQL")
print("="*80)

try:
    from sqlalchemy import create_engine
    # Usar la MISMA string de conexión que usa routes.py
    DATABASE_URI = "postgresql://postgres:654321@localhost:5432/gestor_documental"
    engine = create_engine(DATABASE_URI)
    raw_conn = engine.raw_connection()
    cursor = raw_conn.cursor()
    print("OK Conexion exitosa a PostgreSQL (SQLAlchemy)")
except Exception as e:
    print(f"ERROR conectando: {e}")
    import traceback
    traceback.print_exc()
    exit()

# ============================================================================
# PASO 5: INSERTAR EN TABLA DIAN
# ============================================================================

print("\n" + "="*80)
print("PASO 5: INSERTAR EN TABLA DIAN")
print("="*80)

# Preparar registros
registros_dian = []
fecha_hoy = date.today()

# Crear diccionario de columnas originales
columnas_originales = {}
for col in df_dian.columns:
    col_norm = normalizar_columna(col)
    columnas_originales[col_norm] = col
    columnas_originales[col_norm.replace('_', '')] = col

# Detectar columna CUFE
cufe_col_name = None
for col in df_dian.columns:
    if 'cufe' in col or 'cude' in col:
        cufe_col_name = col
        break
if not cufe_col_name:
    cufe_col_name = 'cufe/cude' if 'cufe/cude' in df_dian.columns else df_dian.columns[1]

print(f"📋 Procesando {len(df_dian):,} facturas DIAN...")

for idx, row in df_dian.iterrows():
    # NIT y razón social
    nit = str(row.get('nit_emisor', row.get('nitemior', ''))).strip()
    nit_limpio = extraer_folio(nit)
    razon_social = str(row.get('nombre_emisor', row.get('nombreemisor', ''))).strip()
    
    # Fecha de emisión
    fecha_emision = fecha_hoy
    try:
        fecha_col = 'fecha_de_emision' if 'fecha_de_emision' in df_dian.columns else 'fechadeemision'
        fecha_raw = row.get(fecha_col)
        if fecha_raw and not pd.isna(fecha_raw):
            if isinstance(fecha_raw, str):
                fecha_emision = pd.to_datetime(fecha_raw, format='%d/%m/%Y', errors='coerce').date()
            elif isinstance(fecha_raw, (pd.Timestamp, datetime)):
                fecha_emision = fecha_raw.date() if hasattr(fecha_raw, 'date') else fecha_raw
    except:
        pass
    
    # Prefijo y folio
    prefijo_folio = str(row.get('numero_de_factura_electronica', row.get('numerodefacturaelectronica', '')))
    prefijo = extraer_prefijo(prefijo_folio)
    folio_raw = extraer_folio(prefijo_folio)
    folio = ultimos_8_sin_ceros(folio_raw)
    
    # Valor
    valor = 0.0
    try:
        valor_col = 'total_factura' if 'total_factura' in df_dian.columns else 'totalfactura'
        valor_raw = row.get(valor_col, 0)
        if valor_raw and not pd.isna(valor_raw):
            if isinstance(valor_raw, str):
                valor = float(valor_raw.strip().replace('.', '').replace(',', '.'))
            else:
                valor = float(valor_raw)
    except:
        pass
    
    # Otros campos
    tipo_documento = str(row.get('tipo_de_documento', 'Factura Electrónica'))
    cufe = str(row.get(cufe_col_name, ''))
    forma_pago = str(row.get('forma_de_pago', '2')).strip()
    
    # Campos calculados
    clave = crear_clave_factura(nit_limpio, prefijo, folio_raw)
    clave_acuse = cufe
    tipo_tercero = tipo_tercero_final.get(nit_limpio, '')
    n_dias = (fecha_hoy - fecha_emision).days if fecha_emision else 0
    modulo = 'DIAN'
    
    registros_dian.append({
        'nit_emisor': nit_limpio,
        'nombre_emisor': razon_social,
        'fecha_emision': fecha_emision,
        'prefijo': prefijo,
        'folio': folio,
        'total': valor,
        'tipo_documento': tipo_documento,
        'cufe_cude': cufe,
        'forma_pago': forma_pago,
        'clave': clave,
        'clave_acuse': clave_acuse,
        'tipo_tercero': tipo_tercero,
        'n_dias': n_dias,
        'modulo': modulo
    })
    
    if (idx + 1) % 10000 == 0:
        print(f"   Procesadas {idx+1:,} facturas...")

print(f"✅ {len(registros_dian):,} registros DIAN preparados")

# Mostrar primeros 3 registros para validación
print("\n🔍 Primeros 3 registros DIAN:")
for i, reg in enumerate(registros_dian[:3]):
    print(f"\n   Registro {i+1}:")
    print(f"      NIT: {reg['nit_emisor']}")
    print(f"      Razón Social: {reg['nombre_emisor'][:50]}...")
    print(f"      Prefijo: '{reg['prefijo']}'")
    print(f"      Folio: '{reg['folio']}'")
    print(f"      Valor: ${reg['total']:,.2f}")
    print(f"      Fecha: {reg['fecha_emision']}")
    print(f"      CUFE: {reg['cufe_cude'][:50]}...")

# Crear tabla temporal
print("\n📦 Creando tabla temporal...")
cursor.execute("""
    CREATE TEMP TABLE temp_dian_nuevos (LIKE dian INCLUDING DEFAULTS) ON COMMIT DROP
""")

# COPY FROM
print("📥 Ejecutando COPY FROM...")
buffer = io.StringIO()
for reg in registros_dian:
    buffer.write(f"{format_value_for_copy(reg['nit_emisor'])}\t")
    buffer.write(f"{format_value_for_copy(reg['nombre_emisor'])}\t")
    buffer.write(f"{format_value_for_copy(reg['fecha_emision'])}\t")
    buffer.write(f"{format_value_for_copy(reg['prefijo'])}\t")
    buffer.write(f"{format_value_for_copy(reg['folio'])}\t")
    buffer.write(f"{format_value_for_copy(reg['total'])}\t")
    buffer.write(f"{format_value_for_copy(reg['tipo_documento'])}\t")
    buffer.write(f"{format_value_for_copy(reg['cufe_cude'])}\t")
    buffer.write(f"{format_value_for_copy(reg['forma_pago'])}\t")
    buffer.write(f"{format_value_for_copy(reg['clave'])}\t")
    buffer.write(f"{format_value_for_copy(reg['clave_acuse'])}\t")
    buffer.write(f"{format_value_for_copy(reg['tipo_tercero'])}\t")
    buffer.write(f"{format_value_for_copy(reg['n_dias'])}\t")
    buffer.write(f"{format_value_for_copy(reg['modulo'])}\n")

buffer.seek(0)
cursor.copy_from(
    buffer,
    'temp_dian_nuevos',
    sep='\t',
    null='',
    columns=(
        'nit_emisor', 'nombre_emisor', 'fecha_emision',
        'prefijo', 'folio', 'total', 'tipo_documento', 'cufe_cude',
        'forma_pago', 'clave', 'clave_acuse', 'tipo_tercero', 'n_dias', 'modulo'
    )
)

print("✅ COPY FROM completado")

# INSERT con protección contra duplicados
print("📝 INSERT INTO dian...")
try:
    cursor.execute("""
        INSERT INTO dian (
            nit_emisor, nombre_emisor, fecha_emision, prefijo, folio, total,
            tipo_documento, cufe_cude, forma_pago, clave, clave_acuse,
            tipo_tercero, n_dias, modulo
        )
        SELECT 
            nit_emisor, nombre_emisor, fecha_emision, prefijo, folio, total,
            tipo_documento, cufe_cude, forma_pago, clave, clave_acuse,
            tipo_tercero, n_dias, modulo
        FROM temp_dian_nuevos
        ON CONFLICT (cufe_cude) DO NOTHING
    """)
    insertados_dian = cursor.rowcount
    print(f"✅ {insertados_dian:,} registros DIAN insertados (duplicados ignorados)")
except Exception as e:
    print(f"ERROR insertando DIAN: {e}")
    raw_conn.rollback()
    cursor.close()
    raw_conn.close()
    exit()

# ============================================================================
# PASO 6: INSERTAR EN TABLA ERP_COMERCIAL
# ============================================================================

print("\n" + "="*80)
print("PASO 6: INSERTAR EN TABLA ERP_COMERCIAL")
print("="*80)

# Detectar columnas dinámicamente
cols_cm = df_cm.columns.tolist()
proveedor_col = next((c for c in cols_cm if "proveedor" in c.lower() and "razon" not in c.lower()), None)
razon_col = next((c for c in cols_cm if "razon" in c.lower() and "social" in c.lower()), None)
docto_col = next((c for c in cols_cm if "docto" in c.lower() and "proveedor" in c.lower()), None)
co_col = next((c for c in cols_cm if c.lower() == "co" or c.lower() == "c.o."), None)
nro_doc_col = next((c for c in cols_cm if "nro" in c.lower() and "documento" in c.lower()), None)
usuario_col = next((c for c in cols_cm if "usuario" in c.lower() and "creac" in c.lower()), None)
clase_col = next((c for c in cols_cm if "clase" in c.lower() and "documento" in c.lower()), None)
fecha_col_cm = next((c for c in cols_cm if "fecha" in c.lower() and "recib" in c.lower()), None)
valor_col_cm = next((c for c in cols_cm if "total" in c.lower() and "bruto" in c.lower()), None)

print(f"📋 Columnas detectadas:")
print(f"   Proveedor: {proveedor_col}")
print(f"   Docto Proveedor: {docto_col}")
print(f"   CO: {co_col}")
print(f"   Valor: {valor_col_cm}")

if not all([proveedor_col, docto_col]):
    print("⚠️ Columnas requeridas no encontradas, saltando ERP Comercial")
    registros_cm = []
else:
    registros_cm = []
    
    for idx, row in df_cm.iterrows():
        proveedor = str(row.get(proveedor_col, '')).strip() if proveedor_col else ''
        razon_social_cm = str(row.get(razon_col, '')).strip() if razon_col else ''
        docto_proveedor = str(row.get(docto_col, '')).strip() if docto_col else ''
        co = str(row.get(co_col, '')).strip() if co_col else ''
        nro_documento = str(row.get(nro_doc_col, '')).strip() if nro_doc_col else ''
        usuario_creacion = str(row.get(usuario_col, '')).strip() if usuario_col else ''
        clase_documento = str(row.get(clase_col, '')).strip() if clase_col else ''
        
        # Fecha
        fecha_recibido = None
        if fecha_col_cm:
            try:
                fecha_raw = row.get(fecha_col_cm)
                if fecha_raw and not pd.isna(fecha_raw):
                    if isinstance(fecha_raw, str):
                        fecha_recibido = pd.to_datetime(fecha_raw, format='%d/%m/%Y', errors='coerce').date()
                    else:
                        fecha_recibido = fecha_raw.date() if hasattr(fecha_raw, 'date') else fecha_raw
            except:
                pass
        
        # Valor
        valor_cm = 0.0
        if valor_col_cm:
            try:
                valor_raw = row.get(valor_col_cm, 0)
                if valor_raw and not pd.isna(valor_raw):
                    if isinstance(valor_raw, str):
                        valor_cm = float(valor_raw.strip().replace('.', '').replace(',', '.'))
                    else:
                        valor_cm = float(valor_raw)
            except:
                pass
        
        # Campos calculados
        prefijo_cm = extraer_prefijo(docto_proveedor)
        folio_raw_cm = extraer_folio(docto_proveedor)
        folio_cm = ultimos_8_sin_ceros(folio_raw_cm)
        clave_erp_comercial = crear_clave_factura(proveedor, prefijo_cm, folio_raw_cm)
        doc_causado_por = f"{co} - {usuario_creacion} - {nro_documento}"
        modulo_cm = 'Comercial'
        
        registros_cm.append({
            'proveedor': proveedor,
            'razon_social': razon_social_cm,
            'docto_proveedor': docto_proveedor,
            'prefijo': prefijo_cm,
            'folio': folio_cm,
            'co': co,
            'nro_documento': nro_documento,
            'fecha_recibido': fecha_recibido,
            'usuario_creacion': usuario_creacion,
            'clase_documento': clase_documento,
            'valor': valor_cm,
            'clave_erp_comercial': clave_erp_comercial,
            'doc_causado_por': doc_causado_por,
            'modulo': modulo_cm
        })
        
        if (idx + 1) % 10000 == 0:
            print(f"   Procesadas {idx+1:,} registros...")
    
    print(f"✅ {len(registros_cm):,} registros ERP Comercial preparados")
    
    # Crear tabla temporal
    cursor.execute("""
        CREATE TEMP TABLE temp_erp_comercial_nuevos (LIKE erp_comercial INCLUDING DEFAULTS) ON COMMIT DROP
    """)
    
    # COPY FROM
    buffer_cm = io.StringIO()
    for reg in registros_cm:
        buffer_cm.write(f"{format_value_for_copy(reg['proveedor'])}\t")
        buffer_cm.write(f"{format_value_for_copy(reg['razon_social'])}\t")
        buffer_cm.write(f"{format_value_for_copy(reg['docto_proveedor'])}\t")
        buffer_cm.write(f"{format_value_for_copy(reg['prefijo'])}\t")
        buffer_cm.write(f"{format_value_for_copy(reg['folio'])}\t")
        buffer_cm.write(f"{format_value_for_copy(reg['co'])}\t")
        buffer_cm.write(f"{format_value_for_copy(reg['nro_documento'])}\t")
        buffer_cm.write(f"{format_value_for_copy(reg['fecha_recibido'])}\t")
        buffer_cm.write(f"{format_value_for_copy(reg['usuario_creacion'])}\t")
        buffer_cm.write(f"{format_value_for_copy(reg['clase_documento'])}\t")
        buffer_cm.write(f"{format_value_for_copy(reg['valor'])}\t")
        buffer_cm.write(f"{format_value_for_copy(reg['clave_erp_comercial'])}\t")
        buffer_cm.write(f"{format_value_for_copy(reg['doc_causado_por'])}\t")
        buffer_cm.write(f"{format_value_for_copy(reg['modulo'])}\n")
    
    buffer_cm.seek(0)
    cursor.copy_from(
        buffer_cm,
        'temp_erp_comercial_nuevos',
        sep='\t',
        null='',
        columns=(
            'proveedor', 'razon_social', 'docto_proveedor', 'prefijo', 'folio',
            'co', 'nro_documento', 'fecha_recibido', 'usuario_creacion',
            'clase_documento', 'valor', 'clave_erp_comercial', 'doc_causado_por', 'modulo'
        )
    )
    
    # INSERT
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
    
    insertados_cm = cursor.rowcount
    print(f"✅ {insertados_cm:,} registros ERP Comercial insertados")

# ============================================================================
# PASO 7: INSERTAR EN TABLA ERP_FINANCIERO
# ============================================================================

print("\n" + "="*80)
print("PASO 7: INSERTAR EN TABLA ERP_FINANCIERO")
print("="*80)

# Detectar columnas dinámicamente
cols_fn = df_fn.columns.tolist()
proveedor_col_fn = next((c for c in cols_fn if "proveedor" in c.lower() and "razon" not in c.lower()), None)
razon_col_fn = next((c for c in cols_fn if "razon" in c.lower() and "social" in c.lower()), None)
docto_col_fn = next((c for c in cols_fn if "docto" in c.lower() and "proveedor" in c.lower()), None)
co_col_fn = next((c for c in cols_fn if c.lower() == "co" or c.lower() == "c.o."), None)
nro_doc_col_fn = next((c for c in cols_fn if "nro" in c.lower() and "documento" in c.lower()), None)
usuario_col_fn = next((c for c in cols_fn if "usuario" in c.lower() and "creac" in c.lower()), None)
clase_col_fn = next((c for c in cols_fn if "clase" in c.lower() and "documento" in c.lower()), None)
fecha_col_fn = next((c for c in cols_fn if "fecha" in c.lower() and "recib" in c.lower()), None)
valor_col_fn = next((c for c in cols_fn if "total" in c.lower() and "bruto" in c.lower()), None)

print(f"📋 Columnas detectadas:")
print(f"   Proveedor: {proveedor_col_fn}")
print(f"   Docto Proveedor: {docto_col_fn}")

if not all([proveedor_col_fn, docto_col_fn]):
    print("⚠️ Columnas requeridas no encontradas, saltando ERP Financiero")
    registros_fn = []
else:
    registros_fn = []
    
    for idx, row in df_fn.iterrows():
        proveedor_fn = str(row.get(proveedor_col_fn, '')).strip() if proveedor_col_fn else ''
        razon_social_fn = str(row.get(razon_col_fn, '')).strip() if razon_col_fn else ''
        docto_proveedor_fn = str(row.get(docto_col_fn, '')).strip() if docto_col_fn else ''
        co_fn = str(row.get(co_col_fn, '')).strip() if co_col_fn else ''
        nro_documento_fn = str(row.get(nro_doc_col_fn, '')).strip() if nro_doc_col_fn else ''
        usuario_creacion_fn = str(row.get(usuario_col_fn, '')).strip() if usuario_col_fn else ''
        clase_documento_fn = str(row.get(clase_col_fn, '')).strip() if clase_col_fn else ''
        
        # Fecha
        fecha_recibido_fn = None
        if fecha_col_fn:
            try:
                fecha_raw = row.get(fecha_col_fn)
                if fecha_raw and not pd.isna(fecha_raw):
                    if isinstance(fecha_raw, str):
                        fecha_recibido_fn = pd.to_datetime(fecha_raw, format='%d/%m/%Y', errors='coerce').date()
                    else:
                        fecha_recibido_fn = fecha_raw.date() if hasattr(fecha_raw, 'date') else fecha_raw
            except:
                pass
        
        # Valor
        valor_fn = 0.0
        if valor_col_fn:
            try:
                valor_raw = row.get(valor_col_fn, 0)
                if valor_raw and not pd.isna(valor_raw):
                    if isinstance(valor_raw, str):
                        valor_fn = float(valor_raw.strip().replace('.', '').replace(',', '.'))
                    else:
                        valor_fn = float(valor_raw)
            except:
                pass
        
        # Campos calculados
        prefijo_fn = extraer_prefijo(docto_proveedor_fn)
        folio_raw_fn = extraer_folio(docto_proveedor_fn)
        folio_fn = ultimos_8_sin_ceros(folio_raw_fn)
        clave_erp_financiero = crear_clave_factura(proveedor_fn, prefijo_fn, folio_raw_fn)
        doc_causado_por_fn = f"{co_fn} - {usuario_creacion_fn} - {nro_documento_fn}"
        modulo_fn = 'Financiero'
        
        registros_fn.append({
            'proveedor': proveedor_fn,
            'razon_social': razon_social_fn,
            'docto_proveedor': docto_proveedor_fn,
            'prefijo': prefijo_fn,
            'folio': folio_fn,
            'co': co_fn,
            'nro_documento': nro_documento_fn,
            'fecha_recibido': fecha_recibido_fn,
            'usuario_creacion': usuario_creacion_fn,
            'clase_documento': clase_documento_fn,
            'valor': valor_fn,
            'clave_erp_financiero': clave_erp_financiero,
            'doc_causado_por': doc_causado_por_fn,
            'modulo': modulo_fn
        })
    
    print(f"✅ {len(registros_fn):,} registros ERP Financiero preparados")
    
    # Crear tabla temporal
    cursor.execute("""
        CREATE TEMP TABLE temp_erp_financiero_nuevos (LIKE erp_financiero INCLUDING DEFAULTS) ON COMMIT DROP
    """)
    
    # COPY FROM
    buffer_fn = io.StringIO()
    for reg in registros_fn:
        buffer_fn.write(f"{format_value_for_copy(reg['proveedor'])}\t")
        buffer_fn.write(f"{format_value_for_copy(reg['razon_social'])}\t")
        buffer_fn.write(f"{format_value_for_copy(reg['docto_proveedor'])}\t")
        buffer_fn.write(f"{format_value_for_copy(reg['prefijo'])}\t")
        buffer_fn.write(f"{format_value_for_copy(reg['folio'])}\t")
        buffer_fn.write(f"{format_value_for_copy(reg['co'])}\t")
        buffer_fn.write(f"{format_value_for_copy(reg['nro_documento'])}\t")
        buffer_fn.write(f"{format_value_for_copy(reg['fecha_recibido'])}\t")
        buffer_fn.write(f"{format_value_for_copy(reg['usuario_creacion'])}\t")
        buffer_fn.write(f"{format_value_for_copy(reg['clase_documento'])}\t")
        buffer_fn.write(f"{format_value_for_copy(reg['valor'])}\t")
        buffer_fn.write(f"{format_value_for_copy(reg['clave_erp_financiero'])}\t")
        buffer_fn.write(f"{format_value_for_copy(reg['doc_causado_por'])}\t")
        buffer_fn.write(f"{format_value_for_copy(reg['modulo'])}\n")
    
    buffer_fn.seek(0)
    cursor.copy_from(
        buffer_fn,
        'temp_erp_financiero_nuevos',
        sep='\t',
        null='',
        columns=(
            'proveedor', 'razon_social', 'docto_proveedor', 'prefijo', 'folio',
            'co', 'nro_documento', 'fecha_recibido', 'usuario_creacion',
            'clase_documento', 'valor', 'clave_erp_financiero', 'doc_causado_por', 'modulo'
        )
    )
    
    # INSERT
    cursor.execute("""
        INSERT INTO erp_financiero (
            proveedor, razon_social, docto_proveedor, prefijo, folio,
            co, nro_documento, fecha_recibido, usuario_creacion,
            clase_documento, valor, clave_erp_financiero, doc_causado_por, modulo
        )
        SELECT 
            proveedor, razon_social, docto_proveedor, prefijo, folio,
            co, nro_documento, fecha_recibido, usuario_creacion,
            clase_documento, valor, clave_erp_financiero, doc_causado_por, modulo
        FROM temp_erp_financiero_nuevos
        ON CONFLICT (clave_erp_financiero) DO NOTHING
    """)
    
    insertados_fn = cursor.rowcount
    print(f"✅ {insertados_fn:,} registros ERP Financiero insertados")

# ============================================================================
# PASO 8: COMMIT DE TODAS LAS INSERCIONES
# ============================================================================

print("\n" + "="*80)
print("PASO 8: COMMIT A BASE DE DATOS")
print("="*80)

try:
    raw_conn.commit()
    print("OK COMMIT exitoso - Todos los datos guardados")
except Exception as e:
    print(f"ERROR en COMMIT: {e}")
    raw_conn.rollback()
    cursor.close()
    raw_conn.close()
    exit()

# ============================================================================
# PASO 9: VALIDAR QUE TODOS LOS DATOS QUEDARON CARGADOS
# ============================================================================

print("\n" + "="*80)
print("PASO 9: VALIDAR DATOS CARGADOS")
print("="*80)

# Contar registros en cada tabla
cursor.execute("SELECT COUNT(*) FROM dian")
count_dian = cursor.fetchone()[0]
print(f"✅ Tabla DIAN: {count_dian:,} registros")

cursor.execute("SELECT COUNT(*) FROM erp_comercial")
count_cm = cursor.fetchone()[0]
print(f"✅ Tabla ERP Comercial: {count_cm:,} registros")

cursor.execute("SELECT COUNT(*) FROM erp_financiero")
count_fn = cursor.fetchone()[0]
print(f"✅ Tabla ERP Financiero: {count_fn:,} registros")

# Validar muestra de DIAN
print("\n🔍 Validando muestra de 3 registros DIAN:")
cursor.execute("""
    SELECT nit_emisor, nombre_emisor, prefijo, folio, total, fecha_emision, cufe_cude
    FROM dian
    LIMIT 3
""")

for i, row in enumerate(cursor.fetchall()):
    print(f"\n   Registro {i+1}:")
    print(f"      NIT: {row[0]}")
    print(f"      Nombre: {row[1][:50]}...")
    print(f"      Prefijo: '{row[2]}'")
    print(f"      Folio: '{row[3]}'")
    print(f"      Valor: ${row[4]:,.2f}")
    print(f"      Fecha: {row[5]}")
    print(f"      CUFE: {row[6][:50]}...")

# ============================================================================
# PASO 10: COMPARAR RESULTADOS
# ============================================================================

print("\n" + "="*80)
print("PASO 10: COMPARACIÓN DE RESULTADOS")
print("="*80)

print(f"\n📊 ESPERADO vs CARGADO:")
print(f"   DIAN Excel: {d.height:,} filas")
print(f"   DIAN DB: {count_dian:,} registros")
print(f"   Diferencia: {d.height - count_dian:,} (duplicados ignorados)")

print(f"\n   ERP Comercial Excel: {erp_cm.height:,} filas")
print(f"   ERP Comercial DB: {count_cm:,} registros")

print(f"\n   ERP Financiero Excel: {erp_fn.height:,} filas")
print(f"   ERP Financiero DB: {count_fn:,} registros")

# ============================================================================
# RESUMEN FINAL
# ============================================================================

print("\n" + "="*80)
print("RESUMEN FINAL")
print("="*80)

if count_dian > 0 and count_cm > 0 and count_fn > 0:
    print("\n✅✅✅ CARGA EXITOSA ✅✅✅")
    print(f"\nTodas las tablas tienen datos:")
    print(f"   ✅ DIAN: {count_dian:,} registros")
    print(f"   ✅ ERP Comercial: {count_cm:,} registros")
    print(f"   ✅ ERP Financiero: {count_fn:,} registros")
    print(f"\n🎯 Los datos están listos para consolidar en la tabla maestro")
    print(f"\n📝 SIGUIENTE PASO: Ejecutar consolidación a maestro_dian_vs_erp")
else:
    print("\n⚠️ ADVERTENCIA: Algunas tablas están vacías")
    print(f"   DIAN: {count_dian:,}")
    print(f"   ERP Comercial: {count_cm:,}")
    print(f"   ERP Financiero: {count_fn:,}")

cursor.close()
raw_conn.close()

print("\n" + "="*80)
print("FIN DEL PROCESO")
print("="*80)
print()
