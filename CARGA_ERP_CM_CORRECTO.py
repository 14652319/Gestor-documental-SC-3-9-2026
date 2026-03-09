# -*- coding: utf-8 -*-
"""Carga ERP COMERCIAL con nombres correctos de columna"""

import psycopg2
import pandas as pd
from datetime import date, datetime
import io

print("="*80)
print("CARGA ERP COMERCIAL - Nombres correctos")
print("="*80)

def extraer_prefijo(docto):
    """Extraer prefijo antes del guion"""
    if not docto or pd.isna(docto):
        return ''
    docto_str = str(docto).strip()
    if '-' in docto_str:
        return docto_str.split('-')[0].strip()
    return docto_str

def extraer_folio(docto):
    """Extraer folio despues del guion"""
    if not docto or pd.isna(docto):
        return ''
    docto_str = str(docto).strip()
    if '-' in docto_str:
        return docto_str.split('-')[1].strip()
    return docto_str

def ultimos_8_sin_ceros(folio):
    """Ultimos 8 digitos sin ceros iniciales"""
    if not folio or folio == '':
        return ''
    folio_str = str(folio).strip().lstrip('0')
    return folio_str[-8:] if len(folio_str) > 8 else folio_str

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
print("\n[2/7] Leyendo ERP comercial 18 02 2026.xlsx...")
df = pd.read_excel(r"C:/Users/Usuario/Downloads/Ricardo/ERP comercial 18 02 2026.xlsx", dtype=str)
print(f"      [OK] {len(df):,} filas")
print(f"      Columnas: {list(df.columns)[:5]}...")

# 3. Normalizar columnas
print("\n[3/7] Preparando datos...")

# Columnas del Excel -> Tabla Postgres
# Proveedor -> proveedor
# Razon social proveedor -> razon_social_proveedor
# Fecha docto. prov. -> fecha_docto_prov
# Docto. proveedor -> docto_proveedor
# Valor bruto -> valor_bruto
# Valor imptos -> valor_imptos
# C.O. -> co
# Usuario creacion -> usuario_creacion
# Clase docto. -> clase_docto
# Nro documento -> nro_documento

df['proveedor'] = df['Proveedor'].fillna('').astype(str).str.strip()
df['razon_social_proveedor'] = df['Razón social proveedor'].fillna('').astype(str).str.strip()[:255]
df['docto_proveedor'] = df['Docto. proveedor'].fillna('').astype(str).str.strip()
df['co'] = df['C.O.'].fillna('').astype(str).str.strip()
df['nro_documento'] = df['Nro documento'].fillna('').astype(str).str.strip()
df['usuario_creacion'] = df['Usuario creación'].fillna('').astype(str).str.strip()
df['clase_docto'] = df['Clase docto.'].fillna('').astype(str).str.strip()

# Fecha
def parse_fecha(f):
    if pd.isna(f) or f == '':
        return None
    try:
        if isinstance(f, str):
            return datetime.strptime(f, '%d/%m/%Y').date()
        return f.date() if hasattr(f, 'date') else f
    except:
        return None

df['fecha_docto_prov'] = df['Fecha docto. prov.'].apply(parse_fecha)

# Valores
df['valor_bruto'] = pd.to_numeric(
    df['Valor bruto'].astype(str).str.replace('.', '').str.replace(',', '.'),
    errors='coerce'
).fillna(0.0)

df['valor_imptos'] = pd.to_numeric(
    df['Valor imptos'].astype(str).str.replace('.', '').str.replace(',', '.'),
    errors='coerce'
).fillna(0.0)

# Calcular prefijo, folio, clave
df['prefijo'] = df['docto_proveedor'].apply(extraer_prefijo)
folio_completo = df['docto_proveedor'].apply(extraer_folio)
df['folio'] = folio_completo.apply(ultimos_8_sin_ceros)
df['clave_erp_comercial'] = df['proveedor'] + df['prefijo'] + folio_completo
df['doc_causado_por'] = df['co'] + ' - ' + df['usuario_creacion'] + ' - ' + df['nro_documento']
df['modulo'] = 'Comercial'

print(f"      [OK]")

# 4. Filtrar sin proveedor
print("\n[4/7] Filtrando registros validos...")
df = df[df['proveedor'] != '']
print(f"      Validos: {len(df):,}")

# Eliminar duplicados por clave
inicial = len(df)
df = df.drop_duplicates(subset=['clave_erp_comercial'], keep='first')
print(f"      Sin duplicados: {len(df):,} (eliminados {inicial - len(df):,})")

# 5. Limpiar tabla
print("\n[5/7] Limpiando tabla erp_comercial...")
cursor.execute("DELETE FROM erp_comercial")
print(f"      [OK] Eliminados: {cursor.rowcount}")

# 6. COPY FROM con nombres correctos
print("\n[6/7] Insertando con COPY FROM...")

columnas = (
    'proveedor', 'razon_social_proveedor', 'fecha_docto_prov', 'docto_proveedor',
    'valor_bruto', 'valor_imptos', 'co', 'usuario_creacion', 'clase_docto',
    'nro_documento', 'prefijo', 'folio', 'clave_erp_comercial', 'doc_causado_por', 'modulo'
)

# Convertir a TSV
buffer = io.StringIO()
df[[
    'proveedor', 'razon_social_proveedor', 'fecha_docto_prov', 'docto_proveedor',
    'valor_bruto', 'valor_imptos', 'co', 'usuario_creacion', 'clase_docto',
    'nro_documento', 'prefijo', 'folio', 'clave_erp_comercial', 'doc_causado_por', 'modulo'
]].to_csv(buffer, sep='\t', header=False, index=False)
buffer.seek(0)

cursor.copy_from(buffer, 'erp_comercial', columns=columnas, sep='\t', null='')
print(f"      [OK]")

# 7. COMMIT
print("\n[7/7] Haciendo COMMIT...")
conn.commit()
print("      [OK]")

# Verificar
cursor.execute("SELECT COUNT(*) FROM erp_comercial")
count = cursor.fetchone()[0]
print(f"\n[COMPLETADO] {count:,} registros en ERP_COMERCIAL")

cursor.close()
conn.close()
print("="*80)
