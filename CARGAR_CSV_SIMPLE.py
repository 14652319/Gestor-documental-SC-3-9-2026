"""
CARGAR_CSV_SIMPLE.py
====================
Script simplificado para cargar CSV con fechas correctas
SIN dependencias de .env
"""

import polars as pl
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
from datetime import datetime

def convertir_fecha_csv(fecha_str):
    """Convierte fecha DD-MM-YYYY a date de Python"""
    if not fecha_str or fecha_str == '':
        return None
    try:
        return datetime.strptime(str(fecha_str), '%d-%m-%Y').date()
    except:
        try:
            return datetime.strptime(str(fecha_str), '%d-%m-%Y %H:%M:%S').date()
        except:
            try:
                return datetime.strptime(str(fecha_str), '%Y-%m-%d').date()
            except:
                return None

# Configuración hardcodeada
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'gestor_documental',
    'user': 'postgres',
    'password': 'Vimer2024*'
}

print("="*80)
print("🚀 CARGAR CSV CON FECHAS CORRECTAS")
print("="*80)
print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# Conectar a PostgreSQL
try:
    print("\n🔌 Conectando a PostgreSQL...")
    # ⚠️ FIX: Usar URI en lugar de dict para evitar error de encoding en Windows
    conn_uri = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    conn = psycopg2.connect(conn_uri)
    cursor = conn.cursor()
    print("✅ Conectado exitosamente")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# PASO 1: Limpiar tabla
print("\n" + "="*80)
print("🗑️  PASO 1: LIMPIAR TABLA maestro_dian_vs_erp")
print("="*80)

try:
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp;")
    count_antes = cursor.fetchone()[0]
    print(f"Registros antes: {count_antes:,}")
    
    cursor.execute("TRUNCATE TABLE maestro_dian_vs_erp;")
    conn.commit()
    print("✅ Tabla limpiada con TRUNCATE")
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp;")
    count_despues = cursor.fetchone()[0]
    print(f"Registros después: {count_despues:,}")
    
except Exception as e:
    print(f"❌ Error limpiando tabla: {e}")
    conn.rollback()
    exit(1)

# PASO 2: Cargar CSV
print("\n" + "="*80)
print("📂 PASO 2: CARGAR CSV")
print("="*80)

csv_path = Path("uploads/dian/Desde_01-01-2025_Hasta_28-02-2025_ea77100881.csv")

if not csv_path.exists():
    print(f"❌ No se encontró el archivo: {csv_path}")
    exit(1)

print(f"✅ Archivo: {csv_path.name}")

try:
    # Leer con Polars (normalizar columnas)
    print("\n🔄 Leyendo CSV con Polars...")
    df = pl.read_csv(
        str(csv_path),
        infer_schema_length=0,
        ignore_errors=True,
        null_values=["", " "]
    )
    
    # Normalizar nombres de columnas
    df = df.rename({c: c.strip().lower() for c in df.columns})
    
    print(f"✅ CSV leído: {df.height:,} registros")
    print(f"📊 Columnas: {len(df.columns)}")
    
    # Convertir a Pandas para procesar
    print("\n🔄 Convirtiendo a Pandas...")
    df_pd = df.to_pandas()
    print("✅ Convertido")
    
    # PASO 3: Procesar datos
    print("\n" + "="*80)
    print("⚙️  PASO 3: PROCESAR DATOS")
    print("="*80)
    
    registros = []
    errores_fecha = 0
    
    for idx, row in df_pd.iterrows():
        # Extraer datos
        nit = str(row.get('nit emisor', '')).strip()
        razon_social = str(row.get('nombre emisor', '')).strip()
        prefijo = str(row.get('prefijo', '')).strip()
        folio = str(row.get('folio', '')).strip()
        
        # Fecha emisión con múltiples variantes
        fecha_emision_raw = None
        for col_var in ['fecha emisión', 'fecha emision', 'fecha_emision']:
            if col_var in row.index:
                val = row[col_var]
                if val and str(val).strip() and str(val) != 'nan':
                    fecha_emision_raw = str(val).strip()
                    break
        
        # Convertir fecha
        if fecha_emision_raw:
            fecha_emision = convertir_fecha_csv(fecha_emision_raw)
            if fecha_emision is None:
                errores_fecha += 1
                if idx < 5:
                    print(f"   ⚠️  Fila {idx}: Error parseando fecha: {fecha_emision_raw}")
        else:
            fecha_emision = None
            errores_fecha += 1
            if idx < 5:
                print(f"   ⚠️  Fila {idx}: Fecha no encontrada")
        
        # Valor/Total
        valor = 0.0
        for col_var in ['total', 'valor']:
            if col_var in row.index:
                val = row[col_var]
                if val and str(val) != 'nan':
                    try:
                        valor = float(str(val).replace(',', '').replace('$', ''))
                        break
                    except:
                        pass
        
        # Forma de pago
        forma_pago = ''
        for col_var in ['forma de pago', 'forma pago', 'forma_pago']:
            if col_var in row.index:
                val = row[col_var]
                if val and str(val) != 'nan':
                    forma_pago = str(val).strip()
                    break
        
        # Agregar registro
        registros.append((
            nit,
            razon_social,
            fecha_emision,
            prefijo,
            folio,
            valor,
            '',  # tipo_documento
            '',  # cufe
            forma_pago,
            'Pendiente',  # estado_aprobacion
            '',  # modulo
            'No Registrada',  # estado_contable
            0,  # acuses_recibidos
            0,  # dias_desde_emision
            '',  # tipo_tercero
            '',  # doc_causado_por
            datetime.now()  # fecha_registro
        ))
        
        # Mostrar progreso
        if (idx + 1) % 10000 == 0:
            print(f"   Procesados: {idx + 1:,} registros...")
    
    print(f"\n✅ Total registros procesados: {len(registros):,}")
    print(f"⚠️  Errores de fecha: {errores_fecha:,}")
    
    # PASO 4: Insertar en base de datos
    print("\n" + "="*80)
    print("💾 PASO 4: INSERTAR EN BASE DE DATOS")
    print("="*80)
    
    insert_sql = """
        INSERT INTO maestro_dian_vs_erp (
            nit_emisor, razon_social, fecha_emision, prefijo, folio, valor,
            tipo_documento, cufe, forma_pago, estado_aprobacion, modulo,
            estado_contable, acuses_recibidos, dias_desde_emision, tipo_tercero,
            doc_causado_por, fecha_registro
        ) VALUES %s
    """
    
    print(f"Insertando {len(registros):,} registros...")
    execute_values(cursor, insert_sql, registros, page_size=10000)
    conn.commit()
    print("✅ Datos insertados")
    
    # Verificar
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp;")
    count_final = cursor.fetchone()[0]
    print(f"📊 Total en BD: {count_final:,} registros")
    
    # Verificar fechas
    cursor.execute("""
        SELECT fecha_emision, COUNT(*) as cantidad
        FROM maestro_dian_vs_erp
        GROUP BY fecha_emision
        ORDER BY cantidad DESC
        LIMIT 5;
    """)
    
    print(f"\n📅 Fechas más comunes:")
    for fecha, cantidad in cursor.fetchall():
        print(f"   {fecha}: {cantidad:,} registros")
    
    print("\n" + "="*80)
    print("✅ ¡PROCESO COMPLETADO EXITOSAMENTE!")
    print("="*80)
    print("\n🌐 Verifica en el navegador:")
    print("   http://localhost:8099/dian_vs_erp/visor_v2")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
    exit(1)
finally:
    cursor.close()
    conn.close()
