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
    
    # Probar ambas contraseñas
    passwords = ["Admin1234$", "Admin12345$"]
    
    for pwd in passwords:
        try:
            resultado = bcrypt.check_password_hash(user.password_hash, pwd)
            
            if resultado:
                print(f"✅ ¡CONTRASEÑA CORRECTA!")
                print(f"   La contraseña es: '{pwd}'\n")
                print(f"Credenciales de acceso:")
                print(f"   NIT: {tercero.nit}")
                print(f"   Usuario: {user.usuario}")
                print(f"   Contraseña: {pwd}\n")
                sys.exit(0)
            else:
                print(f"❌ '{pwd}' - NO coincide")
        except Exception as e:
            print(f"❌ Error con '{pwd}': {e}")
    
    print(f"\n❌ Ninguna de las dos contraseñas coincide")
    print(f"\n¿Quieres que establezca una nueva contraseña temporal?\n")
