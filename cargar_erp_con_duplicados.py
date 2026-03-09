"""
Script optimizado para cargar archivos ERP con manejo de duplicados
Usa INSERT con ON CONFLICT DO NOTHING
"""

import os
import sys
import polars as pl
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'gestor_documental',
    'user': 'postgres',
    'password': 'G3st0radm$2025.'
}

RUTA_BASE = r"D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025"
RUTA_ERP_COMERCIAL = os.path.join(RUTA_BASE, "ERP Comercial")
RUTA_ERP_FINANCIERO = os.path.join(RUTA_BASE, "ERP Financiero")
RUTA_DIAN = os.path.join(RUTA_BASE, "Dian")

def limpiar_valor_numerico(valor):
    if valor is None or valor == '' or valor == 'None':
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    valor = str(valor).replace('$', '').replace(' ', '').strip()
    valor = valor.replace('.', '').replace(',', '.')
    try:
        return float(valor)
    except:
        return 0.0

def limpiar_fecha(valor):
    if valor is None or valor == '' or valor == 'None':
        return None
    try:
        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']:
            try:
                fecha = datetime.strptime(str(valor).strip(), fmt)
                return fecha.strftime('%Y-%m-%d')
            except:
                continue
        return None
    except:
        return None

def limpiar_texto(valor):
    if valor is None or valor == 'None':
        return ''
    return str(valor).strip()

def cargar_erp_comercial(conn):
    print("\n" + "="*80)
    print("CARGANDO ERP COMERCIAL (CON MANEJO DE DUPLICADOS)")
    print("="*80)
    
    archivo = os.path.join(RUTA_ERP_COMERCIAL, "ERP Comercial.xlsx")
    if not os.path.exists(archivo):
        print("⚠️  Archivo no encontrado")
        return 0
    
    print(f"\n📄 Procesando: {os.path.basename(archivo)}")
    
    try:
        df = pl.read_excel(archivo)
        print(f"   Registros encontrados: {len(df):,}")
        
        columnas_esperadas = {
            'Proveedor': 'proveedor',
            'Razón social proveedor': 'razon_social_proveedor',
            'Fecha docto. prov.': 'fecha_docto_prov',
            'Docto. proveedor': 'docto_proveedor',
            'Valor bruto': 'valor_bruto',
            'Valor imptos': 'valor_imptos',
            'C.O.': 'co',
            'Usuario creación': 'usuario_creacion',
            'Clase docto.': 'clase_docto',
            'Nro documento': 'nro_documento'
        }
        
        df_renamed = df.rename({k: v for k, v in columnas_esperadas.items() if k in df.columns})
        
        # Preparar datos
        datos = []
        for row in df_renamed.iter_rows(named=True):
            datos.append((
                limpiar_texto(row.get('proveedor')),
                limpiar_texto(row.get('razon_social_proveedor')),
                limpiar_fecha(row.get('fecha_docto_prov')),
                limpiar_texto(row.get('docto_proveedor')),
                limpiar_valor_numerico(row.get('valor_bruto')),
                limpiar_valor_numerico(row.get('valor_imptos')),
                limpiar_texto(row.get('co')),
                limpiar_texto(row.get('usuario_creacion')),
                limpiar_texto(row.get('clase_docto')),
                limpiar_texto(row.get('nro_documento'))
            ))
        
        # INSERT con ON CONFLICT
        cursor = conn.cursor()
        sql = """
            INSERT INTO erp_comercial 
            (proveedor, razon_social_proveedor, fecha_docto_prov, docto_proveedor,
             valor_bruto, valor_imptos, co, usuario_creacion, clase_docto, nro_documento)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (clave_erp_comercial) DO NOTHING
        """
        
        print("   ⚡ Insertando con manejo de duplicados...")
        execute_batch(cursor, sql, datos, page_size=10000)
        conn.commit()
        
        # Contar registros insertados
        cursor.execute("SELECT COUNT(*) FROM erp_comercial")
        total = cursor.fetchone()[0]
        cursor.close()
        
        print(f"   ✅ Registros únicos cargados: {total:,}")
        return total
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        conn.rollback()
        return 0

