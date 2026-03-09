"""
TEST DE INSERCIÓN REAL A BASE DE DATOS
Inserta 1 registro de prueba usando el código exacto de routes.py
Febrero 23, 2026
"""
import psycopg2
import io
import re
from datetime import datetime

# Función EXACTA de routes.py línea 1062
def extraer_prefijo(docto: str) -> str:
    """Extrae prefijo alfanumérico (letras Y números), limpiando solo guiones y puntos"""
    if not docto:
        return ""
    # Solo eliminar guiones, puntos y espacios - MANTENER números
    prefijo = re.sub(r'[\-\.\s]', '', str(docto)).strip().upper()
    
    # Validar longitud máxima (20 caracteres por esquema BD)
    if len(prefijo) > 20:
        # Si es todo hexadecimal largo, es un CUFE - devolver vacío
        if re.match(r'^[A-F0-9]+$', prefijo) and len(prefijo) > 20:
            return ""  # CUFE mal posicionado
        return prefijo[:20]
    
    return prefijo

def extraer_folio(docto: str) -> str:
    """Extrae solo DÍGITOS del documento"""
    if not docto:
        return ""
    s = str(docto).strip()
    solo_numeros = ''.join(c for c in s if c.isdigit())
    return solo_numeros if solo_numeros else "0"

def ultimos_8_sin_ceros(folio_str):
    """Toma últimos 8 caracteres y remueve ceros a la izquierda"""
    if not folio_str or folio_str == "0":
        return "0"
    ultimos_8 = folio_str[-8:]
    sin_ceros = ultimos_8.lstrip('0')
    return sin_ceros if sin_ceros else "0"

def format_value_for_copy(value):
    """Formatea un valor para COPY FROM"""
    if value is None:
        return ''
    if isinstance(value, bool):
        return 't' if value else 'f'
    s = str(value)
    s = s.replace('\\', '\\\\')
    s = s.replace('\t', '\\t')
    s = s.replace('\n', '\\n')
    s = s.replace('\r', '\\r')
    return s

# Datos de prueba (registro 1 del Excel)
registro_prueba = {
    'nit_emisor': '860025900',
    'razon_social': 'TEST - Alpina Productos Alimenticios',
    'fecha_emision': '2026-02-14',
    'prefijo': '6841',  # ← CRÍTICO: valor numérico
    'folio': '896952',  # ← CRÍTICO
    'valor': 1548683.0,
    'tipo_documento': 'Factura electrónica',
    'cufe': '',
    'forma_pago': '2',
    'estado_aprobacion': '',
    'modulo': 'Financiero',
    'estado_contable': 'No Causada',
    'acuses_recibidos': 0,
    'doc_causado_por': '',
    'dias_desde_emision': 9,
    'tipo_tercero': 'EXTERNO'
}

print("=" * 80)
print("TEST DE INSERCIÓN REAL A BASE DE DATOS PostgreSQL")
print("=" * 80)

# Procesar valor como lo hace routes.py
print("\n🔄 Procesando valores...")
prefijo_procesado = extraer_prefijo(registro_prueba['prefijo'])
folio_procesado = ultimos_8_sin_ceros(extraer_folio(registro_prueba['folio']))

print(f"Prefijo: '{registro_prueba['prefijo']}' → '{prefijo_procesado}'")
print(f"Folio: '{registro_prueba['folio']}' → '{folio_procesado}'")

# Actualizar registro con valores procesados
registro_prueba['prefijo'] = prefijo_procesado
registro_prueba['folio'] = folio_procesado

# Conectar a base de datos
print("\n🔌 Conectando a base de datos...")
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="gestor_documental",
        user="postgres",
        password="G3st0radm$2025."
    )
    cursor = conn.cursor()
    print("✅ Conexión exitosa")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit(1)

