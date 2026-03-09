"""Ver columnas de erp_comercial"""
import psycopg2

conn = psycopg2.connect(
    dbname='gestor_documental',
    user='postgres',
    password='G3st0radm$2025.',
    host='localhost'
)
cursor = conn.cursor()

cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name='erp_comercial'
    ORDER BY ordinal_position
""")

print("\n📋 COLUMNAS DE ERP_COMERCIAL:")
print("="*60)
for row in cursor.fetchall():
    print(f"  {row[0]:30} {row[1]}")

cursor.close()
conn.close()
