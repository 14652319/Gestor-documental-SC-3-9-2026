# -*- coding: utf-8 -*-
"""Carga COMPLETA de las 3 tablas restantes (ERP COMERCIAL, ERP FINANCIERO, ACUSES)"""

import psycopg2
import pandas as pd
from datetime import datetime
import io

print("="*80)
print("CARGA COMPLETA - 3 TABLAS")
print("="*80)

# Conectar
conn = psycopg2.connect(
    host="localhost",
    database="gestor_documental",
    user="postgres",
    password="G3st0radm$2025."
)
conn.autocommit = False
cursor = conn.cursor()
print("[OK] Conectado\n")

# =============================================================================
# 1. ERP COMERCIAL
# =============================================================================
print("="*80)
print("1. ERP COMERCIAL")
print("="*80)

print("\n[1/5] Leyendo archivo...")
df_cm = pd.read_excel(r"C:/Users/Usuario/Downloads/Ricardo/ERP comercial 18 02 2026.xlsx", dtype=str)
print(f"      {len(df_cm):,} filas")

print("[2/5] Normalizando columnas...")
df_cm.columns = [c.lower().strip() for c in df_cm.columns]

# Mapeo de columnas Excel -> Tabla
print("[3/5] Mapeando columnas...")
df_cm['proveedor_col'] = df_cm['proveedor'].astype(str).str.strip()
df_cm['razon_social_proveedor_col'] = df_cm['razón social proveedor'].fillna('').astype(str).str.strip()[:255]

# Fecha
df_cm['fecha_docto_prov_col'] = pd.to_datetime(df_cm['fecha docto. prov.'], errors='coerce')
df_cm['fecha_docto_prov_col'] = df_cm['fecha_docto_prov_col'].dt.date

df_cm['docto_proveedor_col'] = df_cm['docto. proveedor'].fillna('').astype(str).str.strip()[:100]

