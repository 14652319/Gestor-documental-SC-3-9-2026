"""Verificar estados contables en tabla maestro"""
import psycopg2

conn = psycopg2.connect(
    dbname='gestor_documental',
    user='postgres',
    password='G3st0radm$2025.',
    host='localhost'
)
cursor = conn.cursor()

print("\n" + "="*80)
print("📊 ESTADOS CONTABLES EN MAESTRO (NIT 805013653)")
print("="*80 + "\n")

cursor.execute("""
    SELECT estado_contable, COUNT(*) as total
    FROM maestro_dian_vs_erp
    WHERE nit_emisor = '805013653'
    GROUP BY estado_contable
    ORDER BY total DESC
""")

for row in cursor.fetchall():
    estado, total = row
    print(f"  {estado:20} : {total:6,} registros")

print("\n" + "="*80)
cursor.close()
conn.close()
