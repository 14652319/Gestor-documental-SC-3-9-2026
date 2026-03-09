import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='gestor_documental',
    user='postgres',
    password='G3st0radm$2025.'
)
conn.autocommit = True
cur = conn.cursor()

print("Truncando tablas...")
cur.execute('TRUNCATE TABLE erp_comercial, erp_financiero, dian RESTART IDENTITY CASCADE;')
print("✅ Tablas truncadas - listas para recargar")

cur.close()
conn.close()
