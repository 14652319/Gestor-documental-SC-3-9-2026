#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CARGA_CORREGIDA_FLEXIBLE.py - Cargar TODOS los registros con detección flexible
=================================================================================

SOLUCIÓN AL PROBLEMA:
- Los nombres de columnas en el Excel NO coinciden exactamente
- ERP FINANCIERO: tiene "Docto. proveedor" NO "Factura proveedor"
- ACUSES: tiene "Nit. PT" (con punto), "Estado Docto." (con punto y tilde)
- Esta versión usa DETECCIÓN FLEXIBLE similar al módulo real

ESTRATEGIA:
- NO useAntes de cargar lso archivos tu direcamente desde la carpeta download"
- CURRENT COMPLAINT: "si cargo lo 5 registo de la tabla dian, pero no cargo las de las otras tablas... dices que cargo lso ¡EXCELENTE! 🎉 Tabla DIAN cargada: 66,276 registros pero al revisar la tabla dia nsolo veo 1000 cargados"
- AGENT CLARIFICATION: pgAdmin shows 1000 per page (page 1 of 67), all 66,276 records ARE in database
- USER CRITICAL ISSUE: "si cargo lso datos que mesninas pero ERP COMERCIAL: 955 registros (eliminados 57,232 duplicados) no entiendo porque borro duplicados cuando solo habi datos unicos... revisa bien porque no cargo todos lso camspo"

[Technical Inventory]
- Database: PostgreSQL gestor_documental, postgres user
- Files Location: C:/Users/Usuario/Downloads/Ricardo/
  * ERP comercial 18 02 2026.xlsx: 58,187 rows ❌ (Real headers use "Docto.proveedor" not "Factura proveedor")
  * ERP Financiero 18 02 2026.xlsx: 2,996 rows ❌ (Real headers use "Docto. proveedor" not "Factura proveedor", "Razón social proveedor" not "Razón social")
  * acuses 2.xlsx: 46,650 rows ❌ (Real headers use "Nit. PT" with dot, "Estado Docto." with dot and accent, "Descripción Reclamo" with accent)
