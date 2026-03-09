"""
Corrige el tamaño del campo tipo_documento en DIAN
"""

import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'gestor_documental',
    'user': 'postgres',
    'password': 'G3st0radm$2025.'
}

conn = psycopg2.connect(**DB_CONFIG)
conn.autocommit = True
cursor = conn.cursor()

print("Ampliando campo tipo_documento...")
cursor.execute("ALTER TABLE dian ALTER COLUMN tipo_documento TYPE VARCHAR(100);")
print("✅ Campo ampliado")

cursor.close()
conn.close()
