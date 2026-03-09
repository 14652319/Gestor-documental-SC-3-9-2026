# -*- coding: utf-8 -*-
"""CARGA FINAL CORRECTA - usa docto_proveedor como clave principal"""

import psycopg2
import pandas as pd
from datetime import datetime
import io

print("="*80)
print("CARGA FINAL - Usando docto_proveedor como clave")
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
print(f"      {len(df_cm):,} filas originales")

print("[2/5] Normalizando y filtrando...")
df_cm.columns = [c.lower().strip() for c in df_cm.columns]

# Filtrar válidos
df_cm = df_cm[df_cm['proveedor'].notna() & (df_cm['proveedor'] != '')]
print(f"      {len(df_cm):,} con NIT valido")

print("[3/5] Mapeando columnas...")
# Mapear todas las columnas SIN crear columnas intermedias problemáticas
proveedor = df_cm['proveedor'].astype(str).str.strip()[:20]
razon_social = df_cm['razón social proveedor'].fillna('').astype(str).str.strip()[:255]
fecha_docto = pd.to_datetime(df_cm['fecha docto. prov.'], errors='coerce').dt.date
docto_prov = df_cm['docto. proveedor'].fillna('').astype(str).str.strip()[:100]
valor_bruto = pd.to_numeric(df_cm['valor bruto'].astype(str).str.replace(',', '.').str.replace('$', '').str.strip(), errors='coerce').fillna(0.0)
valor_imptos = pd.to_numeric(df_cm['valor imptos'].astype(str).str.replace(',', '.').str.replace('$', '').str.strip(), errors='coerce').fillna(0.0)
co = df_cm['c.o.'].fillna('').astype(str).str.strip()[:50]
usuario = df_cm['usuario creación'].fillna('').astype(str).str.strip()[:100]
clase = df_cm['clase docto.'].fillna('').astype(str).str.strip()[:50]
nro_doc = df_cm['nro documento'].fillna('').astype(str).str.strip()[:50]

# Extraer prefijo y folio
def split_docto(d):
    if '-' in str(d):
        p = str(d).split('-', 1)
        return p[0].strip(), p[1].strip()
    return '', str(d).strip()

prefijo_folio = docto_prov.apply(split_docto)
prefijo = pd.Series([x[0] for x in prefijo_folio])
folio = pd.Series([x[1] for x in prefijo_folio])

# Clave: proveedor + docto_proveedor (simple y efectiva)
clave = proveedor + '_' + docto_prov
modulo = 'ERP_COMERCIAL'
doc_causado = ''

print(f"      Claves únicas: {clave.nunique():,}")

# Crear DataFrame final
df_final = pd.DataFrame({
    'proveedor': proveedor,
    'razon_social_proveedor': razon_social,
    'fecha_docto_prov': fecha_docto,
    'docto_proveedor': docto_prov,
    'valor_bruto': valor_bruto,
    'valor_imptos': valor_imptos,
    'co': co,
    'usuario_creacion': usuario,
    'clase_docto': clase,
    'nro_documento': nro_doc,
    'prefijo': prefijo,
    'folio': folio,
    'clave_erp_comercial': clave,
    'modulo': modulo,
    'doc_causado_por': doc_causado
})

# Eliminar duplicados por clave
antes = len(df_final)
df_final = df_final.drop_duplicates(subset=['clave_erp_comercial'], keep='first')
print(f"      Duplicados eliminados: {antes - len(df_final):,}")
print(f"      Registros finales: {len(df_final):,}")

print("[4/5] Limpiando tabla...")
cursor.execute("DELETE FROM erp_comercial")
print(f"      Eliminados: {cursor.rowcount}")

print("[5/5] Insertando...")
buffer = io.StringIO()
df_final.to_csv(buffer, sep='\t', header=False, index=False, na_rep='')
buffer.seek(0)

cursor.copy_from(buffer, 'erp_comercial', columns=list(df_final.columns), sep='\t')
conn.commit()

cursor.execute("SELECT COUNT(*) FROM erp_comercial")
count_cm = cursor.fetchone()[0]
print(f"      [COMPLETADO] {count_cm:,} registros")

# Muestra
cursor.execute("SELECT proveedor, docto_proveedor, valor_bruto FROM erp_comercial LIMIT 5")
print("\n      Muestra:")
for r in cursor.fetchall():
    print(f"        {r[0]} | {r[1]} | ${r[2]:,.0f}")