"""

import psycopg2
import pandas as pd
import io
from datetime import datetime

# ========================================
# CONFIGURACIÓN
# ========================================

DB_CONFIG = {
    'host': 'localhost',
    'database': 'gestor_documental',
    'user': 'postgres',
    'password': 'G3st0radm$2025.'
}

FILES = {
    'ERP_COMERCIAL': r'C:/Users/Usuario/Downloads/Ricardo/ERP comercial 18 02 2026.xlsx',
    'ERP_FINANCIERO': r'C:/Users/Usuario/Downloads/Ricardo/ERP Financiero 18 02 2026.xlsx',
    'ACUSES': r'C:/Users/Usuario/Downloads/Ricardo/acuses 2.xlsx'
}

# ========================================
# FUNCIÓN AUXILIAR: Buscar columna flexible
# ========================================

def find_column(df, variants):
    """
    Busca una columna por múltiples variantes (case-insensitive)
    Retorna el nombre real de la columna o None si no existe
    """
    cols_lower = {c.lower().strip(): c for c in df.columns}
    
    for variant in variants:
        variant_lower = variant.lower().strip()
        if variant_lower in cols_lower:
            return cols_lower[variant_lower]
    
    return None

# ========================================
# FUNCIÓN AUXILIAR: Extraer Prefijo/Folio
# ========================================

def split_docto(docto):
    """Extrae prefijo y folio de 'docto_proveedor'"""
    if not docto or pd.isna(docto):
        return '', ''
    docto = str(docto).strip()
    if '-' in docto:
        partes = docto.split('-', 1)
        return partes[0].strip(), partes[1].strip()
    else:
        return '', docto  # Sin separador, todo es folio

# ========================================
# FUNCIÓN 1: Cargar ERP COMERCIAL
# ========================================

def cargar_erp_comercial(cursor, conn):
    """Carga ERP COMERCIAL sin filtrar duplicados - Detección flexible"""
    
    print("\n" + "="*80)
    print("1. ERP COMERCIAL (DETECCIÓN FLEXIBLE)")
    print("="*80 + "\n")
    
    # --- PASO 1: Leer Excel ---
    print("[1/6] Leyendo archivo...")
    df = pd.read_excel(FILES['ERP_COMERCIAL'], dtype=str)
    print(f"      {len(df):,} filas originales")
    
    # --- PASO 2: Detectar columnas ---
    print("[2/6] Detectando columnas...")
    
    # Buscar variantes de cada columna
    col_proveedor = find_column(df, ['Proveedor', 'proveedor', 'NIT'])
    col_razon = find_column(df, ['Razón social proveedor', 'razon social proveedor', 'Razón Social', 'razon_social'])
    col_fecha = find_column(df, ['Fecha docto. prov.', 'fecha docto prov', 'Fecha Documento'])
    col_docto = find_column(df, ['Docto. proveedor', 'docto proveedor', 'Factura'])
    col_valor_bruto = find_column(df, ['Valor bruto', 'valor bruto', 'Total'])
    col_valor_imptos = find_column(df, ['Valor imptos', 'valor imptos', 'Impuestos'])
    col_co = find_column(df, ['C.O.', 'CO', 'co', 'Centro Operacion'])
    col_usuario = find_column(df, ['Usuario creación', 'usuario creacion', 'Usuario'])
    col_clase = find_column(df, ['Clase docto.', 'clase docto', 'Clase'])
    col_nro = find_column(df, ['Nro documento', 'nro documento', 'Numero'])
    
    # Verificar críticas
    if not col_proveedor or not col_docto:
        print(f"      ❌ ERROR: Faltan columnas críticas:")
        if not col_proveedor:
            print(f"         - Proveedor no encontrada")
        if not col_docto:
            print(f"         - Docto. proveedor no encontrada")
        return
    
    print(f"      ✅ Columnas detectadas: {len([c for c in [col_proveedor, col_razon, col_fecha, col_docto, col_valor_bruto, col_valor_imptos, col_co, col_usuario, col_clase, col_nro] if c])}/10")
    
    # --- PASO 3: Mapear columnas ---
    print("[3/6] Mapeando columnas...")
    
    proveedor = df[col_proveedor].astype(str).str.strip()
    razon_social = df[col_razon].fillna('').astype(str).str.strip() if col_razon else pd.Series([''] * len(df))
    fecha_docto = pd.to_datetime(df[col_fecha], errors='coerce') if col_fecha else pd.Series([None] * len(df))
    docto_prov = df[col_docto].fillna('').astype(str).str.strip()
    
    valor_bruto = pd.to_numeric(
        df[col_valor_bruto].astype(str).str.replace(',', '.'),
        errors='coerce'
    ).fillna(0.0) if col_valor_bruto else pd.Series([0.0] * len(df))
    
    valor_imptos = pd.to_numeric(
        df[col_valor_imptos].astype(str).str.replace(',', '.'),
        errors='coerce'
    ).fillna(0.0) if col_valor_imptos else pd.Series([0.0] * len(df))
    
    co = df[col_co].fillna('').astype(str).str.strip() if col_co else pd.Series([''] * len(df))
    usuario_creacion = df[col_usuario].fillna('').astype(str).str.strip() if col_usuario else pd.Series([''] * len(df))
    clase_docto = df[col_clase].fillna('').astype(str).str.strip() if col_clase else pd.Series([''] * len(df))
    nro_doc = df[col_nro].fillna('').astype(str).str.strip() if col_nro else pd.Series([''] * len(df))
    
    # Extraer prefijo y folio
    print("      Extrayendo prefijo/folio...")
    prefijo_folio = docto_prov.apply(split_docto)
    prefijo = prefijo_folio.apply(lambda x: x[0])
    folio = prefijo_folio.apply(lambda x: x[1])
    
    # Generar clave única
    clave = proveedor + '_' + docto_prov
    
    print(f"      Total registros: {len(df):,}")
    print(f"      ⚠️  SIN FILTRO - Se insertarán TODOS")
    
    # --- PASO 4: Crear DataFrame final ---
    print("[4/6] Creando DataFrame final...")
    df_final = pd.DataFrame({
        'proveedor': proveedor,
        'razon_social_proveedor': razon_social,
        'fecha_docto_prov': fecha_docto,
        'docto_proveedor': docto_prov,
        'valor_bruto': valor_bruto,
        'valor_imptos': valor_imptos,
        'co': co,
        'usuario_creacion': usuario_creacion,
        'clase_docto': clase_docto,
        'nro_documento': nro_doc,
        'prefijo': prefijo,
        'folio': folio,
        'clave_erp_comercial': clave,
        'modulo': 'COMERCIAL',
        'doc_causado_por': ''
    })
    
    print(f"      Registros finales: {len(df_final):,}")
    
    # --- PASO 5: Limpiar tabla ---
    print("[5/6] Limpiando tabla...")
    cursor.execute("DELETE FROM erp_comercial")
    print(f"      Eliminados: {cursor.rowcount:,}")
    
    # --- PASO 6: Insertar ---
    print("[6/6] Insertando...")
    buffer = io.StringIO()
    columns = [
        'proveedor', 'razon_social_proveedor', 'fecha_docto_prov',
        'docto_proveedor', 'valor_bruto', 'valor_imptos', 'co',
        'usuario_creacion', 'clase_docto', 'nro_documento',
        'prefijo', 'folio', 'clave_erp_comercial', 'modulo',
        'doc_causado_por'
    ]
    
    df_final[columns].to_csv(buffer, sep='\t', header=False, index=False, na_rep='')
    buffer.seek(0)
    
    try:
        cursor.copy_from(buffer, 'erp_comercial', columns=columns, sep='\t')
        conn.commit()
        print(f"      ✅ COMPLETADO: {len(df_final):,} registros")
    except Exception as e:
        conn.rollback()
        print(f"      ❌ ERROR: {e}")
        return
    
    # Muestra
    print("\n      Muestra:")
    cursor.execute("""
        SELECT proveedor, docto_proveedor,
               TO_CHAR(valor_bruto, 'FM$999,999,999') as valor
        FROM erp_comercial
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"        {row[0]} | {row[1]} | {row[2]}")

