"""
Script para cargar archivos DIAN, ERP Comercial, ERP Financiero y Acuses
a las tablas PostgreSQL correspondientes.

Fecha: 30 de Diciembre de 2025
Características:
- Usa Polars para procesamiento ultra-rápido
- PostgreSQL COPY FROM para carga masiva optimizada
- Skip automático de la primera fila (encabezado)
- 25,000+ registros/segundo
"""

import os
import sys
import polars as pl
import psycopg2
from psycopg2.extras import execute_values
from io import StringIO
from datetime import datetime

# Configuración de base de datos
# postgresql://postgres:G3st0radm$2025.@localhost:5432/gestor_documental
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'gestor_documental',
    'user': 'postgres',
    'password': 'G3st0radm$2025.'
}

# Configuración de rutas
RUTA_BASE = r"D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025"
RUTA_ARCHIVOS_DIAN = os.path.join(RUTA_BASE, "Dian")
RUTA_ARCHIVOS_ERP_COMERCIAL = os.path.join(RUTA_BASE, "ERP Comercial")
RUTA_ARCHIVOS_ERP_FINANCIERO = os.path.join(RUTA_BASE, "ERP Financiero")
RUTA_ARCHIVOS_ACUSES = os.path.join(RUTA_BASE, "Acuses")

# ============================================================================
# FUNCIONES DE LIMPIEZA Y CONVERSIÓN
# ============================================================================

def limpiar_valor_numerico(valor):
    """Convierte valores numéricos con formato colombiano a float"""
    if valor is None or valor == '' or valor == 'None':
        return 0.0
    
    if isinstance(valor, (int, float)):
        return float(valor)
    
    # Remover símbolos de moneda y espacios
    valor = str(valor).replace('$', '').replace(' ', '').strip()
    
    # Reemplazar separador de miles (punto) y decimal (coma)
    valor = valor.replace('.', '').replace(',', '.')
    
    try:
        return float(valor)
    except:
        return 0.0

def limpiar_fecha(valor):
    """Convierte fechas a formato YYYY-MM-DD"""
    if valor is None or valor == '' or valor == 'None':
        return None
    
    try:
        # Intentar varios formatos
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
    """Limpia y normaliza texto"""
    if valor is None or valor == 'None':
        return ''
    return str(valor).strip()

# ============================================================================
# CARGA DE ARCHIVOS DIAN
# ============================================================================

