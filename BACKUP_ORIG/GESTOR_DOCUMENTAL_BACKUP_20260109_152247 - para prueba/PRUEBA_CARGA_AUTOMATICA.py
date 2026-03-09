# -*- coding: utf-8 -*-
"""
PRUEBA DE CARGA AUTOMÁTICA - Versión Standalone
Fecha: 30 de Diciembre de 2025
Propósito: Probar carga automática de archivos sin usar navegador
"""

import psycopg2
import pandas as pd
import polars as pl
from pathlib import Path
import hashlib
import time
import shutil
from datetime import datetime

# Configuración de conexión
DB_CONFIG = {
    'dbname': 'gestor_documental',
    'user': 'gestor_user',
    'password': 'Gestor2024$',
    'host': 'localhost',
    'port': '5432'
}

def calcular_hash_archivo(ruta_archivo):
    """Calcula hash MD5 de un archivo"""
    try:
        with open(ruta_archivo, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"❌ Error calculando hash: {str(e)}")
        return None

def archivo_ya_procesado(conn, hash_md5):
    """Verifica si un archivo ya fue procesado"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, fecha_procesamiento FROM archivos_procesados WHERE hash_md5 = %s",
        (hash_md5,)
    )
    resultado = cursor.fetchone()
    cursor.close()
    return resultado

def procesar_archivo_excel(ruta_archivo, tipo_archivo, conn):
    """Procesa un archivo Excel/CSV y lo inserta en maestro"""
    tiempo_inicio = time.time()
    
    try:
        print(f"\n   📄 Procesando: {Path(ruta_archivo).name}")
        
        # Leer archivo
        if ruta_archivo.endswith('.csv'):
            df = pd.read_csv(ruta_archivo, dtype=str, encoding='utf-8')
        else:
            df = pd.read_excel(ruta_archivo, dtype=str, engine='openpyxl')
        
        print(f"   📊 Registros leídos: {len(df):,}")
        
        # Guardar como CSV temporal
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as tmp:
            df.to_csv(tmp.name, index=False)
            csv_path = tmp.name
        
        # Cargar con Polars para mayor velocidad
        df_polars = pl.read_csv(csv_path, encoding='utf-8-sig', infer_schema_length=10000)
        
        if df_polars.is_empty():
            print("   ⚠️ Archivo vacío, omitiendo...")
            return 0, 0
        
        # Insertar en maestro usando COPY FROM
        cursor = conn.cursor()
        
        # Preparar CSV en memoria
        import io
        csv_buffer = io.StringIO()
        
        # Mapear columnas (simplificado - ajustar según necesidad)
        # Por ahora asumimos que el archivo ya tiene las columnas correctas
        df_polars.write_csv(csv_buffer)
        csv_buffer.seek(0)
        
        # INSERT masivo
        try:
            # Leer primera línea para obtener nombres de columnas
            primera_linea = csv_buffer.readline()
            csv_buffer.seek(0)
            
            columnas = primera_linea.strip().split(',')
            columnas_str = ','.join(columnas)
            
            cursor.copy_expert(
                sql=f"COPY maestro_dian_vs_erp ({columnas_str}) FROM STDIN WITH CSV HEADER",
                file=csv_buffer
            )
            
            registros_insertados = len(df_polars)
            print(f"   ✅ {registros_insertados:,} registros insertados")
            
        except Exception as e:
            print(f"   ⚠️ Error en COPY FROM: {str(e)}")
            print("   🔄 Intentando INSERT convencional...")
            
            # Fallback: INSERT fila por fila (más lento pero más robusto)
            registros_insertados = 0
            for row in df.itertuples(index=False):
                try:
                    # Construir INSERT dinámico
                    valores = ', '.join(['%s'] * len(row))
                    cursor.execute(
                        f"INSERT INTO maestro_dian_vs_erp ({columnas_str}) VALUES ({valores})",
                        tuple(row)
                    )
                    registros_insertados += 1
                except Exception as e_insert:
                    # Ignorar duplicados
                    pass
        
        conn.commit()
        cursor.close()
        
        # Eliminar duplicados
        print("   🔄 Eliminando duplicados...")
        registros_duplicados = eliminar_duplicados(conn)
        print(f"   ✅ {registros_duplicados:,} duplicados eliminados")
        
        # Limpiar archivo temporal
        Path(csv_path).unlink(missing_ok=True)
        
        tiempo_proceso = time.time() - tiempo_inicio
        print(f"   ⏱️ Tiempo: {tiempo_proceso:.2f} segundos")
        
        return registros_insertados, registros_duplicados
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        conn.rollback()
        return 0, 0

def eliminar_duplicados(conn):
    """Elimina registros duplicados de maestro"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM maestro_dian_vs_erp
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM maestro_dian_vs_erp
                GROUP BY prefijo, folio, nit_proveedor, nit_empresa
            )
        """)
        eliminados = cursor.rowcount
        conn.commit()
        cursor.close()
        return eliminados
    except Exception as e:
        print(f"Error eliminando duplicados: {str(e)}")
        conn.rollback()
        return 0

def registrar_archivo_procesado(conn, nombre, ruta, carpeta, hash_md5, 
                                 insertados, duplicados, tiempo, estado='COMPLETADO', error=None):
    """Registra un archivo como procesado en la base de datos"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO archivos_procesados 
            (nombre_archivo, ruta_completa, carpeta_origen, hash_md5,
             registros_insertados, registros_duplicados, tiempo_proceso_segundos,
             usuario_proceso, estado, mensaje_error)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre, ruta, carpeta, hash_md5, insertados, duplicados, 
              tiempo, 'SISTEMA', estado, error))
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"⚠️ Error registrando archivo: {str(e)}")
        conn.rollback()

