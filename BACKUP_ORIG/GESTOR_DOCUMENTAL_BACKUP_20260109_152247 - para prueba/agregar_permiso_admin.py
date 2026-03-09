"""
Script para agregar permiso de configuración a usuarios específicos por nombre
"""
from extensions import db
from sqlalchemy import text
from app import app

def agregar_permiso_por_usuario(nombre_usuario):
    """Agrega permiso de configuración a un usuario por su nombre"""
    
    with app.app_context():
        try:
            # 1. Buscar usuario por nombre
            result = db.session.execute(text("""
                SELECT u.id, u.usuario, t.nit, t.razon_social
                FROM usuarios u
                JOIN terceros t ON u.tercero_id = t.id
                WHERE LOWER(u.usuario) = LOWER(:nombre_usuario)
            """), {'nombre_usuario': nombre_usuario})
            
            usuarios = result.fetchall()
            
            if not usuarios:
                print(f"❌ No se encontró usuario: {nombre_usuario}")
                return False
            
            print(f"\n{'=' * 70}")
            print(f" 🔐 AGREGANDO PERMISO: facturas_digitales → configuracion")
            print(f"{'=' * 70}\n")
            
            for usuario_id, usuario, nit, razon_social in usuarios:
                print(f"📋 Usuario: {usuario} (ID: {usuario_id})")
                print(f"   NIT: {nit}")
                print(f"   Razón Social: {razon_social}")
                
                # 2. Verificar si ya tiene el permiso
                result = db.session.execute(text("""
                    SELECT permitido 
                    FROM permisos_usuarios
                    WHERE usuario_id = :usuario_id
                      AND modulo = 'facturas_digitales'
                      AND accion = 'configuracion'
                """), {'usuario_id': usuario_id})
                
                permiso_existente = result.fetchone()
                
                if permiso_existente:
                    if permiso_existente[0]:
                        print(f"   ✅ YA tiene el permiso HABILITADO\n")
                        continue
                    else:
                        print(f"   ⚠️  Permiso existe pero DESHABILITADO, actualizando...")
                        db.session.execute(text("""
                            UPDATE permisos_usuarios
                            SET permitido = true
                            WHERE usuario_id = :usuario_id
                              AND modulo = 'facturas_digitales'
                              AND accion = 'configuracion'
                        """), {'usuario_id': usuario_id})
                        db.session.commit()
                        print(f"   ✅ Permiso actualizado correctamente\n")
                        continue
                
                # 3. Crear el permiso
                print(f"   📝 Creando permiso...")
                db.session.execute(text("""
                    INSERT INTO permisos_usuarios (usuario_id, modulo, accion, permitido)
                    VALUES (:usuario_id, 'facturas_digitales', 'configuracion', true)
                """), {'usuario_id': usuario_id})
                db.session.commit()
                print(f"   ✅ Permiso creado correctamente\n")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=" * 70)
    print(" 🔐 AGREGAR PERMISO DE CONFIGURACIÓN - FACTURAS DIGITALES")
    print("=" * 70)
    
    # Agregar permiso a todos los usuarios "admin" (mayúsculas y minúsculas)
    usuarios_admin = ['admin', 'ADMIN']
    
    exitos = 0
    for usuario in usuarios_admin:
        if agregar_permiso_por_usuario(usuario):
            exitos += 1
    
    if exitos > 0:
        print(f"{'=' * 70}")
        print(f" ✅ PERMISOS AGREGADOS CORRECTAMENTE ({exitos} usuarios)")
        print(f"{'=' * 70}")
        print(f"\n💡 Los usuarios ahora pueden acceder a:")
        print(f"   /facturas-digitales/configuracion/")
        print(f"\n🔄 Recarga la página (F5) para aplicar cambios")
        print()
    else:
        print(f"{'=' * 70}")
        print(f" ❌ ERROR AL AGREGAR PERMISOS")
        print(f"{'=' * 70}\n")
