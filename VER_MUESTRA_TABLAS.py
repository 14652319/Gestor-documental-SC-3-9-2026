from dotenv import load_dotenv; load_dotenv()
import os, psycopg2

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()

for tabla in ['erp_comercial', 'erp_financiero', 'acuses']:
    cur.execute(f"SELECT * FROM {tabla} LIMIT 2")
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    print(f"\n=== {tabla.upper()} - Primeros 2 registros ===")
    for row in rows:
        for col, val in zip(cols, row):
            print(f"  {col:30} = {repr(str(val))[:80]}")
        print()

cur.close(); conn.close()
