# -*- coding: utf-8 -*-
"""Script para arreglar asociación usuario admin con NIT 805028041"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar desde app.py que ya tiene la configuración correcta
from app import app, db, Usuario, Tercero

print("\n" + "="*60)
print("DIAGNÓSTICO Y CORRECCIÓN - USUARIO ADMIN")
print("="*60 + "\n")

with app.app_context():
    # 1. Buscar tercero con NIT 805028041
    print("1️⃣ Buscando tercero con NIT 805028041...")
    tercero_805 = Tercero.query.filter_by(nit='805028041').first()
    
    if not tercero_805:
        print("   ❌ NO EXISTE tercero con NIT 805028041")
        print("\n   Listando todos los terceros:")
        todos = Tercero.query.limit(10).all()
        for t in todos:
            print(f"   - NIT: {t.nit} | {t.razon_social}")
        sys.exit(1)
    
    print(f"   ✅ Tercero encontrado:")
    print(f"      ID: {tercero_805.id}")
    print(f"      NIT: {tercero_805.nit}")
    print(f"      Razón Social: {tercero_805.razon_social}")
    
    # 2. Buscar usuario admin
    print(f"\n2️⃣ Buscando usuario 'admin'...")
    user_admin = Usuario.query.filter(
        db.func.lower(Usuario.usuario) == 'admin'
    ).first()
    
    if not user_admin:
        print("   ❌ NO EXISTE usuario admin")
        sys.exit(1)
    
    print(f"   ✅ Usuario encontrado:")
    print(f"      ID: {user_admin.id}")
    print(f"      Usuario: {user_admin.usuario}")
    print(f"      Tercero_ID actual: {user_admin.tercero_id}")
    print(f"      Activo: {user_admin.activo}")
    print(f"      Rol: {user_admin.rol}")
    
    # 3. Verificar tercero actual del usuario
    print(f"\n3️⃣ Verificando tercero actual del usuario admin...")
    tercero_actual = Tercero.query.get(user_admin.tercero_id)
    
    if tercero_actual:
        print(f"   Tercero actual:")
        print(f"      ID: {tercero_actual.id}")
        print(f"      NIT: {tercero_actual.nit}")
        print(f"      Razón Social: {tercero_actual.razon_social}")
    else:
        print(f"   ❌ No existe tercero con ID {user_admin.tercero_id}")
    
    # 4. Comparar
    print(f"\n4️⃣ Comparación:")
    if user_admin.tercero_id == tercero_805.id:
        print(f"   ✅ LA ASOCIACIÓN YA ES CORRECTA")
        print(f"\n   Puedes iniciar sesión con:")
        print(f"      NIT: 805028041")
        print(f"      Usuario: admin")
        print(f"      Contraseña: Admin12345$")
    else:
        print(f"   ❌ LA ASOCIACIÓN ES INCORRECTA")
        print(f"      Usuario admin está asociado al tercero ID: {user_admin.tercero_id} (NIT: {tercero_actual.nit if tercero_actual else 'N/A'})")
        print(f"      Debería estar asociado al tercero ID: {tercero_805.id} (NIT: 805028041)")
        
        print(f"\n5️⃣ CORRIGIENDO...")
        try:
            user_admin.tercero_id = tercero_805.id
            db.session.commit()
            print(f"   ✅ ASOCIACIÓN CORREGIDA EXITOSAMENTE")
            print(f"\n   Ahora puedes iniciar sesión con:")
            print(f"      NIT: 805028041")
            print(f"      Usuario: admin")
            print(f"      Contraseña: Admin12345$")
        except Exception as e:
            db.session.rollback()
            print(f"   ❌ Error al corregir: {e}")
            sys.exit(1)

print("\n" + "="*60)
print("PROCESO COMPLETADO")
print("="*60 + "\n")
