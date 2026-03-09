#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CARGA_POSTGRESQL_DIRECTA.py - Solución definitiva sin drop_duplicates
======================================================================

ESTRATEGIA FINAL:
- NO usar drop_duplicates() (está completamente roto)
- Insertar TODOS los registros
- PostgreSQL maneja duplicados con UNIQUE constraint
- Usar INSERT ... ON CONFLICT DO NOTHING

Resultado esperado:
- ERP COMERCIAL: 58,187 registros
- ERP FINANCIERO: 2,996 registros
- ACUSES: 46,650 registros
"""

import psycopg2
import pandas as pd
from pathlib import Path

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
# FUNCIÓN: Buscar columna flexible
# ========================================

def find_col(df, *variants):
    """Busca columna por variantes (case-insensitive)"""
    cols_lower = {c.lower().strip(): c for c in df.columns}
    for v in variants:
        if v.lower().strip() in cols_lower:
            return cols_lower[v.lower().strip()]
    return None

# ========================================
# FUNCIÓN: Extraer prefijo/folio
# ========================================

def split_docto(docto):
    """Extrae prefijo y folio"""
    if not docto or pd.isna(docto):
        return '', ''
    docto = str(docto).strip()
    if '-' in docto:
        partes = docto.split('-', 1)
        return partes[0].strip(), partes[1].strip()
    return '', docto

# ========================================
# FUNCIÓN 1: Cargar ERP COMERCIAL
# ========================================

def cargar_erp_comercial(cursor, conn):
    """Carga ERP COMERCIAL con INSERT ON CONFLICT"""
    
    print("\n" + "="*80)
    print("1. ERP COMERCIAL")
    print("="*80)
    
    try:
        print("[1/4] Leyendo Excel (puede tomar 30-60 segundos)...")
        df = pd.read_excel(FILES['ERP_COMERCIAL'], dtype=str, nrows=None)
        print(f"      ✅ {len(df):,} filas leídas")
    except Exception as e:
        print(f"      ❌ ERROR: {e}")
        return
    
    # Detectar columnas
    print("[2/4] Detectando columnas...")
    col_proveedor = find_col(df, 'Proveedor', 'proveedor')
    col_razon = find_col(df, 'Razón social proveedor', 'razon social', 'Razon Social')
    col_fecha = find_col(df, 'Fecha docto. prov.', 'fecha docto', 'Fecha')
    col_docto = find_col(df, 'Docto. proveedor', 'docto proveedor')
    col_val_bruto = find_col(df, 'Valor bruto', 'valor bruto', 'Total')
    col_val_imptos = find_col(df, 'Valor imptos', 'valor imptos', 'Impuestos')
    col_co = find_col(df, 'C.O.', 'co', 'CO')
    col_usuario = find_col(df, 'Usuario creación', 'usuario creacion')
    col_clase = find_col(df, 'Clase docto.', 'clase docto', 'Clase')
    col_nro = find_col(df, 'Nro documento', 'nro documento', 'Numero')
    
    if not col_proveedor or not col_docto:
        print(f"      ❌ Faltan columnas críticas")
        return
    
    print(f"      ✅ Columnas detectadas")
    
    # Limpiar tabla
    print("[3/4]Limpiando tabla...")
    cursor.execute("DELETE FROM erp_comercial")
    print(f"      {cursor.rowcount:,} registros eliminados")
    conn.commit()
    
    # Insertar registro por registro con ON CONFLICT
    print("[4/4] Insertando (registro por registro)...")
    
    insertados = 0
    duplicados = 0
    errores = 0
    
    for idx, row in df.iterrows():
        try:
            proveedor = str(row[col_proveedor]).strip() if col_proveedor else ''
            razon = str(row[col_razon]).strip() if col_razon and pd.notna(row.get(col_razon)) else ''
            fecha = pd.to_datetime(row[col_fecha], errors='coerce') if col_fecha and pd.notna(row.get(col_fecha)) else None
            docto = str(row[col_docto]).strip() if col_docto else ''
            
            # Valores numéricos
            val_bruto = float(str(row[col_val_bruto]).replace(',', '.')) if col_val_bruto and pd.notna(row.get(col_val_bruto)) and str(row[col_val_bruto]).strip() != '' else 0.0
            val_imptos = float(str(row[col_val_imptos]).replace(',', '.')) if col_val_imptos and pd.notna(row.get(col_val_imptos)) and str(row[col_val_imptos]).strip() != '' else 0.0
            
            co = str(row[col_co]).strip() if col_co and pd.notna(row.get(col_co)) else ''
            usuario = str(row[col_usuario]).strip() if col_usuario and pd.notna(row.get(col_usuario)) else ''
            clase = str(row[col_clase]).strip() if col_clase and pd.notna(row.get(col_clase)) else ''
            nro = str(row[col_nro]).strip() if col_nro and pd.notna(row.get(col_nro)) else ''
            
            # Prefijo/folio
            prefijo, folio = split_docto(docto)
            
            # Clave
            clave = f"{proveedor}_{docto}"
            
            # INSERT con ON CONFLICT
            cursor.execute("""
                INSERT INTO erp_comercial (
                    proveedor, razon_social_proveedor, fecha_docto_prov,
                    docto_proveedor, valor_bruto, valor_imptos, co,
                    usuario_creacion, clase_docto, nro_documento,
                    prefijo, folio, clave_erp_comercial, modulo,
                    doc_causado_por
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (clave_erp_comercial) DO NOTHING
            """, (
                proveedor, razon, fecha, docto, val_bruto, val_imptos,
                co, usuario, clase, nro, prefijo, folio, clave,
                'COMERCIAL', ''
            ))
            
            if cursor.rowcount > 0:
                insertados += 1
            else:
                duplicados += 1
                
        except Exception as e:
            errores += 1
            if errores <= 3:  # Solo mostrar primeros 3 errores
                print(f"      ⚠️  Error fila {idx}: {e}")
        
        # Progreso cada 5000
        if (idx + 1) % 5000 == 0:
            print(f"      Procesadas: {idx + 1:,} | Insertadas: {insertados:,} | Duplicadas: {duplicados:,}")
            conn.commit()  # Commit cada 5000
    
    # Commit final
    conn.commit()
    
    print(f"\n      ✅ COMPLETADO:")
    print(f"         Insertados: {insertados:,}")
    print(f"         Duplicados: {duplicados:,}")
    print(f"         Errores: {errores:,}")

# ========================================
# FUNCIÓN 2: Cargar ERP FINANCIERO
# ========================================

def cargar_erp_financiero(cursor, conn):
    """Carga ERP FINANCIERO con INSERT ON CONFLICT"""
    
    print("\n" + "="*80)
    print("2. ERP FINANCIERO")
    print("="*80)
    
    try:
        print("[1/4] Leyendo Excel...")
        df = pd.read_excel(FILES['ERP_FINANCIERO'], dtype=str)
        print(f"      ✅ {len(df):,} filas leídas")
    except Exception as e:
        print(f"      ❌ ERROR: {e}")
        return
    
    # Detectar columnas
    print("[2/4] Detectand columnas...")
    col_proveedor = find_col(df, 'Proveedor')
    col_razon = find_col(df, 'Razón social proveedor', 'razon social')
    col_fecha = find_col(df, 'Fecha proveedor', 'fecha')
    col_docto = find_col(df, 'Docto. proveedor', 'factura proveedor')  # ← CORRECTO: "Docto. proveedor"
    col_subtotal = find_col(df, 'Valor subtotal', 'subtotal')
    col_impuestos = find_col(df, 'Valor impuestos', 'impuestos')
    col_co = find_col(df, 'C.O.', 'co')
    col_usuario = find_col(df, 'Usuario creación', 'usuario creacion')
    col_clase = find_col(df, 'Clase docto.', 'clase')
    col_nro = find_col(df, 'Nro documento', 'numero')
    
    if not col_proveedor or not col_docto:
        print(f"      ❌ Faltan columnas críticas")
        return
    
    print(f"      ✅ Columnas detectadas")
    
    # Limpiar
    print("[3/4] Limpiando tabla...")
    cursor.execute("DELETE FROM erp_financiero")
    print(f"      {cursor.rowcount:,} eliminados")
    conn.commit()
    
    # Insertar
    print("[4/4] Insertando...")
    
    insertados = 0
    duplicados = 0
    errores = 0
    
    for idx, row in df.iterrows():
        try:
            proveedor = str(row[col_proveedor]).strip()
            razon = str(row[col_razon]).strip() if col_razon and pd.notna(row.get(col_razon)) else ''
            fecha = pd.to_datetime(row[col_fecha], errors='coerce') if col_fecha and pd.notna(row.get(col_fecha)) else None
            docto = str(row[col_docto]).strip()
            
            subtotal = float(str(row[col_subtotal]).replace(',', '.')) if col_subtotal and pd.notna(row.get(col_subtotal)) and str(row[col_subtotal]).strip() != '' else 0.0
            impuestos = float(str(row[col_impuestos]).replace(',', '.')) if col_impuestos and pd.notna(row.get(col_impuestos)) and str(row[col_impuestos]).strip() != '' else 0.0
            
            co = str(row[col_co]).strip() if col_co and pd.notna(row.get(col_co)) else ''
            usuario = str(row[col_usuario]).strip() if col_usuario and pd.notna(row.get(col_usuario)) else ''
            clase = str(row[col_clase]).strip() if col_clase and pd.notna(row.get(col_clase)) else ''
            nro = str(row[col_nro]).strip() if col_nro and pd.notna(row.get(col_nro)) else ''
            
            prefijo, folio = split_docto(docto)
            clave = f"{proveedor}_{docto}"
            
            cursor.execute("""
                INSERT INTO erp_financiero (
                    proveedor, razon_social_proveedor, fecha_docto_prov,
                    docto_proveedor, valor_bruto, valor_imptos, co,
                    usuario_creacion, clase_docto, nro_documento,
                    prefijo, folio, clave_erp_financiero, modulo,
                    doc_causado_por
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (clave_erp_financiero) DO NOTHING
            """, (
                proveedor, razon, fecha, docto, subtotal, impuestos,
                co, usuario, clase, nro, prefijo, folio, clave,
                'FINANCIERO', ''
            ))
            
            if cursor.rowcount > 0:
                insertados += 1
            else:
                duplicados += 1
                
        except Exception as e:
            errores += 1
            if errores <= 3:
                print(f"      ⚠️  Error fila {idx}: {e}")
        
        # Progress
        if (idx + 1) % 500 == 0:
            print(f"      Procesadas: {idx + 1:,} | Insertadas: {insertados:,}")
            conn.commit()
    
    conn.commit()
    
    print(f"\n      ✅ COMPLETADO:")
    print(f"         Insertados: {insertados:,}")
    print(f"         Duplicados: {duplicados:,}")
    print(f"         Errores: {errores:,}")

# ========================================
# FUNCIÓN 3: Cargar ACUSES
# ========================================

def cargar_acuses(cursor, conn):
    """Carga ACUSES con INSERT ON CONFLICT"""
    
    print("\n" + "="*80)
    print("3. ACUSES")
    print("="*80)
    
    try:
        print("[1/4] Leyendo Excel (46k filas, puede tomar 60-90 segundos)...")
        df = pd.read_excel(FILES['ACUSES'], dtype=str)
        print(f"      ✅ {len(df):,} filas leídas")
    except Exception as e:
        print(f"      ❌ ERROR: {e}")
        return
    
    # Detectar
    print("[2/4] Detectando columnas...")
    col_fecha = find_col(df, 'Fecha')
    col_adquiriente = find_col(df, 'Adquiriente')
    col_factura = find_col(df, 'Factura')
    col_emisor = find_col(df, 'Emisor')
    col_nit_emisor = find_col(df, 'Nit Emisor', 'nit emisor')
    col_nit_pt = find_col(df, 'Nit. PT', 'nit. pt', 'Nit PT')
    col_estado = find_col(df, 'Estado Docto.', 'estado docto', 'Estado')
    col_descripcion = find_col(df, 'Descripción Reclamo', 'descripcion reclamo')
    col_tipo = find_col(df, 'Tipo Documento', 'tipo')
    col_cufe = find_col(df, 'CUFE', 'cufe')
    col_valor = find_col(df, 'Valor', 'valor', 'Total')
    
    if not col_cufe:
        print(f"      ❌ Falta columna CUFE")
        return
    
    # Filtrar solo con CUFE válido
    df = df[df[col_cufe].notna() & (df[col_cufe].astype(str).str.strip() != '')]
    print(f"      ✅ {len(df):,} con CUFE válido")
    
    # Limpiar
    print("[3/4] Limpiando tabla...")
    cursor.execute("DELETE FROM acuses")
    print(f"      {cursor.rowcount:,} eliminados")
    conn.commit()
    
    #Insertar
    print("[4/4] Insertando...")
    
    insertados = 0
    duplicados = 0
    errores = 0
    
    for idx, row in df.iterrows():
        try:
            fecha = pd.to_datetime(row[col_fecha], errors='coerce') if col_fecha and pd.notna(row.get(col_fecha)) else None
            adquiriente = str(row[col_adquiriente]).strip() if col_adquiriente and pd.notna(row.get(col_adquiriente)) else ''
            factura = str(row[col_factura]).strip() if col_factura and pd.notna(row.get(col_factura)) else ''
            emisor = str(row[col_emisor]).strip() if col_emisor and pd.notna(row.get(col_emisor)) else ''
            nit_emisor = str(row[col_nit_emisor]).strip() if col_nit_emisor and pd.notna(row.get(col_nit_emisor)) else ''
            nit_pt = str(row[col_nit_pt]).strip() if col_nit_pt and pd.notna(row.get(col_nit_pt)) else ''
            estado = str(row[col_estado]).strip() if col_estado and pd.notna(row.get(col_estado)) else ''
            descripcion = str(row[col_descripcion]).strip() if col_descripcion and pd.notna(row.get(col_descripcion)) else ''
            tipo = str(row[col_tipo]).strip() if col_tipo and pd.notna(row.get(col_tipo)) else ''
            cufe = str(row[col_cufe]).strip()
            
            valor = float(str(row[col_valor]).replace(',', '.')) if col_valor and pd.notna(row.get(col_valor)) and str(row[col_valor]).strip() != '' else 0.0
            
            # Insertar con ON CONFLICT en CUFE
            cursor.execute("""
                INSERT INTO acuses (
                    fecha, adquiriente, factura, emisor, nit_emisor,
                    nit_pt, estado_docto, descripcion_reclamo, tipo_documento,
                    cufe, valor, aprobacion_acuse, recibo_bien_fe,
                    aceptacion_expresa, acuse_recibo, reclamo,
                    fecha_aprobacion_acuse, fecha_recibo_bien_fe,
                    fecha_aceptacion_expresa, fecha_reclamo
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (cufe) DO NOTHING
            """, (
                fecha, adquiriente, factura, emisor, nit_emisor,
                nit_pt, estado, descripcion, tipo, cufe, valor,
                '', '', '', '', '',  # Campos de acuse vacíos por ahora
                None, None, None, None  # Fechas de acuse
            ))
            
            if cursor.rowcount > 0:
                insertados += 1
            else:
                duplicados += 1
                
        except Exception as e:
            errores += 1
            if errores <= 3:
                print(f"      ⚠️  Error fila {idx}: {e}")
        
        # Progress
        if (idx + 1) % 5000 == 0:
            print(f"      Procesadas: {idx + 1:,} | Insertadas: {insertados:,}")
            conn.commit()
    
    conn.commit()
    
    print(f"\n      ✅ COMPLETADO:")
    print(f"         Insertados: {insertados:,}")
    print(f"         Duplicados: {duplicados:,}")
    print(f"         Errores: {errores:,}")

# ========================================
# MAIN
# ========================================

def main():
    """Ejecuta carga completa"""
    
    print("\n" + "="*80)
    print("🎯 CARGA DIRECTA A POSTGRESQL (SIN drop_duplicates)")
    print("="*80)
    print("INSERT ... ON CONFLICT DO NOTHING")
    print("PostgreSQL maneja duplicados automáticamente")
    print("="*80)
    
    # Conectar
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("\n[OK] Conectado a PostgreSQL")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return
    
    # Cargar
    cargar_erp_comercial(cursor, conn)
    cargar_erp_financiero(cursor, conn)
    cargar_acuses(cursor, conn)
    
    # Resumen
    print("\n" + "="*80)
    print("📊 RESUMEN FINAL")
    print("="*80)
    
    cursor.execute("SELECT COUNT(*) FROM dian")
    print(f"\nDIAN:           {cursor.fetchone()[0]:,}")
    
    cursor.execute("SELECT COUNT(*) FROM erp_comercial")
    print(f"ERP COMERCIAL:  {cursor.fetchone()[0]:,}")
    
    cursor.execute("SELECT COUNT(*) FROM erp_financiero")
    print(f"ERP FINANCIERO: {cursor.fetchone()[0]:,}")
    
    cursor.execute("SELECT COUNT(*) FROM acuses")
    print(f"ACUSES:         {cursor.fetchone()[0]:,}")
    
    print("\n" + "="*80)
    print("✅ CARGA COMPLETADA")
    print("="*80 + "\n")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
