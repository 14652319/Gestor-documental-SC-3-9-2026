"""
Script para agregar permiso de configuración de facturas digitales a usuario
"""
import sys
from extensions import db
from sqlalchemy import text
from app import app

def agregar_permiso_configuracion(nit_usuario):
    """Agrega permiso de configuración a un usuario específico"""
    
    with app.app_context():
        try:
            # 1. Buscar usuario por NIT
            result = db.session.execute(text("""
                SELECT u.id, u.usuario, t.razon_social
                FROM usuarios u
                JOIN terceros t ON u.tercero_id = t.id
                WHERE t.nit = :nit
            """), {'nit': nit_usuario})
            
            usuario = result.fetchone()
            
            if not usuario:
                print(f"❌ No se encontró usuario con NIT: {nit_usuario}")
                return False
            
            usuario_id = usuario[0]
            usuario_nombre = usuario[1]
            razon_social = usuario[2]
            
            print(f"\n📋 Usuario encontrado:")
            print(f"   ID: {usuario_id}")
            print(f"   Usuario: {usuario_nombre}")
            print(f"   Razón Social: {razon_social}")
            print(f"   NIT: {nit_usuario}")
            
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
                    print(f"\n✅ El usuario YA tiene el permiso 'configuracion' HABILITADO")
                    return True
                else:
                    print(f"\n⚠️  El usuario tiene el permiso pero está DESHABILITADO")
                    print(f"   Actualizando a 'permitido = true'...")
                    
                    db.session.execute(text("""
                        UPDATE permisos_usuarios
                        SET permitido = true
                        WHERE usuario_id = :usuario_id
                          AND modulo = 'facturas_digitales'
                          AND accion = 'configuracion'
                    """), {'usuario_id': usuario_id})
                    
                    db.session.commit()
                    print(f"✅ Permiso actualizado correctamente")
                    return True
            
            # 3. Crear el permiso
            print(f"\n📝 Creando permiso 'configuracion' para el usuario...")
            
            db.session.execute(text("""
                INSERT INTO permisos_usuarios (usuario_id, modulo, accion, permitido)
                VALUES (:usuario_id, 'facturas_digitales', 'configuracion', true)
            """), {'usuario_id': usuario_id})
            
            db.session.commit()
            
            print(f"✅ Permiso creado correctamente!")
            print(f"\n📋 Resumen:")
            print(f"   Módulo: facturas_digitales")
            print(f"   Acción: configuracion")
            print(f"   Permitido: ✅ Sí")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al agregar permiso: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=" * 70)
    print(" 🔐 AGREGAR PERMISO DE CONFIGURACIÓN - FACTURAS DIGITALES")
    print("=" * 70)
    
    if len(sys.argv) > 1:
        nit = sys.argv[1]
    else:
        nit = input("\n📝 Ingrese el NIT del usuario: ").strip()
    
    if not nit:
        print("❌ Debe ingresar un NIT")
        sys.exit(1)
    
    exito = agregar_permiso_configuracion(nit)
    
    if exito:
        print(f"\n{'=' * 70}")
        print(f" ✅ PERMISO AGREGADO CORRECTAMENTE")
        print(f"{'=' * 70}")
        print(f"\n💡 El usuario ahora puede acceder a:")
        print(f"   /facturas-digitales/configuracion/")
        print(f"\n🔄 Cierre sesión y vuelva a iniciar para aplicar cambios")
        print()
    else:
        print(f"\n{'=' * 70}")
        print(f" ❌ ERROR AL AGREGAR PERMISO")
        print(f"{'=' * 70}")
        sys.exit(1)
