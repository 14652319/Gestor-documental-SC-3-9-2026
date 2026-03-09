"""Verifica el estado de todas las tablas DIAN."""
import sys, os
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dotenv import load_dotenv; load_dotenv()
import psycopg2
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
for t in ['erp_comercial', 'erp_financiero', 'dian', 'acuses', 'maestro_dian_vs_erp']:
    cur.execute(f'SELECT COUNT(*) FROM {t}')
    print(f'{t}: {cur.fetchone()[0]:,}')
cur.execute('SELECT forma_pago, COUNT(*) FROM maestro_dian_vs_erp GROUP BY forma_pago ORDER BY 2 DESC')
print('Maestro por forma_pago:', cur.fetchall())
conn.close()
print("OK")
