#!/usr/bin/env python3
"""Script para verificar y actualizar el estado de usuarios en la base de datos"""

from app import app, db, Usuario, Tercero

def check_user_status(nit=None, usuario=None):
    with app.app_context():
        query = Usuario.query
        if usuario:
            query = query.filter_by(usuario=usuario)
        if nit:
            # Buscar el tercero por NIT y filtrar usuarios asociados
            tercero = Tercero.query.filter_by(nit=nit).first()
            if tercero:
                query = query.filter_by(tercero_id=tercero.id)
            else:
                print(f"Tercero con NIT {nit} no encontrado")
                return None
        user = query.first()
        if user:
            print(f"Usuario encontrado:")
            print(f"  ID: {user.id}")
            print(f"  Usuario: {user.usuario}")
            print(f"  Correo: {user.correo}")
            print(f"  Activo: {user.activo}")
            print(f"  Rol: {user.rol}")
            print(f"  Fecha Creación: {user.fecha_creacion}")
            tercero = Tercero.query.get(user.tercero_id)
            if tercero:
                print(f"\nTercero asociado:")
                print(f"  NIT: {tercero.nit}")
                print(f"  Razón Social: {tercero.razon_social}")
                print(f"  Estado: {tercero.estado}")
            return user
        else:
            print(f"Usuario {usuario if usuario else ''} no encontrado para NIT {nit if nit else ''}")
            return None

def deactivate_user(user_id):
    """Desactivar un usuario específico"""
    with app.app_context():
        user = Usuario.query.get(user_id)
        if user:
            user.activo = False
            db.session.commit()
            print(f"Usuario {user.usuario} (ID: {user_id}) desactivado correctamente")
        else:
            print(f"Usuario con ID {user_id} no encontrado")

if __name__ == "__main__":
    import sys
    print("=== Verificación del estado del usuario ===")
    nit = None
    usuario = None
    if len(sys.argv) >= 2:
        nit = sys.argv[1]
    if len(sys.argv) >= 3:
        usuario = sys.argv[2]
    user = check_user_status(nit=nit, usuario=usuario)
    if user:
        if user.activo:
            print(f"\n⚠️  El usuario está ACTIVO")
        else:
            print(f"\n✅ El usuario está INACTIVO")
    print("\n=== Verificación completada ===")