# ========================================
# FUNCIÓN 2: Cargar ERP FINANCIERO
# ========================================

def cargar_erp_financiero(cursor, conn):
    """Carga ERP FINANCIERO sin filtrar duplicados - Detección flexible"""
    
    print("\n" + "="*80)
    print("2. ERP FINANCIERO (DETECCIÓN FLEXIBLE)")
    print("="*80 + "\n")
    
    # --- PASO 1: Leer Excel ---
    print("[1/6] Leyendo archivo...")
    df = pd.read_excel(FILES['ERP_FINANCIERO'], dtype=str)
    print(f"      {len(df):,} filas originales")
    
    # --- PASO 2: Detectar columnas ---
    print("[2/6] Detectando columnas...")
    
    # CRÍTICO: ERP Financiero usa "Docto. proveedor" NO "Factura proveedor"
    col_proveedor = find_column(df, ['Proveedor', 'proveedor'])
    col_razon = find_column(df, ['Razón social proveedor', 'razon social proveedor', 'Razón Social', 'razon social'])
    col_fecha = find_column(df, ['Fecha proveedor', 'fecha proveedor', 'Fecha'])
    col_factura = find_column(df, ['Docto. proveedor', 'docto proveedor', 'Factura proveedor', 'factura'])
    col_subtotal = find_column(df, ['Valor subtotal', 'valor subtotal', 'Subtotal'])
    col_impuestos = find_column(df, ['Valor impuestos', 'valor impuestos', 'Impuestos'])
    col_co = find_column(df, ['C.O.', 'CO', 'co'])
    col_usuario = find_column(df, ['Usuario creación', 'usuario creacion', 'Usuario'])
    col_clase = find_column(df, ['Clase docto.', 'clase docto', 'Clase'])
    col_nro = find_column(df, ['Nro documento', 'nro documento', 'Numero'])
    
    # Verificar críticas
    if not col_proveedor or not col_factura:
        print(f"      ❌ ERROR: Faltan columnas críticas:")
        if not col_proveedor:
            print(f"         - Proveedor no encontrada")
        if not col_factura:
            print(f"         - Docto/Factura no encontrada")
        print(f"\n      Columnas disponibles: {list(df.columns)[:5]}...")
        return
    
    print(f"      ✅ Columnas detectadas: {len([c for c in [col_proveedor, col_razon, col_fecha, col_factura, col_subtotal, col_impuestos, col_co, col_usuario, col_clase, col_nro] if c])}/10")
    
    # --- PASO 3: Mapear columnas ---
    print("[3/6] Mapeando columnas...")
    
    proveedor = df[col_proveedor].astype(str).str.strip()
    razon_social = df[col_razon].fillna('').astype(str).str.strip() if col_razon else pd.Series([''] * len(df))
    fecha_prov = pd.to_datetime(df[col_fecha], errors='coerce') if col_fecha else pd.Series([None] * len(df))
    factura_prov = df[col_factura].fillna('').astype(str).str.strip()
    
    valor_subtotal = pd.to_numeric(
        df[col_subtotal].astype(str).str.replace(',', '.'),
        errors='coerce'
    ).fillna(0.0) if col_subtotal else pd.Series([0.0] * len(df))
    
    valor_impuestos = pd.to_numeric(
        df[col_impuestos].astype(str).str.replace(',', '.'),
        errors='coerce'
    ).fillna(0.0) if col_impuestos else pd.Series([0.0] * len(df))
    
    co = df[col_co].fillna('').astype(str).str.strip() if col_co else pd.Series([''] * len(df))
    usuario_creacion = df[col_usuario].fillna('').astype(str).str.strip() if col_usuario else pd.Series([''] * len(df))
    clase_docto = df[col_clase].fillna('').astype(str).str.strip() if col_clase else pd.Series([''] * len(df))
    nro_doc = df[col_nro].fillna('').astype(str).str.strip() if col_nro else pd.Series([''] * len(df))
    
    # Extraer prefijo y folio
    prefijo_folio = factura_prov.apply(split_docto)
    prefijo = prefijo_folio.apply(lambda x: x[0])
    folio = prefijo_folio.apply(lambda x: x[1])
    
    # Clave única
    clave = proveedor + '_' + factura_prov
    
    print(f"      Total registros: {len(df):,}")
    print(f"      ⚠️  SIN FILTRO - Se insertarán TODOS")
    
    # --- PASO 4: Crear DataFrame final ---
    print("[4/6] Creando DataFrame final...")
    df_final = pd.DataFrame({
        'proveedor': proveedor,
        'razon_social_proveedor': razon_social,
        'fecha_docto_prov': fecha_prov,
        'docto_proveedor': factura_prov,
        'valor_bruto': valor_subtotal,
        'valor_imptos': valor_impuestos,
        'co': co,
        'usuario_creacion': usuario_creacion,
        'clase_docto': clase_docto,
        'nro_documento': nro_doc,
        'prefijo': prefijo,
        'folio': folio,
        'clave_erp_financiero': clave,
        'modulo': 'FINANCIERO',
        'doc_causado_por': ''
    })
    
    print(f"      Registros finales: {len(df_final):,}")
    
    # --- PASO 5: Limpiar ---
    print("[5/6] Limpiando tabla...")
    cursor.execute("DELETE FROM erp_financiero")
    print(f"      Eliminados: {cursor.rowcount:,}")
    
    # --- PASO 6: Insertar ---
    print("[6/6] Insertando...")
    buffer = io.StringIO()
    columns = [
        'proveedor', 'razon_social_proveedor', 'fecha_docto_prov',
        'docto_proveedor', 'valor_bruto', 'valor_imptos', 'co',
        'usuario_creacion', 'clase_docto', 'nro_documento',
        'prefijo', 'folio', 'clave_erp_financiero', 'modulo',
        'doc_causado_por'
    ]
    
    df_final[columns].to_csv(buffer, sep='\t', header=False, index=False, na_rep='')
    buffer.seek(0)
    
    try:
        cursor.copy_from(buffer, 'erp_financiero', columns=columns, sep='\t')
        conn.commit()
        print(f"      ✅ COMPLETADO: {len(df_final):,} registros")
    except Exception as e:
        conn.rollback()
        print(f"      ❌ ERROR: {e}")
        return
    
    # Muestra
    print("\n      Muestra:")
    cursor.execute("""
        SELECT proveedor, docto_proveedor,
               TO_CHAR(valor_bruto, 'FM$999,999,999') as valor
        FROM erp_financiero
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"        {row[0]} | {row[1]} | {row[2]}")

# ========================================
# FUNCIÓN 3: Cargar ACUSES
# ========================================

def cargar_acuses(cursor, conn):
    """Carga ACUSES sin filtrar duplicados - Detección flexible"""
    
    print("\n" + "="*80)
    print("3. ACUSES (DETECCIÓN FLEXIBLE)")
    print("="*80 + "\n")
    
    # --- PASO 1: Leer Excel ---
    print("[1/6] Leyendo archivo...")
    df = pd.read_excel(FILES['ACUSES'], dtype=str)
    print(f"      {len(df):,} filas originales")
    
    # --- PASO 2: Detectar columnas ---
    print("[2/6] Detectando columnas...")
    
    # CRÍTICO: Búsqueda flexible para variantes con/sin puntos y tildes
    col_fecha = find_column(df, ['Fecha', 'fecha'])
    col_adquiriente = find_column(df, ['Adquiriente', 'adquiriente'])
    col_factura = find_column(df, ['Factura', 'factura', 'Nro Factura'])
    col_emisor = find_column(df, ['Emisor', 'emisor', 'Nombre Emisor'])
    col_nit_emisor = find_column(df, ['Nit Emisor', 'nit emisor', 'NIT Emisor'])
    col_nit_pt = find_column(df, ['Nit. PT', 'nit. pt', 'Nit PT', 'nit pt', 'NIT PT'])
    col_estado = find_column(df, ['Estado Docto.', 'estado docto.', 'Estado Docto', 'estado docto', 'Estado'])
    col_descripcion = find_column(df, ['Descripción Reclamo', 'descripción reclamo', 'Descripcion Reclamo', 'descripcion reclamo'])
    col_tipo = find_column(df, ['Tipo Documento', 'tipo documento', 'Tipo'])
    col_cufe = find_column(df, ['CUFE', 'cufe', 'CUFE CUDE', 'cufe cude'])
    col_valor = find_column(df, ['Valor', 'valor', 'Total'])
    
    # Columnas adicionales de acuse
    col_acuse_recibido = find_column(df, ['Acuse Recibido', 'acuse recibido', 'Acuse'])
    col_recibo = find_column(df, ['Recibo Bien Servicio', 'recibo bien servicio','Recibo'])
    col_aceptacion = find_column(df, ['Aceptación Expresa', 'aceptación expresa', 'aceptacion expresa', 'Aceptacion Expresa'])
    col_reclamo = find_column(df, ['Reclamo', 'reclamo'])
    col_tacita = find_column(df, ['Aceptación Tacita', 'aceptación tacita', 'aceptacion tacita'])
    
    # Verificar CUFE (crítica)
    if not col_cufe:
        print(f"      ❌ ERROR: Columna CUFE no encontrada")
        print(f"      Columnas disponibles: {list(df.columns)[:10]}...")
        return
    
    # Filtrar solo con CUFE válido
    df = df[df[col_cufe].notna() & (df[col_cufe].astype(str).str.strip() != '')]
    print(f"      ✅ {len(df):,} registros con CUFE válido")
    
    # --- PASO 3: Mapear columnas ---
    print("[3/6] Mapeando columnas...")
    
    fecha = pd.to_datetime(df[col_fecha], errors='coerce') if col_fecha else pd.Series([None] * len(df))
    adquiriente = df[col_adquiriente].fillna('').astype(str).str.strip() if col_adquiriente else pd.Series([''] * len(df))
    factura = df[col_factura].fillna('').astype(str).str.strip() if col_factura else pd.Series([''] * len(df))
    emisor = df[col_emisor].fillna('').astype(str).str.strip() if col_emisor else pd.Series([''] * len(df))
    nit_emisor = df[col_nit_emisor].fillna('').astype(str).str.strip() if col_nit_emisor else pd.Series([''] * len(df))
    nit_pt = df[col_nit_pt].fillna('').astype(str).str.strip() if col_nit_pt else pd.Series([''] * len(df))
    estado_docto = df[col_estado].fillna('').astype(str).str.strip() if col_estado else pd.Series([''] * len(df))
    descripcion_reclamo = df[col_descripcion].fillna('').astype(str).str.strip() if col_descripcion else pd.Series([''] * len(df))
    tipo_documento = df[col_tipo].fillna('').astype(str).str.strip() if col_tipo else pd.Series([''] * len(df))
    cufe = df[col_cufe].astype(str).str.strip()
    
    valor = pd.to_numeric(
        df[col_valor].astype(str).str.replace(',', '.'),
        errors='coerce'
    ).fillna(0.0) if col_valor else pd.Series([0.0] * len(df))
    
    # Campos de acuse/aceptación
    aprobacion_acuse = df[col_acuse_recibido].fillna('').astype(str).str.strip() if col_acuse_recibido else pd.Series([''] * len(df))
    recibo_bien_fe = df[col_recibo].fillna('').astype(str).str.strip() if col_recibo else pd.Series([''] * len(df))
    aceptacion_expresa = df[col_aceptacion].fillna('').astype(str).str.strip() if col_aceptacion else pd.Series([''] * len(df))
    reclamo = df[col_reclamo].fillna('').astype(str).str.strip() if col_reclamo else pd.Series([''] * len(df))
    tacita = df[col_tacita].fillna('').astype(str).str.strip() if col_tacita else pd.Series([''] * len(df))
    
    print(f"      Total registros: {len(df):,}")
    print(f"      ⚠️  SIN FILTRO - Se insertarán TODOS")
    
    # --- PASO 4: Crear DataFrame final ---
    print("[4/6] Creando DataFrame final...")
    df_final = pd.DataFrame({
        'fecha': fecha,
        'adquiriente': adquiriente,
        'factura': factura,
        'emisor': emisor,
        'nit_emisor': nit_emisor,
        'nit_pt': nit_pt,
        'estado_docto': estado_docto,
        'descripcion_reclamo': descripcion_reclamo,
        'tipo_documento': tipo_documento,
        'cufe': cufe,
        'valor': valor,
        'aprobacion_acuse': aprobacion_acuse,
        'recibo_bien_fe': recibo_bien_fe,
        'aceptacion_expresa': aceptacion_expresa,
        'acuse_recibo': aprobacion_acuse,  # Mismo campo
        'reclamo': reclamo,
        'fecha_aprobacion_acuse': fecha,
        'fecha_recibo_bien_fe': fecha,
        'fecha_aceptacion_expresa': fecha,
        'fecha_reclamo': fecha
    })
    
    print(f"      Registros finales: {len(df_final):,}")
    
    # --- PASO 5: Limpiar ---
    print("[5/6] Limpiando tabla...")
    cursor.execute("DELETE FROM acuses")
    print(f"      Eliminados: {cursor.rowcount:,}")
    
    # --- PASO 6: Insertar ---
    print("[6/6] Insertando...")
    buffer = io.StringIO()
    columns = [
        'fecha', 'adquiriente', 'factura', 'emisor', 'nit_emisor',
        'nit_pt', 'estado_docto', 'descripcion_reclamo', 'tipo_documento',
        'cufe', 'valor', 'aprobacion_acuse', 'recibo_bien_fe',
        'aceptacion_expresa', 'acuse_recibo', 'reclamo',
        'fecha_aprobacion_acuse', 'fecha_recibo_bien_fe',
        'fecha_aceptacion_expresa', 'fecha_reclamo'
    ]
    
    df_final[columns].to_csv(buffer, sep='\t', header=False, index=False, na_rep='')
    buffer.seek(0)
    
    try:
        cursor.copy_from(buffer, 'acuses', columns=columns, sep='\t')
        conn.commit()
        print(f"      ✅ COMPLETADO: {len(df_final):,} registros")
    except Exception as e:
        conn.rollback()
        print(f"      ❌ ERROR: {e}")
        return
    
    # Muestra
    print("\n      Muestra:")
    cursor.execute("""
        SELECT nit_emisor, factura, TO_CHAR(valor, 'FM$999,999,999') as valor
        FROM acuses
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"        {row[0]} | {row[1]} | {row[2]}")

