import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'database': 'gestor_documental',
    'user': 'postgres',
    'password': 'G3st0radm$2025.'
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

print("\n" + "="*60)
print("CONTEOS ACTUALES - " + str(__import__('datetime').datetime.now().strftime('%H:%M:%S')))
print("="*60)

cursor.execute("SELECT COUNT(*) FROM dian")
print(f"DIAN:           {cursor.fetchone()[0]:,}")

cursor.execute("SELECT COUNT(*) FROM erp_comercial")
print(f"ERP COMERCIAL:  {cursor.fetchone()[0]:,}")

cursor.execute("SELECT COUNT(*) FROM erp_financiero")
print(f"ERP FINANCIERO: {cursor.fetchone()[0]:,}")

cursor.execute("SELECT COUNT(*) FROM acuses")
print(f"ACUSES:         {cursor.fetchone()[0]:,}")

print("="*60)

cursor.close()
conn.close()
