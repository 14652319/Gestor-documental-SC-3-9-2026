"""
Script para diagnosticar el sistema de permisos de un usuario específico
Muestra:
1. Permisos en base de datos
2. Decoradores aplicados en las rutas
3. Lógica de validación de permisos
"""

from app import app, db
from sqlalchemy import text

def diagnosticar_usuario(usuario_input):
    """Diagnostica los permisos de un usuario específico"""
    
    with app.app_context():
        print("=" * 100)
        print(f"DIAGNÓSTICO DE PERMISOS - Usuario: {usuario_input}")
        print("=" * 100)
        print()
        
        # 1. Buscar usuario
        result = db.session.execute(text("""
            SELECT u.id, u.usuario, u.nit, u.activo, u.rol, t.razon_social
            FROM usuarios u
            LEFT JOIN terceros t ON u.tercero_id = t.id
            WHERE u.usuario = :usuario
        """), {'usuario': usuario_input})
        
        usuario = result.fetchone()
        
        if not usuario:
            print(f"❌ Usuario '{usuario_input}' no encontrado")
            return
        
        usuario_id, usuario_nombre, nit, activo, rol, razon_social = usuario
        
        print(f"✅ USUARIO ENCONTRADO:")
        print(f"   • ID: {usuario_id}")
        print(f"   • Usuario: {usuario_nombre}")
        print(f"   • NIT: {nit}")
        print(f"   • Razón Social: {razon_social}")
        print(f"   • Activo: {'✅ Sí' if activo else '❌ No'}")
        print(f"   • Rol: {rol or 'Sin rol asignado'}")
        print()
        
        # 2. Contar permisos en base de datos
        result = db.session.execute(text("""
            SELECT COUNT(*) 
            FROM permisos_usuario 
            WHERE usuario_id = :usuario_id AND tiene_permiso = TRUE
        """), {'usuario_id': usuario_id})
        
        total_permisos = result.scalar()
        
        print(f"📊 PERMISOS EN BASE DE DATOS:")
        print(f"   • Total de permisos activos: {total_permisos}")
        print()
        
        # 3. Detallar permisos por módulo
        result = db.session.execute(text("""
            SELECT modulo, COUNT(*) as total,
                   SUM(CASE WHEN tiene_permiso = TRUE THEN 1 ELSE 0 END) as activos
            FROM permisos_usuario
            WHERE usuario_id = :usuario_id
            GROUP BY modulo
            ORDER BY modulo
        """), {'usuario_id': usuario_id})
        
        permisos_modulo = result.fetchall()
        
        if permisos_modulo:
            print("📦 PERMISOS POR MÓDULO:")
            for modulo, total, activos in permisos_modulo:
                porcentaje = (activos / total * 100) if total > 0 else 0
                estado = "✅" if activos > 0 else "❌"
                print(f"   {estado} {modulo:25} → {activos}/{total} permisos ({porcentaje:.1f}%)")
            print()
        
        # 4. Listar permisos activos
        result = db.session.execute(text("""
            SELECT modulo, accion
            FROM permisos_usuario
            WHERE usuario_id = :usuario_id AND tiene_permiso = TRUE
            ORDER BY modulo, accion
        """), {'usuario_id': usuario_id})
        
        permisos_activos = result.fetchall()
        
        if permisos_activos:
            print(f"✅ PERMISOS ACTIVOS ({len(permisos_activos)}):")
            modulo_actual = None
            for modulo, accion in permisos_activos:
                if modulo != modulo_actual:
                    print(f"\n   📦 {modulo}:")
                    modulo_actual = modulo
                print(f"      ✓ {accion}")
            print()
        else:
            print("❌ SIN PERMISOS ACTIVOS")
            print()
        
        # 5. Verificar decoradores en el código
        print("=" * 100)
        print("🔍 ANÁLISIS DEL SISTEMA DE DECORADORES")
        print("=" * 100)
        print()
        
        # Revisar decoradores_permisos.py
        try:
            with open('decoradores_permisos.py', 'r', encoding='utf-8') as f:
                contenido = f.read()
                
            # Buscar función requiere_permiso
            if 'def requiere_permiso(' in contenido:
                print("✅ Decorador @requiere_permiso encontrado")
                
                # Buscar lógica de validación
                if 'session.get(' in contenido:
                    print("   ✓ Valida sesión del usuario")
                
                if 'permisos_usuario' in contenido or 'PermisoUsuario' in contenido:
                    print("   ✓ Consulta tabla permisos_usuario")
                
                if 'tiene_permiso' in contenido:
                    print("   ✓ Verifica campo tiene_permiso")
                
                # ⚠️ BUSCAR SI HAY BYPASS O CONDICIONES ESPECIALES
                if 'rol' in contenido and ('admin' in contenido or 'administrador' in contenido):
                    print("   ⚠️  DETECTADO: Lógica especial para rol admin")
                
                if 'return True' in contenido and 'if' in contenido:
                    print("   ⚠️  DETECTADO: Condiciones que permiten acceso sin validar permisos")
                
                print()
        except FileNotFoundError:
            print("❌ Archivo decoradores_permisos.py no encontrado")
            print()
        
        # 6. Verificar si el usuario está logeándose
        print("=" * 100)
        print("🔐 VERIFICACIÓN DE ACCESO A MÓDULOS")
        print("=" * 100)
        print()
        
        # Simulación de validación
        modulos_sistema = [
            'recibir_facturas',
            'relaciones',
            'causaciones',
            'archivo_digital',
            'configuracion',
            'monitoreo',
            'admin'
        ]
        
        print("Verificando acceso sin decorador (TODOS los usuarios pueden entrar):")
        for modulo in modulos_sistema:
            # Verificar si tiene permiso
            result = db.session.execute(text("""
                SELECT tiene_permiso
                FROM permisos_usuario
                WHERE usuario_id = :usuario_id 
                  AND modulo = :modulo 
                  AND accion = 'acceder_modulo'
            """), {'usuario_id': usuario_id, 'modulo': modulo})
            
            permiso = result.fetchone()
            tiene_permiso = permiso[0] if permiso else False
            
            if tiene_permiso:
                print(f"   ✅ {modulo:25} → ACCESO PERMITIDO (tiene permiso en BD)")
            else:
                print(f"   ⚠️  {modulo:25} → ACCESO DENEGADO (sin permiso en BD)")
        
        print()
        print("=" * 100)
        print("🔍 CONCLUSIÓN DEL DIAGNÓSTICO")
        print("=" * 100)
        print()
        
        if total_permisos == 0:
            print("❌ PROBLEMA DETECTADO:")
            print("   El usuario NO tiene permisos activos en la base de datos.")
            print("   Pero puede acceder a los módulos porque:")
            print()
            print("   1. Los decoradores @requiere_permiso NO están aplicados en las rutas")
            print("   2. O hay una condición que permite acceso sin validar permisos")
            print("   3. O el rol del usuario tiene bypass automático")
            print()
            print("   SOLUCIÓN:")
            print("   - Asignar permisos desde /admin/usuarios-permisos/")
            print("   - O verificar la lógica de decoradores_permisos.py")
        elif total_permisos == 1:
            print("⚠️  PROBLEMA DETECTADO:")
            print(f"   El usuario tiene SOLO 1 permiso activo: {permisos_activos[0][0]}.{permisos_activos[0][1]}")
            print("   Pero puede acceder a múltiples módulos porque:")
            print()
            print("   1. Los decoradores NO validan permisos correctamente")
            print("   2. O hay una lógica que permite acceso con permisos mínimos")
            print()
            print("   SOLUCIÓN:")
            print("   - Revisar decoradores_permisos.py")
            print("   - Asignar permisos completos desde /admin/usuarios-permisos/")
        else:
            print("✅ El usuario tiene permisos configurados correctamente")
            print(f"   Total de permisos: {total_permisos}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        usuario = sys.argv[1]
    else:
        usuario = input("Ingrese el nombre de usuario: ")
    
    diagnosticar_usuario(usuario)
