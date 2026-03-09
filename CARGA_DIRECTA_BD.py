"""
CARGA DIRECTA A BASE DE DATOS
Replica exactamente el código de routes.py sin usar HTTP
"""
import polars as pl
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from unicodedata import normalize
import re

load_dotenv()

# ============================================================================
# FUNCIONES DE PROCESAMIENTO (COPIADAS DE ROUTES.PY)
# ============================================================================

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
    if value is None or (isinstance(value, float) and pl.plugins.polars.is_nan(value)):
        return '\\N'
    if isinstance(value, str):
        value = value.replace('\\', '\\\\')
        value = value.replace('\t', '\\t')
        value = value.replace('\n', '\\n')
        value = value.replace('\r', '\\r')
        return value
    return str(value)

# ============================================================================
# PASO 1: VERIFICAR ARCHIVOS
# ============================================================================

print("\n" + "="*80)
print("CARGA DIRECTA A BASE DE DATOS - DIAN VS ERP")
print("="*80)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

archivos = {
    'dian': r'uploads\dian\Dian_23022026.xlsx',
    'erp_fn': r'uploads\erp_fn\erp_financiero_23022026.xlsx',
    'erp_cm': r'uploads\erp_cm\ERP_comercial_23022026.xlsx',
    'acuses': r'uploads\acuses\acuses_23022026.xlsx'
}

print("="*80)
print("PASO 1: VERIFICAR ARCHIVOS")
print("="*80)

for nombre, ruta in archivos.items():
    if os.path.exists(ruta):
        size_mb = os.path.getsize(ruta) / (1024*1024)
        print(f"✓ {nombre}: {ruta} ({size_mb:.2f} MB)")
    else:
        print(f"✗ {nombre}: NO ENCONTRADO - {ruta}")
        exit(1)

# ============================================================================
# PASO 2: LEER ARCHIVOS CON POLARS
# ============================================================================

print("\n" + "="*80)
print("PASO 2: LEER ARCHIVOS CON POLARS")
print("="*80)

print("\nLeyendo DIAN...")
df_dian = pl.read_excel(archivos['dian'], engine='calamine')
df_dian.columns = [normalizar_columna(col) for col in df_dian.columns]
print(f"✓ DIAN: {len(df_dian):,} filas, {len(df_dian.columns)} columnas")

print("Leyendo ERP Financiero...")
df_erp_fn = pl.read_excel(archivos['erp_fn'], engine='calamine')
df_erp_fn.columns = [normalizar_columna(col) for col in df_erp_fn.columns]
print(f"✓ ERP Financiero: {len(df_erp_fn):,} filas, {len(df_erp_fn.columns)} columnas")

print("Leyendo ERP Comercial...")
df_erp_cm = pl.read_excel(archivos['erp_cm'], engine='calamine')
df_erp_cm.columns = [normalizar_columna(col) for col in df_erp_cm.columns]
print(f"✓ ERP Comercial: {len(df_erp_cm):,} filas, {len(df_erp_cm.columns)} columnas")

print("Leyendo ACUSES...")
df_acuses = pl.read_excel(archivos['acuses'], engine='calamine')
df_acuses.columns = [normalizar_columna(col) for col in df_acuses.columns]
print(f"✓ ACUSES: {len(df_acuses):,} filas, {len(df_acuses.columns)} columnas")

# Procesar acuses CUFE → Estado
acuses_dict = {}
if 'cufe_cude' in df_acuses.columns or 'cufe/cude' in df_acuses.columns:
    cufe_col = 'cufe_cude' if 'cufe_cude' in df_acuses.columns else 'cufe/cude'
    estado_col = None
    for col in df_acuses.columns:
        if 'estado' in col and 'docto' in col:
            estado_col = col
            break
    
    if estado_col:
        print(f"  Usando columnas: {cufe_col} → {estado_col}")
        for row in df_acuses.iter_rows(named=True):
            cufe = row.get(cufe_col)
            estado = row.get(estado_col)
            if cufe and estado:
                acuses_dict[str(cufe).strip()] = str(estado).strip()
        print(f"✓ {len(acuses_dict):,} acuses procesados (CUFE → Estado)")
    else:
        print("  ⚠ No se encontró columna de estado")
else:
    print("  ⚠ No se encontró columna CUFE")

# ============================================================================
# PASO 3: CONSOLIDAR TIPOS TERCERO
# ============================================================================

