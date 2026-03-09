"""
CARGA SOLO DIAN - DIAGNÓSTICO
Versión ultra simple para identificar dónde falla
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
print("CARGA SOLO DIAN - VERSIÓN DIAGNÓSTICO")
print("="*80)

archivo_dian = r'uploads\dian\Dian_23022026.xlsx'

# Verificar archivo existe
if not os.path.exists(archivo_dian):
    print(f"❌ ERROR: Archivo no encontrado: {archivo_dian}")
    exit(1)

file_size_mb = os.path.getsize(archivo_dian) / (1024*1024)
print(f"\n📁 Archivo: {archivo_dian}")
print(f"📦 Tamaño: {file_size_mb:.2f} MB")

print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')} - Iniciando lectura Excel...")
print("   (Esto puede tomar 60-120 segundos para 13.96 MB)")

try:
    inicio_lectura = datetime.now()
    df = pd.read_excel(archivo_dian, engine='openpyxl')
    tiempo_lectura = (datetime.now() - inicio_lectura).total_seconds()
    
    print(f"✅ {datetime.now().strftime('%H:%M:%S')} - Lectura completada en {tiempo_lectura:.1f}s")
    print(f"   Filas leídas: {len(df):,}")
    print(f"   Columnas: {len(df.columns)}")
    
except Exception as e:
    print(f"❌ ERROR al leer Excel: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

print(f"\n🔍 Primeras 3 columnas: {df.columns[:3].tolist()}")

def normalizar_columna(nombre):
    nombre = str(nombre).strip()
    nombre = normalize('NFD', nombre)
    nombre = ''.join(c for c in nombre if c.isalnum() or c in ' _-')
    nombre = nombre.lower().replace(' ', '_').replace('-', '_')
    nombre = re.sub(r'_+', '_', nombre)
    return nombre.rstrip('.')

print("\n📝 Normalizando columnas...")
df.columns = [normalizar_columna(col) for col in df.columns]
print(f"   Primeras 3 normalizadas: {df.columns[:3].tolist()}")

# Detectar columnas
cols = df.columns.tolist()
nit_col = next((c for c in cols if "nit" in c.lower() and "adquir" in c.lower()), None)
razon_col = next((c for c in cols if "razon" in c.lower() and "social" in c.lower()), None)
numero_col = next((c for c in cols if "numero" in c.lower() and "documento" not in c.lower()), None)
fecha_col = next((c for c in cols if "fecha" in c.lower() and ("factur" in c.lower() or "gener" in c.lower())), None)
valor_col = next((c for c in cols if "total" in c.lower() and "documento" in c.lower()), None)

print(f"\n🎯 Columnas detectadas:")
print(f"   NIT Adquiriente: {nit_col}")
print(f"   Razón Social: {razon_col}")
print(f"   Número: {numero_col}")
print(f"   Fecha: {fecha_col}")
print(f"   Valor: {valor_col}")

if not all([nit_col, razon_col, numero_col, fecha_col, valor_col]):
    print("\n❌ ERROR: No se detectaron todas las columnas necesarias")
    print("\nColumnas disponibles:")
    for i, col in enumerate(cols, 1):
        print(f"   {i}. {col}")
    exit(1)

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

print(f"\n⚙️  Procesando {len(df):,} registros...")
inicio_proc = datetime.now()

registros = []
errores = 0

for idx, (_, row) in enumerate(df.iterrows()):
    try:
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
        
        registros.append((nit, razon, numero, prefijo, folio, fecha_factura, valor, clave))
        
        if (idx + 1) % 10000 == 0:
            print(f"   {idx+1:,} registros procesados...")
            
    except Exception as e:
        errores += 1
        if errores <= 5:
            print(f"   ⚠️  Error en fila {idx}: {str(e)}")

tiempo_proc = (datetime.now() - inicio_proc).total_seconds()
print(f"✅ Procesamiento completado en {tiempo_proc:.1f}s")
print(f"   Total procesados: {len(registros):,}")
print(f"   Errores: {errores}")

if len(registros) == 0:
    print("\n❌ ERROR: No se procesaron registros")
    exit(1)

print(f"\n🔍 Muestra de 3 registros:")
for i in range(min(3, len(registros))):
    nit, razon, numero, prefijo, folio, fecha, valor, clave = registros[i]
    print(f"   {i+1}. NIT: {nit[:20]} | Número: {numero[:20]} | Fecha: {fecha} | Valor: {valor:,.0f}")

print(f"\n💾 Conectando a PostgreSQL...")
database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)

try:
    raw_conn = engine.raw_connection()
    cursor = raw_conn.cursor()
    
    print(f"   Creando tabla temporal...")
    cursor.execute("CREATE TEMP TABLE temp_dian (LIKE dian INCLUDING DEFAULTS) ON COMMIT DROP")
    
    print(f"   Preparando buffer COPY...")
    inicio_copy = datetime.now()
    buffer = io.StringIO()
    for r in registros:
        buffer.write('\t'.join([format_value(v) for v in r]) + '\n')
    
    buffer.seek(0)
    print(f"   Ejecutando COPY FROM...")
    cursor.copy_from(buffer, 'temp_dian', sep='\t', null='', columns=('nit_adquiriente', 'razon_social', 'numero', 'prefijo', 'folio', 'fecha_factura', 'valor', 'clave_dian'))
    
    print(f"   Insertando en tabla principal...")
    cursor.execute("INSERT INTO dian SELECT * FROM temp_dian ON CONFLICT (clave_dian) DO NOTHING")
    insertados = cursor.rowcount
    
    raw_conn.commit()
    tiempo_copy = (datetime.now() - inicio_copy).total_seconds()
    
    print(f"✅ Inserción completada en {tiempo_copy:.1f}s")
    print(f"   Registros insertados: {insertados:,}")
    
    cursor.close()
    raw_conn.close()
    
    # Verificar conteo final
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM dian"))
        total = result.scalar()
        print(f"\n📊 Verificación final: {total:,} registros en tabla DIAN")
    
    print("\n" + "="*80)
    print("✅ CARGA COMPLETADA EXITOSAMENTE")
    print("="*80 + "\n")
    
except Exception as e:
    print(f"\n❌ ERROR en PostgreSQL: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