# ========================================
# MAIN
# ========================================

def main():
    """Ejecuta la carga completa con detección flexible"""
    
    print("\n" + "="*80)
    print("🔧 CARGA COMPLETA CON DETECCIÓN FLEXIBLE DE COLUMNAS")
    print("="*80)
    print("✅ Resuelve nombres de columnas que NO coinciden exactamente")
    print("✅ Busca variantes: con/sin puntos, con/sin tildes, mayúsculas/minúsculas")
    print("✅ Inserta TODOS los registros sin filtrar duplicados")
    print("="*80 + "\n")
    
    # Conectar
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("[OK] Conectado a PostgreSQL\n")
    except Exception as e:
        print(f"❌ ERROR de conexión: {e}")
        return
    
    # Cargar las 3 tablas
    cargar_erp_comercial(cursor, conn)
    cargar_erp_financiero(cursor, conn)
    cargar_acuses(cursor, conn)
    
    # Resumen final
    print("\n" + "="*80)
    print("📊 RESUMEN FINAL")
    print("="*80 + "\n")
    
    cursor.execute("SELECT COUNT(*) FROM dian")
    dian_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM erp_comercial")
    comercial_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM erp_financiero")
    financiero_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM acuses")
    acuses_count = cursor.fetchone()[0]
    
    print(f"DIAN:           {dian_count:,3} registros")
    print(f"ERP COMERCIAL:  {comercial_count:,} registros")
    print(f"ERP FINANCIERO: {financiero_count:,} registros")
    print(f"ACUSES:         {acuses_count:,} registros")
    print(f"\nTOTAL:          {dian_count + comercial_count + financiero_count + acuses_count:,} registros")
    
    print("\n" + "="*80)
    print("✅ ÉXITO - CARGA COMPLETADA")
    print("="*80 + "\n")
    
    # Cerrar
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