try:
    # Crear tabla temporal de prueba
    print("\n📦 Creando tabla temporal de prueba...")
    cursor.execute("DROP TABLE IF EXISTS test_insert_prefijo")
    cursor.execute("""
        CREATE TABLE test_insert_prefijo (
            id SERIAL PRIMARY KEY,
            nit_emisor VARCHAR(20),
            razon_social VARCHAR(255),
            fecha_emision DATE,
            prefijo VARCHAR(10),
            folio VARCHAR(20),
            valor NUMERIC(15,2),
            tipo_documento VARCHAR(100),
            cufe VARCHAR(255),
            forma_pago VARCHAR(20),
            estado_aprobacion VARCHAR(50),
            modulo VARCHAR(20),
            estado_contable VARCHAR(50),
            acuses_recibidos INTEGER,
            doc_causado_por VARCHAR(255),
            dias_desde_emision INTEGER,
            tipo_tercero VARCHAR(50),
            fecha_insercion TIMESTAMP DEFAULT NOW()
        )
    """)
    print("✅ Tabla temporal creada")
    
    # Serializar registro a buffer (igual que routes.py)
    print("\n📝 Serializando registro a buffer...")
    buffer = io.StringIO()
    linea_partes = []
    linea_partes.append(format_value_for_copy(registro_prueba['nit_emisor']))
    linea_partes.append(format_value_for_copy(registro_prueba['razon_social']))
    linea_partes.append(format_value_for_copy(registro_prueba['fecha_emision']))
    linea_partes.append(format_value_for_copy(registro_prueba['prefijo']))  # ← CRÍTICO
    linea_partes.append(format_value_for_copy(registro_prueba['folio']))    # ← CRÍTICO
    linea_partes.append(format_value_for_copy(registro_prueba['valor']))
    linea_partes.append(format_value_for_copy(registro_prueba['tipo_documento']))
    linea_partes.append(format_value_for_copy(registro_prueba['cufe']))
    linea_partes.append(format_value_for_copy(registro_prueba['forma_pago']))
    linea_partes.append(format_value_for_copy(registro_prueba['estado_aprobacion']))
    linea_partes.append(format_value_for_copy(registro_prueba['modulo']))
    linea_partes.append(format_value_for_copy(registro_prueba['estado_contable']))
    linea_partes.append(format_value_for_copy(registro_prueba['acuses_recibidos']))
    linea_partes.append(format_value_for_copy(registro_prueba['doc_causado_por']))
    linea_partes.append(format_value_for_copy(registro_prueba['dias_desde_emision']))
    linea_partes.append(format_value_for_copy(registro_prueba['tipo_tercero']))
    
    linea = '\t'.join(linea_partes) + '\n'
    buffer.write(linea)
    
    print(f"Campos críticos en buffer:")
    print(f"  Campo 4 (prefijo): '{linea_partes[3]}'")
    print(f"  Campo 5 (folio): '{linea_partes[4]}'")
    print(f"  Campo 6 (valor): '{linea_partes[5]}'")
    print(f"\nLínea completa:")
    print(linea)
    
    # Ejecutar COPY FROM (igual que routes.py)
    print("\n📥 Ejecutando COPY FROM...")
    buffer.seek(0)
    cursor.copy_from(
        buffer,
        'test_insert_prefijo',
        sep='\t',
        null='',
        columns=(
            'nit_emisor', 'razon_social', 'fecha_emision', 'prefijo', 'folio',
            'valor', 'tipo_documento', 'cufe', 'forma_pago', 'estado_aprobacion',
            'modulo', 'estado_contable', 'acuses_recibidos', 'doc_causado_por',
            'dias_desde_emision', 'tipo_tercero'
        )
    )
    conn.commit()
    print("✅ COPY FROM exitoso")
    
    # Verificar lo que se insertó
    print("\n🔍 Verificando datos insertados...")
    cursor.execute("""
        SELECT nit_emisor, razon_social, fecha_emision, prefijo, folio, valor
        FROM test_insert_prefijo
    """)
    fila = cursor.fetchone()
    
    print("=" * 80)
    print("RESULTADO EN BASE DE DATOS")
    print("=" * 80)
    print(f"NIT Emisor: {fila[0]}")
    print(f"Razón Social: {fila[1]}")
    print(f"Fecha Emisión: {fila[2]}")
    print(f"Prefijo: '{fila[3]}' ← {'✅ CORRECTO' if fila[3] == '6841' else '❌ INCORRECTO'}")
    print(f"Folio: '{fila[4]}' ← {'✅ CORRECTO' if fila[4] == '896952' else '❌ INCORRECTO'}")
    print(f"Valor: {fila[5]} ← {'✅ CORRECTO' if float(fila[5]) == 1548683.0 else '❌ INCORRECTO'}")
    print("=" * 80)
    
    if fila[3] == '6841' and fila[4] == '896952':
        print("\n✅✅✅ INSERCIÓN CORRECTA - El código funciona bien")
        print("⚠️  Si los datos de actualizar_maestro() están mal, es porque:")
        print("   1. El servidor Flask está usando código viejo en memoria")
        print("   2. La columna 'prefijo' en Excel está vacía")
        print("   3. Hay otro bug en el flujo de lectura de Excel")
    else:
        print("\n❌❌❌ INSERCIÓN INCORRECTA - Hay un bug en el código")
    
finally:
    # Limpiar tabla de prueba
    print("\n🧹 Limpiando tabla de prueba...")
    cursor.execute("DROP TABLE IF EXISTS test_insert_prefijo")
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Conexión cerrada")
