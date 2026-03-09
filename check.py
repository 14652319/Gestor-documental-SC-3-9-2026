import psycopg2
from datetime import datetime

conn = psycopg2.connect(host='localhost', database='gestor_documental', user='postgres', password='G3st0radm$2025.')
cursor = conn.cursor()

print(f"\n[{datetime.now().strftime('%H:%M:%S')}] CONTEOS:")
cursor.execute("SELECT COUNT(*) FROM dian"); print(f"  DIAN: {cursor.fetchone()[0]:,}")
cursor.execute("SELECT COUNT(*) FROM erp_comercial"); print(f"  ERP_COMERCIAL: {cursor.fetchone()[0]:,}")
cursor.execute("SELECT COUNT(*) FROM erp_financiero"); print(f"  ERP_FINANCIERO: {cursor.fetchone()[0]:,}")
cursor.execute("SELECT COUNT(*) FROM acuses"); print(f"  ACUSES: {cursor.fetchone()[0]:,}\n")

cursor.close()
conn.close()
