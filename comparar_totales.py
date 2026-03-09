import psycopg2
conn=psycopg2.connect(dbname='gestor_documental',user='postgres',password='G3st0radm$2025.',host='localhost')
c=conn.cursor()
c.execute('SELECT COUNT(*) FROM maestro_dian_vs_erp')
print(f"Total MAESTRO: {c.fetchone()[0]:,}")
c.execute('SELECT COUNT(*) FROM dian')
print(f"Total DIAN:    {c.fetchone()[0]:,}")
conn.close()
