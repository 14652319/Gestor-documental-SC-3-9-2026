import psycopg2
conn = psycopg2.connect('postgresql://postgres:G3st0radm$2025.@localhost:5432/gestor_documental')
cur = conn.cursor()

# Simular exactamente la consulta que hace Flask en el login para usuario='admin'
print("=== Consulta 1: usuario='admin' OR lower(correo)='admin' (sin ORDER BY, como en app.py) ===")
cur.execute("""
    SELECT id, usuario, correo, rol, activo 
    FROM usuarios 
    WHERE usuario = 'admin' OR LOWER(correo) = 'admin'
    LIMIT 1
""")
row = cur.fetchone()
print(f"  Resultado .first(): {row}")

print("\n=== Todos los que matchean 'admin' ===")
cur.execute("""
    SELECT id, usuario, correo, rol, activo 
    FROM usuarios 
    WHERE LOWER(usuario) = 'admin' OR LOWER(correo) = 'admin'
    ORDER BY id
""")
rows = cur.fetchall()
for r in rows:
    print(f"  ID={r[0]}, usuario='{r[1]}', correo='{r[2]}', rol='{r[3]}', activo={r[4]}")

print("\n=== Revisando correos de TODOS los usuarios con usuario LIKE admin ===")
cur.execute("""
    SELECT id, usuario, correo, rol, activo 
    FROM usuarios 
    WHERE LOWER(usuario) LIKE '%admin%'
    ORDER BY id
""")
rows = cur.fetchall()
for r in rows:
    print(f"  ID={r[0]}, usuario='{r[1]}', correo='{r[2]}', rol='{r[3]}', activo={r[4]}")

conn.close()
