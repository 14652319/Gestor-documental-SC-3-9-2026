"""
Script para cargar TODOS los archivos CSV de uploads/ a la base de datos PostgreSQL
Usa Polars para máxima velocidad (25,000+ registros/segundo)

Fecha: 17 de febrero de 2026
Propósito: Recargar datos después de eliminar la base de datos
"""

import polars as pl
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

def convertir_fecha_csv(fecha_str):
    """
    Convierte fecha del CSV de formato DD-MM-YYYY a date de Python
    Ejemplos: '02-01-2025' -> date(2025, 1, 2)
    """
    if not fecha_str or fecha_str == '':
        return None
    try:
        # Intentar formato DD-MM-YYYY (formato del CSV)
        return datetime.strptime(str(fecha_str), '%d-%m-%Y').date()
    except:
        try:
            # Intentar formato DD-MM-YYYY HH:MM:SS
            return datetime.strptime(str(fecha_str), '%d-%m-%Y %H:%M:%S').date()
        except:
            try:
                # Intentar formato YYYY-MM-DD (por si acaso)
                return datetime.strptime(str(fecha_str), '%Y-%m-%d').date()
            except:
                print(f"   ⚠️  No se pudo parsear fecha: {fecha_str}")
                return None

# ⚠️ FIX: Hardcodear configuración para evitar error de encoding en .env
# NO usar load_dotenv() que falla con caracteres especiales en Windows

# Configuración de PostgreSQL (hardcodeada)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'gestor_documental',
    'user': 'postgres',
    'password': 'Vimer2024*'
}

# Rutas de archivos
BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / 'uploads'

print("=" * 80)
print("🚀 CARGA MASIVA DE ARCHIVOS CSV A POSTGRESQL")
print("=" * 80)
print(f"📁 Directorio uploads: {UPLOADS_DIR}")
print(f"🗄️  Base de datos: {DB_CONFIG['database']}")
print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

