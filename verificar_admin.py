# -*- coding: utf-8 -*-
"""
Verificar datos del usuario admin
"""
import sys
import os

# Agregar ruta al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from flask import Flask
from sqlalchemy import text
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Inicio2024*@localhost/gestor_documental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Consultar usuario admin
    result = db.session.execute(
        text("""
            SELECT u.id, u.usuario, u.correo, u.activo, u.password_hash, 
                   t.nit, t.razon_social
            FROM usuarios u 
            JOIN terceros t ON u.tercero_id = t.id 
            WHERE u.usuario = :usuario
        """),
        {'usuario': 'admin'}
    )
    
    row = result.fetchone()
    
    if row:
        print(f"\n{'='*60}")
        print(f"DATOS DEL USUARIO ADMIN")
        print(f"{'='*60}")
        print(f"ID Usuario: {row[0]}")
        print(f"Usuario: {row[1]}")
        print(f"Correo: {row[2]}")
        print(f"Activo: {row[3]}")
        print(f"Tiene password: {'Sí' if row[4] else 'NO'}")
        print(f"NIT: {row[5]}")
        print(f"Tercero: {row[6]}")
        print(f"{'='*60}")
        
        if row[4]:
            # Probar contraseña
            test_password = "Admin123"
            password_hash = row[4].encode('utf-8') if isinstance(row[4], str) else row[4]
            
            try:
                resultado = bcrypt.checkpw(test_password.encode('utf-8'), password_hash)
                print(f"\n✓ La contraseña '{test_password}' {'COINCIDE' if resultado else 'NO COINCIDE'}")
            except Exception as e:
                print(f"\n✗ Error al verificar contraseña: {e}")
            
            print(f"\nHash almacenado (primeros 50 chars): {row[4][:50]}...")
        else:
            print(f"\n⚠ El usuario NO TIENE contraseña establecida")
            print(f"\nDebes establecer la contraseña usando el enlace de recuperación")
    else:
        print(f"\n✗ No se encontró el usuario 'admin'")
