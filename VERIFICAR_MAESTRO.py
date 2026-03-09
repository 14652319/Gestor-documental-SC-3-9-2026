from dotenv import load_dotenv; load_dotenv()
import os, psycopg2

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
print("maestro_dian_vs_erp:", f"{cur.fetchone()[0]:,}")

cur.execute("SELECT forma_pago, COUNT(*) FROM maestro_dian_vs_erp GROUP BY forma_pago ORDER BY 2 DESC")
print("Distribucion forma_pago:")
for r in cur.fetchall():
    print(f"  {str(r[0]):20}: {r[1]:,}")

cur.execute("SELECT tipo_documento, COUNT(*) FROM maestro_dian_vs_erp GROUP BY tipo_documento ORDER BY 2 DESC LIMIT 10")
print("\nTop tipo_documento:")
for r in cur.fetchall():
    print(f"  {str(r[0])[:55]:55}: {r[1]:,}")

cur.close(); conn.close()
