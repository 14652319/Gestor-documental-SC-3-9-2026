import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="gestor_documental",
    user="postgres",
    password="G3st0radm$2025."
)
cursor = conn.cursor()

print("\nESTRUCTURA DE TABLAS:")
print("="*80)

# ERP COMERCIAL
cursor.execute("""
    SELECT column_name, data_type, character_maximum_length
    FROM information_schema.columns
    WHERE table_name='erp_comercial'
    ORDER BY ordinal_position
""")
print("\nERP_COMERCIAL:")
for row in cursor.fetchall():
    col_type = f"{row[1]}({row[2]})" if row[2] else row[1]
    print(f"  - {row[0]}: {col_type}")

# ERP FINANCIERO
cursor.execute("""
    SELECT column_name, data_type, character_maximum_length
    FROM information_schema.columns
    WHERE table_name='erp_financiero'
    ORDER BY ordinal_position
""")
print("\nERP_FINANCIERO:")
for row in cursor.fetchall():
    col_type = f"{row[1]}({row[2]})" if row[2] else row[1]
    print(f"  - {row[0]}: {col_type}")

# ACUSES
cursor.execute("""
    SELECT column_name, data_type, character_maximum_length
    FROM information_schema.columns
    WHERE table_name='acuses'
    ORDER BY ordinal_position
""")
print("\nACUSES:")
for row in cursor.fetchall():
    col_type = f"{row[1]}({row[2]})" if row[2] else row[1]
    print(f"  - {row[0]}: {col_type}")

print("\n" + "="*80)
conn.close()
