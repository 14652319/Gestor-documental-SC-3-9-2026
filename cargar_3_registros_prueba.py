"""
CARGA MANUAL DIRECTA - PASO 1: 3 REGISTROS DE PRUEBA DIAN
Usa el código EXACTO de routes.py para procesar y cargar
Febrero 23, 2026
"""
import pandas as pd
import psycopg2
import io
import re
import unicodedata
from datetime import datetime
import os

# ===== FUNCIONES EXACTAS DE routes.py =====

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

def normalizar_columna(nombre):
    """Normaliza nombre de columna quitando tildes"""
    sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', str(nombre))
        if unicodedata.category(c) != 'Mn'
    )
    return sin_tildes.lower().strip().replace(' ', '_')

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

# ===== INICIO DEL SCRIPT =====

print("=" * 80)
print("CARGA MANUAL DIRECTA - PRUEBA CON 3 REGISTROS DIAN")
print("=" * 80)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 1. VERIFICAR ARCHIVO
archivo = r"uploads\dian\Dian.xlsx"
if not os.path.exists(archivo):
    print(f"❌ Archivo no encontrado: {archivo}")
    exit(1)

print(f"📂 Archivo encontrado: {archivo}")
print(f"   Tamaño: {os.path.getsize(archivo) / 1024:.1f} KB")
print(f"   Modificado: {datetime.fromtimestamp(os.path.getmtime(archivo))}\n")

# 2. CONECTAR A BD
print("🔌 Conectando a base de datos...")
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="gestor_documental",
        user="postgres",
        password="G3st0radm$2025."
    )
    cursor = conn.cursor()
    print("✅ Conexión exitosa\n")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit(1)

