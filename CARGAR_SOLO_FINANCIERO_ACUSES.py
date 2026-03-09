#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CARGAR_SOLO_FINANCIERO_ACUSES.py - Carga SOLO las dos tablas faltantes
========================================================================

Ya tenemos:
- DIAN: 66,276 ✅
- ERP COMERCIAL: 57,191 ✅

Faltan:
- ERP FINANCIERO: 2,996 registros
- ACUSES: 46,650 registros
"""

import psycopg2
import pandas as pd
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
    'ERP_FINANCIERO': r'C:/Users/Usuario/Downloads/Ricardo/ERP Financiero 18 02 2026.xlsx',
    'ACUSES': r'C:/Users/Usuario/Downloads/Ricardo/acuses 2.xlsx'
}

# ========================================
# FUNCIÓN 1: Cargar ERP FINANCIERO
# ========================================

def cargar_erp_financiero(cursor, conn):
    """Carga ERP FINANCIERO con INSERT individual"""
    
    print("\n" + "="*80)
    print("1. ERP FINANCIERO")
    print("="*80 + "\n")
    
    # --- Leer Excel (chunk pequeño para no colgar) ---
    print("[1/4] Leyendo archivo...")
    try:
        df = pd.read_excel(FILES['ERP_FINANCIERO'], dtype=str, nrows=3000)
        print(f"      {len(df):,} filas leídas")
    except Exception as e:
        print(f"      ❌ ERROR leyendo Excel: {e}")
        return
    
    # --- Normalizar columnas ---
    print("[2/4] Normalizando columnas...")
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Columnas esperadas (según la documentación)
    col_map = {
        'proveedor': 'proveedor',
        'razón social proveedor': 'razon_social',
        'fecha proveedor': 'fecha',
        'docto. proveedor': 'factura',
        'valor subtotal': 'subtotal',
        'valor impuestos': 'impuestos',
        'c.o.': 'co',
        'usuario creación': 'usuario',
        'clase docto.': 'clase',
        'nro documento': 'nro_doc'
    }
    
    # Mapear columnas flexiblemente
    df_cols = {}
    for excel_col, target_col in col_map.items():
        if excel_col in df.columns:
            df_cols[target_col] = df[excel_col]
        else:
            print(f"      ⚠️  Columna no encontrada: {excel_col}")
            df_cols[target_col] = pd.Series([''] * len(df))
    
    print(f"      Columnas mapeadas: {len(df_cols)}")
    
    # --- Limpiar tabla ---
    print("[3/4] Limpiando tabla...")
    cursor.execute("DELETE FROM erp_financiero")
    conn.commit()
    print(f"      Eliminados: {cursor.rowcount:,}")
    
    # --- Insertar registro por registro ---
    print("[4/4] Insertando registros...")
    
    sql = """
        INSERT INTO erp_financiero (
            proveedor, razon_social_proveedor, fecha_proveedor, 
            docto_proveedor, valor_subtotal, valor_impuestos, co,
            usuario_creacion, clase_docto, nro_documento,
            prefijo, folio, clave_erp_financiero, modulo, doc_causado_por
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (clave_erp_financiero) DO NOTHING
    """
    
    insertados = 0
    errores = 0
    
    for idx, row in enumerate(df.iterrows(), 1):
        i, r = row
        
        try:
            # Extraer valores
            proveedor = str(df_cols['proveedor'].iloc[i]).strip()[:20]
            razon = str(df_cols['razon_social'].iloc[i]).strip()[:255]
            
            # Fecha
            fecha_str = str(df_cols['fecha'].iloc[i])
            try:
                fecha = pd.to_datetime(fecha_str).date()
            except:
                fecha = None
            
            # Factura
            factura = str(df_cols['factura'].iloc[i]).strip()[:100]
            
            # Valores
            try:
                subtotal = float(str(df_cols['subtotal'].iloc[i]).replace(',', '.'))
            except:
                subtotal = 0.0
            
            try:
                impuestos = float(str(df_cols['impuestos'].iloc[i]).replace(',', '.'))
            except:
                impuestos = 0.0
            
            # Otros campos
            co = str(df_cols['co'].iloc[i]).strip()[:50]
            usuario = str(df_cols['usuario'].iloc[i]).strip()[:100]
            clase = str(df_cols['clase'].iloc[i]).strip()[:50]
            nro_doc = str(df_cols['nro_doc'].iloc[i]).strip()[:50]
            
            # Extraer prefijo y folio
            if '-' in factura:
                partes = factura.split('-', 1)
                prefijo = partes[0].strip()[:20]
                folio = partes[1].strip()[:50]
            else:
                prefijo = ''
                folio = factura[:50]
            
            # Clave única
            clave = f"{proveedor}_{factura}"[:100]
            
            # Insertar
            cursor.execute(sql, (
                proveedor, razon, fecha, factura, subtotal, impuestos,
                co, usuario, clase, nro_doc, prefijo, folio,
                clave, 'FINANCIERO', ''
            ))
            insertados += 1
            
            # Progreso cada 500
            if idx % 500 == 0:
                conn.commit()
                print(f"      Procesados: {idx:,} | Insertados: {insertados:,}")
        
        except Exception as e:
            errores += 1
            if errores < 5:
                print(f"      ⚠️  Error en fila {idx}: {e}")
    
    # Commit final
    conn.commit()
    
    print(f"\n      ✅ COMPLETADO:")
    print(f"         Total procesados: {len(df):,}")
    print(f"         Insertados: {insertados:,}")
    print(f"         Errores: {errores:,}")
    
    # Muestra
    print("\n      Muestra:")
    cursor.execute("""
        SELECT proveedor, docto_proveedor, 
               TO_CHAR(valor_subtotal, 'FM$999,999,999') as valor
        FROM erp_financiero 
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"        {row[0]} | {row[1]} | {row[2]}")

