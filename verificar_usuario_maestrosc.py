"""
Script para verificar el estado del usuario MAESTROSC
"""
from app import app, db, Usuario, Tercero

with app.app_context():
    # Buscar usuario MAESTROSC
    usuario = Usuario.query.filter_by(usuario='MAESTROSC').first()
    
    if usuario:
        print("="*60)
        print("USUARIO ENCONTRADO: MAESTROSC")
        print("="*60)
        print(f"ID: {usuario.id}")
        print(f"Usuario: {usuario.usuario}")
        print(f"Correo: {usuario.correo}")
        print(f"Activo: {'✅ SÍ' if usuario.activo else '❌ NO'}")
        print(f"Tiene contraseña: {'✅ SÍ' if usuario.password_hash else '❌ NO (password_hash es NULL)'}")
        print(f"Tercero ID: {usuario.tercero_id}")
        
        # Buscar tercero asociado
        if usuario.tercero_id:
            tercero = Tercero.query.get(usuario.tercero_id)
            if tercero:
                print(f"\nTERCERO ASOCIADO:")
                print(f"  NIT: {tercero.nit}")
                print(f"  Razón Social: {tercero.razon_social}")
                print(f"  Estado: {tercero.estado}")
        
        print("="*60)
        
        # Diagnóstico
        print("\n🔍 DIAGNÓSTICO:")
        if not usuario.password_hash:
            print("⚠️  PROBLEMA: El usuario NO tiene contraseña establecida (password_hash es NULL)")
            print("   Esto explica por qué el sistema de recuperación muestra 'undefined'")
            print("   El usuario necesita ESTABLECER su contraseña inicial, NO recuperarla.")
        
        if not usuario.activo:
            print("⚠️  PROBLEMA: El usuario NO está activo")
            print("   Debe activarse desde el módulo de administración")
        
        if usuario.password_hash and usuario.activo:
            print("✅ El usuario está correctamente configurado")
    else:
        print("❌ NO se encontró el usuario MAESTROSC en la base de datos")