print("\n" + "="*80)
print("PASO 3: CONSOLIDAR TIPOS DE TERCERO")
print("="*80)

tipos_tercero = {}

# DIAN → PROVEEDOR
if 'nit_emisor' in df_dian.columns:
    for nit in df_dian['nit_emisor'].unique():
        if nit and str(nit).strip():
            nit_str = str(nit).strip()
            tipos_tercero[nit_str] = 'PROVEEDOR'

# ERP FN → ACREEDOR
if 'proveedor' in df_erp_fn.columns:
    for nit in df_erp_fn['proveedor'].unique():
        if nit and str(nit).strip():
            nit_str = str(nit).strip()
            if nit_str in tipos_tercero:
                tipos_tercero[nit_str] = 'PROVEEDOR Y ACREEDOR'
            else:
                tipos_tercero[nit_str] = 'ACREEDOR'

# ERP CM → PROVEEDOR
if 'proveedor' in df_erp_cm.columns:
    for nit in df_erp_cm['proveedor'].unique():
        if nit and str(nit).strip():
            nit_str = str(nit).strip()
            if nit_str not in tipos_tercero:
                tipos_tercero[nit_str] = 'PROVEEDOR'
            elif tipos_tercero[nit_str] == 'ACREEDOR':
                tipos_tercero[nit_str] = 'PROVEEDOR Y ACREEDOR'

print(f"✓ {len(tipos_tercero):,} terceros clasificados")
if len(tipos_tercero) > 0:
    primeros_5 = list(tipos_tercero.items())[:5]
    print(f"  Primeros 5: {primeros_5}")

# ============================================================================
# PASO 4: CONECTAR A POSTGRESQL
# ============================================================================

print("\n" + "="*80)
print("PASO 4: CONECTAR A POSTGRESQL")
print("="*80)

database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("✗ ERROR: DATABASE_URL no configurada en .env")
    exit(1)

engine = create_engine(database_url)
raw_conn = engine.raw_connection()
cursor = raw_conn.cursor()

print("✓ Conectado a PostgreSQL")

# ============================================================================
# PASO 5: INSERTAR TABLA DIAN
# ============================================================================

print("\n" + "="*80)
print("PASO 5: INSERTAR EN TABLA DIAN")
print("="*80)

print(f"Procesando {len(df_dian):,} facturas DIAN...")

registros_dian = []
for row in df_dian.iter_rows(named=True):
    nit_emisor = row.get('nit_emisor', '')
    razon_social = row.get('razon_social_emisor', '')
    docto = row.get('folio', '')
    valor = row.get('valor_total', 0)
    fecha = row.get('fecha_emision', '')
    cufe = row.get('cufe_cude', '') or row.get('cufe/cude', '')
    
    prefijo = extraer_prefijo(docto)
    folio_digits = extraer_folio(docto)
    folio_formateado = ultimos_8_sin_ceros(folio_digits)
    clave = crear_clave_factura(nit_emisor, prefijo, folio_formateado)
    tipo_tercero = tipos_tercero.get(str(nit_emisor).strip(), 'PROVEEDOR')
    estado_acuse = acuses_dict.get(str(cufe).strip(), '') if cufe else ''
    
    registros_dian.append((
        format_value_for_copy(nit_emisor),
        format_value_for_copy(razon_social),
        format_value_for_copy(prefijo),
        format_value_for_copy(folio_formateado),
        format_value_for_copy(valor),
        format_value_for_copy(fecha),
        format_value_for_copy(cufe),
        format_value_for_copy(clave),
        format_value_for_copy(tipo_tercero),
        format_value_for_copy(estado_acuse)
    ))

print(f"  {len(registros_dian):,} registros preparados")

# Crear temp table
cursor.execute("DROP TABLE IF EXISTS temp_dian_nuevos")
cursor.execute("""
    CREATE TEMP TABLE temp_dian_nuevos (
        nit_emisor VARCHAR(50),
        razon_social VARCHAR(255),
        prefijo VARCHAR(20),
        folio VARCHAR(50),
        valor NUMERIC(15,2),
        fecha_emision VARCHAR(50),
        cufe_cude VARCHAR(255),
        clave_factura VARCHAR(150),
        tipo_tercero VARCHAR(50),
        estado_acuse VARCHAR(100)
    )
""")

