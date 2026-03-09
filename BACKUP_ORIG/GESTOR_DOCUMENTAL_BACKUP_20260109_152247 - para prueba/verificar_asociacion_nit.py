# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Usuario, Tercero

with app.app_context():
    # Buscar usuario admin
    user = Usuario.query.filter(
        (db.func.lower(Usuario.usuario) == 'admin')
    ).first()
    
    if not user:
        print("❌ No se encontró usuario admin")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"VERIFICACIÓN DE ASOCIACIÓN NIT-USUARIO")
    print(f"{'='*60}\n")
    
    print(f"Usuario admin:")
    print(f"  ID: {user.id}")
    print(f"  Usuario: {user.usuario}")
    print(f"  Tercero_ID: {user.tercero_id}")
    print(f"  Rol: {user.rol}")
    print(f"  Activo: {user.activo}")
    
    # Buscar el tercero asociado
    tercero = Tercero.query.get(user.tercero_id)
    
    if tercero:
        print(f"\nTercero asociado al usuario admin:")
        print(f"  ID: {tercero.id}")
        print(f"  NIT: {tercero.nit}")
        print(f"  Razón Social: {tercero.razon_social}")
    else:
        print(f"\n❌ No se encontró tercero con ID {user.tercero_id}")
    
    # Buscar el NIT que estás intentando usar
    nit_intentado = "805028041"
    tercero_intentado = Tercero.query.filter_by(nit=nit_intentado).first()
    
    print(f"\n{'='*60}")
    print(f"Verificación del NIT {nit_intentado}:")
    print(f"{'='*60}")
    
    if tercero_intentado:
        print(f"  ID: {tercero_intentado.id}")
        print(f"  NIT: {tercero_intentado.nit}")
        print(f"  Razón Social: {tercero_intentado.razon_social}")
        
        if tercero_intentado.id == user.tercero_id:
            print(f"\n✅ EL NIT COINCIDE con el tercero del usuario admin")
        else:
            print(f"\n❌ EL NIT NO COINCIDE")
            print(f"   Tercero del usuario admin: ID {user.tercero_id}")
            print(f"   Tercero del NIT ingresado: ID {tercero_intentado.id}")
            print(f"\n🔧 SOLUCIÓN: Actualizar el tercero_id del usuario admin")
            print(f"   UPDATE usuarios SET tercero_id = {tercero_intentado.id} WHERE id = {user.id};")
    else:
        print(f"❌ No existe tercero con NIT {nit_intentado}")