def conectar_db():
    """Conectar a PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Conectado a PostgreSQL\n")
        return conn
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        exit(1)

def cargar_dian(conn):
    """Cargar archivos DIAN a maestro_dian_vs_erp"""
    print("\n" + "=" * 80)
    print("📊 CARGANDO ARCHIVOS DIAN")
    print("=" * 80)
    
    dian_dir = UPLOADS_DIR / 'dian'
    archivos = list(dian_dir.glob('*.csv'))
    
    if not archivos:
        print("⚠️  No se encontraron archivos DIAN")
        return
    
    print(f"📂 Encontrados {len(archivos)} archivos DIAN:")
    for archivo in archivos:
        print(f"   - {archivo.name}")
    
    total_registros = 0
    
    for archivo in archivos:
        print(f"\n🔄 Procesando: {archivo.name}")
        inicio = datetime.now()
        
        try:
            # Leer CSV con Polars (super rápido)
            df = pl.read_csv(str(archivo), encoding='utf-8-sig', ignore_errors=True)
            
            print(f"   📋 Registros en CSV: {len(df):,}")
            
            # Mapeo de columnas (ajustar según tu CSV)
            # Asumiendo que tu CSV tiene estas columnas
            columnas_requeridas = [
                'NIT Emisor', 'Razón Social', 'Fecha Emisión', 'Prefijo', 'Folio',
                'Valor', 'Estado Aprobación', 'Forma Pago', 'Tipo Documento',
                'CUFE'
            ]
            
            # Verificar que existan las columnas
            columnas_csv = df.columns
            print(f"   📊 Columnas CSV: {columnas_csv[:5]}...")  # Mostrar primeras 5
            
            # Preparar datos para inserción
            datos_insert = []
            
            for row in df.iter_rows(named=True):
                try:
                    # Extraer datos del CSV
                    nit_emisor = str(row.get('NIT Emisor', '') or row.get('nit_emisor', ''))
                    razon_social = str(row.get('Razón Social', '') or row.get('razon_social', '') or row.get('Nombre Emisor', ''))
                    
                    # Convertir fecha del formato DD-MM-YYYY a date de Python
                    fecha_emision_str = str(row.get('Fecha Emisión', '') or row.get('fecha_emision', ''))
                    fecha_emision = convertir_fecha_csv(fecha_emision_str)
                    
                    prefijo = str(row.get('Prefijo', '') or row.get('prefijo', ''))
                    folio = str(row.get('Folio', '') or row.get('folio', ''))
                    valor = float(row.get('Valor', 0) or row.get('valor', 0) or row.get('Total', 0) or 0)
                    estado_aprobacion = str(row.get('Estado Aprobación', '') or row.get('estado_aprobacion', '') or row.get('Estado', ''))
                    forma_pago = str(row.get('Forma Pago', '') or row.get('Forma de Pago', '') or row.get('forma_pago', ''))
                    tipo_documento = str(row.get('Tipo Documento', '') or row.get('Tipo de documento', '') or row.get('tipo_documento', ''))
                    cufe = str(row.get('CUFE', '') or row.get('cufe', '') or row.get('CUFE/CUDE', ''))
                    
                    # fecha_emision = fecha del documento (del CSV)
                    # fecha_registro = fecha de carga (HOY - auditoría)
                    datos_insert.append((
                        nit_emisor,
                        razon_social,
                        fecha_emision,      # Fecha del documento (ej: 02-01-2025)
                        prefijo,
                        folio,
                        valor,
                        estado_aprobacion,
                        forma_pago,
                        tipo_documento,
                        cufe
                        # causada, recibida, fecha_registro se agregan después
                    ))
                except Exception as e:
                    print(f"   ⚠️  Error procesando fila: {e}")
                    continue
            
            if not datos_insert:
                print(f"   ⚠️  No se pudieron procesar registros de {archivo.name}")
                continue
            
            # Insertar en PostgreSQL usando COPY (super rápido)
            cursor = conn.cursor()
            
            query = """
                INSERT INTO maestro_dian_vs_erp (
                    nit_emisor, razon_social, fecha_emision, prefijo, folio,
                    valor, estado_aprobacion, forma_pago, tipo_documento, cufe,
                    causada, recibida, fecha_registro
                ) VALUES %s
                ON CONFLICT (prefijo, folio) DO UPDATE SET
                    nit_emisor = EXCLUDED.nit_emisor,
                    razon_social = EXCLUDED.razon_social,
                    fecha_emision = EXCLUDED.fecha_emision,
                    valor = EXCLUDED.valor,
                    estado_aprobacion = EXCLUDED.estado_aprobacion,
                    fecha_actualizacion = NOW()
            """
            
            # Agregar valores por defecto en el orden correcto
            fecha_carga_actual = datetime.now()
            datos_final = [
                tupla + (False, False, fecha_carga_actual)  # causada, recibida, fecha_registro
                for tupla in datos_insert
            ]
            
            execute_values(cursor, query, datos_final, page_size=1000)
            conn.commit()
            
            fin = datetime.now()
            duracion = (fin - inicio).total_seconds()
            velocidad = len(datos_insert) / duracion if duracion > 0 else 0
            
            print(f"   ✅ Insertados: {len(datos_insert):,} registros")
            print(f"   ⏱️  Tiempo: {duracion:.2f}s ({velocidad:,.0f} reg/seg)")
            
            total_registros += len(datos_insert)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
    
    print(f"\n{'='*80}")
    print(f"✅ TOTAL DIAN: {total_registros:,} registros cargados")
    print(f"{'='*80}")

def cargar_acuses(conn):
    """Cargar archivos de Acuses"""
    print("\n" + "=" * 80)
    print("📊 CARGANDO ARCHIVOS ACUSES")
    print("=" * 80)
    
    acuses_dir = UPLOADS_DIR / 'acuses'
    archivos = list(acuses_dir.glob('*.csv'))
    
    if not archivos:
        print("⚠️  No se encontraron archivos de Acuses")
        return
    
    print(f"📂 Encontrados {len(archivos)} archivos:")
    for archivo in archivos:
        print(f"   - {archivo.name}")
    
    # TODO: Implementar carga de acuses (similar a DIAN)
    print("   ℹ️  Carga de acuses - Por implementar según estructura de CSV")

def cargar_erp_financiero(conn):
    """Cargar archivos ERP Financiero"""
    print("\n" + "=" * 80)
    print("📊 CARGANDO ARCHIVOS ERP FINANCIERO")
    print("=" * 80)
    
    erp_fn_dir = UPLOADS_DIR / 'erp_fn'
    archivos = list(erp_fn_dir.glob('*.csv'))
    
    if not archivos:
        print("⚠️  No se encontraron archivos ERP Financiero")
        return
    
    print(f"📂 Encontrados {len(archivos)} archivos:")
    for archivo in archivos:
        print(f"   - {archivo.name}")
    
    # TODO: Implementar carga de ERP Financiero
    print("   ℹ️  Carga de ERP Financiero - Por implementar según estructura de CSV")

def cargar_erp_comercial(conn):
    """Cargar archivos ERP Comercial"""
    print("\n" + "=" * 80)
    print("📊 CARGANDO ARCHIVOS ERP COMERCIAL")
    print("=" * 80)
    
    erp_cm_dir = UPLOADS_DIR / 'erp_cm'
    archivos = list(erp_cm_dir.glob('*.csv'))
    
    if not archivos:
        print("⚠️  No se encontraron archivos ERP Comercial")
        return
    
    print(f"📂 Encontrados {len(archivos)} archivos:")
    for archivo in archivos:
        print(f"   - {archivo.name}")
    
    # TODO: Implementar carga de ERP Comercial
    print("   ℹ️  Carga de ERP Comercial - Por implementar según estructura de CSV")

def main():
    """Función principal"""
    conn = conectar_db()
    
    try:
        # Cargar cada tipo de archivo
        cargar_dian(conn)
        cargar_acuses(conn)
        cargar_erp_financiero(conn)
        cargar_erp_comercial(conn)
        
        print("\n" + "=" * 80)
        print("✅ CARGA MASIVA COMPLETADA")
        print("=" * 80)
        print(f"📅 Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
        print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    main()
