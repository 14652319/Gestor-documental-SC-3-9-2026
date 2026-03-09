#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Análisis de las 3 tablas de permisos
"""
import psycopg2
from psycopg2 import sql

def main():
    conn = psycopg2.connect(
        dbname='gestor_documental',
        user='postgres',
        password='123456',
        host='localhost'
    )
    cur = conn.cursor()
    
    print("=" * 100)
    print("🔍 ANÁLISIS DE LAS 3 TABLAS DE PERMISOS")
    print("=" * 100)
    
    # 1. Listar todas las tablas de permisos
    print("\n1️⃣ TABLAS DE PERMISOS EXISTENTES:")
    print("-" * 100)
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_name LIKE '%permiso%'
        ORDER BY table_name
    """)
    
    tablas = cur.fetchall()
    for t in tablas:
        cur.execute(f"SELECT COUNT(*) FROM {t[0]}")
        count = cur.fetchone()[0]
        print(f"   📁 {t[0]}: {count} registros")
    
    # 2. Estructura de permisos_modulos
    print("\n2️⃣ ESTRUCTURA DE permisos_modulos:")
    print("-" * 100)
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'permisos_modulos'
        ORDER BY ordinal_position
    """)
    
    columnas = cur.fetchall()
    for col in columnas:
        print(f"   - {col[0]} ({col[1]}) - NULL: {col[2]}")
    
    cur.execute("SELECT * FROM permisos_modulos LIMIT 5")
    rows = cur.fetchall()
    print(f"\n   Registros: {len(rows)}")
    if rows:
        print("   Primeros 5 registros:")
        for r in rows:
            print(f"     {r}")
    else:
        print("   ⚠️ TABLA VACÍA")
    
    # 3. Estructura de permisos_usuarios
    print("\n3️⃣ ESTRUCTURA DE permisos_usuarios:")
    print("-" * 100)
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'permisos_usuarios'
        ORDER BY ordinal_position
    """)
    
    columnas = cur.fetchall()
    for col in columnas:
        print(f"   - {col[0]} ({col[1]}) - NULL: {col[2]}")
    
    # 4. Verificar usuario 14652319 (ID 22)
    print("\n4️⃣ USUARIO 14652319:")
    print("-" * 100)
    cur.execute("""
        SELECT id, usuario, nit, activo, rol
        FROM usuarios
        WHERE usuario = '14652319'
    """)
    
    user = cur.fetchone()
    if user:
        print(f"   ID: {user[0]}")
        print(f"   Usuario: {user[1]}")
        print(f"   NIT: {user[2]}")
        print(f"   Activo: {user[3]}")
        print(f"   Rol: {user[4]}")
        usuario_id = user[0]
    else:
        print("   ❌ Usuario NO encontrado")
        conn.close()
        return
    
    # 5. Permisos del usuario 14652319 en permisos_usuarios
    print("\n5️⃣ PERMISOS EN permisos_usuarios PARA usuario_id=22:")
    print("-" * 100)
    
    cur.execute("""
        SELECT COUNT(*) as total,
               COUNT(*) FILTER (WHERE permitido = true) as activos,
               COUNT(*) FILTER (WHERE permitido = false) as inactivos
        FROM permisos_usuarios
        WHERE usuario_id = %s
    """, (usuario_id,))
    
    stats = cur.fetchone()
    print(f"   Total: {stats[0]}")
    print(f"   ✅ Activos (permitido=TRUE): {stats[1]}")
    print(f"   ❌ Inactivos (permitido=FALSE): {stats[2]}")
    
    # Mostrar permisos activos
    if stats[1] > 0:
        print("\n   📋 PERMISOS ACTIVOS:")
        cur.execute("""
            SELECT modulo, accion, permitido, fecha_asignacion
            FROM permisos_usuarios
            WHERE usuario_id = %s AND permitido = true
            ORDER BY modulo, accion
            LIMIT 10
        """, (usuario_id,))
        
        permisos = cur.fetchall()
        for p in permisos:
            print(f"     ✅ {p[0]}.{p[1]} (fecha: {p[3]})")
        
        if stats[1] > 10:
            print(f"     ... y {stats[1] - 10} permisos más")
    
    # 6. Verificar cómo se usa usuario_id en decoradores
    print("\n6️⃣ SIMULACIÓN DE QUERY DE DECORADORES:")
    print("-" * 100)
    print("   Los decoradores usan: session['usuario_id']")
    print(f"   Para usuario 14652319, usuario_id en sesión = {usuario_id}")
    print("\n   Query ejecutada por decoradores:")
    print("   SELECT permitido FROM permisos_usuarios")
    print("   WHERE usuario_id = :usuario_id AND modulo = :modulo AND accion = :accion")
    
    # Simular query
    modulos_prueba = [
        ('causaciones', 'acceder_modulo'),
        ('facturas_digitales', 'acceder_modulo'),
        ('gestion_usuarios', 'acceder_modulo')
    ]
    
    print("\n   Resultados de simulación:")
    for modulo, accion in modulos_prueba:
        cur.execute("""
            SELECT permitido 
            FROM permisos_usuarios 
            WHERE usuario_id = %s 
              AND modulo = %s 
              AND accion = %s
        """, (usuario_id, modulo, accion))
        
        row = cur.fetchone()
        if row:
            resultado = "✅ PERMITIDO" if row[0] else "❌ DENEGADO"
            print(f"     {modulo}.{accion}: {resultado}")
        else:
            print(f"     {modulo}.{accion}: ⚠️ NO REGISTRADO")
    
    # 7. Verificar datos en sesión durante login
    print("\n7️⃣ DATOS QUE SE GUARDAN EN SESIÓN (app.py línea 1177-1180):")
    print("-" * 100)
    print("   session['usuario_id'] = user.id  # ID de la tabla usuarios (22)")
    print("   session['usuario'] = user.usuario  # Código de usuario ('14652319')")
    print("   session['nit'] = working_nit  # NIT ('14652319')")
    print("   session['rol'] = user.rol  # Rol (externo/interno/admin)")
    
    # 8. Verificar tabla permisos_modulos (si existe y tiene datos)
    print("\n8️⃣ TABLA permisos_modulos:")
    print("-" * 100)
    try:
        cur.execute("SELECT COUNT(*) FROM permisos_modulos")
        count = cur.fetchone()[0]
        
        if count == 0:
            print("   ⚠️ TABLA VACÍA - Esta tabla NO se está usando")
            print("   ℹ️ El sistema usa permisos_usuarios para todo")
        else:
            print(f"   Registros: {count}")
            cur.execute("SELECT * FROM permisos_modulos LIMIT 5")
            rows = cur.fetchall()
            for r in rows:
                print(f"     {r}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 9. Verificar endpoint de actualización de permisos
    print("\n9️⃣ ENDPOINT /admin/usuarios-permisos/api/usuarios/<id>/permisos:")
    print("-" * 100)
    print("   Ruta: modules/admin/usuarios_permisos/routes.py")
    print("   Método: PUT")
    print("   Operación: UPDATE permisos_usuarios SET permitido = :valor")
    print("   WHERE usuario_id = :usuario_id AND modulo = :modulo AND accion = :accion")
    
    # 10. Verificar si hay registros recientes
    print("\n🔟 ÚLTIMAS ACTUALIZACIONES DE PERMISOS:")
    print("-" * 100)
    cur.execute("""
        SELECT modulo, accion, permitido, fecha_asignacion
        FROM permisos_usuarios
        WHERE usuario_id = %s
        ORDER BY fecha_asignacion DESC
        LIMIT 10
    """, (usuario_id,))
    
    ultimos = cur.fetchall()
    for u in ultimos:
        estado = "✅ TRUE" if u[2] else "❌ FALSE"
        print(f"   {u[0]}.{u[1]}: {estado} (actualizado: {u[3]})")
    
    conn.close()
    
    print("\n" + "=" * 100)
    print("✅ ANÁLISIS COMPLETADO")
    print("=" * 100)

if __name__ == "__main__":
    main()
