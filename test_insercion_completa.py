"""
TEST DE INSERCIÓN COMPLETA - Reproducir el flujo exacto hasta base de datos
Diciembre 23, 2025
"""
import pandas as pd
from datetime import datetime
import unicodedata
import re
import io
import os

# ===== FUNCIONES COPIADAS EXACTAMENTE DE routes.py =====

def extraer_folio(celda):
    """Extrae el folio numérico de una celda que puede tener prefijo"""
    if pd.isna(celda) or celda is None:
        return "0"
    celda = str(celda).strip()
    if not celda:
        return "0"
    partes = re.split(r'[-_\s]+', celda)
    for parte in reversed(partes):
        parte_limpia = ''.join(c for c in parte if c.isdigit())
        if parte_limpia and parte_limpia != '0':
            return parte_limpia
    solo_numeros = ''.join(c for c in celda if c.isdigit())
    return solo_numeros if solo_numeros else "0"

def extraer_prefijo(celda):
    """Extrae solo la parte alfabética del prefijo"""
    if pd.isna(celda) or celda is None:
        return ""
    s = str(celda).strip()
    prefijo_alpha = ''.join(c for c in s if c.isalpha())
    return prefijo_alpha.strip()

def ultimos_8_sin_ceros(folio_str):
    """Toma últimos 8 caracteres y remueve ceros a la izquierda"""
    if not folio_str or folio_str == "0":
        return "0"
    ultimos_8 = folio_str[-8:]
    sin_ceros = ultimos_8.lstrip('0')
    return sin_ceros if sin_ceros else "0"