# COPY FROM
from io import StringIO
buffer = StringIO()
for reg in registros_dian:
    buffer.write('\t'.join(reg) + '\n')
buffer.seek(0)

cursor.copy_from(buffer, 'temp_dian_nuevos', columns=[
    'nit_emisor', 'razon_social', 'prefijo', 'folio', 'valor',
    'fecha_emision', 'cufe_cude', 'clave_factura', 'tipo_tercero', 'estado_acuse'
])

print("  Datos copiados a tabla temporal")

# INSERT con ON CONFLICT
cursor.execute("""
    INSERT INTO dian (
        nit_emisor, razon_social, prefijo, folio, valor,
        fecha_emision, cufe_cude, clave_factura, tipo_tercero, estado_acuse
    )
    SELECT 
        nit_emisor, razon_social, prefijo, folio,
        CAST(valor AS NUMERIC(15,2)),
        fecha_emision, cufe_cude, clave_factura, tipo_tercero, estado_acuse
    FROM temp_dian_nuevos
    ON CONFLICT (cufe_cude) DO NOTHING
""")

cursor.execute("SELECT COUNT(*) FROM dian")
count_dian = cursor.fetchone()[0]
print(f"✓ DIAN: {count_dian:,} registros insertados")

# ============================================================================
# PASO 6: INSERTAR TABLA ERP COMERCIAL
# ============================================================================

print("\n" + "="*80)
print("PASO 6: INSERTAR EN ERP_COMERCIAL")
print("="*80)

print(f"Procesando {len(df_erp_cm):,} registros ERP Comercial...")

registros_erp_cm = []
for row in df_erp_cm.iter_rows(named=True):
    proveedor = row.get('proveedor', '')
    razon_social = row.get('razon_social', '')
    docto = row.get('docto_proveedor', '') or row.get('docto', '')
    co = row.get('co', '')
    valor = row.get('valor', 0)
    fecha = row.get('fecha', '')
    
    prefijo = extraer_prefijo(docto)
    folio_digits = extraer_folio(docto)
    folio_formateado = ultimos_8_sin_ceros(folio_digits)
    clave = crear_clave_factura(proveedor, prefijo, folio_formateado)
    tipo_tercero = tipos_tercero.get(str(proveedor).strip(), 'PROVEEDOR')
    
    registros_erp_cm.append((
        format_value_for_copy(proveedor),
        format_value_for_copy(razon_social),
        format_value_for_copy(prefijo),
        format_value_for_copy(folio_formateado),
        format_value_for_copy(co),
        format_value_for_copy(valor),
        format_value_for_copy(fecha),
        format_value_for_copy(clave),
        format_value_for_copy(tipo_tercero)
    ))

print(f"  {len(registros_erp_cm):,} registros preparados")

# Crear temp table
cursor.execute("DROP TABLE IF EXISTS temp_erp_comercial_nuevos")
cursor.execute("""
    CREATE TEMP TABLE temp_erp_comercial_nuevos (
        proveedor VARCHAR(50),
        razon_social VARCHAR(255),
        prefijo VARCHAR(20),
        folio VARCHAR(50),
        co VARCHAR(10),
        valor NUMERIC(15,2),
        fecha VARCHAR(50),
        clave_factura VARCHAR(150),
        tipo_tercero VARCHAR(50)
    )
""")

# COPY FROM
buffer = StringIO()
for reg in registros_erp_cm:
    buffer.write('\t'.join(reg) + '\n')
buffer.seek(0)

cursor.copy_from(buffer, 'temp_erp_comercial_nuevos', columns=[
    'proveedor', 'razon_social', 'prefijo', 'folio', 'co', 'valor',
    'fecha', 'clave_factura', 'tipo_tercero'
])

print("  Datos copiados a tabla temporal")

# INSERT con ON CONFLICT
cursor.execute("""
    INSERT INTO erp_comercial (
        proveedor, razon_social, prefijo, folio, co, valor,
        fecha, clave_factura, tipo_tercero
    )
    SELECT 
        proveedor, razon_social, prefijo, folio, co,
        CAST(valor AS NUMERIC(15,2)),
        fecha, clave_factura, tipo_tercero
    FROM temp_erp_comercial_nuevos
    ON CONFLICT (clave_factura, co) DO NOTHING
""")