# =============================================================================
# 2. ERP FINANCIERO
# =============================================================================
print("\n" + "="*80)
print("2. ERP FINANCIERO")
print("="*80)

print("\n[1/5] Leyendo archivo...")
df_fn = pd.read_excel(r"C:/Users/Usuario/Downloads/Ricardo/ERP Financiero 18 02 2026.xlsx", dtype=str)
print(f"      {len(df_fn):,} filas originales")

print("[2/5] Normalizando y filtrando...")
df_fn.columns = [c.lower().strip() for c in df_fn.columns]
df_fn = df_fn[df_fn['proveedor'].notna() & (df_fn['proveedor'] != '')]
print(f"      {len(df_fn):,} con NIT valido")

print("[3/5] Mapeando columnas...")
proveedor = df_fn['proveedor'].astype(str).str.strip()[:20]
razon_social = df_fn['razón social proveedor'].fillna('').astype(str).str.strip()[:255]
fecha_prov = pd.to_datetime(df_fn['fecha proveedor'], errors='coerce').dt.date
docto_prov = df_fn['docto. proveedor'].fillna('').astype(str).str.strip()[:100]
valor_subtotal = pd.to_numeric(df_fn['valor subtotal'].astype(str).str.replace(',', '.').str.replace('$', '').str.strip(), errors='coerce').fillna(0.0)
valor_impuestos = pd.to_numeric(df_fn['valor impuestos'].astype(str).str.replace(',', '.').str.replace('$', '').str.strip(), errors='coerce').fillna(0.0)
co = df_fn['c.o.'].fillna('').astype(str).str.strip()[:50]
usuario = df_fn['usuario creación'].fillna('').astype(str).str.strip()[:100]
clase = df_fn['clase docto.'].fillna('').astype(str).str.strip()[:50]
nro_doc = df_fn['nro documento'].fillna('').astype(str).str.strip()[:50]

prefijo_folio = docto_prov.apply(split_docto)
prefijo = pd.Series([x[0] for x in prefijo_folio])
folio = pd.Series([x[1] for x in prefijo_folio])

clave = proveedor + '_' + docto_prov
modulo = 'ERP_FINANCIERO'

print(f"      Claves únicas: {clave.nunique():,}")

df_final = pd.DataFrame({
    'proveedor': proveedor,
    'razon_social_proveedor': razon_social,
    'fecha_proveedor': fecha_prov,
    'docto_proveedor': docto_prov,
    'valor_subtotal': valor_subtotal,
    'valor_impuestos': valor_impuestos,
    'co': co,
    'usuario_creacion': usuario,
    'clase_docto': clase,
    'nro_documento': nro_doc,
    'prefijo': prefijo,
    'folio': folio,
    'clave_erp_financiero': clave,
    'modulo': modulo,
    'doc_causado_por': ''
})

antes = len(df_final)
df_final = df_final.drop_duplicates(subset=['clave_erp_financiero'], keep='first')
print(f"      Duplicados eliminados: {antes - len(df_final):,}")
print(f"      Registros finales: {len(df_final):,}")

print("[4/5] Limpiando tabla...")
cursor.execute("DELETE FROM erp_financiero")
print(f"      Eliminados: {cursor.rowcount}")

print("[5/5] Insertando...")
buffer = io.StringIO()
df_final.to_csv(buffer, sep='\t', header=False, index=False, na_rep='')
buffer.seek(0)

cursor.copy_from(buffer, 'erp_financiero', columns=list(df_final.columns), sep='\t')
conn.commit()

cursor.execute("SELECT COUNT(*) FROM erp_financiero")
count_fn = cursor.fetchone()[0]
print(f"      [COMPLETADO] {count_fn:,} registros")

cursor.execute("SELECT proveedor, docto_proveedor, valor_subtotal FROM erp_financiero LIMIT 5")
print("\n      Muestra:")
for r in cursor.fetchall():
    print(f"        {r[0]} | {r[1]} | ${r[2]:,.0f}")

# =============================================================================
# 3. ACUSES
# =============================================================================
print("\n" + "="*80)
print("3. ACUSES")
print("="*80)

print("\n[1/5] Leyendo archivo...")
df_ac = pd.read_excel(r"C:/Users/Usuario/Downloads/Ricardo/acuses 2.xlsx", dtype=str)
print(f"      {len(df_ac):,} filas originales")

