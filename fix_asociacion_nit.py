# -*- coding: utf-8 -*-
"""Verificar asociación NIT-Usuario sin importar app.py"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='gestor_documental',
    user='postgres',
    password='Inicio2024*',
    client_encoding='utf8'
)

cur = conn.cursor()

# Buscar usuario admin
cur.execute("""
    SELECT u.id, u.usuario, u.tercero_id, u.rol, u.activo, u.correo
    FROM usuarios u
    WHERE LOWER(u.usuario) = 'admin'
""")

user_row = cur.fetchone()

if not user_row:
    print("❌ No se encontró usuario admin")
    exit(1)

user_id, usuario, tercero_id, rol, activo, correo = user_row

print(f"\n{'='*60}")
print(f"VERIFICACIÓN DE ASOCIACIÓN NIT-USUARIO")
print(f"{'='*60}\n")

print(f"Usuario admin:")
print(f"  ID: {user_id}")
print(f"  Usuario: {usuario}")
print(f"  Tercero_ID: {tercero_id}")
print(f"  Rol: {rol}")
print(f"  Activo: {activo}")
print(f"  Correo: {correo}")

# Buscar tercero asociado
cur.execute("SELECT id, nit, razon_social FROM terceros WHERE id = %s", (tercero_id,))
tercero_row = cur.fetchone()

if tercero_row:
    print(f"\nTercero asociado al usuario admin:")
    print(f"  ID: {tercero_row[0]}")
    print(f"  NIT: {tercero_row[1]}")
    print(f"  Razón Social: {tercero_row[2]}")
else:
    print(f"\n❌ No se encontró tercero con ID {tercero_id}")

# Buscar el NIT que estás intentando usar
nit_intentado = "805028041"
cur.execute("SELECT id, nit, razon_social FROM terceros WHERE nit = %s", (nit_intentado,))
tercero_intentado = cur.fetchone()

print(f"\n{'='*60}")
print(f"Verificación del NIT {nit_intentado}:")
print(f"{'='*60}")

if tercero_intentado:
    print(f"  ID: {tercero_intentado[0]}")
    print(f"  NIT: {tercero_intentado[1]}")
    print(f"  Razón Social: {tercero_intentado[2]}")
    
    if tercero_intentado[0] == tercero_id:
        print(f"\n✅ EL NIT COINCIDE con el tercero del usuario admin")
    else:
        print(f"\n❌ EL NIT NO COINCIDE")
        print(f"   Tercero del usuario admin: ID {tercero_id}")
        print(f"   Tercero del NIT ingresado: ID {tercero_intentado[0]}")
        print(f"\n🔧 SOLUCIÓN: Actualizar el tercero_id del usuario admin")
        print(f"   SQL: UPDATE usuarios SET tercero_id = {tercero_intentado[0]} WHERE id = {user_id};")
        
        respuesta = input(f"\n¿Quieres actualizar automáticamente? (s/n): ")
        if respuesta.lower() == 's':
            cur.execute("UPDATE usuarios SET tercero_id = %s WHERE id = %s", (tercero_intentado[0], user_id))
            conn.commit()
            print(f"\n✅ Usuario actualizado correctamente")
        else:
            print(f"\n❌ No se realizaron cambios")
else:
    print(f"❌ No existe tercero con NIT {nit_intentado}")

cur.close()
conn.close()
