"""Ver primeras filas de tabla DIAN con TODAS las columnas"""
import psycopg2

conn = psycopg2.connect(
    dbname='gestor_documental',
    user='postgres',
    password='G3st0radm$2025.',
    host='localhost'
)
cursor = conn.cursor()

# Ver columnas de la tabla
cursor.execute("""
    SELECT column_name, data_type, character_maximum_length
    FROM information_schema.columns
    WHERE table_name='dian'
    ORDER BY ordinal_position
""")

print("\n" + "="*80)
print("📋 COLUMNAS DE LA TABLA DIAN")
print("="*80 + "\n")

columnas = []
for row in cursor.fetchall():
    col_name, data_type, max_len = row
    columnas.append(col_name)
    if max_len:
        print(f"  {col_name:30} {data_type}({max_len})")
    else:
        print(f"  {col_name:30} {data_type}")

# Ver datos de primeras 3 filas CON prefijo y folio
print("\n" + "="*80)
print("📊 PRIMERAS 3 FILAS DE DIAN")
print("="*80 + "\n")

cursor.execute("""
    SELECT id, nit_emisor, nombre_emisor, prefijo, folio, clave, fecha_emision, total
    FROM dian
    LIMIT 3
""")

for row in cursor.fetchall():
    print(f"\n  ID: {row[0]}")
    print(f"  NIT: {row[1]}")
    print(f"  Nombre: {row[2]}")
    print(f"  Prefijo: '{row[3]}'")  # Lo que debería tener valor
    print(f"  Folio: '{row[4]}'")    # Lo que debería tener valor
    print(f"  Clave: '{row[5]}'")
    print(f"  Fecha: {row[6]}")
    print(f"  Total: {row[7]}")

cursor.close()
conn.close()
