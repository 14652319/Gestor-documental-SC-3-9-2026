import psycopg2

conn = psycopg2.connect(dbname='gestor_documental',user='gestor_user',password='Gestor2024$',host='localhost')
cur = conn.cursor()

tablas = ['dian', 'erp_comercial', 'erp_financiero', 'acuses', 'maestro_dian_vs_erp']

print("VERIFICACION DE TABLAS:")
print("-" * 60)

for tabla in tablas:
    cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)", (tabla,))
    existe = cur.fetchone()[0]
    
    if existe:
        cur.execute(f"SELECT COUNT(*) FROM {tabla}")
        count = cur.fetchone()[0]
        print(f"{tabla:25} EXISTE - {count:,} registros")
    else:
        print(f"{tabla:25} NO EXISTE")

print("-" * 60)
print("\nTODAS LAS TABLAS EN LA BASE DE DATOS:")
print("-" * 60)

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
todas = cur.fetchall()

for i, (t,) in enumerate(todas, 1):
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    count = cur.fetchone()[0]
    print(f"{i:2}. {t:35} {count:,} registros")

cur.close()
conn.close()
