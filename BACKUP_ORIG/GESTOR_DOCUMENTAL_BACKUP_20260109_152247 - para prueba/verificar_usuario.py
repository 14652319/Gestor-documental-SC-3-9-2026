#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, Usuario, Tercero

with app.app_context():
    # Buscar usuario
    usuario = Usuario.query.filter_by(usuario='14652319').first()
    
    if usuario:
        print(f"✅ Usuario encontrado: {usuario.usuario}")
        print(f"📧 Correo: {usuario.correo}")
        print(f"🆔 Tercero ID: {usuario.tercero_id}")
        
        # Buscar tercero relacionado
        tercero = Tercero.query.get(usuario.tercero_id)
        if tercero:
            print(f"🏢 NIT del tercero: {tercero.nit}")
            print(f"📋 Razón social: {tercero.razon_social}")
        else:
            print("❌ Tercero no encontrado")
    else:
        print("❌ Usuario no encontrado")
        print("\n🔍 Usuarios existentes:")
        todos_usuarios = Usuario.query.all()
        for u in todos_usuarios:
            t = Tercero.query.get(u.tercero_id)
            print(f"  - Usuario: {u.usuario}, NIT: {t.nit if t else 'N/A'}")