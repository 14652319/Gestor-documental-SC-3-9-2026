#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear usuario de prueba
"""
from app import app, Tercero, Usuario, bcrypt, db

def crear_usuario_prueba():
    with app.app_context():
        try:
            # 1. Crear tercero
            tercero_existente = Tercero.query.filter_by(nit="805028041").first()
            if tercero_existente:
                print(f"❌ Tercero con NIT 805028041 ya existe")
                tercero = tercero_existente
            else:
                tercero = Tercero(
                    nit="805028041",
                    tipo_persona="juridica",
                    razon_social="SUPERTIENDAS CAÑAVERAL S.A.S",
                    correo="admin@supertiendascanaveral.com",
                    celular="3001234567",
                    acepta_terminos=True,
                    acepta_contacto=True,
                    estado="activo"  # ACTIVO para pruebas
                )
                db.session.add(tercero)
                db.session.flush()
                print(f"✅ Tercero creado: {tercero.razon_social} (ID: {tercero.id})")
            
            # 2. Crear usuario
            usuario_existente = Usuario.query.filter_by(usuario="14652319").first()
            if usuario_existente:
                print(f"❌ Usuario 14652319 ya existe")
                return
                
            password_hash = bcrypt.generate_password_hash("R1c4rd0$").decode('utf-8')
            
            usuario = Usuario(
                tercero_id=tercero.id,
                usuario="14652319",
                correo="ricardo@supertiendascanaveral.com",
                password_hash=password_hash,
                estado="activo"
            )
            db.session.add(usuario)
            db.session.commit()
            
            print(f"✅ Usuario creado exitosamente:")
            print(f"   - Usuario: 14652319")
            print(f"   - Contraseña: R1c4rd0$")
            print(f"   - NIT: 805028041")
            print(f"   - Tercero: {tercero.razon_social}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    crear_usuario_prueba()