def format_value_for_copy(value):
    """Formatea un valor para COPY FROM"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    if isinstance(value, bool):
        return 't' if value else 'f'
    s = str(value)
    s = s.replace('\\', '\\\\')
    s = s.replace('\t', '\\t')
    s = s.replace('\n', '\\n')
    s = s.replace('\r', '\\r')
    return s

def normalizar_columna(nombre):
    """Normaliza nombre de columna quitando tildes"""
    sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', str(nombre))
        if unicodedata.category(c) != 'Mn'
    )
    return sin_tildes.lower().strip().replace(' ', '_')

# ===== TEST =====

print("=" * 80)
print("TEST DE INSERCIÓN COMPLETA CON ARCHIVO REAL")
print("=" * 80)

# 1. Leer archivo
archivo = r"uploads\dian\Dian.xlsx"
if not os.path.exists(archivo):
    print(f"❌ Archivo no encontrado: {archivo}")
    exit(1)

print(f"\n📂 Archivo: {archivo}")
print(f"📊 Tamaño: {os.path.getsize(archivo) / 1024:.1f} KB")
print(f"📅 Modificado: {datetime.fromtimestamp(os.path.getmtime(archivo))}")

# 2. Leer con pandas (igual que routes.py)
print("\n🔄 Leyendo Excel con pandas (primeras 3 filas)...")
df = pd.read_excel(archivo, nrows=3)
print(f"✅ Leído: {len(df)} filas, {len(df.columns)} columnas")

# 3. Normalizar columnas (igual que routes.py)
print("\n🔄 Normalizando nombres de columnas...")
df.columns = [c.strip().lower() for c in df.columns]
print(f"✅ Columnas después de .lower():")
for i, col in enumerate(df.columns[:10], 1):
    print(f"   {i}. '{col}'")

# 4. Crear diccionario columnas_originales (igual que routes.py)
print("\n🔄 Creando diccionario columnas_originales...")
columnas_originales = {}
for col in df.columns:
    col_norm = normalizar_columna(col)
    columnas_originales[col_norm] = col
    if col_norm in ['prefijo', 'folio', 'fecha_emision', 'total']:
        print(f"   '{col_norm}' → '{col}'")

# 5. Procesar registros (igual que routes.py)
print("\n🔄 Procesando registros...")
registros = []

for idx, (_, row) in enumerate(df.iterrows(), 1):
    print(f"\n--- REGISTRO {idx} ---")
    
    # NIT
    nit_raw = str(row.get(columnas_originales.get('nit_emisor', 'NIT Emisor'), ''))
    nit_limpio = extraer_folio(nit_raw)
    print(f"NIT: '{nit_raw}' → '{nit_limpio}'")
    
    # Razón Social
    razon_social = str(row.get(columnas_originales.get('nombre_emisor', 'Nombre Emisor'), ''))[:255]
    print(f"Razón Social: '{razon_social[:50]}...'")
    
    # PREFIJO (CRÍTICO)
    prefijo_raw = str(row.get(columnas_originales.get('prefijo', 'Prefijo'), ''))
    prefijo = extraer_prefijo(prefijo_raw)
    print(f"Prefijo:")
    print(f"  Columna: '{columnas_originales.get('prefijo')}'")
    print(f"  Raw: '{prefijo_raw}'")
    print(f"  Final: '{prefijo}' ✅")
    
    # FOLIO (CRÍTICO)
    folio_raw = str(row.get(columnas_originales.get('folio', 'Folio'), ''))
    folio_temp = extraer_folio(folio_raw)
    folio = ultimos_8_sin_ceros(folio_temp)
    print(f"Folio:")
    print(f"  Columna: '{columnas_originales.get('folio')}'")
    print(f"  Raw: '{folio_raw}'")
    print(f"  Temp: '{folio_temp}'")
    print(f"  Final: '{folio}' ✅")
    
    # TOTAL (CRÍTICO)
    total_raw = row.get(columnas_originales.get('total', 'Total'), 0)
    try:
        valor = float(str(total_raw).replace(',', '').replace('$', '').strip())
        print(f"Total: '{total_raw}' → {valor:,.2f} ✅")
    except:
        valor = 0.0
        print(f"Total: '{total_raw}' → ERROR → 0.00 ❌")
    
    # FECHA (CRÍTICO)
    fecha_raw = row.get(columnas_originales.get('fecha_emision', 'Fecha Emisión'))
    try:
        if isinstance(fecha_raw, str):
            fecha_emision = datetime.strptime(fecha_raw, '%d-%m-%Y').date()
        elif isinstance(fecha_raw, datetime):
            fecha_emision = fecha_raw.date()
        else:
            fecha_emision = datetime.now().date()
        print(f"Fecha Emisión: '{fecha_raw}' → {fecha_emision} ✅")
    except:
        fecha_emision = datetime.now().date()
        print(f"Fecha Emisión: '{fecha_raw}' → ERROR → {fecha_emision} ❌")
    
    # Otros campos (simplificados)
    tipo_documento = str(row.get(columnas_originales.get('tipo_de_documento', 'Tipo de documento'), ''))[:100]
    cufe = str(row.get(columnas_originales.get('cufe_cude', 'CUFE/CUDE'), ''))[:255]
    forma_pago = str(row.get(columnas_originales.get('forma_de_pago', 'Forma de Pago'), ''))[:20]
    estado_aprobacion = str(row.get(columnas_originales.get('estado_de_aprobacion', 'Estado de Aprobación'), ''))[:50]
    
    # CREAR REGISTRO (igual que routes.py línea 2350)
    registro = {
        'nit_emisor': nit_limpio,
        'razon_social': razon_social,
        'fecha_emision': fecha_emision,
        'prefijo': prefijo,  # ← CRÍTICO
        'folio': folio,      # ← CRÍTICO
        'valor': valor,      # ← CRÍTICO
        'tipo_documento': tipo_documento,
        'cufe': cufe,
        'forma_pago': forma_pago,
        'estado_aprobacion': estado_aprobacion,
        'modulo': 'Financiero',
        'estado_contable': 'No Causada',
        'acuses_recibidos': 0,
        'doc_causado_por': '',
        'dias_desde_emision': (datetime.now().date() - fecha_emision).days,
        'tipo_tercero': 'EXTERNO'
    }
    
    print(f"\n📋 REGISTRO DICT CREADO:")
    print(f"   prefijo: '{registro['prefijo']}'")
    print(f"   folio: '{registro['folio']}'")
    print(f"   valor: {registro['valor']}")
    print(f"   fecha_emision: {registro['fecha_emision']}")
    
    registros.append(registro)

# 6. Serializar a buffer (igual que routes.py línea 2433)
print("\n" + "=" * 80)
print("SERIALIZACIÓN A BUFFER PARA COPY FROM")
print("=" * 80)

buffer = io.StringIO()
for i, reg in enumerate(registros, 1):
    print(f"\n--- SERIALIZANDO REGISTRO {i} ---")
    
    # Crear línea exactamente como routes.py
    linea_partes = []
    linea_partes.append(format_value_for_copy(reg['nit_emisor']))
    linea_partes.append(format_value_for_copy(reg['razon_social']))
    linea_partes.append(format_value_for_copy(reg['fecha_emision']))
    linea_partes.append(format_value_for_copy(reg['prefijo']))  # ← CRÍTICO
    linea_partes.append(format_value_for_copy(reg['folio']))    # ← CRÍTICO
    linea_partes.append(format_value_for_copy(reg['valor']))    # ← CRÍTICO
    linea_partes.append(format_value_for_copy(reg['tipo_documento']))
    linea_partes.append(format_value_for_copy(reg['cufe']))
    linea_partes.append(format_value_for_copy(reg['forma_pago']))
    linea_partes.append(format_value_for_copy(reg['estado_aprobacion']))
    linea_partes.append(format_value_for_copy(reg['modulo']))
    linea_partes.append(format_value_for_copy(reg['estado_contable']))
    linea_partes.append(format_value_for_copy(reg['acuses_recibidos']))
    linea_partes.append(format_value_for_copy(reg['doc_causado_por']))
    linea_partes.append(format_value_for_copy(reg['dias_desde_emision']))
    linea_partes.append(format_value_for_copy(reg['tipo_tercero']))
    
    linea = '\t'.join(linea_partes) + '\n'
    
    print(f"Campo 3 (fecha_emision): '{linea_partes[2]}'")
    print(f"Campo 4 (prefijo): '{linea_partes[3]}' ← CRÍTICO")
    print(f"Campo 5 (folio): '{linea_partes[4]}' ← CRÍTICO")
    print(f"Campo 6 (valor): '{linea_partes[5]}' ← CRÍTICO")
    
    print(f"\nLínea completa ({len(linea)} chars):")
    print(linea[:200] + "..." if len(linea) > 200 else linea)
    
    buffer.write(linea)

# 7. Mostrar buffer completo
print("\n" + "=" * 80)
print("CONTENIDO COMPLETO DEL BUFFER")
print("=" * 80)
buffer.seek(0)
buffer_contenido = buffer.read()
print(buffer_contenido)

# 8. Simular COPY FROM (sin ejecutar)
print("\n" + "=" * 80)
print("COMANDO COPY FROM QUE SE EJECUTARÍA")
print("=" * 80)
print("""
cursor.copy_from(
    buffer,
    'temp_maestro_nuevos',
    sep='\\t',
    null='',
    columns=(
        'nit_emisor', 'razon_social', 'fecha_emision', 'prefijo', 'folio',
        'valor', 'tipo_documento', 'cufe', 'forma_pago', 'estado_aprobacion',
        'modulo', 'estado_contable', 'acuses_recibidos', 'doc_causado_por',
        'dias_desde_emision', 'tipo_tercero'
    )
)
""")

# 9. Verificar orden de columnas
print("\n" + "=" * 80)
print("VERIFICACIÓN DE ORDEN DE COLUMNAS")
print("=" * 80)
print("\nORDEN EN BUFFER (líneas 2433-2449 routes.py):")
orden_buffer = [
    'nit_emisor', 'razon_social', 'fecha_emision', 'prefijo', 'folio',
    'valor', 'tipo_documento', 'cufe', 'forma_pago', 'estado_aprobacion',
    'modulo', 'estado_contable', 'acuses_recibidos', 'doc_causado_por',
    'dias_desde_emision', 'tipo_tercero'
]
for i, col in enumerate(orden_buffer, 1):
    print(f"   {i}. {col}")

print("\nORDEN EN COPY FROM (líneas 2457-2461 routes.py):")
orden_copy = [
    'nit_emisor', 'razon_social', 'fecha_emision', 'prefijo', 'folio',
    'valor', 'tipo_documento', 'cufe', 'forma_pago', 'estado_aprobacion',
    'modulo', 'estado_contable', 'acuses_recibidos', 'doc_causado_por',
    'dias_desde_emision', 'tipo_tercero'
]
for i, col in enumerate(orden_copy, 1):
    print(f"   {i}. {col}")

if orden_buffer == orden_copy:
    print("\n✅ EL ORDEN COINCIDE - No debería haber problema")
else:
    print("\n❌ EL ORDEN NO COINCIDE - ¡AHÍ ESTÁ EL BUG!")

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print(f"Total registros procesados: {len(registros)}")
print(f"Tamaño del buffer: {len(buffer_contenido)} bytes")
print(f"Líneas en buffer: {buffer_contenido.count(chr(10))}")
print("\nSi los datos del buffer son correctos pero la BD está mal,")
print("el problema está en el COPY FROM o en la tabla destino.")
print("=" * 80)
