# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar desde app.py
from app import app, db, bcrypt, Usuario, Tercero

with app.app_context():
    # Buscar usuario admin
    user = Usuario.query.filter(
        (db.func.lower(Usuario.usuario) == 'admin')
    ).first()
    
    if not user:
        print("❌ No se encontró el usuario admin")
        sys.exit(1)
    
    # Obtener tercero
    tercero = Tercero.query.get(user.tercero_id)
    
    print(f"\n{'='*60}")
    print(f"DATOS DEL USUARIO ADMIN")
    print(f"{'='*60}")
    print(f"ID: {user.id}")
    print(f"Usuario: {user.usuario}")
    print(f"Correo: {user.correo}")
    print(f"Activo: {user.activo}")
    print(f"Tiene password: {'Sí' if user.password_hash else 'NO'}")
    print(f"NIT: {tercero.nit if tercero else 'N/A'}")
    print(f"Tercero: {tercero.razon_social if tercero else 'N/A'}")
    print(f"{'='*60}\n")
    
    if not user.password_hash:
        print("⚠️  EL USUARIO NO TIENE CONTRASEÑA")
        print("Debe establecer la contraseña usando el enlace de recuperación\n")
        sys.exit(0)
    
    # Probar contraseñas
    test_passwords = [
        "Admin123",
        "admin123",
        "ADMIN123",
        "Admin123!",
        "Inicio2024*"
    ]
    
    print("Probando contraseñas...\n")
    for pwd in test_passwords:
        try:
            resultado = bcrypt.check_password_hash(user.password_hash, pwd)
            status = "✅ CORRECTA" if resultado else "❌ incorrecta"
            print(f"{status}: '{pwd}'")
            if resultado:
                print(f"\n🎯 LA CONTRASEÑA CORRECTA ES: '{pwd}'\n")
                break
        except Exception as e:
            print(f"❌ Error al probar '{pwd}': {e}")
    else:
        print(f"\n❌ Ninguna de las contraseñas probadas funcionó")
        print(f"\nHash almacenado (primeros 60 chars):")
        print(f"{user.password_hash[:60] if user.password_hash else 'NULL'}...\n")