print("[2/5] Normalizando y filtrando...")
df_ac.columns = [c.lower().strip() for c in df_ac.columns]
df_ac = df_ac[df_ac['cufe'].notna() & (df_ac['cufe'] != '')]
print(f"      {len(df_ac):,} con CUFE valido")

print("[3/5] Mapeando columnas...")
fecha = pd.to_datetime(df_ac['fecha'], errors='coerce').dt.date
adquiriente = df_ac['adquiriente'].fillna('').astype(str).str.strip()[:255]
factura = df_ac['factura'].fillna('').astype(str).str.strip()[:100]
emisor = df_ac['emisor'].fillna('').astype(str).str.strip()[:255]
nit_emisor = df_ac['nit emisor'].fillna('').astype(str).str.strip()[:20]
nit_pt = df_ac['nit. pt'].fillna('').astype(str).str.strip()[:20]
estado = df_ac['estado docto.'].fillna('').astype(str).str.strip()[:100]
descripcion = df_ac['descripción reclamo'].fillna('').astype(str).str.strip()
tipo_doc = df_ac['tipo documento'].fillna('').astype(str).str.strip()[:50]
cufe = df_ac['cufe'].fillna('').astype(str).str.strip()[:255]
valor = pd.to_numeric(df_ac['valor'].astype(str).str.replace(',', '.').str.replace('$', '').str.strip(), errors='coerce').fillna(0.0)
acuse_rec = df_ac['acuse recibido'].fillna('').astype(str).str.strip()[:50]
recibo = df_ac['recibo bien servicio'].fillna('').astype(str).str.strip()[:50]
aceptacion_exp = df_ac['aceptación expresa'].fillna('').astype(str).str.strip()[:50]
reclamo = df_ac['reclamo'].fillna('').astype(str).str.strip()[:50]
aceptacion_tac = df_ac['aceptación tacita'].fillna('').astype(str).str.strip()[:50]

# Clave = CUFE (único por factura)
clave = cufe

print(f"      Claves únicas: {clave.nunique():,}")

df_final = pd.DataFrame({
    'fecha': fecha,
    'adquiriente': adquiriente,
    'factura': factura,
    'emisor': emisor,
    'nit_emisor': nit_emisor,
    'nit_pt': nit_pt,
    'estado_docto': estado,
    'descripcion_reclamo': descripcion,
    'tipo_documento': tipo_doc,
    'cufe': cufe,
    'valor': valor,
    'acuse_recibido': acuse_rec,
    'recibo_bien_servicio': recibo,
    'aceptacion_expresa': aceptacion_exp,
    'reclamo': reclamo,
    'aceptacion_tacita': aceptacion_tac,
    'clave_acuse': clave
})

antes = len(df_final)
df_final = df_final.drop_duplicates(subset=['clave_acuse'], keep='first')
print(f"      Duplicados eliminados: {antes - len(df_final):,}")
print(f"      Registros finales: {len(df_final):,}")

print("[4/5] Limpiando tabla...")
cursor.execute("DELETE FROM acuses")
print(f"      Eliminados: {cursor.rowcount}")

print("[5/5] Insertando...")
buffer = io.StringIO()
df_final.to_csv(buffer, sep='\t', header=False, index=False, na_rep='')
buffer.seek(0)

cursor.copy_from(buffer, 'acuses', columns=list(df_final.columns), sep='\t')
conn.commit()

cursor.execute("SELECT COUNT(*) FROM acuses")
count_ac = cursor.fetchone()[0]
print(f"      [COMPLETADO] {count_ac:,} registros")

cursor.execute("SELECT nit_emisor, factura, valor FROM acuses LIMIT 5")
print("\n      Muestra:")
for r in cursor.fetchall():
    print(f"        {r[0]} | {r[1]} | ${r[2]:,.0f}")

# =============================================================================
# RESUMEN
# =============================================================================
print("\n" + "="*80)
print("RESUMEN FINAL")
print("="*80)

cursor.execute("SELECT COUNT(*) FROM dian")
count_dian = cursor.fetchone()[0]

print(f"\nDIAN:           {count_dian:,}")
print(f"ERP COMERCIAL:  {count_cm:,}")
print(f"ERP FINANCIERO: {count_fn:,}")
print(f"ACUSES:         {count_ac:,}")
print(f"\nTOTAL:          {count_dian + count_cm + count_fn + count_ac:,}")

print("\n" + "="*80)
print("[EXITO] CARGA COMPLETADA")
print("="*80)

cursor.close()
conn.close()
