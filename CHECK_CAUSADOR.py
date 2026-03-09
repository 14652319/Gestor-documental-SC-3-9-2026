import os; from dotenv import load_dotenv; load_dotenv()
import psycopg2
conn = psycopg2.connect(os.environ['DATABASE_URL']); cur = conn.cursor()

print('=== erp_comercial: co, usuario, nro_doc, doc_causado_por (5 filas) ===')
cur.execute("SELECT co, usuario_creacion, nro_documento, doc_causado_por FROM erp_comercial WHERE doc_causado_por IS NOT NULL AND doc_causado_por != '' LIMIT 5")
for r in cur.fetchall(): print(r)

print()
print('=== maestro_dian_vs_erp: modulo, doc_causado_por (causadas, 5 filas) ===')
cur.execute("SELECT modulo, doc_causado_por FROM maestro_dian_vs_erp WHERE modulo IS NOT NULL AND modulo != '' AND doc_causado_por IS NOT NULL AND doc_causado_por != '' LIMIT 5")
for r in cur.fetchall(): print(r)

conn.close()
