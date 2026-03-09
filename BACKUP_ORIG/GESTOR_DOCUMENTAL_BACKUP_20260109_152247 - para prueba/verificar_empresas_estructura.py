import psycopg2
import sys

try:
    conn = psycopg2.connect(
        host='localhost',
        database='gestor_documental',
        user='postgres',
        password='Inicio2024*',
        options='-c client_encoding=UTF8'
    )
    
    cursor = conn.cursor()
    
    print("=== ESTRUCTURA TABLA EMPRESAS ===")
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'empresas'
        ORDER BY ordinal_position;
    """)
    
    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]} ({row[2]})")
    
    print("\n=== EMPRESAS REGISTRADAS ===")
    cursor.execute("SELECT id, sigla, nombre, activo FROM empresas LIMIT 10;")
    
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Sigla: {row[1]}, Nombre: {row[2]}, Activo: {row[3]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
