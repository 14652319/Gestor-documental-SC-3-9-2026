"""
Script de diagnóstico de permisos - Facturas Digitales
Verifica el estado actual de permisos para un usuario
"""
import sys
from extensions import db
from sqlalchemy import text
from app import app

def diagnosticar_permisos(nit_usuario):
    """Diagnostica permisos de un usuario"""
    
    with app.app_context():
        try:
            # 1. Buscar usuario
            result = db.session.execute(text("""
                SELECT u.id, u.usuario, t.razon_social, t.nit
                FROM usuarios u
                JOIN terceros t ON u.tercero_id = t.id
                WHERE t.nit = :nit
            """), {'nit': nit_usuario})
            
            usuario = result.fetchone()
            
            if not usuario:
                print(f"❌ No se encontró usuario con NIT: {nit_usuario}")
                return
            
            usuario_id, usuario_nombre, razon_social, nit = usuario
            
            print(f"\n📋 INFORMACIÓN DEL USUARIO:")
            print(f"{'=' * 70}")
            print(f"   ID: {usuario_id}")
            print(f"   Usuario: {usuario_nombre}")
            print(f"   Razón Social: {razon_social}")
            print(f"   NIT: {nit}")
            
            # 2. Buscar TODOS los permisos del usuario
            result = db.session.execute(text("""
                SELECT modulo, accion, permitido
                FROM permisos_usuarios
                WHERE usuario_id = :usuario_id
                ORDER BY modulo, accion
            """), {'usuario_id': usuario_id})
            
            permisos = result.fetchall()
            
            print(f"\n🔐 PERMISOS DEL USUARIO:")
            print(f"{'=' * 70}")
            
            if not permisos:
                print(f"   ⚠️  NO tiene ningún permiso registrado")
            else:
                print(f"   Total: {len(permisos)} permisos")
                print(f"\n   {'Módulo':<30} {'Acción':<30} {'Estado':<10}")
                print(f"   {'-' * 70}")
                for modulo, accion, permitido in permisos:
                    estado = "✅ ACTIVO" if permitido else "❌ INACTIVO"
                    print(f"   {modulo:<30} {accion:<30} {estado:<10}")
            
            # 3. Verificar específicamente el permiso de configuración
            result = db.session.execute(text("""
                SELECT permitido
                FROM permisos_usuarios
                WHERE usuario_id = :usuario_id
                  AND modulo = 'facturas_digitales'
                  AND accion = 'configuracion'
            """), {'usuario_id': usuario_id})
            
            permiso_config = result.fetchone()
            
            print(f"\n🎯 PERMISO ESPECÍFICO: facturas_digitales → configuracion")
            print(f"{'=' * 70}")
            
            if not permiso_config:
                print(f"   ❌ NO EXISTE este permiso en la base de datos")
                print(f"\n💡 Solución: Ejecutar")
                print(f"   python agregar_permiso_configuracion.py {nit}")
            elif permiso_config[0]:
                print(f"   ✅ EXISTE y está HABILITADO")
                print(f"\n💡 El usuario DEBERÍA poder acceder a /facturas-digitales/configuracion/")
            else:
                print(f"   ⚠️  EXISTE pero está DESHABILITADO")
                print(f"\n💡 Solución: Ejecutar")
                print(f"   python agregar_permiso_configuracion.py {nit}")
            
            # 4. Verificar permisos relacionados con facturas digitales
            result = db.session.execute(text("""
                SELECT accion, permitido
                FROM permisos_usuarios
                WHERE usuario_id = :usuario_id
                  AND modulo = 'facturas_digitales'
                ORDER BY accion
            """), {'usuario_id': usuario_id})
            
            permisos_fd = result.fetchall()
            
            print(f"\n📋 PERMISOS EN MÓDULO 'facturas_digitales':")
            print(f"{'=' * 70}")
            
            if not permisos_fd:
                print(f"   ⚠️  NO tiene ningún permiso en este módulo")
            else:
                print(f"   Total: {len(permisos_fd)} permisos")
                print(f"\n   {'Acción':<40} {'Estado':<10}")
                print(f"   {'-' * 50}")
                for accion, permitido in permisos_fd:
                    estado = "✅ ACTIVO" if permitido else "❌ INACTIVO"
                    print(f"   {accion:<40} {estado:<10}")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("=" * 70)
    print(" 🔍 DIAGNÓSTICO DE PERMISOS - FACTURAS DIGITALES")
    print("=" * 70)
    
    if len(sys.argv) > 1:
        nit = sys.argv[1]
    else:
        nit = input("\n📝 Ingrese el NIT del usuario: ").strip()
    
    if not nit:
        print("❌ Debe ingresar un NIT")
        sys.exit(1)
    
    diagnosticar_permisos(nit)
    print(f"\n{'=' * 70}\n")
