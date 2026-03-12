import psycopg2
conn = psycopg2.connect('postgresql://postgres:G3st0radm$2025.@localhost:5432/gestor_documental')
cur = conn.cursor()

# Ver permisos sagrilaft del usuario admin (id=23)
cur.execute("SELECT modulo, accion, permitido FROM permisos_usuarios WHERE usuario_id=23 AND modulo='sagrilaft'")
rows = cur.fetchall()
print("=== Permisos sagrilaft de admin (ID=23) ===")
for r in rows:
    print(f"  modulo={r[0]}, accion={r[1]}, permitido={r[2]}")

if not rows:
    print("  (ninguno - por eso no puede acceder)")

# Agregar todos los permisos sagrilaft para admin
permisos = [
    'acceder_modulo',
    'listar_radicados',
    'revisar_documentos',
    'actualizar_estado_documento',
    'actualizar_estado_radicado',
    'exportar_radicados',
    'descargar_documentos',
]
for accion in permisos:
    cur.execute("""
        INSERT INTO permisos_usuarios (usuario_id, modulo, accion, permitido)
        VALUES (23, 'sagrilaft', %s, true)
        ON CONFLICT (usuario_id, modulo, accion) DO UPDATE SET permitido=true
    """, (accion,))

conn.commit()
print(f"\n>>> {len(permisos)} permisos SAGRILAFT asignados al admin")

# Verificar resultado
cur.execute("SELECT modulo, accion, permitido FROM permisos_usuarios WHERE usuario_id=23 AND modulo='sagrilaft'")
rows = cur.fetchall()
print("\n=== Estado final ===")
for r in rows:
    print(f"  {r[1]}: {r[2]}")

conn.close()
