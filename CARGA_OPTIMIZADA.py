# -*- coding: utf-8 -*-
"""Carga OPTIMIZADA DIAN - vectorizado con pandas"""

import psycopg2
import pandas as pd
from datetime import date
import io

print("="*80)
print("CARGA OPTIM IZADA DIAN - Vectorizado")
print("="*80)

# 1. Conectar
print("\n[1/7] Conectando...")
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
print("\n[2/7] Leyendo Dian.xlsx (esto toma 30-60 seg)...")
df = pd.read_excel(r"C:/Users/Usuario/Downloads/Ricardo/Dian.xlsx", dtype=str)
print(f"      [OK] {len(df):,} filas")

# 3. Normalizar columnas
print("\n[3/7] Normalizando columnas...")
df.columns = [c.lower().strip() for c in df.columns]

# Detectar CUFE
cufe_col = None
for col in df.columns:
    if 'cufe' in col or 'cude' in col:
        cufe_col = col
        break
print(f"      [OK] CUFE: '{cufe_col}'")

# 4. Limpiar NIT vacios
print("\n[4/7] Limpiando datos...")
df = df[df['nit emisor'].notna()]
df = df[df['nit emisor'] != '']
print(f"      [OK] {len(df):,} registros validos")

# 5. Preparar columnas (VECTORIZADO - rapido)
print("\n[5/7] Preparando datos...")

# Columnas simples
df['nit_emisor'] = df['nit emisor'].astype(str).str.strip()
df['nombre_emisor'] = df.get('nombre  emisor', df.get('nombre emisor', '')).astype(str).str.strip().str[:255]
df['prefijo'] = df['prefijo'].fillna('').astype(str).str.strip()
df['folio'] = df['folio'].fillna('').astype(str).str.strip()
df['cufe_cude'] = df[cufe_col].fillna('') if cufe_col else ''

# Valor total (convertir a float)
df['total'] = pd.to_numeric(
    df.get('valor total', df.get('total', 0)).astype(str).str.replace(',', '.'),
    errors='coerce'
).fillna(0.0)

# Columnas fijas
df['fecha_emision'] = date.today().isoformat()
df['tipo_documento'] = 'Factura Electronica'
df['forma_pago'] = '2'
df['tipo_tercero'] = 'Externo'
df['n_dias'] = '0'
df['modulo'] = 'DIAN'

# Clave
df['clave'] = df['nit_emisor'] + df['prefijo'] + df['folio']
df['clave_acuse'] = df['cufe_cude']

print(f"      [OK]")

# 6. Limpiar tabla
print("\n[6/7] Limpiando tabla dian...")
cursor.execute("DELETE FROM dian")
print(f"      [OK] Eliminados: {cursor.rowcount}")

# 7. COPY FROM con to_csv (super rapido)
print("\n[7/7] Insertando con COPY FROM...")

# Seleccionar columnas en orden
columnas = [
    'nit_emisor', 'nombre_emisor', 'fecha_emision',
    'prefijo', 'folio', 'total', 'tipo_documento', 'cufe_cude',
    'forma_pago', 'clave', 'clave_acuse', 'tipo_tercero', 'n_dias', 'modulo'
]

# Convertir a TSV en memoria (muy rapido)
buffer = io.StringIO()
df[columnas].to_csv(buffer, sep='\t', header=False, index=False)
buffer.seek(0)

# COPY FROM
cursor.copy_from(buffer, 'dian', columns=columnas, sep='\t')
print(f"      [OK]")

# COMMIT
print("\nHaciendo COMMIT...")
conn.commit()
print("      [OK]")

# Verificar
print("\nVerificando...")
cursor.execute("SELECT COUNT(*) FROM dian")
count = cursor.fetchone()[0]
print(f"      Total: {count:,} registros")

if count > 0:
    cursor.execute("""
        SELECT nit_emisor, prefijo, folio, LENGTH(cufe_cude)
        FROM dian ORDER BY id LIMIT 3
    """)
    print("\nPrimeros 3:")
    for row in cursor.fetchall():
        print(f"  - {row[0]} {row[1]}-{row[2]} (CUFE len={row[3]})")

cursor.close()
conn.close()

print("\n" + "="*80)
print(f"[COMPLETADO] {count:,} registros en DIAN")
print("="*80)