def cargar_erp_financiero(conn):
    print("\n" + "="*80)
    print("CARGANDO ERP FINANCIERO (CON MANEJO DE DUPLICADOS)")
    print("="*80)
    
    archivo = os.path.join(RUTA_ERP_FINANCIERO, "ERP Financiero.xlsx")
    if not os.path.exists(archivo):
        print("⚠️  Archivo no encontrado")
        return 0
    
    print(f"\n📄 Procesando: {os.path.basename(archivo)}")
    
    try:
        df = pl.read_excel(archivo)
        print(f"   Registros encontrados: {len(df):,}")
        
        columnas_esperadas = {
            'Proveedor': 'proveedor',
            'Razón social proveedor': 'razon_social_proveedor',
            'Fecha proveedor': 'fecha_proveedor',
            'Docto. proveedor': 'docto_proveedor',
            'Valor subtotal': 'valor_subtotal',
            'Valor impuestos': 'valor_impuestos',
            'C.O.': 'co',
            'Usuario creación': 'usuario_creacion',
            'Clase docto.': 'clase_docto',
            'Nro documento': 'nro_documento'
        }
        
        df_renamed = df.rename({k: v for k, v in columnas_esperadas.items() if k in df.columns})
        
        datos = []
        for row in df_renamed.iter_rows(named=True):
            datos.append((
                limpiar_texto(row.get('proveedor')),
                limpiar_texto(row.get('razon_social_proveedor')),
                limpiar_fecha(row.get('fecha_proveedor')),
                limpiar_texto(row.get('docto_proveedor')),
                limpiar_valor_numerico(row.get('valor_subtotal')),
                limpiar_valor_numerico(row.get('valor_impuestos')),
                limpiar_texto(row.get('co')),
                limpiar_texto(row.get('usuario_creacion')),
                limpiar_texto(row.get('clase_docto')),
                limpiar_texto(row.get('nro_documento'))
            ))
        
        cursor = conn.cursor()
        sql = """
            INSERT INTO erp_financiero 
            (proveedor, razon_social_proveedor, fecha_proveedor, docto_proveedor,
             valor_subtotal, valor_impuestos, co, usuario_creacion, clase_docto, nro_documento)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (clave_erp_financiero) DO NOTHING
        """
        
        print("   ⚡ Insertando con manejo de duplicados...")
        execute_batch(cursor, sql, datos, page_size=10000)
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM erp_financiero")
        total = cursor.fetchone()[0]
        cursor.close()
        
        print(f"   ✅ Registros únicos cargados: {total:,}")
        return total
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        conn.rollback()
        return 0

