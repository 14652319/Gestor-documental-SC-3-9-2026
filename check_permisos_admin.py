import psycopg2

conn = psycopg2.connect(
    dbname='gestor_documental',
    user='postgres',
    password='123456',
    host='localhost'
)

cur = conn.cursor()

print("=" * 80)
print("PERMISOS DE GESTION_USUARIOS PARA USUARIO 14652319 (ID: 22)")
print("=" * 80)

cur.execute("""
    SELECT modulo, accion, permitido 
    FROM permisos_usuarios 
    WHERE usuario_id = 22 AND modulo = 'gestion_usuarios' 
    ORDER BY accion
""")

rows = cur.fetchall()
print(f"\nTotal de permisos en gestion_usuarios: {len(rows)}")

activos = [r for r in rows if r[2]]
inactivos = [r for r in rows if not r[2]]

print(f"Activos (TRUE): {len(activos)}")
print(f"Inactivos (FALSE): {len(inactivos)}")

if activos:
    print("\n✅ PERMISOS ACTIVOS:")
    for r in activos:
        print(f"   {r[0]}.{r[1]}")

print("\n" + "=" * 80)
print("VERIFICAR ACCESO AL MÓDULO ADMIN")
print("=" * 80)

cur.execute("""
    SELECT permitido 
    FROM permisos_usuarios 
    WHERE usuario_id = 22 
      AND modulo = 'gestion_usuarios' 
      AND accion = 'acceder_modulo'
""")

row = cur.fetchone()
if row:
    print(f"gestion_usuarios.acceder_modulo: {'✅ TRUE (TIENE ACCESO)' if row[0] else '❌ FALSE (SIN ACCESO)'}")
else:
    print("⚠️ NO hay registro para gestion_usuarios.acceder_modulo")

conn.close()
