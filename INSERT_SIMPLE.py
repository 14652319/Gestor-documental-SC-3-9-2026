# -*- coding: utf-8 -*-
"""Inserción simple y directa - 5 registros de prueba"""

import psycopg2
import pandas as pd
from datetime import date

print("="*80)
print("INSERCIÓN SIMPLE - 5 REGISTROS DE PRUEBA")
print("="*80)

# Conectar
print("\n1. Conectando...")
conn = psycopg2.connect(
    host="localhost",
    database="gestor_documental", 
    user="postgres",
    password="G3st0radm$2025."
)
conn.autocommit = False
cursor = conn.cursor()
print("   ✅ Conectado")

# Leer archivo DIAN (solo primeras 10 filas)
print("\n2. Leyendo Dian.xlsx (primeras 10 filas)...")
try:
    dian_path = r"C:/Users/Usuario/Downloads/Ricardo/Dian.xlsx"
    df = pd.read_excel(dian_path, nrows=10, dtype=str)
    print(f"   ✅ Leído: {len(df)} filas")
    print(f"   Columnas: {list(df.columns)[:5]}...")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    exit(1)

# Normalizar columnas
df.columns = [c.lower().strip() for c in df.columns]

# Detectar columna CUFE
cufe_col = None
for col in df.columns:
    if 'cufe' in col or 'cude' in col:
        cufe_col = col
        print(f"   ✅ CUFE: '{cufe_col}'")
        break

# Limpiar tabla
print("\n3. Limpiando tabla dian...")
cursor.execute("DELETE FROM dian")
print(f"   ✅ Limpiada")

# Insertar 5 registros
print("\n4. Insertando 5 registros...")
for idx, row in df.head(5).iterrows():
    nit = str(row.get('nit emisor', '')).strip()
    nombre = str(row.get('nombre  emisor', row.get('nombre emisor', ''))).strip()[:255]
    prefijo = str(row.get('prefijo', '')).strip()
    folio = str(row.get('folio', '')).strip()
    valor = 0.0
    try:
        valor = float(str(row.get('valor total', row.get('total', 0))).replace(',', '.'))
    except:
        pass
    
    cufe = str(row.get(cufe_col, '')) if cufe_col else ''
    clave = f"{nit}{prefijo}{folio}"
    
    cursor.execute("""
        INSERT INTO dian (
            nit_emisor, nombre_emisor, fecha_emision,
            prefijo, folio, total, tipo_documento, cufe_cude,
            forma_pago, clave, clave_acuse, tipo_tercero, n_dias, modulo
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """, (
        nit, nombre, date.today(),
        prefijo, folio, valor, 'Factura Electrónica', cufe,
        '2', clave, cufe, 'Externo', 0, 'DIAN'
    ))
    
    print(f"   ✅ Registro {idx+1}: {nit} - {prefijo}-{folio}")

# COMMIT
print("\n5. Haciendo COMMIT...")
conn.commit()
print("   ✅ COMMIT exitoso")

# Verificar
print("\n6. Verificando...")
cursor.execute("SELECT COUNT(*) FROM dian")
count = cursor.fetchone()[0]
print(f"   📊 DIAN: {count} registros")

if count > 0:
    cursor.execute("""
        SELECT nit_emisor, prefijo, folio, LENGTH(cufe_cude)
        FROM dian LIMIT 3
    """)
    for row in cursor.fetchall():
        print(f"      • {row[0]} - {row[1]}-{row[2]} (CUFE len={row[3]})")

cursor.close()
conn.close()

print("\n" + "="*80)
print("✅ COMPLETADO")
print("="*80)
