#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CARGA_SIN_FILTRO.py - Cargar TODOS los registros sin drop_duplicates()
=======================================================================

ESTRATEGIA:
- NO usar drop_duplicates() (está roto en pandas para este caso)
- Insertar TODOS los registros del Excel
- Dejar que PostgreSQL maneje duplicados con UNIQUE constraint
- Si hay error de duplicado, simplemente continuar

TABLAS:
1. erp_comercial: 18 columnas, UNIQUE(clave_erp_comercial)
2. erp_financiero: 18 columnas, UNIQUE(clave_erp_financiero)  
3. acuses: 19 columnas, UNIQUE(clave_acuse)
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
    """Carga ERP COMERCIAL sin filtrar duplicados"""
    
    print("\n" + "="*80)
    print("1. ERP COMERCIAL (SIN FILTRO)")
    print("="*80 + "\n")
    
    # --- PASO 1: Leer Excel ---
    print("[1/5] Leyendo archivo...")
    df = pd.read_excel(FILES['ERP_COMERCIAL'], dtype=str)
    print(f"      {len(df):,} filas originales")
    
    # --- PASO 2: Normalizar columnas ---
    print("[2/5] Normalizando columnas...")
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Verificar columnas mínimas requeridas
    required = ['proveedor', 'razón social proveedor', 'fecha docto. prov.', 
                'docto. proveedor', 'valor bruto', 'valor imptos']
    missing = [col for col in required if col not in df.columns]
    if missing:
        print(f"      ❌ ERROR: Faltan columnas: {missing}")
        return
    
    print(f"      {len(df.columns)} columnas detectadas")
    
    # --- PASO 3: Mapear columnas ---
    print("[3/5] Mapeando columnas...")
    
    # Crear Series para cada campo (vectorizado, rápido)
    proveedor = df['proveedor'].astype(str).str.strip()
    razon_social = df['razón social proveedor'].fillna('').astype(str).str.strip()
    fecha_docto = pd.to_datetime(df['fecha docto. prov.'], errors='coerce')
    docto_prov = df['docto. proveedor'].fillna('').astype(str).str.strip()
    
    # Valores numéricos
    valor_bruto = pd.to_numeric(
        df['valor bruto'].astype(str).str.replace(',', '.'), 
        errors='coerce'
    ).fillna(0.0)
    valor_imptos = pd.to_numeric(
        df['valor imptos'].astype(str).str.replace(',', '.'), 
        errors='coerce'
    ).fillna(0.0)
    
    # Campos opcionales
    co = df.get('c.o.', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    usuario_creacion = df.get('usuario creación', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    clase_docto = df.get('clase docto.', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    nro_doc = df.get('nro documento', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    
    # Extraer prefijo y folio
    print("      Extrayendo prefijo/folio...")
    prefijo_folio = docto_prov.apply(split_docto)
    prefijo = prefijo_folio.apply(lambda x: x[0])
    folio = prefijo_folio.apply(lambda x: x[1])
    
    # Generar clave única: proveedor + docto_proveedor
    print("      Generando claves únicas...")
    clave = proveedor + '_' + docto_prov
    
    print(f"      Total registros: {len(df):,}")
    print(f"      Claves generadas: {len(clave):,}")
    print(f"      ⚠️  SIN FILTRO - Se insertarán TODOS los registros")
    
    # --- PASO 4: Crear DataFrame final ---
    print("[4/5] Creando DataFrame final...")
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
    
    # --- PASO 5: Limpiar tabla e insertar ---
    print("[5/5] Limpiando tabla e insertando...")
    cursor.execute("DELETE FROM erp_comercial")
    eliminados = cursor.rowcount
    print(f"      Eliminados: {eliminados:,}")
    
    # Preparar buffer para COPY FROM
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
    
    # Insertar con COPY FROM
    try:
        cursor.copy_from(buffer, 'erp_comercial', columns=columns, sep='\t')
        conn.commit()
        print(f"      ✅ COMPLETADO: {len(df_final):,} registros insertados")
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
    """Carga ERP FINANCIERO sin filtrar duplicados"""
    
    print("\n" + "="*80)
    print("2. ERP FINANCIERO (SIN FILTRO)")
    print("="*80 + "\n")
    
    # --- PASO 1: Leer Excel ---
    print("[1/5] Leyendo archivo...")
    df = pd.read_excel(FILES['ERP_FINANCIERO'], dtype=str)
    print(f"      {len(df):,} filas originales")
    
    # --- PASO 2: Normalizar columnas ---
    print("[2/5] Normalizando columnas...")
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Verificar columnas mínimas
    required = ['proveedor', 'razón social', 'fecha proveedor',
                'factura proveedor', 'valor subtotal', 'valor impuestos']
    missing = [col for col in required if col not in df.columns]
    if missing:
        print(f"      ❌ ERROR: Faltan columnas: {missing}")
        return
    
    print(f"      {len(df.columns)} columnas detectadas")
    
    # --- PASO 3: Mapear columnas ---
    print("[3/5] Mapeando columnas...")
    
    proveedor = df['proveedor'].astype(str).str.strip()
    razon_social = df['razón social'].fillna('').astype(str).str.strip()
    fecha_prov = pd.to_datetime(df['fecha proveedor'], errors='coerce')
    factura_prov = df['factura proveedor'].fillna('').astype(str).str.strip()
    
    valor_subtotal = pd.to_numeric(
        df['valor subtotal'].astype(str).str.replace(',', '.'),
        errors='coerce'
    ).fillna(0.0)
    valor_impuestos = pd.to_numeric(
        df['valor impuestos'].astype(str).str.replace(',', '.'),
        errors='coerce'
    ).fillna(0.0)
    
    # Campos opcionales
    co = df.get('c.o.', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    usuario_creacion = df.get('usuario creación', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    clase_docto = df.get('clase docto.', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    nro_doc = df.get('nro documento', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    
    # Extraer prefijo y folio
    prefijo_folio = factura_prov.apply(split_docto)
    prefijo = prefijo_folio.apply(lambda x: x[0])
    folio = prefijo_folio.apply(lambda x: x[1])
    
    # Clave única
    clave = proveedor + '_' + factura_prov
    
    print(f"      Total registros: {len(df):,}")
    print(f"      ⚠️  SIN FILTRO - Se insertarán TODOS los registros")
    
    # --- PASO 4: Crear DataFrame final ---
    print("[4/5] Creando DataFrame final...")
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
    
    # --- PASO 5: Insertar ---
    print("[5/5] Limpiando tabla e insertando...")
    cursor.execute("DELETE FROM erp_financiero")
    print(f"      Eliminados: {cursor.rowcount:,}")
    
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
        print(f"      ✅ COMPLETADO: {len(df_final):,} registros insertados")
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
    """Carga ACUSES sin filtrar duplicados"""
    
    print("\n" + "="*80)
    print("3. ACUSES (SIN FILTRO)")
    print("="*80 + "\n")
    
    # --- PASO 1: Leer Excel ---
    print("[1/5] Leyendo archivo...")
    df = pd.read_excel(FILES['ACUSES'], dtype=str)
    print(f"      {len(df):,} filas originales")
    
    # --- PASO 2: Normalizar ---
    print("[2/5] Normalizando columnas...")
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Verificar CUFE
    if 'cufe' not in df.columns:
        print("      ❌ ERROR: Falta columna 'CUFE'")
        return
    
    # Filtrar solo registros con CUFE válido
    df = df[df['cufe'].notna() & (df['cufe'].astype(str).str.strip() != '')]
    print(f"      {len(df):,} con CUFE válido")
    
    # --- PASO 3: Mapear columnas ---
    print("[3/5] Mapeando columnas...")
    
    fecha = pd.to_datetime(df.get('fecha', pd.Series([None] * len(df))), errors='coerce')
    adquiriente = df.get('adquiriente', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    factura = df.get('factura', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    emisor = df.get('emisor', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    nit_emisor = df.get('nit emisor', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    nit_pt = df.get('nit pt', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    estado_docto = df.get('estado docto', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    descripcion_reclamo = df.get('descripcion reclamo', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    tipo_documento = df.get('tipo documento', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    cufe = df['cufe'].astype(str).str.strip()
    
    valor = pd.to_numeric(
        df.get('valor', pd.Series([0] * len(df))).astype(str).str.replace(',', '.'),
        errors='coerce'
    ).fillna(0.0)
    
    # Campos de acuse
    aprobacion_acuse = df.get('aprobacion acuse', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    recibo_bien_fe = df.get('recibo bien fe', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    aceptacion_expresa = df.get('aceptacion expresa', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    acuse_recibo = df.get('acuse recibo', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    reclamo = df.get('reclamo', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    
    # Fechas de acuse
    fecha_aprobacion = pd.to_datetime(df.get('fecha aprobacion', pd.Series([None] * len(df))), errors='coerce')
    fecha_recibo = pd.to_datetime(df.get('fecha recibo', pd.Series([None] * len(df))), errors='coerce')
    fecha_aceptacion = pd.to_datetime(df.get('fecha aceptacion', pd.Series([None] * len(df))), errors='coerce')
    fecha_reclamo = pd.to_datetime(df.get('fecha reclamo', pd.Series([None] * len(df))), errors='coerce')
    
    # Clave única = CUFE
    clave = cufe
    
    print(f"      Total registros: {len(df):,}")
    print(f"      ⚠️  SIN FILTRO - Se insertarán TODOS los registros")
    
    # --- PASO 4: Crear DataFrame final ---
    print("[4/5] Creando DataFrame final...")
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
        'acuse_recibo': acuse_recibo,
        'reclamo': reclamo,
        'fecha_aprobacion_acuse': fecha_aprobacion,
        'fecha_recibo_bien_fe': fecha_recibo,
        'fecha_aceptacion_expresa': fecha_aceptacion,
        'fecha_reclamo': fecha_reclamo
    })
    
    print(f"      Registros finales: {len(df_final):,}")
    
    # --- PASO 5: Insertar ---
    print("[5/5] Limpiando tabla e insertando...")
    cursor.execute("DELETE FROM acuses")
    print(f"      Eliminados: {cursor.rowcount:,}")
    
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
        print(f"      ✅ COMPLETADO: {len(df_final):,} registros insertados")
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
    """Ejecuta la carga completa"""
    
    print("\n" + "="*80)
    print("CARGA COMPLETA SIN FILTRO - PostgreSQL")
    print("="*80)
    print("⚠️  ESTRATEGIA: Insertar TODO, dejar que BD maneje duplicados")
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
    print("RESUMEN FINAL")
    print("="*80 + "\n")
    
    cursor.execute("SELECT COUNT(*) FROM dian")
    dian_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM erp_comercial")
    comercial_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM erp_financiero")
    financiero_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM acuses")
    acuses_count = cursor.fetchone()[0]
    
    print(f"DIAN:           {dian_count:,}")
    print(f"ERP COMERCIAL:  {comercial_count:,}")
    print(f"ERP FINANCIERO: {financiero_count:,}")
    print(f"ACUSES:         {acuses_count:,}")
    print(f"\nTOTAL:          {dian_count + comercial_count + financiero_count + acuses_count:,}")
    
    print("\n" + "="*80)
    print("[ÉXITO] CARGA COMPLETADA")
    print("="*80 + "\n")
    
    # Cerrar
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
