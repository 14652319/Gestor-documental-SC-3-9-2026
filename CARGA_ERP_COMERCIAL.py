# -*- coding: utf-8 -*-
"""Carga OPTIMIZADA ERP COMERCIAL"""

import psycopg2
import pandas as pd
from datetime import date
import io

print("="*80)
print("CARGA ERP COMERCIAL")
print("="*80)

# 1. Conectar
print("\n[1/6] Conectando...")
conn = psycopg2.connect(
    host="localhost",
    database="gestor_documental",
    user="postgres",
    password="G3st0radm$2025."
)
conn.autocommit = False
cursor = conn.cursor()
print("      [OK]")

# 2. Leer Excel
print("\n[2/6] Leyendo ERP comercial 18 02 2026.xlsx...")
df = pd.read_excel(r"C:/Users/Usuario/Downloads/Ricardo/ERP comercial 18 02 2026.xlsx", dtype=str)
print(f"      [OK] {len(df):,} filas")

# 3. Normalizar columnas
print("\n[3/6] Normalizando...")
df.columns = [c.lower().strip() for c in df.columns]

# Detectar CUFE
cufe_col = None
for col in df.columns:
    if 'cufe' in col or 'cude' in col:
        cufe_col = col
        break
print(f"      CUFE: '{cufe_col}'")

# 4. Limpiar NIT vacios
df = df[df['nit proveedor'].notna()]
df = df[df['nit proveedor'] != '']
print(f"      [OK] {len(df):,} validos")

# 5. Preparar columnas
print("\n[4/6] Preparando datos...")

df['nit_proveedor'] = df['nit proveedor'].astype(str).str.strip()
df['prefijo'] = df['prefijo de factura'].fillna('').astype(str).str.strip()
df['numero_factura'] = df['numero de factura'].fillna('').astype(str).str.strip()
df['cufe_cude'] = df[cufe_col].fillna('') if cufe_col else ''

# Valor
df['valor'] = pd.to_numeric(
    df.get('importe', df.get('valor', 0)).astype(str).str.replace(',', '.'),
    errors='coerce'
).fillna(0.0)

# Clave
df['clave'] = df['nit_proveedor'] + df['prefijo'] + df['numero_factura']
df['clave_acuse'] = df['cufe_cude']

print(f"      [OK]")

# 6. Limpiar tabla
print("\n[5/6] Limpiando tabla...")
cursor.execute("DELETE FROM erp_comercial")
print(f"      [OK] Eliminados: {cursor.rowcount}")

# 7. COPY FROM
print("\n[6/6] Insertando con COPY FROM...")

columnas = [
    'nit_proveedor', 'prefijo', 'numero_factura',
    'valor', 'cufe_cude', 'clave', 'clave_acuse'
]

buffer = io.StringIO()
df[columnas].to_csv(buffer, sep='\t', header=False, index=False)
buffer.seek(0)

cursor.copy_from(buffer, 'erp_comercial', columns=columnas, sep='\t')
print(f"      [OK]")

# COMMIT
print("\nCOMMIT...")
conn.commit()
print("      [OK]")

# Verificar
cursor.execute("SELECT COUNT(*) FROM erp_comercial")
count = cursor.fetchone()[0]
print(f"\n[COMPLETADO] {count:,} registros en ERP_COMERCIAL")

cursor.close()
conn.close()
print("="*80)