# ========================================
# FUNCIÓN 2: Cargar ACUSES
# ========================================

def cargar_acuses(cursor, conn):
    """Carga ACUSES con INSERT individual"""
    
    print("\n" + "="*80)
    print("2. ACUSES")
    print("="*80 + "\n")
    
    # --- Leer Excel ---
    print("[1/4] Leyendo archivo...")
    try:
        # Leer en chunks si es muy grande
        df = pd.read_excel(FILES['ACUSES'], dtype=str)
        print(f"      {len(df):,} filas leídas")
    except Exception as e:
        print(f"      ❌ ERROR leyendo Excel: {e}")
        return
    
    # --- Normalizar columnas ---
    print("[2/4] Normalizando columnas...")
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Columnas esperadas
    col_map = {
        'fecha': 'fecha',
        'adquiriente': 'adquiriente',
        'factura': 'factura',
        'emisor': 'emisor',
        'nit emisor': 'nit_emisor',
        'nit. pt': 'nit_pt',
        'estado docto.': 'estado',
        'descripción reclamo': 'desc_reclamo',
        'tipo documento': 'tipo_doc',
        'cufe': 'cufe',
        'valor': 'valor',
        'acuse recibido': 'acuse_recibido',
        'recibo bien servicio': 'recibo_servicio',
        'aceptacion expresa': 'acep_expresa',
        'reclamo': 'reclamo',
        'aceptacion tacita': 'acep_tacita'
    }
    
    # Mapear columnas
    df_cols = {}
    for excel_col, target_col in col_map.items():
        if excel_col in df.columns:
            df_cols[target_col] = df[excel_col]
        else:
            print(f"      ⚠️  Columna no encontrada: {excel_col}")
            df_cols[target_col] = pd.Series([''] * len(df))
    
    print(f"      Columnas mapeadas: {len(df_cols)}")
    
    # Filtrar solo con CUFE válido
    df_cufe_valido = df_cols['cufe'].notna() & (df_cols['cufe'].astype(str).str.strip() != '')
    total_validos = df_cufe_valido.sum()
    print(f"      Registros con CUFE válido: {total_validos:,}")
    
    # --- Limpiar tabla ---
    print("[3/4] Limpiando tabla...")
    cursor.execute("DELETE FROM acuses")
    conn.commit()
    print(f"      Eliminados: {cursor.rowcount:,}")
    
    # --- Insertar registro por registro ---
    print("[4/4] Insertando registros...")
    
    sql = """
        INSERT INTO acuses (
            fecha, adquiriente, factura, emisor, nit_emisor, nit_pt,
            estado_docto, descripcion_reclamo, tipo_documento, cufe, valor,
            acuse_recibido, recibo_bien_servicio, aceptacion_expresa, 
            reclamo, aceptacion_tacita, clave_acuse
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (cufe) DO NOTHING
    """
    
    insertados = 0
    errores = 0
    
    for idx in range(len(df)):
        if not df_cufe_valido.iloc[idx]:
            continue
        
        try:
            # Fecha principal
            fecha_str = str(df_cols['fecha'].iloc[idx])
            try:
                fecha = pd.to_datetime(fecha_str).date()
            except:
                fecha = None
            
            # Campos de texto
            adquiriente = str(df_cols['adquiriente'].iloc[idx]).strip()[:255]
            factura = str(df_cols['factura'].iloc[idx]).strip()[:100]
            emisor = str(df_cols['emisor'].iloc[idx]).strip()[:255]
            nit_emisor = str(df_cols['nit_emisor'].iloc[idx]).strip()[:20]
            nit_pt = str(df_cols['nit_pt'].iloc[idx]).strip()[:20]
            estado = str(df_cols['estado'].iloc[idx]).strip()[:100]
            desc_reclamo = str(df_cols['desc_reclamo'].iloc[idx]).strip()[:500]
            tipo_doc = str(df_cols['tipo_doc'].iloc[idx]).strip()[:50]
            cufe = str(df_cols['cufe'].iloc[idx]).strip()[:255]
            
            # Valor
            try:
                valor = float(str(df_cols['valor'].iloc[idx]).replace(',', '.'))
            except:
                valor = 0.0
            
            # Campos de acuse
            acuse_recibido = str(df_cols['acuse_recibido'].iloc[idx]).strip()[:50]
            recibo_servicio = str(df_cols['recibo_servicio'].iloc[idx]).strip()[:50]
            acep_expresa = str(df_cols['acep_expresa'].iloc[idx]).strip()[:50]
            reclamo = str(df_cols['reclamo'].iloc[idx]).strip()[:50]
            acep_tacita = str(df_cols['acep_tacita'].iloc[idx]).strip()[:50]
            
            # Clave = CUFE
            clave_acuse = cufe
            
            # Insertar
            cursor.execute(sql, (
                fecha, adquiriente, factura, emisor, nit_emisor, nit_pt,
                estado, desc_reclamo, tipo_doc, cufe, valor,
                acuse_recibido, recibo_servicio, acep_expresa, reclamo, acep_tacita,
                clave_acuse
            ))
            insertados += 1
            
            # Progreso cada 5000
            if insertados % 5000 == 0:
                conn.commit()
                print(f"      Procesados: {insertados:,}")
        
        except Exception as e:
            errores += 1
            if errores < 5:
                print(f"      ⚠️  Error en fila {idx}: {e}")
    
    # Commit final
    conn.commit()
    
    print(f"\n      ✅ COMPLETADO:")
    print(f"         Total procesados: {total_validos:,}")
    print(f"         Insertados: {insertados:,}")
    print(f"         Errores: {errores:,}")
    
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
    """Ejecuta la carga de las dos tablas faltantes"""
    
    print("\n" + "="*80)
    print("CARGA DE ERP FINANCIERO Y ACUSES")
    print("="*80)
    print("Estado actual:")
    print("  DIAN: 66,276 ✅")
    print("  ERP COMERCIAL: 57,191 ✅")
    print("  ERP FINANCIERO: 0 ❌")
    print("  ACUSES: 0 ❌")
    print("="*80 + "\n")
    
    # Conectar
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("[OK] Conectado a PostgreSQL\n")
    except Exception as e:
        print(f"❌ ERROR de conexión: {e}")
        return
    
    # Cargar las dos tablas
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
