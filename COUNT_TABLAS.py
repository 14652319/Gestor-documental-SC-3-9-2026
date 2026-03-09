from dotenv import load_dotenv; load_dotenv()
import os, psycopg2

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()

for tabla in ['dian', 'erp_comercial', 'erp_financiero', 'acuses', 'maestro_dian_vs_erp']:
    cur.execute(f"SELECT COUNT(*) FROM {tabla}")
    print(f"  {tabla:30}: {cur.fetchone()[0]:,}")

cur.close(); conn.close()