def mover_a_procesados(ruta_origen, ruta_procesados_base):
    """Mueve archivo a carpeta de procesados"""
    try:
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        carpeta_destino = Path(ruta_procesados_base) / fecha_hoy
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        
        archivo = Path(ruta_origen)
        destino = carpeta_destino / archivo.name
        
        shutil.move(str(archivo), str(destino))
        print(f"   📁 Movido a: {destino}")
        return True
    except Exception as e:
        print(f"   ⚠️ Error moviendo archivo: {str(e)}")
        return False

def main():
    """Función principal"""
    print("=" * 80)
    print("🚀 CARGA AUTOMÁTICA DE ARCHIVOS - Versión Standalone")
    print("=" * 80)
    
    try:
        # Conectar a PostgreSQL
        print("\n1️⃣ Conectando a base de datos...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        print("   ✅ Conectado")
        
        # Obtener configuraciones
        print("\n2️⃣ Obteniendo configuraciones...")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nombre_carpeta, ruta_pendientes, ruta_procesados, tipo_archivo
            FROM configuracion_rutas_carga
            WHERE activa = TRUE
            ORDER BY orden_procesamiento
        """)
        configuraciones = cursor.fetchall()
        cursor.close()
        
        print(f"   ✅ {len(configuraciones)} configuraciones activas")
        
        # Procesar cada configuración
        total_archivos = 0
        total_procesados = 0
        total_omitidos = 0
        total_registros = 0
        
        for config in configuraciones:
            nombre_carpeta, ruta_pendientes, ruta_procesados, tipo_archivo = config
            
            print(f"\n3️⃣ Procesando carpeta: {nombre_carpeta}")
            print(f"   📁 Ruta: {ruta_pendientes}")
            
            # Verificar que existe
            path = Path(ruta_pendientes)
            if not path.exists():
                print(f"   ⚠️ Carpeta no existe, omitiendo...")
                continue
            
            # Buscar archivos
            archivos = list(path.glob('*.xlsx')) + list(path.glob('*.xlsm')) + list(path.glob('*.csv'))
            print(f"   📊 Archivos encontrados: {len(archivos)}")
            
            for archivo in archivos:
                total_archivos += 1
                
                # Calcular hash
                hash_md5 = calcular_hash_archivo(archivo)
                if not hash_md5:
                    continue
                
                # Verificar si ya fue procesado
                ya_procesado = archivo_ya_procesado(conn, hash_md5)
                if ya_procesado:
                    print(f"\n   ⏭️ Ya procesado: {archivo.name}")
                    print(f"      Fecha: {ya_procesado[1]}")
                    total_omitidos += 1
                    continue
                
                # Procesar archivo
                tiempo_inicio = time.time()
                insertados, duplicados = procesar_archivo_excel(
                    str(archivo), tipo_archivo, conn
                )
                tiempo_proceso = time.time() - tiempo_inicio
                
                if insertados > 0:
                    total_procesados += 1
                    total_registros += insertados
                    
                    # Registrar en BD
                    registrar_archivo_procesado(
                        conn, archivo.name, str(archivo), nombre_carpeta,
                        hash_md5, insertados, duplicados, tiempo_proceso
                    )
                    
                    # Mover a procesados
                    if ruta_procesados:
                        mover_a_procesados(archivo, ruta_procesados)
        
        # Resumen final
        print("\n" + "=" * 80)
        print("✅ PROCESAMIENTO COMPLETADO")
        print("=" * 80)
        print(f"\n📊 RESUMEN:")
        print(f"   • Archivos encontrados:  {total_archivos}")
        print(f"   • Archivos procesados:   {total_procesados}")
        print(f"   • Archivos omitidos:     {total_omitidos} (ya procesados)")
        print(f"   • Total registros:       {total_registros:,}")
        print()
        
        conn.close()
        
    except psycopg2.Error as e:
        print(f"\n❌ Error de PostgreSQL: {e}")
        if conn:
            conn.rollback()
            conn.close()
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()

if __name__ == '__main__':
    main()
    input("\n✅ Presiona Enter para cerrar...")