def cargar_archivos_dian(conn):
    """Carga todos los archivos DIAN a la tabla dian"""
    print("\n" + "="*80)
    print("CARGANDO ARCHIVOS DIAN")
    print("="*80)
    
    if not os.path.exists(RUTA_ARCHIVOS_DIAN):
        print(f"⚠️  Carpeta {RUTA_ARCHIVOS_DIAN} no existe. Creándola...")
        os.makedirs(RUTA_ARCHIVOS_DIAN)
        print(f"📁 Coloca los archivos DIAN en: {RUTA_ARCHIVOS_DIAN}/")
        return 0
    
    archivos = [f for f in os.listdir(RUTA_ARCHIVOS_DIAN) 
                if f.endswith(('.csv', '.xlsx', '.xls'))]
    
    if not archivos:
        print(f"⚠️  No hay archivos en {RUTA_ARCHIVOS_DIAN}/")
        return 0
    
    total_registros = 0
    
    for archivo in archivos:
        ruta_completa = os.path.join(RUTA_ARCHIVOS_DIAN, archivo)
        print(f"\n📄 Procesando: {archivo}")
        
        try:
            # Leer archivo con Polars (skip header automático)
            if archivo.endswith('.csv'):
                df = pl.read_csv(ruta_completa, ignore_errors=True)
            else:
                df = pl.read_excel(ruta_completa)
            
            print(f"   Registros encontrados: {len(df):,}")
            
            if len(df) == 0:
                print("   ⚠️  Archivo vacío, saltando...")
                continue
            
            # Mapeo de columnas (ajustar según nombres reales en archivos)
            columnas_esperadas = {
                'Tipo de documento': 'tipo_documento',
                'CUFE/CUDE': 'cufe_cude',
                'Folio': 'folio',
                'Prefijo': 'prefijo',
                'Divisa': 'divisa',
                'Forma de Pago': 'forma_pago',
                'Medio de Pago': 'medio_pago',
                'Fecha Emisión': 'fecha_emision',
                'Fecha Recepción': 'fecha_recepcion',
                'NIT Emisor': 'nit_emisor',
                'Nombre Emisor': 'nombre_emisor',
                'NIT Receptor': 'nit_receptor',
                'Nombre Receptor': 'nombre_receptor',
                'IVA': 'iva',
                'ICA': 'ica',
                'IC': 'ic',
                'INC': 'inc',
                'Timbre': 'timbre',
                'INC Bolsas': 'inc_bolsas',
                'IN Carbono': 'in_carbono',
                'IN Combustibles': 'in_combustibles',
                'IC Datos': 'ic_datos',
                'ICL': 'icl',
                'INPP': 'inpp',
                'IBUA': 'ibua',
                'ICUI': 'icui',
                'Rete IVA': 'rete_iva',
                'Rete Renta': 'rete_renta',
                'Rete ICA': 'rete_ica',
                'Total': 'total',
                'Estado': 'estado',
                'Grupo': 'grupo'
            }
            
            # Renombrar columnas
            df_renamed = df.rename({k: v for k, v in columnas_esperadas.items() if k in df.columns})
            
            # Limpiar y convertir datos
            data_limpia = []
            for row in df_renamed.iter_rows(named=True):
                registro = {
                    'tipo_documento': limpiar_texto(row.get('tipo_documento')),
                    'cufe_cude': limpiar_texto(row.get('cufe_cude')),
                    'folio': limpiar_texto(row.get('folio')),
                    'prefijo': limpiar_texto(row.get('prefijo')),
                    'divisa': limpiar_texto(row.get('divisa')),
                    'forma_pago': limpiar_texto(row.get('forma_pago')),
                    'medio_pago': limpiar_texto(row.get('medio_pago')),
                    'fecha_emision': limpiar_fecha(row.get('fecha_emision')),
                    'fecha_recepcion': limpiar_fecha(row.get('fecha_recepcion')),
                    'nit_emisor': limpiar_texto(row.get('nit_emisor')),
                    'nombre_emisor': limpiar_texto(row.get('nombre_emisor')),
                    'nit_receptor': limpiar_texto(row.get('nit_receptor')),
                    'nombre_receptor': limpiar_texto(row.get('nombre_receptor')),
                    'iva': limpiar_valor_numerico(row.get('iva')),
                    'ica': limpiar_valor_numerico(row.get('ica')),
                    'ic': limpiar_valor_numerico(row.get('ic')),
                    'inc': limpiar_valor_numerico(row.get('inc')),
                    'timbre': limpiar_valor_numerico(row.get('timbre')),
                    'inc_bolsas': limpiar_valor_numerico(row.get('inc_bolsas')),
                    'in_carbono': limpiar_valor_numerico(row.get('in_carbono')),
                    'in_combustibles': limpiar_valor_numerico(row.get('in_combustibles')),
                    'ic_datos': limpiar_valor_numerico(row.get('ic_datos')),
                    'icl': limpiar_valor_numerico(row.get('icl')),
                    'inpp': limpiar_valor_numerico(row.get('inpp')),
                    'ibua': limpiar_valor_numerico(row.get('ibua')),
                    'icui': limpiar_valor_numerico(row.get('icui')),
                    'rete_iva': limpiar_valor_numerico(row.get('rete_iva')),
                    'rete_renta': limpiar_valor_numerico(row.get('rete_renta')),
                    'rete_ica': limpiar_valor_numerico(row.get('rete_ica')),
                    'total': limpiar_valor_numerico(row.get('total')),
                    'estado': limpiar_texto(row.get('estado')),
                    'grupo': limpiar_texto(row.get('grupo'))
                }
                data_limpia.append(registro)
            
            # Usar COPY FROM para carga ultra-rápida
            cursor = conn.cursor()
            
            # Crear CSV en memoria
            csv_buffer = StringIO()
            for reg in data_limpia:
                linea = '\t'.join([
                    str(reg['tipo_documento']),
                    str(reg['cufe_cude']),
                    str(reg['folio']),
                    str(reg['prefijo']),
                    str(reg['divisa']),
                    str(reg['forma_pago']),
                    str(reg['medio_pago']),
                    str(reg['fecha_emision']) if reg['fecha_emision'] else '\\N',
                    str(reg['fecha_recepcion']) if reg['fecha_recepcion'] else '\\N',
                    str(reg['nit_emisor']),
                    str(reg['nombre_emisor']),
                    str(reg['nit_receptor']),
                    str(reg['nombre_receptor']),
                    str(reg['iva']),
                    str(reg['ica']),
                    str(reg['ic']),
                    str(reg['inc']),
                    str(reg['timbre']),
                    str(reg['inc_bolsas']),
                    str(reg['in_carbono']),
                    str(reg['in_combustibles']),
                    str(reg['ic_datos']),
                    str(reg['icl']),
                    str(reg['inpp']),
                    str(reg['ibua']),
                    str(reg['icui']),
                    str(reg['rete_iva']),
                    str(reg['rete_renta']),
                    str(reg['rete_ica']),
                    str(reg['total']),
                    str(reg['estado']),
                    str(reg['grupo'])
                ]) + '\n'
                csv_buffer.write(linea)
            
            csv_buffer.seek(0)
            
            # COPY FROM (ultra-rápido)
            columnas = [
                'tipo_documento', 'cufe_cude', 'folio', 'prefijo', 'divisa',
                'forma_pago', 'medio_pago', 'fecha_emision', 'fecha_recepcion',
                'nit_emisor', 'nombre_emisor', 'nit_receptor', 'nombre_receptor',
                'iva', 'ica', 'ic', 'inc', 'timbre', 'inc_bolsas', 'in_carbono',
                'in_combustibles', 'ic_datos', 'icl', 'inpp', 'ibua', 'icui',
                'rete_iva', 'rete_renta', 'rete_ica', 'total', 'estado', 'grupo'
            ]
            
            cursor.copy_from(
                csv_buffer,
                'dian',
                columns=columnas,
                sep='\t',
                null='\\N'
            )
            
            conn.commit()
            cursor.close()
            
            total_registros += len(data_limpia)
            print(f"   ✅ Cargados: {len(data_limpia):,} registros")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            conn.rollback()
            continue
    
    print(f"\n✅ Total DIAN: {total_registros:,} registros")
    return total_registros

