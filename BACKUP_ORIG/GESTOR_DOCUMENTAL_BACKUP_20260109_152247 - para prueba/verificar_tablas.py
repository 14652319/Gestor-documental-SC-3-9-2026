# -*- coding: utf-8 -*-
import psycopg2

conn = psycopg2.connect(
    dbname='gestor_documental',
    user='gestor_user',
    password='Gestor2024$',
    host='localhost'
)

cur = conn.cursor()

# Verificar tablas
cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'archivos_procesados')")
existe_archivos = cur.fetchone()[0]

cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'configuracion_rutas_carga')")
existe_config = cur.fetchone()[0]

print(f"archivos_procesados: {existe_archivos}")
print(f"configuracion_rutas_carga: {existe_config}")

cur.close()
conn.close()