# Valores numéricos
df_cm['valor_bruto_col'] = pd.to_numeric(df_cm['valor bruto'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)
df_cm['valor_imptos_col'] = pd.to_numeric(df_cm['valor imptos'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)

df_cm['co_col'] = df_cm['c.o.'].fillna('').astype(str).str.strip()[:50]
df_cm['usuario_creacion_col'] = df_cm['usuario creación'].fillna('').astype(str).str.strip()[:100]
df_cm['clase_docto_col'] = df_cm['clase docto.'].fillna('').astype(str).str.strip()[:50]
df_cm['nro_documento_col'] = df_cm['nro documento'].fillna('').astype(str).str.strip()[:50]

# Extraer prefijo y folio del docto_proveedor
def extraer_prefijo_folio(docto):
    if not docto or docto == 'nan':
        return '', ''
    partes = str(docto).split('-', 1)
    if len(partes) == 2:
        return partes[0].strip(), partes[1].strip()
    return '', str(docto).strip()

df_cm[['prefijo_col', 'folio_col']] = df_cm['docto_proveedor_col'].apply(
    lambda x: pd.Series(extraer_prefijo_folio(x))
)

# Clave
df_cm['clave_erp_comercial_col'] = df_cm['proveedor_col'] + df_cm['prefijo_col'] + df_cm['folio_col']
df_cm['modulo_col'] = 'ERP_COMERCIAL'

# Filtrar registros válidos
df_cm = df_cm[df_cm['proveedor_col'].notna()]
df_cm = df_cm[df_cm['proveedor_col'] != '']
df_cm = df_cm[df_cm['proveedor_col'] != 'nan']

# Eliminar duplicados por clave
df_cm = df_cm.drop_duplicates(subset=['clave_erp_comercial_col'], keep='first')

print(f"      {len(df_cm):,} registros validos (sin duplicados)")

# Limpiar tabla
print("[4/5] Limpiando tabla...")
cursor.execute("DELETE FROM erp_comercial")
print(f"      Eliminados: {cursor.rowcount}")

# COPY FROM
print("[5/5] Insertando...")
columnas = [
    'proveedor', 'razon_social_proveedor', 'fecha_docto_prov',
    'docto_proveedor', 'valor_bruto', 'valor_imptos',
    'co', 'usuario_creacion', 'clase_docto', 'nro_documento',
    'prefijo', 'folio', 'clave_erp_comercial', 'modulo'
]

columnas_df = [
    'proveedor_col', 'razon_social_proveedor_col', 'fecha_docto_prov_col',
    'docto_proveedor_col', 'valor_bruto_col', 'valor_imptos_col',
    'co_col', 'usuario_creacion_col', 'clase_docto_col', 'nro_documento_col',
    'prefijo_col', 'folio_col', 'clave_erp_comercial_col', 'modulo_col'
]

buffer = io.StringIO()
df_cm[columnas_df].to_csv(buffer, sep='\t', header=False, index=False, na_rep='')
buffer.seek(0)

cursor.copy_from(buffer, 'erp_comercial', columns=columnas, sep='\t')
conn.commit()

cursor.execute("SELECT COUNT(*) FROM erp_comercial")
count_cm = cursor.fetchone()[0]
print(f"      [COMPLETADO] {count_cm:,} registros en ERP_COMERCIAL\n")

# =============================================================================
# 2. ERP FINANCIERO
# =============================================================================
print("="*80)
print("2. ERP FINANCIERO")
print("="*80)

print("\n[1/5] Leyendo archivo...")
df_fn = pd.read_excel(r"C:/Users/Usuario/Downloads/Ricardo/ERP Financiero 18 02 2026.xlsx", dtype=str)
print(f"      {len(df_fn):,} filas")

print("[2/5] Normalizando columnas...")
df_fn.columns = [c.lower().strip() for c in df_fn.columns]

print("[3/5] Mapeando columnas...")
df_fn['proveedor_col'] = df_fn['proveedor'].astype(str).str.strip()
df_fn['razon_social_proveedor_col'] = df_fn['razón social proveedor'].fillna('').astype(str).str.strip()[:255]

# Fecha
df_fn['fecha_proveedor_col'] = pd.to_datetime(df_fn['fecha proveedor'], errors='coerce')
df_fn['fecha_proveedor_col'] = df_fn['fecha_proveedor_col'].dt.date

df_fn['docto_proveedor_col'] = df_fn['docto. proveedor'].fillna('').astype(str).str.strip()[:100]

# Valores
df_fn['valor_subtotal_col'] = pd.to_numeric(df_fn['valor subtotal'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)
df_fn['valor_impuestos_col'] = pd.to_numeric(df_fn['valor impuestos'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)

df_fn['co_col'] = df_fn['c.o.'].fillna('').astype(str).str.strip()[:50]
df_fn['usuario_creacion_col'] = df_fn['usuario creación'].fillna('').astype(str).str.strip()[:100]
df_fn['clase_docto_col'] = df_fn['clase docto.'].fillna('').astype(str).str.strip()[:50]
df_fn['nro_documento_col'] = df_fn['nro documento'].fillna('').astype(str).str.strip()[:50]

# Prefijo y folio
df_fn[['prefijo_col', 'folio_col']] = df_fn['docto_proveedor_col'].apply(
    lambda x: pd.Series(extraer_prefijo_folio(x))
)

# Clave
df_fn['clave_erp_financiero_col'] = df_fn['proveedor_col'] + df_fn['prefijo_col'] + df_fn['folio_col']
df_fn['modulo_col'] = 'ERP_FINANCIERO'

# Filtrar válidos
df_fn = df_fn[df_fn['proveedor_col'].notna()]
df_fn = df_fn[df_fn['proveedor_col'] != '']
df_fn = df_fn[df_fn['proveedor_col'] != 'nan']

# Eliminar duplicados
df_fn = df_fn.drop_duplicates(subset=['clave_erp_financiero_col'], keep='first')

print(f"      {len(df_fn):,} registros validos (sin duplicados)")

# Limpiar tabla
print("[4/5] Limpiando tabla...")
cursor.execute("DELETE FROM erp_financiero")
print(f"      Eliminados: {cursor.rowcount}")

# COPY FROM
print("[5/5] Insertando...")
columnas = [
    'proveedor', 'razon_social_proveedor', 'fecha_proveedor',
    'docto_proveedor', 'valor_subtotal', 'valor_impuestos',
    'co', 'usuario_creacion', 'clase_docto', 'nro_documento',
    'prefijo', 'folio', 'clave_erp_financiero', 'modulo'
]

columnas_df = [
    'proveedor_col', 'razon_social_proveedor_col', 'fecha_proveedor_col',
    'docto_proveedor_col', 'valor_subtotal_col', 'valor_impuestos_col',
    'co_col', 'usuario_creacion_col', 'clase_docto_col', 'nro_documento_col',
    'prefijo_col', 'folio_col', 'clave_erp_financiero_col', 'modulo_col'
]

buffer = io.StringIO()
df_fn[columnas_df].to_csv(buffer, sep='\t', header=False, index=False, na_rep='')
buffer.seek(0)

cursor.copy_from(buffer, 'erp_financiero', columns=columnas, sep='\t')
conn.commit()

cursor.execute("SELECT COUNT(*) FROM erp_financiero")
count_fn = cursor.fetchone()[0]
print(f"      [COMPLETADO] {count_fn:,} registros en ERP_FINANCIERO\n")

# =============================================================================
# 3. ACUSES
# =============================================================================
print("="*80)
print("3. ACUSES")
print("="*80)

print("\n[1/5] Leyendo archivo...")
df_ac = pd.read_excel(r"C:/Users/Usuario/Downloads/Ricardo/acuses 2.xlsx", dtype=str)
print(f"      {len(df_ac):,} filas")

print("[2/5] Normalizando columnas...")
df_ac.columns = [c.lower().strip() for c in df_ac.columns]

print("[3/5] Mapeando columnas...")

# Fecha
df_ac['fecha_col'] = pd.to_datetime(df_ac['fecha'], errors='coerce')
df_ac['fecha_col'] = df_ac['fecha_col'].dt.date

df_ac['adquiriente_col'] = df_ac['adquiriente'].fillna('').astype(str).str.strip()[:255]
df_ac['factura_col'] = df_ac['factura'].fillna('').astype(str).str.strip()[:100]
df_ac['emisor_col'] = df_ac['emisor'].fillna('').astype(str).str.strip()[:255]
df_ac['nit_emisor_col'] = df_ac['nit emisor'].fillna('').astype(str).str.strip()[:20]
df_ac['nit_pt_col'] = df_ac['nit. pt'].fillna('').astype(str).str.strip()[:20]
df_ac['estado_docto_col'] = df_ac['estado docto.'].fillna('').astype(str).str.strip()[:100]
df_ac['descripcion_reclamo_col'] = df_ac['descripción reclamo'].fillna('').astype(str).str.strip()
df_ac['tipo_documento_col'] = df_ac['tipo documento'].fillna('').astype(str).str.strip()[:50]
df_ac['cufe_col'] = df_ac['cufe'].fillna('').astype(str).str.strip()[:255]

# Valor
df_ac['valor_col'] = pd.to_numeric(df_ac['valor'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)

df_ac['acuse_recibido_col'] = df_ac['acuse recibido'].fillna('').astype(str).str.strip()[:50]
df_ac['recibo_bien_servicio_col'] = df_ac['recibo bien servicio'].fillna('').astype(str).str.strip()[:50]
df_ac['aceptacion_expresa_col'] = df_ac['aceptación expresa'].fillna('').astype(str).str.strip()[:50]
df_ac['reclamo_col'] = df_ac['reclamo'].fillna('').astype(str).str.strip()[:50]
df_ac['aceptacion_tacita_col'] = df_ac['aceptación tacita'].fillna('').astype(str).str.strip()[:50]

# Clave = CUFE
df_ac['clave_acuse_col'] = df_ac['cufe_col']

# Filtrar válidos
df_ac = df_ac[df_ac['cufe_col'].notna()]
df_ac = df_ac[df_ac['cufe_col'] != '']
df_ac = df_ac[df_ac['cufe_col'] != 'nan']

# Eliminar duplicados
df_ac = df_ac.drop_duplicates(subset=['clave_acuse_col'], keep='first')

print(f"      {len(df_ac):,} registros validos (sin duplicados)")

# Limpiar tabla
print("[4/5] Limpiando tabla...")
cursor.execute("DELETE FROM acuses")
print(f"      Eliminados: {cursor.rowcount}")

# COPY FROM
print("[5/5] Insertando...")
columnas = [
    'fecha', 'adquiriente', 'factura', 'emisor', 'nit_emisor', 'nit_pt',
    'estado_docto', 'descripcion_reclamo', 'tipo_documento', 'cufe', 'valor',
    'acuse_recibido', 'recibo_bien_servicio', 'aceptacion_expresa',
    'reclamo', 'aceptacion_tacita', 'clave_acuse'
]

columnas_df = [
    'fecha_col', 'adquiriente_col', 'factura_col', 'emisor_col', 'nit_emisor_col', 'nit_pt_col',
    'estado_docto_col', 'descripcion_reclamo_col', 'tipo_documento_col', 'cufe_col', 'valor_col',
    'acuse_recibido_col', 'recibo_bien_servicio_col', 'aceptacion_expresa_col',
    'reclamo_col', 'aceptacion_tacita_col', 'clave_acuse_col'
]

buffer = io.StringIO()
df_ac[columnas_df].to_csv(buffer, sep='\t', header=False, index=False, na_rep='')
buffer.seek(0)

cursor.copy_from(buffer, 'acuses', columns=columnas, sep='\t')
conn.commit()

cursor.execute("SELECT COUNT(*) FROM acuses")
count_ac = cursor.fetchone()[0]
print(f"      [COMPLETADO] {count_ac:,} registros en ACUSES\n")

# =============================================================================
# RESUMEN FINAL
# =============================================================================
print("="*80)
print("RESUMEN FINAL")
print("="*80)

cursor.execute("SELECT COUNT(*) FROM dian")
count_dian = cursor.fetchone()[0]

print(f"\nDIAN:          {count_dian:,} registros")
print(f"ERP COMERCIAL: {count_cm:,} registros")
print(f"ERP FINANCIERO: {count_fn:,} registros")
print(f"ACUSES:        {count_ac:,} registros")
print(f"\nTOTAL:         {count_dian + count_cm + count_fn + count_ac:,} registros")

print("\n" + "="*80)
print("[EXITO] TODAS LAS TABLAS CARGADAS")
print("="*80)

cursor.close()
conn.close()
