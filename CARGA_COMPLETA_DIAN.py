# -*- coding: utf-8 -*-
"""Carga COMPLETA de archivo DIAN (66k registros) usando COPY FROM"""

import psycopg2
import pandas as pd
from datetime import date
import io

print("="*80)
print("CARGA COMPLETA - ARCHIVO DIAN (66,276 registros)")
print("="*80)

# 1. Conectar
print("\n1. Conectando a PostgreSQL...")
conn = psycopg2.connect(
    host="localhost",
    database="gestor_documental",
    user="postgres",
    password="G3st0radm$2025."
)
conn.autocommit = False
cursor = conn.cursor()
print("   [OK] Conectado")

# 2. Leer archivo COMPLETO
print("\n2. Leyendo Dian.xlsx COMPLETO (esto toma ~30 segundos)...")
try:
    dian_path = r"C:/Users/Usuario/Downloads/Ricardo/Dian.xlsx"
    df = pd.read_excel(dian_path, dtype=str)
    print(f"   [OK] Leido: {len(df):,} filas")
except Exception as e:
    print(f"   [ERROR] {e}")
    conn.close()
    exit(1)

# 3. Normalizar columnas
df.columns = [c.lower().strip() for c in df.columns]

# Detectar CUFE
cufe_col = None
for col in df.columns:
    if 'cufe' in col or 'cude' in col:
        cufe_col = col
        break
print(f"   [OK] Columna CUFE: '{cufe_col}'")

# 4. Limpiar tabla
print("\n3. Limpiando tabla dian...")
cursor.execute("DELETE FROM dian")
deleted = cursor.rowcount
print(f"   [OK] Eliminados: {deleted} registros antiguos")

# 5. Preparar datos
print("\n4. Preparando datos para COPY FROM...")
registros = []
for _, row in df.iterrows():
    nit = str(row.get('nit emisor', '')).strip()
    if not nit or nit == 'nan':
        continue
        
    nombre = str(row.get('nombre  emisor', row.get('nombre emisor', ''))).strip()[:255]
    prefijo = str(row.get('prefijo', '')).strip()
    folio = str(row.get('folio', '')).strip()
    cufe = str(row.get(cufe_col, '')) if cufe_col else ''
    
    # Valor total
    valor = 0.0
    try:
        val_str = str(row.get('valor total', row.get('total', 0)))
        valor = float(val_str.replace(',', '.'))
    except:
        pass
    
    clave = f"{nit}{prefijo}{folio}"
    
    registros.append({
        'nit_emisor': nit,
        'nombre_emisor': nombre,
        'fecha_emision': date.today().isoformat(),
        'prefijo': prefijo,
        'folio': folio,
        'total': valor,
        'tipo_documento': 'Factura Electrónica',
        'cufe_cude': cufe,
        'forma_pago': '2',
        'clave': clave,
        'clave_acuse': cufe,
        'tipo_tercero': 'Externo',
        'n_dias': '0',
        'modulo': 'DIAN'
    })

print(f"   [OK] Preparados: {len(registros):,} registros validos")

# 6. Usar COPY FROM (método de routes.py)
print("\n5. Insertando con COPY FROM...")
try:
    # Crear buffer StringIO
    buffer = io.StringIO()
    for reg in registros:
        line = '\t'.join([
            str(reg['nit_emisor']),
            str(reg['nombre_emisor']),
            str(reg['fecha_emision']),
            str(reg['prefijo']),
            str(reg['folio']),
            str(reg['total']),
            str(reg['tipo_documento']),
            str(reg['cufe_cude']),
            str(reg['forma_pago']),
            str(reg['clave']),
            str(reg['clave_acuse']),
            str(reg['tipo_tercero']),
            str(reg['n_dias']),
            str(reg['modulo'])
        ])
        buffer.write(line + '\n')
    
    buffer.seek(0)  # Volver al inicio
    
    # COPY FROM
    cursor.copy_from(
        buffer,
        'dian',
        columns=(
            'nit_emisor', 'nombre_emisor', 'fecha_emision',
            'prefijo', 'folio', 'total', 'tipo_documento', 'cufe_cude',
            'forma_pago', 'clave', 'clave_acuse', 'tipo_tercero', 'n_dias', 'modulo'
        ),
        sep='\t'
    )
    print(f"   [OK] COPY FROM completado")
    
except Exception as e:
    print(f"   [ERROR] en COPY FROM: {e}")
    conn.rollback()
    conn.close()
    exit(1)

# 7. COMMIT
print("\n6. Haciendo COMMIT...")
try:
    conn.commit()
    print("   [OK] COMMIT exitoso")
except Exception as e:
    print(f"   [ERROR] en COMMIT: {e}")
    conn.rollback()
    conn.close()
    exit(1)

# 8. Verificar
print("\n7. Verificando resultado...")
cursor.execute("SELECT COUNT(*) FROM dian")
count = cursor.fetchone()[0]
print(f"   [INFO] Total en tabla DIAN: {count:,} registros")

if count > 0:
    cursor.execute("""
        SELECT nit_emisor, prefijo, folio, LENGTH(cufe_cude)
        FROM dian
        ORDER BY id
        LIMIT 5
    """)
    print("\n   Primeros 5 registros:")
    for row in cursor.fetchall():
        print(f"      • {row[0]} - {row[1]}-{row[2]} (CUFE len={row[3]})")

cursor.close()
conn.close()

print("\n" + "="*80)
print(f"[COMPLETADO] {count:,} registros insertados en tabla DIAN")
print("="*80)
