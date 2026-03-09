# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, bcrypt, Usuario, Tercero

with app.app_context():
    # Buscar usuario admin con NIT 805028041
    tercero = Tercero.query.filter_by(nit='805028041').first()
    user = Usuario.query.filter_by(tercero_id=tercero.id, usuario='admin').first()
    
    print(f"\n{'='*60}")
    print(f"VERIFICACIÓN DE CONTRASEÑA")
    print(f"{'='*60}\n")
    
    print(f"Usuario: {user.usuario}")
    print(f"NIT: {tercero.nit}")
    print(f"Activo: {user.activo}\n")
    
    # Probar la contraseña que dijo el usuario
    password_to_test = "Admin1234$"
    
    try:
        resultado = bcrypt.check_password_hash(user.password_hash, password_to_test)
        
        if resultado:
            print(f"✅ ¡CONTRASEÑA CORRECTA!")
            print(f"   La contraseña '{password_to_test}' FUNCIONA\n")
            print(f"Puedes iniciar sesión con:")
            print(f"   NIT: {tercero.nit}")
            print(f"   Usuario: {user.usuario}")
            print(f"   Contraseña: {password_to_test}\n")
        else:
            print(f"❌ Contraseña INCORRECTA")
            print(f"   La contraseña '{password_to_test}' NO coincide\n")
            print(f"¿Quieres que establezca una nueva contraseña?\n")
    except Exception as e:
        print(f"❌ Error al verificar: {e}\n")
