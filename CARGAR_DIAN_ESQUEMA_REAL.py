"""
CARGA DIAN CON ESQUEMA CORRECTO
Usa las columnas reales que tiene la tabla DIAN en PostgreSQL
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

print("\n" + "="*80)
print("CARGA DIAN - ESQUEMA CORRECTO")
print("="*80)

archivo_dian = r'uploads\dian\Dian_23022026.xlsx'

print(f"\n📁 Archivo: {archivo_dian}")
print(f"🕐 Iniciando lectura Excel... (60-120 segundos)")

inicio = datetime.now()
df = pd.read_excel(archivo_dian, engine='openpyxl')
tiempo = (datetime.now() - inicio).total_seconds()

print(f"✅ Lectura completada en {tiempo:.1f}s")
print(f"   {len(df):,} filas, {len(df.columns)} columnas")

def normalizar_columna(nombre):
    nombre = str(nombre).strip()
    nombre = normalize('NFD', nombre)
    nombre = ''.join(c for c in nombre if c.isalnum() or c in ' _-')
    nombre = nombre.lower().replace(' ', '_').replace('-', '_')
    nombre = re.sub(r'_+', '_', nombre)
    return nombre.rstrip('.')

df.columns = [normalizar_columna(col) for col in df.columns]
cols = df.columns.tolist()

print(f"\n🔍 Primeras 5 columnas normalizadas: {cols[:5]}")

# Detectar columnas del Excel DIAN (esquema real)
tipo_doc_col = next((c for c in cols if "tipo" in c.lower() and "documento" in c.lower()), None)
cufe_col = next((c for c in cols if "cufe" in c.lower() or "cude" in c.lower()), None)
folio_col = next((c for c in cols if c.lower() == "folio"), None)
prefijo_col = next((c for c in cols if c.lower() == "prefijo"), None)
divisa_col = next((c for c in cols if "divisa" in c.lower()), None)
forma_pago_col = next((c  for c in cols if "forma" in c.lower() and "pago" in c.lower()), None)
medio_pago_col = next((c for c in cols if "medio" in c.lower() and "pago" in c.lower()), None)
fecha_emision_col = next((c for c in cols if "fecha" in c.lower() and ("emision" in c.lower() or "generac" in c.lower() or "factur" in c.lower())), None)
fecha_recepcion_col = next((c for c in cols if "fecha" in c.lower() and "recepcion" in c.lower()), None)
nit_emisor_col = next((c for c in cols if "nit" in c.lower() and ("emisor" in c.lower() or "proveedor" in c.lower() or "vendedor" in c.lower())), None)
nombre_emisor_col = next((c for c in cols if ("nombre" in c.lower() or "razon" in c.lower()) and ("emisor" in c.lower() or "proveedor" in c.lower() or "vendedor" in c.lower())), None)
nit_receptor_col = next((c for c in cols if "nit" in c.lower() and ("receptor" in c.lower() or "adquir" in c.lower() or "comprador" in c.lower())), None)
nombre_receptor_col = next((c for c in cols if ("nombre" in c.lower() or "razon" in c.lower()) and ("receptor" in c.lower() or "adquir" in c.lower() or "comprador" in c.lower())), None)
iva_col = next((c for c in cols if c.lower() == "iva"), None)
ica_col = next((c for c in cols if c.lower() == "ica"), None)
ic_col = next((c for c in cols if c.lower() == "ic"), None)
inc_col = next((c for c in cols if c.lower() == "inc"), None)
timbre_col = next((c for c in cols if "timbre" in c.lower()), None)
inc_bolsas_col = next((c for c in cols if "bolsa" in c.lower()), None)
in_carbono_col = next((c for c in cols if "carbono" in c.lower()), None)
in_combustibles_col = next((c for c in cols if "combustible" in c.lower()), None)
ic_datos_col = next((c for c in cols if "datos" in c.lower()), None)
icl_col = next((c for c in cols if c.lower() == "icl"), None)
inpp_col = next((c for c in cols if c.lower() == "inpp"), None)
ibua_col = next((c for c in cols if c.lower() == "ibua"), None)
icui_col = next((c for c in cols if c.lower() == "icui"), None)
rete_iva_col = next((c for c in cols if "rete" in c.lower() and "iva" in c.lower()), None)
rete_renta_col = next((c for c in cols if "rete" in c.lower() and "renta" in c.lower()), None)
rete_ica_col = next((c for c in cols if "rete" in c.lower() and "ica" in c.lower()), None)
total_col = next((c for c in cols if c.lower() == "total" or ("total" in c.lower() and "documento" in c.lower())), None)
estado_col = next((c for c in cols if c.lower() == "estado"), None)
grupo_col = next((c for c in cols if c.lower() == "grupo"), None)

print(f"\n🎯 Columnas clave detectadas:")
print(f"   Tipo Documento: {tipo_doc_col}")
print(f"   CUFE/CUDE: {cufe_col}")
print(f"   Folio: {folio_col}")
print(f"   Prefijo: {prefijo_col}")
print(f"   Fecha Emisión: {fecha_emision_col}")
print(f"   NIT Emisor: {nit_emisor_col}")
print(f"   Nombre Emisor: {nombre_emisor_col}")
print(f"   NIT Receptor: {nit_receptor_col}")
print(f"   Nombre Receptor: {nombre_receptor_col}")
print(f"   Total: {total_col}")

# Tipos de documento DIAN que NO se deben procesar
TIPOS_EXCLUIDOS_DIAN = {
    'tipo de documento',          # fila de encabezado accidental
    'application response',
    'documento soporte con no obligados',
    'nota de ajuste del documento soporte',
}

def safe_str(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ''
    return str(val).strip()

def mapear_forma_pago(val):
    """Convierte código numérico a texto: 1/1.0 → Contado, 2/2.0 → Crédito"""
    s = safe_str(val).replace('.0', '').strip()
    if s == '1':
        return 'Contado'
    elif s == '2':
        return 'Crédito'
    return s  # Si ya es texto (ej: 'Contado'), lo deja igual

def safe_date(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    try:
        return pd.to_datetime(val, errors='coerce').date() if isinstance(val, str) else (val.date() if hasattr(val, 'date') else val)
    except:
        return None

def safe_float(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return 0.0
    try:
        return float(val)
    except:
        return 0.0

def format_value(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    if isinstance(value, str):
        value = value.replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
        return value
    return str(value)

print(f"\n⚙️  Procesando {len(df):,} registros...")
inicio_proc = datetime.now()

registros = []
for idx, (_, row) in enumerate(df.iterrows()):
    tipo_documento = safe_str(row.get(tipo_doc_col, ''))

    # ─── FILTRO: omitir tipos de documento que no se procesan ───
    if tipo_documento.lower().strip() in TIPOS_EXCLUIDOS_DIAN:
        continue
    if not tipo_documento:  # omitir filas sin tipo de documento
        continue

    cufe_cude = safe_str(row.get(cufe_col, ''))
    folio = safe_str(row.get(folio_col, ''))
    prefijo = safe_str(row.get(prefijo_col, ''))
    divisa = safe_str(row.get(divisa_col, ''))
    forma_pago = mapear_forma_pago(row.get(forma_pago_col, ''))  # 1→Contado, 2→Crédito
    medio_pago = safe_str(row.get(medio_pago_col, ''))
    fecha_emision = safe_date(row.get(fecha_emision_col))
    fecha_recepcion = safe_date(row.get(fecha_recepcion_col))
    nit_emisor = safe_str(row.get(nit_emisor_col, ''))
    nombre_emisor = safe_str(row.get(nombre_emisor_col, ''))
    nit_receptor = safe_str(row.get(nit_receptor_col, ''))
    nombre_receptor = safe_str(row.get(nombre_receptor_col, ''))
    iva = safe_float(row.get(iva_col, 0))
    ica = safe_float(row.get(ica_col, 0))
    ic = safe_float(row.get(ic_col, 0))
    inc = safe_float(row.get(inc_col, 0))
    timbre = safe_float(row.get(timbre_col, 0))
    inc_bolsas = safe_float(row.get(inc_bolsas_col, 0))
    in_carbono = safe_float(row.get(in_carbono_col, 0))
    in_combustibles = safe_float(row.get(in_combustibles_col, 0))
    ic_datos = safe_float(row.get(ic_datos_col, 0))
    icl = safe_float(row.get(icl_col, 0))
    inpp = safe_float(row.get(inpp_col, 0))
    ibua = safe_float(row.get(ibua_col, 0))
    icui = safe_float(row.get(icui_col, 0))
    rete_iva = safe_float(row.get(rete_iva_col, 0))
    rete_renta = safe_float(row.get(rete_renta_col, 0))
    rete_ica = safe_float(row.get(rete_ica_col, 0))
    total = safe_float(row.get(total_col, 0))
    estado = safe_str(row.get(estado_col, ''))
    grupo = safe_str(row.get(grupo_col, ''))
    
    # Clave única para dian
    clave = f"{nit_emisor}-{prefijo}-{folio}"
    
    registros.append((
        tipo_documento, cufe_cude, folio, prefijo, divisa, forma_pago, medio_pago,
        fecha_emision, fecha_recepcion, nit_emisor, nombre_emisor, nit_receptor, nombre_receptor,
        iva, ica, ic, inc, timbre, inc_bolsas, in_carbono, in_combustibles, ic_datos,
        icl, inpp, ibua, icui, rete_iva, rete_renta, rete_ica, total, estado, grupo, clave
    ))
    
    if (idx + 1) % 10000 == 0:
        print(f"   {idx+1:,} registros...")

tiempo_proc = (datetime.now() - inicio_proc).total_seconds()
print(f"✅ {len(registros):,} procesados en {tiempo_proc:.1f}s")

print(f"\n💾 Conectando a PostgreSQL...")
database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)
raw_conn = engine.raw_connection()
cursor = raw_conn.cursor()

print(f"   Creando tabla temporal...")
cursor.execute("CREATE TEMP TABLE temp_dian (LIKE dian INCLUDING DEFAULTS) ON COMMIT DROP")

print(f"   Preparando COPY...")
inicio_copy = datetime.now()
buffer = io.StringIO()
for r in registros:
    buffer.write('\t'.join([format_value(v) for v in r]) + '\n')

buffer.seek(0)

print(f"   Ejecutando COPY FROM...")
cursor.copy_from(buffer, 'temp_dian', sep='\t', null='', 
                 columns=('tipo_documento', 'cufe_cude', 'folio', 'prefijo', 'divisa', 'forma_pago', 'medio_pago',
                          'fecha_emision', 'fecha_recepcion', 'nit_emisor', 'nombre_emisor', 'nit_receptor', 'nombre_receptor',
                          'iva', 'ica', 'ic', 'inc', 'timbre', 'inc_bolsas', 'in_carbono', 'in_combustibles', 'ic_datos',
                          'icl', 'inpp', 'ibua', 'icui', 'rete_iva', 'rete_renta', 'rete_ica', 'total', 'estado', 'grupo', 'clave'))

print(f"   Insertando... (ON CONFLICT DO NOTHING)")
cursor.execute("INSERT INTO dian SELECT * FROM temp_dian ON CONFLICT (clave) DO NOTHING")
insertados = cursor.rowcount

raw_conn.commit()
tiempo_copy = (datetime.now() - inicio_copy).total_seconds()

print(f"✅ {insertados:,} insertados en {tiempo_copy:.1f}s")

cursor.close()
raw_conn.close()

# Verificar
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM dian"))
    total = result.scalar()
    print(f"\n📊 Total en tabla DIAN: {total:,} registros")

print("\n" + "="*80)
print("✅ CARGA COMPLETADA")
print("="*80 + "\n")