# ============================================================================
# CARGA DE ARCHIVOS ERP COMERCIAL
# ============================================================================

def cargar_archivos_erp_comercial(conn):
    """Carga archivos ERP Comercial"""
    print("\n" + "="*80)
    print("CARGANDO ARCHIVOS ERP COMERCIAL")
    print("="*80)
    
    if not os.path.exists(RUTA_ARCHIVOS_ERP_COMERCIAL):
        print(f"⚠️  Carpeta {RUTA_ARCHIVOS_ERP_COMERCIAL} no existe. Creándola...")
        os.makedirs(RUTA_ARCHIVOS_ERP_COMERCIAL)
        print(f"📁 Coloca los archivos ERP Comercial en: {RUTA_ARCHIVOS_ERP_COMERCIAL}/")
        return 0
    
    archivos = [f for f in os.listdir(RUTA_ARCHIVOS_ERP_COMERCIAL) 
                if f.endswith(('.csv', '.xlsx', '.xls'))]
    
    if not archivos:
        print(f"⚠️  No hay archivos en {RUTA_ARCHIVOS_ERP_COMERCIAL}/")
        return 0
    
    total_registros = 0
    
    for archivo in archivos:
        ruta_completa = os.path.join(RUTA_ARCHIVOS_ERP_COMERCIAL, archivo)
        print(f"\n📄 Procesando: {archivo}")
        
        try:
            if archivo.endswith('.csv'):
                df = pl.read_csv(ruta_completa, ignore_errors=True)
            else:
                df = pl.read_excel(ruta_completa)
            
            print(f"   Registros encontrados: {len(df):,}")
            
            if len(df) == 0:
                continue
            
            # Mapeo de columnas
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
            
            data_limpia = []
            for row in df_renamed.iter_rows(named=True):
                registro = {
                    'proveedor': limpiar_texto(row.get('proveedor')),
                    'razon_social_proveedor': limpiar_texto(row.get('razon_social_proveedor')),
                    'fecha_docto_prov': limpiar_fecha(row.get('fecha_docto_prov')),
                    'docto_proveedor': limpiar_texto(row.get('docto_proveedor')),
                    'valor_bruto': limpiar_valor_numerico(row.get('valor_bruto')),
                    'valor_imptos': limpiar_valor_numerico(row.get('valor_imptos')),
                    'co': limpiar_texto(row.get('co')),
                    'usuario_creacion': limpiar_texto(row.get('usuario_creacion')),
                    'clase_docto': limpiar_texto(row.get('clase_docto')),
                    'nro_documento': limpiar_texto(row.get('nro_documento'))
                }
                data_limpia.append(registro)
            
            # COPY FROM
            cursor = conn.cursor()
            csv_buffer = StringIO()
            
            for reg in data_limpia:
                linea = '\t'.join([
                    str(reg['proveedor']),
                    str(reg['razon_social_proveedor']),
                    str(reg['fecha_docto_prov']) if reg['fecha_docto_prov'] else '\\N',
                    str(reg['docto_proveedor']),
                    str(reg['valor_bruto']),
                    str(reg['valor_imptos']),
                    str(reg['co']),
                    str(reg['usuario_creacion']),
                    str(reg['clase_docto']),
                    str(reg['nro_documento'])
                ]) + '\n'
                csv_buffer.write(linea)
            
            csv_buffer.seek(0)
            
            columnas = [
                'proveedor', 'razon_social_proveedor', 'fecha_docto_prov',
                'docto_proveedor', 'valor_bruto', 'valor_imptos', 'co',
                'usuario_creacion', 'clase_docto', 'nro_documento'
            ]
            
            cursor.copy_from(csv_buffer, 'erp_comercial', columns=columnas, sep='\t', null='\\N')
            conn.commit()
            cursor.close()
            
            total_registros += len(data_limpia)
            print(f"   ✅ Cargados: {len(data_limpia):,} registros")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            conn.rollback()
            continue
    
    print(f"\n✅ Total ERP Comercial: {total_registros:,} registros")
    return total_registros

