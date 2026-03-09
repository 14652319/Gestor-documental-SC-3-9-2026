# -*- coding: utf-8 -*-
"""Activar usuario admin y asignar rol correcto"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Usuario

with app.app_context():
    user = Usuario.query.filter(db.func.lower(Usuario.usuario) == 'admin').first()
    
    if not user:
        print("❌ No se encontró usuario admin")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"ACTIVANDO Y CORRIGIENDO ROL DEL USUARIO ADMIN")
    print(f"{'='*60}\n")
    
    print(f"Estado actual:")
    print(f"  Activo: {user.activo}")
    print(f"  Rol: {user.rol}")
    
    # Activar y corregir rol
    user.activo = True
    user.rol = 'admin'
    db.session.commit()
    
    print(f"\nEstado corregido:")
    print(f"  Activo: {user.activo} ✅")
    print(f"  Rol: {user.rol} ✅")
    
    print(f"\n{'='*60}")
    print(f"✅ USUARIO ADMIN LISTO PARA USAR")
    print(f"{'='*60}")
    print(f"\nCredenciales:")
    print(f"  NIT: 805028041")
    print(f"  Usuario: admin")
    print(f"  Contraseña: Admin12345$")
    print(f"{'='*60}\n")
