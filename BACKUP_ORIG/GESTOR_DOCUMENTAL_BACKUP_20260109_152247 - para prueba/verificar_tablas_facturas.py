"""
Verificar qué tablas de facturas recibidas existen
"""
import psycopg2
from dotenv import load_dotenv
import os
from urllib.parse import urlparse

load_dotenv()

database_url = os.getenv('DATABASE_URL')
result = urlparse(database_url)

conn = psycopg2.connect(
    database=result.path[1:],
    user=result.username,
    password=result.password,
    host=result.hostname,
    port=result.port
)

cur = conn.cursor()

print("=" * 100)
print("TABLAS RELACIONADAS CON FACTURAS RECIBIDAS")
print("=" * 100)
print()

# Buscar todas las tablas que contengan "factura" y "recibida"
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name LIKE '%factura%recibida%'
    ORDER BY table_name
""")

tablas = cur.fetchall()

if tablas:
    print(f"📋 Tablas encontradas: {len(tablas)}\n")
    
    for tabla in tablas:
        nombre_tabla = tabla[0]
        print(f"{'=' * 100}")
        print(f"TABLA: {nombre_tabla}")
        print(f"{'=' * 100}")
        
        # Contar registros
        cur.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
        total = cur.fetchone()[0]
        print(f"📊 Total registros: {total:,}")
        
        # Obtener columnas
        cur.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{nombre_tabla}'
            ORDER BY ordinal_position
        """)
        columnas = cur.fetchall()
        
        print(f"\n📋 Columnas ({len(columnas)}):")
        for col in columnas[:10]:  # Primeras 10
            print(f"   - {col[0]} ({col[1]})")
        
        if len(columnas) > 10:
            print(f"   ... y {len(columnas) - 10} más")
        
        print()

else:
    print("❌ No se encontraron tablas")

cur.close()
conn.close()

print("=" * 100)