cursor.execute("SELECT COUNT(*) FROM erp_comercial")
count_erp_cm = cursor.fetchone()[0]
print(f"✓ ERP COMERCIAL: {count_erp_cm:,} registros insertados")

# ============================================================================
# PASO 7: INSERTAR TABLA ERP FINANCIERO
# ============================================================================

print("\n" + "="*80)
print("PASO 7: INSERTAR EN ERP_FINANCIERO")
print("="*80)

print(f"Procesando {len(df_erp_fn):,} registros ERP Financiero...")

registros_erp_fn = []
for row in df_erp_fn.iter_rows(named=True):
    proveedor = row.get('proveedor', '')
    razon_social = row.get('razon_social', '')
    docto = row.get('docto_proveedor', '') or row.get('docto', '')
    co = row.get('co', '')
    valor = row.get('valor', 0)
    fecha = row.get('fecha', '')
    
    prefijo = extraer_prefijo(docto)
    folio_digits = extraer_folio(docto)
    folio_formateado = ultimos_8_sin_ceros(folio_digits)
    clave = crear_clave_factura(proveedor, prefijo, folio_formateado)
    tipo_tercero = tipos_tercero.get(str(proveedor).strip(), 'ACREEDOR')
    
    registros_erp_fn.append((
        format_value_for_copy(proveedor),
        format_value_for_copy(razon_social),
        format_value_for_copy(prefijo),
        format_value_for_copy(folio_formateado),
        format_value_for_copy(co),
        format_value_for_copy(valor),
        format_value_for_copy(fecha),
        format_value_for_copy(clave),
        format_value_for_copy(tipo_tercero)
    ))

print(f"  {len(registros_erp_fn):,} registros preparados")

# Crear temp table
cursor.execute("DROP TABLE IF EXISTS temp_erp_financiero_nuevos")
cursor.execute("""
    CREATE TEMP TABLE temp_erp_financiero_nuevos (
        proveedor VARCHAR(50),
        razon_social VARCHAR(255),
        prefijo VARCHAR(20),
        folio VARCHAR(50),
        co VARCHAR(10),
        valor NUMERIC(15,2),
        fecha VARCHAR(50),
        clave_factura VARCHAR(150),
        tipo_tercero VARCHAR(50)
    )
""")

# COPY FROM
buffer = StringIO()
for reg in registros_erp_fn:
    buffer.write('\t'.join(reg) + '\n')
buffer.seek(0)

cursor.copy_from(buffer, 'temp_erp_financiero_nuevos', columns=[
    'proveedor', 'razon_social', 'prefijo', 'folio', 'co', 'valor',
    'fecha', 'clave_factura', 'tipo_tercero'
])

print("  Datos copiados a tabla temporal")

# INSERT con ON CONFLICT
cursor.execute("""
    INSERT INTO erp_financiero (
        proveedor, razon_social, prefijo, folio, co, valor,
        fecha, clave_factura, tipo_tercero
    )
    SELECT 
        proveedor, razon_social, prefijo, folio, co,
        CAST(valor AS NUMERIC(15,2)),
        fecha, clave_factura, tipo_tercero
    FROM temp_erp_financiero_nuevos
    ON CONFLICT (clave_factura, co) DO NOTHING
""")

cursor.execute("SELECT COUNT(*) FROM erp_financiero")
count_erp_fn = cursor.fetchone()[0]
print(f"✓ ERP FINANCIERO: {count_erp_fn:,} registros insertados")

# ============================================================================
# PASO 8: COMMIT
# ============================================================================

print("\n" + "="*80)
print("PASO 8: COMMIT")
print("="*80)

raw_conn.commit()
print("✓ Transacción confirmada")

cursor.close()
raw_conn.close()

# ============================================================================
# RESUMEN FINAL
# ============================================================================

print("\n" + "="*80)
print("RESUMEN FINAL")
print("="*80)
print(f"✓ DIAN:           {count_dian:>10,} registros")
print(f"✓ ERP Comercial:  {count_erp_cm:>10,} registros")
print(f"✓ ERP Financiero: {count_erp_fn:>10,} registros")
print(f"✓ Tipos Tercero:  {len(tipos_tercero):>10,} NITs clasificados")
print(f"✓ Acuses:         {len(acuses_dict):>10,} estados procesados")
print("="*80)
print("\n✓✓✓ CARGA COMPLETADA EXITOSAMENTE ✓✓✓\n")
