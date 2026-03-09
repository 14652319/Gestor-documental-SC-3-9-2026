"""
Limpia la tabla dian:
1. Corrige forma_pago: '1'/'1.0' → 'Contado', '2'/'2.0' → 'Crédito'
2. Elimina registros con tipos de documento excluidos
"""
from dotenv import load_dotenv
load_dotenv()

import os
import psycopg2

conn = psycopg2.connect(os.environ['DATABASE_URL'])
conn.autocommit = False
cur = conn.cursor()

print("=== LIMPIEZA TABLA dian ===\n")

# 1. Contar antes
cur.execute("SELECT COUNT(*) FROM dian")
total_antes = cur.fetchone()[0]
print(f"Total antes: {total_antes:,}")

# 2. Corregir forma_pago
cur.execute("UPDATE dian SET forma_pago = 'Contado' WHERE TRIM(forma_pago) IN ('1', '1.0')")
n_contado = cur.rowcount
print(f"  forma_pago → 'Contado': {n_contado:,}")

cur.execute("UPDATE dian SET forma_pago = 'Crédito' WHERE TRIM(forma_pago) IN ('2', '2.0')")
n_credito = cur.rowcount
print(f"  forma_pago → 'Crédito': {n_credito:,}")

# 3. Eliminar tipos excluidos
TIPOS_EXCLUIDOS = (
    'tipo de documento',
    'application response',
    'documento soporte con no obligados',
    'nota de ajuste del documento soporte',
)
placeholders = ','.join(['%s'] * len(TIPOS_EXCLUIDOS))
cur.execute(
    f"DELETE FROM dian WHERE LOWER(TRIM(tipo_documento)) IN ({placeholders})",
    TIPOS_EXCLUIDOS
)
n_eliminados = cur.rowcount
print(f"  Eliminados (tipos excluidos): {n_eliminados:,}")

conn.commit()

# 4. Verificar resultado
cur.execute("SELECT COUNT(*) FROM dian")
total_despues = cur.fetchone()[0]
print(f"\nTotal después: {total_despues:,}")

cur.execute("SELECT forma_pago, COUNT(*) FROM dian GROUP BY forma_pago ORDER BY 2 DESC")
print("\nDistribución forma_pago:")
for row in cur.fetchall():
    print(f"  {str(row[0]):20} : {row[1]:,}")

cur.execute("""
    SELECT tipo_documento, COUNT(*) 
    FROM dian 
    GROUP BY tipo_documento 
    ORDER BY 2 DESC 
    LIMIT 15
""")
print("\nTop tipos_documento:")
for row in cur.fetchall():
    print(f"  {str(row[0])[:50]:50} : {row[1]:,}")

cur.close()
conn.close()
print("\n✅ Limpieza completada.")