try:
    # 3. VERIFICAR TABLA VACÍA
    print("🔍 Verificando tabla maestro_dian_vs_erp...")
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
    total = cursor.fetchone()[0]
    
    if total > 0:
        print(f"⚠️  ADVERTENCIA: Tabla tiene {total:,} registros")
        print("   Se agregarán registros nuevos\n")
    else:
        print("✅ Tabla vacía - Lista para cargar\n")
    
    # 4. LEER EXCEL (solo 3 filas)
    print("📖 Leyendo Excel (primeras 3 filas)...")
    df = pd.read_excel(archivo, nrows=3)
    print(f"✅ Leído: {len(df)} filas, {len(df.columns)} columnas\n")
    
    # 5. NORMALIZAR COLUMNAS (igual que routes.py)
    print("🔄 Normalizando columnas...")
    df.columns = [c.strip().lower() for c in df.columns]
    print(f"✅ Columnas normalizadas\n")
    
    # 6. CREAR DICCIONARIO columnas_originales
    print("📋 Creando diccionario de columnas...")
    columnas_originales = {}
    for col in df.columns:
        col_norm = normalizar_columna(col)
        columnas_originales[col_norm] = col
    print(f"✅ Diccionario creado ({len(columnas_originales)} columnas)\n")
    
    # 7. PROCESAR REGISTROS
    print("=" * 80)
    print("PROCESANDO REGISTROS")
    print("=" * 80)
    
    registros = []
    
    for idx, (_, row) in enumerate(df.iterrows(), 1):
        print(f"\n--- REGISTRO {idx} ---")
        
        # NIT
        nit_raw = str(row.get(columnas_originales.get('nit_emisor', 'NIT Emisor'), ''))
        nit_limpio = extraer_folio(nit_raw)
        print(f"NIT: '{nit_raw}' → '{nit_limpio}'")
        
        # Razón Social
        razon_social = str(row.get(columnas_originales.get('nombre_emisor', 'Nombre Emisor'), ''))[:255]
        print(f"Razón Social: '{razon_social[:50]}'...")
        
        # PREFIJO (CRÍTICO)
        prefijo_raw = str(row.get(columnas_originales.get('prefijo', 'Prefijo'), ''))
        prefijo = extraer_prefijo(prefijo_raw)
        print(f"Prefijo: '{prefijo_raw}' → '{prefijo}' {'✅' if prefijo else '⚠️ VACÍO'}")
        
        # FOLIO (CRÍTICO)
        folio_raw = str(row.get(columnas_originales.get('folio', 'Folio'), ''))
        folio_temp = extraer_folio(folio_raw)
        folio = ultimos_8_sin_ceros(folio_temp)
        print(f"Folio: '{folio_raw}' → '{folio}' {'✅' if folio != '0' else '⚠️ CERO'}")
        
        # TOTAL (CRÍTICO)
        total_raw = row.get(columnas_originales.get('total', 'Total'), 0)
        try:
            valor = float(str(total_raw).replace(',', '').replace('$', '').strip())
            print(f"Total: '{total_raw}' → ${valor:,.2f} {'✅' if valor > 0 else '⚠️ CERO'}")
        except:
            valor = 0.0
            print(f"Total: '{total_raw}' → ERROR → $0.00 ❌")
        
        # FECHA (CRÍTICO)
        fecha_raw = row.get(columnas_originales.get('fecha_emision', 'Fecha Emisión'))
        try:
            if isinstance(fecha_raw, str):
                fecha_emision = datetime.strptime(fecha_raw, '%d-%m-%Y').date()
            elif isinstance(fecha_raw, datetime):
                fecha_emision = fecha_raw.date()
            elif hasattr(fecha_raw, 'date'):
                fecha_emision = fecha_raw.date()
            else:
                fecha_emision = datetime.now().date()
            print(f"Fecha: '{fecha_raw}' → {fecha_emision} {'✅' if fecha_emision != datetime.now().date() else '⚠️ HOY'}")
        except Exception as e:
            fecha_emision = datetime.now().date()
            print(f"Fecha: '{fecha_raw}' → ERROR → {fecha_emision} ❌")
        
        # Otros campos
        tipo_documento = str(row.get(columnas_originales.get('tipo_de_documento', 'Tipo de documento'), ''))[:100]
        cufe = str(row.get(columnas_originales.get('cufe_cude', 'CUFE/CUDE'), ''))[:255]
        forma_pago = str(row.get(columnas_originales.get('forma_de_pago', 'Forma de Pago'), ''))[:20]
        estado_aprobacion = str(row.get(columnas_originales.get('estado_de_aprobacion', 'Estado de Aprobación'), ''))[:50]
        
        # CREAR REGISTRO
        registro = {
            'nit_emisor': nit_limpio,
            'razon_social': razon_social,
            'fecha_emision': fecha_emision,
            'prefijo': prefijo,
            'folio': folio,
            'valor': valor,
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
        
        registros.append(registro)
    
    # 8. INSERTAR EN BASE DE DATOS
    print("\n" + "=" * 80)
    print("INSERTANDO EN BASE DE DATOS")
    print("=" * 80)
    
    # Crear tabla temporal
    print("\n📦 Creando tabla temporal...")
    cursor.execute("DROP TABLE IF EXISTS temp_maestro_prueba")
    cursor.execute("""
        CREATE TABLE temp_maestro_prueba (
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
            tipo_tercero VARCHAR(50)
        )
    """)
    print("✅ Tabla temporal creada\n")
    
    # Serializar a buffer
    print("📝 Serializando registros...")
    buffer = io.StringIO()
    for i, reg in enumerate(registros, 1):
        linea_partes = []
        linea_partes.append(format_value_for_copy(reg['nit_emisor']))
        linea_partes.append(format_value_for_copy(reg['razon_social']))
        linea_partes.append(format_value_for_copy(reg['fecha_emision']))
        linea_partes.append(format_value_for_copy(reg['prefijo']))
        linea_partes.append(format_value_for_copy(reg['folio']))
        linea_partes.append(format_value_for_copy(reg['valor']))
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
        buffer.write(linea)
        
        print(f"Registro {i}: Prefijo='{linea_partes[3]}', Folio='{linea_partes[4]}', Valor='{linea_partes[5]}'")
    
    print(f"✅ {len(registros)} registros serializados\n")
    
    # COPY FROM
    print("📥 Ejecutando COPY FROM...")
    buffer.seek(0)
    cursor.copy_from(
        buffer,
        'temp_maestro_prueba',
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
    print("✅ COPY FROM exitoso\n")
    
    # 9. VERIFICAR DATOS INSERTADOS
    print("=" * 80)
    print("VERIFICACIÓN DE DATOS EN TABLA TEMPORAL")
    print("=" * 80)
    
    cursor.execute("""
        SELECT nit_emisor, razon_social, fecha_emision, prefijo, folio, valor
        FROM temp_maestro_prueba
        ORDER BY nit_emisor
    """)
    
    print(f"\n{'NIT':<12} {'Razón Social':<30} {'Fecha':<12} {'Prefijo':<8} {'Folio':<10} {'Valor':<15}")
    print("-" * 95)
    
    errores = []
    for i, fila in enumerate(cursor.fetchall(), 1):
        nit, razon, fecha, prefijo, folio, valor = fila
        
        # Verificar cada campo
        problemas = []
        if not prefijo or prefijo == '':
            problemas.append("PREFIJO_VACÍO")
        if not folio or folio == '0':
            problemas.append("FOLIO_0")
        if not valor or valor == 0:
            problemas.append("VALOR_0")
        if fecha == datetime.now().date():
            problemas.append("FECHA_HOY")
        
        if problemas:
            estado = "❌ " + ", ".join(problemas)
            errores.append(f"Registro {i}: {estado}")
        else:
            estado = "✅"
        
        razon_corta = razon[:28] + ".." if len(razon) > 30 else razon
        prefijo_str = f"'{prefijo}'" if prefijo else "NULL"
        folio_str = f"'{folio}'" if folio else "NULL"
        valor_str = f"${valor:,.2f}" if valor else "$0.00"
        
        print(f"{nit:<12} {razon_corta:<30} {fecha} {prefijo_str:<8} {folio_str:<10} {valor_str:<15} {estado}")
    
    # 10. RESUMEN
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    
    if errores:
        print("\n❌ SE ENCONTRARON PROBLEMAS:")
        for error in errores:
            print(f"   • {error}")
        print("\n⚠️  NO SE INSERTARÁN A LA TABLA maestro_dian_vs_erp")
        print("   El problema está en el código de lectura - necesitamos corregirlo")
    else:
        print("\n✅✅✅ TODOS LOS DATOS SON CORRECTOS ✅✅✅")
        print(f"\nInsertando {len(registros)} registros a maestro_dian_vs_erp...\n")
        
        # Insertar a tabla real
        cursor.execute("""
            INSERT INTO maestro_dian_vs_erp (
                nit_emisor, razon_social, fecha_emision, prefijo, folio,
                valor, tipo_documento, cufe, forma_pago, estado_aprobacion,
                modulo, estado_contable, acuses_recibidos, doc_causado_por,
                dias_desde_emision, tipo_tercero
            )
            SELECT * FROM temp_maestro_prueba
        """)
        conn.commit()
        
        # Verificar
        cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
        total_final = cursor.fetchone()[0]
        
        print(f"✅ Registros en maestro_dian_vs_erp: {total_final:,}")
        print("\n🎉 CARGA DE PRUEBA EXITOSA 🎉")
        print("\nSi quieres cargar TODO el archivo, ejecuta:")
        print("   python cargar_todo_dian.py")
    
    # Limpiar tabla temporal
    print("\n🧹 Limpiando tabla temporal...")
    cursor.execute("DROP TABLE IF EXISTS temp_maestro_prueba")
    conn.commit()
    print("✅ Limpieza completa")
    
    print("\n" + "=" * 80)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
    
finally:
    cursor.close()
    conn.close()
    print("\n✅ Conexión cerrada")