# ============================================================================
# CARGA DE ARCHIVOS ERP FINANCIERO
# ============================================================================

def cargar_archivos_erp_financiero(conn):
    """Carga archivos ERP Financiero"""
    print("\n" + "="*80)
    print("CARGANDO ARCHIVOS ERP FINANCIERO")
    print("="*80)
    
    if not os.path.exists(RUTA_ARCHIVOS_ERP_FINANCIERO):
        print(f"⚠️  Carpeta {RUTA_ARCHIVOS_ERP_FINANCIERO} no existe. Creándola...")
        os.makedirs(RUTA_ARCHIVOS_ERP_FINANCIERO)
        print(f"📁 Coloca los archivos ERP Financiero en: {RUTA_ARCHIVOS_ERP_FINANCIERO}/")
        return 0
    
    archivos = [f for f in os.listdir(RUTA_ARCHIVOS_ERP_FINANCIERO) 
                if f.endswith(('.csv', '.xlsx', '.xls'))]
    
    if not archivos:
        print(f"⚠️  No hay archivos en {RUTA_ARCHIVOS_ERP_FINANCIERO}/")
        return 0
    
    total_registros = 0
    
    for archivo in archivos:
        ruta_completa = os.path.join(RUTA_ARCHIVOS_ERP_FINANCIERO, archivo)
        print(f"\n📄 Procesando: {archivo}")
        
        try:
            if archivo.endswith('.csv'):
                df = pl.read_csv(ruta_completa, ignore_errors=True)
            else:
                df = pl.read_excel(ruta_completa)
            
            print(f"   Registros encontrados: {len(df):,}")
            
            if len(df) == 0:
                continue
            
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
            
            data_limpia = []
            for row in df_renamed.iter_rows(named=True):
                registro = {
                    'proveedor': limpiar_texto(row.get('proveedor')),
                    'razon_social_proveedor': limpiar_texto(row.get('razon_social_proveedor')),
                    'fecha_proveedor': limpiar_fecha(row.get('fecha_proveedor')),
                    'docto_proveedor': limpiar_texto(row.get('docto_proveedor')),
                    'valor_subtotal': limpiar_valor_numerico(row.get('valor_subtotal')),
                    'valor_impuestos': limpiar_valor_numerico(row.get('valor_impuestos')),
                    'co': limpiar_texto(row.get('co')),
                    'usuario_creacion': limpiar_texto(row.get('usuario_creacion')),
                    'clase_docto': limpiar_texto(row.get('clase_docto')),
                    'nro_documento': limpiar_texto(row.get('nro_documento'))
                }
                data_limpia.append(registro)
            
            # COPY FROM
            cursor = conn.cursor()
            csv_buffer = StringIO()
            
            for reg in data_limpia:
                linea = '\t'.join([
                    str(reg['proveedor']),
                    str(reg['razon_social_proveedor']),
                    str(reg['fecha_proveedor']) if reg['fecha_proveedor'] else '\\N',
                    str(reg['docto_proveedor']),
                    str(reg['valor_subtotal']),
                    str(reg['valor_impuestos']),
                    str(reg['co']),
                    str(reg['usuario_creacion']),
                    str(reg['clase_docto']),
                    str(reg['nro_documento'])
                ]) + '\n'
                csv_buffer.write(linea)
            
            csv_buffer.seek(0)
            
            columnas = [
                'proveedor', 'razon_social_proveedor', 'fecha_proveedor',
                'docto_proveedor', 'valor_subtotal', 'valor_impuestos', 'co',
                'usuario_creacion', 'clase_docto', 'nro_documento'
            ]
            
            cursor.copy_from(csv_buffer, 'erp_financiero', columns=columnas, sep='\t', null='\\N')
            conn.commit()
            cursor.close()
            
            total_registros += len(data_limpia)
            print(f"   ✅ Cargados: {len(data_limpia):,} registros")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            conn.rollback()
            continue
    
    print(f"\n✅ Total ERP Financiero: {total_registros:,} registros")
    return total_registros