def cargar_dian_faltantes(conn):
    """Carga solo los archivos DIAN que fallaron con duplicados"""
    print("\n" + "="*80)
    print("COMPLETANDO CARGA DE DIAN (ARCHIVOS PENDIENTES)")
    print("="*80)
    
    archivos_pendientes = [
        "Desde 01-03-2025 Hasta 30-04-2025.xlsx",
        "Desde 01-07-2025 Hasta 31-08-2025.xlsx"
    ]
    
    total = 0
    
    for nombre_archivo in archivos_pendientes:
        archivo = os.path.join(RUTA_DIAN, nombre_archivo)
        if not os.path.exists(archivo):
            print(f"\n⚠️  Archivo no encontrado: {nombre_archivo}")
            continue
        
        print(f"\n📄 Procesando: {nombre_archivo}")
        
        try:
            df = pl.read_excel(archivo)
            print(f"   Registros encontrados: {len(df):,}")
            
            # Usar INSERT con ON CONFLICT para ignorar duplicados
            cursor = conn.cursor()
            
            registros_nuevos = 0
            for row in df.iter_rows(named=True):
                try:
                    cursor.execute("""
                        INSERT INTO dian 
                        (tipo_documento, cufe_cude, folio, prefijo, divisa, forma_pago, medio_pago,
                         fecha_emision, fecha_recepcion, nit_emisor, nombre_emisor, nit_receptor,
                         nombre_receptor, iva, ica, ic, inc, timbre, inc_bolsas, in_carbono,
                         in_combustibles, ic_datos, icl, inpp, ibua, icui, rete_iva, rete_renta,
                         rete_ica, total, estado, grupo)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (clave) DO NOTHING
                    """, (
                        limpiar_texto(row.get('Tipo de documento')),
                        limpiar_texto(row.get('CUFE/CUDE')),
                        limpiar_texto(row.get('Folio')),
                        limpiar_texto(row.get('Prefijo')),
                        limpiar_texto(row.get('Divisa')),
                        limpiar_texto(row.get('Forma de Pago')),
                        limpiar_texto(row.get('Medio de Pago')),
                        limpiar_fecha(row.get('Fecha Emisión')),
                        limpiar_fecha(row.get('Fecha Recepción')),
                        limpiar_texto(row.get('NIT Emisor')),
                        limpiar_texto(row.get('Nombre Emisor')),
                        limpiar_texto(row.get('NIT Receptor')),
                        limpiar_texto(row.get('Nombre Receptor')),
                        limpiar_valor_numerico(row.get('IVA')),
                        limpiar_valor_numerico(row.get('ICA')),
                        limpiar_valor_numerico(row.get('IC')),
                        limpiar_valor_numerico(row.get('INC')),
                        limpiar_valor_numerico(row.get('Timbre')),
                        limpiar_valor_numerico(row.get('INC Bolsas')),
                        limpiar_valor_numerico(row.get('IN Carbono')),
                        limpiar_valor_numerico(row.get('IN Combustibles')),
                        limpiar_valor_numerico(row.get('IC Datos')),
                        limpiar_valor_numerico(row.get('ICL')),
                        limpiar_valor_numerico(row.get('INPP')),
                        limpiar_valor_numerico(row.get('IBUA')),
                        limpiar_valor_numerico(row.get('ICUI')),
                        limpiar_valor_numerico(row.get('Rete IVA')),
                        limpiar_valor_numerico(row.get('Rete Renta')),
                        limpiar_valor_numerico(row.get('Rete ICA')),
                        limpiar_valor_numerico(row.get('Total')),
                        limpiar_texto(row.get('Estado')),
                        limpiar_texto(row.get('Grupo'))
                    ))
                    registros_nuevos += 1
                    
                    if registros_nuevos % 10000 == 0:
                        conn.commit()
                        print(f"      Procesados: {registros_nuevos:,}...")
                        
                except:
                    pass  # Ignora duplicados
            
            conn.commit()
            cursor.close()
            
            print(f"   ✅ Registros nuevos cargados: {registros_nuevos:,}")
            total += registros_nuevos
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            conn.rollback()
    
    return total

def main():
    print("\n" + "="*80)
    print("COMPLETAR CARGA DE ARCHIVOS DIAN VS ERP")
    print("Manejo automático de duplicados")
    print("="*80)
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    inicio = datetime.now()
    
    try:
        print("\n🔌 Conectando a PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Conexión exitosa")
        
        total_erp_comercial = cargar_erp_comercial(conn)
        total_erp_financiero = cargar_erp_financiero(conn)
        total_dian_nuevos = cargar_dian_faltantes(conn)
        
        # Totales finales
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dian")
        total_dian = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM acuses")
        total_acuses = cursor.fetchone()[0]
        cursor.close()
        
        fin = datetime.now()
        duracion = (fin - inicio).total_seconds()
        
        print("\n" + "="*80)
        print("RESUMEN FINAL COMPLETO")
        print("="*80)
        print(f"✅ DIAN:           {total_dian:>10,} registros")
        print(f"✅ ERP Comercial:  {total_erp_comercial:>10,} registros")
        print(f"✅ ERP Financiero: {total_erp_financiero:>10,} registros")
        print(f"✅ Acuses:         {total_acuses:>10,} registros")
        print(f"{'─'*80}")
        print(f"✅ TOTAL:          {total_dian + total_erp_comercial + total_erp_financiero + total_acuses:>10,} registros")
        print(f"\n⏱️  Tiempo: {duracion:.2f} segundos")
        
        if duracion > 0:
            velocidad = (total_erp_comercial + total_erp_financiero + total_dian_nuevos) / duracion
            print(f"⚡ Velocidad: {velocidad:,.0f} registros/segundo")
        
        print("\n" + "="*80)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
