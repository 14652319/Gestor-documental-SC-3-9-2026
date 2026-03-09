import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="gestor_documental",
    user="postgres",
    password="G3st0radm$2025."
)
cursor = conn.cursor()

print("\nConteo de registros:")
print("-" * 40)

cursor.execute("SELECT COUNT(*) FROM dian")
print(f"DIAN:          {cursor.fetchone()[0]:,}")

cursor.execute("SELECT COUNT(*) FROM erp_comercial")
print(f"ERP COMERCIAL: {cursor.fetchone()[0]:,}")

cursor.execute("SELECT COUNT(*) FROM erp_financiero")
print(f"ERP FINANCIERO: {cursor.fetchone()[0]:,}")

cursor.execute("SELECT COUNT(*) FROM acuses")
print(f"ACUSES:        {cursor.fetchone()[0]:,}")

print("-" * 40)
conn.close()