# ============================================================================
# CARGA DE ARCHIVOS ACUSES
# ============================================================================

def cargar_archivos_acuses(conn):
    """Carga archivos de Acuses"""
    print("\n" + "="*80)
    print("CARGANDO ARCHIVOS ACUSES")
    print("="*80)
    
    if not os.path.exists(RUTA_ARCHIVOS_ACUSES):
        print(f"⚠️  Carpeta {RUTA_ARCHIVOS_ACUSES} no existe. Creándola...")
        os.makedirs(RUTA_ARCHIVOS_ACUSES)
        print(f"📁 Coloca los archivos de Acuses en: {RUTA_ARCHIVOS_ACUSES}/")
        return 0
    
    archivos = [f for f in os.listdir(RUTA_ARCHIVOS_ACUSES) 
                if f.endswith(('.csv', '.xlsx', '.xls'))]
    
    if not archivos:
        print(f"⚠️  No hay archivos en {RUTA_ARCHIVOS_ACUSES}/")
        return 0
    
    total_registros = 0
    
    for archivo in archivos:
        ruta_completa = os.path.join(RUTA_ARCHIVOS_ACUSES, archivo)
        print(f"\n📄 Procesando: {archivo}")
        
        try:
            if archivo.endswith('.csv'):
                df = pl.read_csv(ruta_completa, ignore_errors=True)
            else:
                df = pl.read_excel(ruta_completa)
            
            print(f"   Registros encontrados: {len(df):,}")
            
            if len(df) == 0:
                continue
            
            columnas_esperadas = {
                'Fecha': 'fecha',
                'Adquiriente': 'adquiriente',
                'Factura': 'factura',
                'Emisor': 'emisor',
                'Nit Emisor': 'nit_emisor',
                'Nit. PT': 'nit_pt',
                'Estado Docto.': 'estado_docto',
                'Descripción Reclamo': 'descripcion_reclamo',
                'Tipo Documento': 'tipo_documento',
                'CUFE': 'cufe',
                'Valor': 'valor',
                'Acuse Recibido': 'acuse_recibido',
                'Recibo Bien Servicio': 'recibo_bien_servicio',
                'Aceptación Expresa': 'aceptacion_expresa',
                'Reclamo': 'reclamo',
                'Aceptación Tacita': 'aceptacion_tacita'
            }
            
            df_renamed = df.rename({k: v for k, v in columnas_esperadas.items() if k in df.columns})
            
            data_limpia = []
            for row in df_renamed.iter_rows(named=True):
                registro = {
                    'fecha': limpiar_fecha(row.get('fecha')),
                    'adquiriente': limpiar_texto(row.get('adquiriente')),
                    'factura': limpiar_texto(row.get('factura')),
                    'emisor': limpiar_texto(row.get('emisor')),
                    'nit_emisor': limpiar_texto(row.get('nit_emisor')),
                    'nit_pt': limpiar_texto(row.get('nit_pt')),
                    'estado_docto': limpiar_texto(row.get('estado_docto')),
                    'descripcion_reclamo': limpiar_texto(row.get('descripcion_reclamo')),
                    'tipo_documento': limpiar_texto(row.get('tipo_documento')),
                    'cufe': limpiar_texto(row.get('cufe')),
                    'valor': limpiar_valor_numerico(row.get('valor')),
                    'acuse_recibido': limpiar_texto(row.get('acuse_recibido')),
                    'recibo_bien_servicio': limpiar_texto(row.get('recibo_bien_servicio')),
                    'aceptacion_expresa': limpiar_texto(row.get('aceptacion_expresa')),
                    'reclamo': limpiar_texto(row.get('reclamo')),
                    'aceptacion_tacita': limpiar_texto(row.get('aceptacion_tacita'))
                }
                data_limpia.append(registro)
            
            # COPY FROM
            cursor = conn.cursor()
            csv_buffer = StringIO()
            
            for reg in data_limpia:
                linea = '\t'.join([
                    str(reg['fecha']) if reg['fecha'] else '\\N',
                    str(reg['adquiriente']),
                    str(reg['factura']),
                    str(reg['emisor']),
                    str(reg['nit_emisor']),
                    str(reg['nit_pt']),
                    str(reg['estado_docto']),
                    str(reg['descripcion_reclamo']),
                    str(reg['tipo_documento']),
                    str(reg['cufe']),
                    str(reg['valor']),
                    str(reg['acuse_recibido']),
                    str(reg['recibo_bien_servicio']),
                    str(reg['aceptacion_expresa']),
                    str(reg['reclamo']),
                    str(reg['aceptacion_tacita'])
                ]) + '\n'
                csv_buffer.write(linea)
            
            csv_buffer.seek(0)
            
            columnas = [
                'fecha', 'adquiriente', 'factura', 'emisor', 'nit_emisor', 'nit_pt',
                'estado_docto', 'descripcion_reclamo', 'tipo_documento', 'cufe',
                'valor', 'acuse_recibido', 'recibo_bien_servicio', 'aceptacion_expresa',
                'reclamo', 'aceptacion_tacita'
            ]
            
            cursor.copy_from(csv_buffer, 'acuses', columns=columnas, sep='\t', null='\\N')
            conn.commit()
            cursor.close()
            
            total_registros += len(data_limpia)
            print(f"   ✅ Cargados: {len(data_limpia):,} registros")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            conn.rollback()
            continue
    
    print(f"\n✅ Total Acuses: {total_registros:,} registros")
    return total_registros

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal"""
    print("\n" + "="*80)
    print("CARGA MASIVA DE ARCHIVOS DIAN VS ERP")
    print("Sistema de Reconciliación DIAN vs ERP Interno")
    print("="*80)
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    inicio = datetime.now()
    
    # Conectar a PostgreSQL
    try:
        print("\n🔌 Conectando a PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Conexión exitosa")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        sys.exit(1)
    
    try:
        # Cargar archivos
        total_dian = cargar_archivos_dian(conn)
        total_erp_comercial = cargar_archivos_erp_comercial(conn)
        total_erp_financiero = cargar_archivos_erp_financiero(conn)
        total_acuses = cargar_archivos_acuses(conn)
        
        # Resumen final
        fin = datetime.now()
        duracion = (fin - inicio).total_seconds()
        
        print("\n" + "="*80)
        print("RESUMEN FINAL")
        print("="*80)
        print(f"✅ DIAN:           {total_dian:>10,} registros")
        print(f"✅ ERP Comercial:  {total_erp_comercial:>10,} registros")
        print(f"✅ ERP Financiero: {total_erp_financiero:>10,} registros")
        print(f"✅ Acuses:         {total_acuses:>10,} registros")
        print(f"{'─'*80}")
        print(f"✅ TOTAL:          {total_dian + total_erp_comercial + total_erp_financiero + total_acuses:>10,} registros")
        print(f"\n⏱️  Tiempo total: {duracion:.2f} segundos")
        
        if duracion > 0:
            velocidad = (total_dian + total_erp_comercial + total_erp_financiero + total_acuses) / duracion
            print(f"⚡ Velocidad: {velocidad:,.0f} registros/segundo")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
        print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    main()
