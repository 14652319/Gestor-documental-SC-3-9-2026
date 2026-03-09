#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CARGAR_ACUSES_CSV.py - Convierte Excel a CSV y carga con COPY FROM
======================================================================

ESTRATEGIA MÁS RÁPIDA:
1. Leer Excel de ACUSES (46,650 filas)
2. Convertir a CSV en memoria
3. Cargar con cursor.copy_from() (igual que DIAN)
"""

import psycopg2
import pandas as pd
import io

# ========================================
# CONFIGURACIÓN
# ========================================

DB_CONFIG = {
    'host': 'localhost',
    'database': 'gestor_documental',
    'user': 'postgres',
    'password': 'G3st0radm$2025.'
}

ARCHIVO_ACUSES = r'C:/Users/Usuario/Downloads/Ricardo/acuses 2.xlsx'

# ========================================
# FUNCIÓN: Cargar ACUSES
# ========================================

def cargar_acuses():
    """Carga ACUSES con COPY FROM (método más rápido)"""
    
    print("\n" + "="*80)
    print("CARGA RÁPIDA DE ACUSES")
    print("="*80 + "\n")
    
    # --- PASO 1: Leer Excel ---
    print("[1/5] Leyendo Excel...")
    try:
        df = pd.read_excel(ARCHIVO_ACUSES, dtype=str)
        print(f"      {len(df):,} filas leídas")
    except Exception as e:
        print(f"      ❌ ERROR: {e}")
        return 1
    
    # --- PASO 2: Normalizar columnas ---
    print("[2/5] Normalizando columnas...")
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Mapeo de columnas Excel → Base de datos
    col_map = {
        'fecha': 'fecha',
        'adquiriente': 'adquiriente',
        'factura': 'factura',
        'emisor': 'emisor',
        'nit emisor': 'nit_emisor',
        'nit. pt': 'nit_pt',  # Nota: con punto
        'estado docto.': 'estado_docto',
        'descripción reclamo': 'descripcion_reclamo',
        'tipo documento': 'tipo_documento',
        'cufe': 'cufe',
        'valor': 'valor',
        'acuse recibido': 'acuse_recibido',
        'recibo bien servicio': 'recibo_bien_servicio',
        'aceptacion expresa': 'aceptacion_expresa',
        'reclamo': 'reclamo',
        'aceptacion tacita': 'aceptacion_tacita'
    }
    
    # Verificar columnas existentes
    print("      Columnas encontradas:")
    for excel_col in col_map.keys():
        if excel_col in df.columns:
            print(f"        ✅ {excel_col}")
        else:
            print(f"        ❌ {excel_col} (falta)")
    
    # --- PASO 3: Filtrar y mapear ---
    print("[3/5] Filtrando registros con CUFE...")
    
    # Filtrar solo con CUFE
    if 'cufe' not in df.columns:
        print("      ❌ ERROR: No existe columna 'cufe'")
        return 1
    
    df = df[df['cufe'].notna() & (df['cufe'].astype(str).str.strip() != '')]
    print(f"      {len(df):,} registros con CUFE válido")
    
    # --- PASO 4: Crear DataFrame final ---
    print("[4/5] Mapeando datos...")
    
    df_final = pd.DataFrame()
    
    # Fecha
    df_final['fecha'] = pd.to_datetime(df.get('fecha', pd.Series([None] * len(df))), errors='coerce')
    
    # Campos de texto
    df_final['adquiriente'] = df.get('adquiriente', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    df_final['factura'] = df.get('factura', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    df_final['emisor'] = df.get('emisor', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    df_final['nit_emisor'] = df.get('nit emisor', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    df_final['nit_pt'] = df.get('nit. pt', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    df_final['estado_docto'] = df.get('estado docto.', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    df_final['descripcion_reclamo'] = df.get('descripción reclamo', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    df_final['tipo_documento'] = df.get('tipo documento', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    df_final['cufe'] = df['cufe'].astype(str).str.strip()
    
    # Valor numérico
    df_final['valor'] = pd.to_numeric(
        df.get('valor', pd.Series([0] * len(df))).astype(str).str.replace(',', '.'),
        errors='coerce'
    ).fillna(0.0)
    
    # Campos de acuse
    df_final['acuse_recibido'] = df.get('acuse recibido', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    df_final['recibo_bien_servicio'] = df.get('recibo bien servicio', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    df_final['aceptacion_expresa'] = df.get('aceptacion expresa', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    df_final['reclamo'] = df.get('reclamo', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    df_final['aceptacion_tacita'] = df.get('aceptacion tacita', pd.Series([''] * len(df))).fillna('').astype(str).str.strip()
    
    # Clave = CUFE
    df_final['clave_acuse'] = df_final['cufe']
    
    print(f"      Registros finales: {len(df_final):,}")
    
    # --- PASO 5: Cargar con COPY FROM ---
    print("[5/5] Insertando en PostgreSQL...")
    
    # Conectar
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("      Conectado a BD")
    except Exception as e:
        print(f"      ❌ ERROR de conexión: {e}")
        return 1
    
    # Limpiar tabla
    cursor.execute("DELETE FROM acuses")
    eliminados = cursor.rowcount
    conn.commit()
    print(f"      Eliminados: {eliminados:,} registros anteriores")
    
    # Preparar buffer CSV
    columns = [
        'fecha', 'adquiriente', 'factura', 'emisor', 'nit_emisor', 'nit_pt',
        'estado_docto', 'descripcion_reclamo', 'tipo_documento', 'cufe', 'valor',
        'acuse_recibido', 'recibo_bien_servicio', 'aceptacion_expresa',
        'reclamo', 'aceptacion_tacita', 'clave_acuse'
    ]
    
    buffer = io.StringIO()
    df_final[columns].to_csv(buffer, sep='\t', header=False, index=False, na_rep='')
    buffer.seek(0)
    
    # Insertar
    try:
        cursor.copy_from(buffer, 'acuses', columns=columns, sep='\t')
        conn.commit()
        print(f"      ✅ COMPLETADO: {len(df_final):,} registros insertados")
    except Exception as e:
        conn.rollback()
        print(f"      ❌ ERROR en INSERT: {e}")
        cursor.close()
        conn.close()
        return 1
    
    # Muestra
    print("\n      Muestra de datos:")
    cursor.execute("""
        SELECT nit_emisor, factura, TO_CHAR(valor, 'FM$999,999,999') as valor
        FROM acuses 
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"        {row[0]} | {row[1]} | {row[2]}")
    
    # Cerrar
    cursor.close()
    conn.close()
    
    return 0

# ========================================
# MAIN
# ========================================

def main():
    print("\n" + "="*80)
    print("CARGA RÁPIDA DE ACUSES CON COPY FROM")
    print("="*80)
    print("Estado previo:")
    print("  DIAN: 66,276 ✅")
    print("  ERP COMERCIAL: 57,191 ✅")
    print("  ERP FINANCIERO: 2,995 ✅")
    print("  ACUSES: 0 ❌")
    print("="*80 + "\n")
    
    resultado = cargar_acuses()
    
    if resultado == 0:
        # Verificar conteos finales
        print("\n" + "="*80)
        print("RESUMEN FINAL")
        print("="*80 + "\n")
        
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
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
            print("[ÉXITO] TODAS LAS TABLAS CARGADAS")
            print("="*80 + "\n")
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error al verificar conteos: {e}")
    else:
        print("\n❌ Hubo errores en la carga")

if __name__ == '__main__':
    main()
