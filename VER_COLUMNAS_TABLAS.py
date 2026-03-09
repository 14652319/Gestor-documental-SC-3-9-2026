from dotenv import load_dotenv; load_dotenv()
import os, psycopg2

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()

for tabla in ['erp_comercial', 'erp_financiero', 'acuses']:
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (tabla,))
    cols = cur.fetchall()
    print(f"\n=== {tabla.upper()} ({len(cols)} columnas) ===")
    for col, dtype in cols:
        print(f"  {col:35} {dtype}")

cur.close(); conn.close()
