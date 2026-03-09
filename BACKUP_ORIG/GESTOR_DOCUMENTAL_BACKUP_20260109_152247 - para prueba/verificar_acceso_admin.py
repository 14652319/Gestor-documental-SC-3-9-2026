# -*- coding: utf-8 -*-
"""Verificar estado completo del usuario admin y IPs bloqueadas"""
from app import app, db, Usuario, IPListaNegra, IPSospechosa, bcrypt

with app.app_context():
    print("\n" + "="*60)
    print("VERIFICACIÓN DE ACCESO - USUARIO ADMIN")
    print("="*60)
    
    # 1. Verificar usuario
    user = Usuario.query.filter_by(usuario='admin').first()
    
    if not user:
        print("\n❌ ERROR: Usuario 'admin' no encontrado")
        exit(1)
    
    print(f"\n📋 DATOS DEL USUARIO:")
    print(f"   ID: {user.id}")
    print(f"   Usuario: {user.usuario}")
    print(f"   Activo: {'✅ SÍ' if user.activo else '❌ NO'}")
    print(f"   Rol: {user.rol}")
    
    # Obtener tercero
    from app import Tercero
    tercero = Tercero.query.get(user.tercero_id) if user.tercero_id else None
    print(f"   NIT: {tercero.nit if tercero else 'Sin tercero'}")
    
    # 2. Verificar contraseñas
    print(f"\n🔐 VERIFICACIÓN DE CONTRASEÑAS:")
    
    contraseñas_a_probar = [
        "Admin12345$",
        "Admin123456$",
        "admin123",
        "Admin1234$"
    ]
    
    for pwd in contraseñas_a_probar:
        es_correcta = bcrypt.check_password_hash(user.password_hash, pwd)
        if es_correcta:
            print(f"   ✅ '{pwd}' → CORRECTA")
        else:
            print(f"   ❌ '{pwd}' → Incorrecta")
    
    # 3. Verificar IPs bloqueadas
    print(f"\n🚫 IPs EN LISTA NEGRA:")
    ips_negras = IPListaNegra.query.all()
    
    if ips_negras:
        for ip in ips_negras:
            print(f"   🔴 {ip.ip} - Bloqueada desde {ip.fecha}")
    else:
        print("   ✅ No hay IPs en lista negra")
    
    # 4. Verificar IPs sospechosas
    print(f"\n⚠️  IPs SOSPECHOSAS:")
    ips_sospechosas = IPSospechosa.query.all()
    
    if ips_sospechosas:
        for ip in ips_sospechosas:
            print(f"   🟡 {ip.ip}")
            print(f"      Intentos fallidos: {ip.intentos_fallidos}")
            print(f"      Último intento: {ip.ultimo_intento}")
            print(f"      Bloqueada: {'SÍ' if ip.bloqueada else 'NO'}")
    else:
        print("   ✅ No hay IPs sospechosas registradas")
    
    # 5. Obtener IP actual (localhost)
    print(f"\n🌐 TU IP ACTUAL:")
    print(f"   Localhost: 127.0.0.1")
    print(f"   Verifica si está bloqueada arriba ☝️")
    
    print(f"\n" + "="*60)
    print("RESUMEN:")
    print("="*60)
    
    if user.activo:
        print("✅ Usuario está ACTIVO")
    else:
        print("❌ Usuario está INACTIVO - Necesita activación")
    
    # Buscar contraseña correcta
    contraseña_correcta = None
    for pwd in contraseñas_a_probar:
        if bcrypt.check_password_hash(user.password_hash, pwd):
            contraseña_correcta = pwd
            break
    
    if contraseña_correcta:
        print(f"✅ Contraseña actual: {contraseña_correcta}")
    else:
        print("⚠️  Ninguna de las contraseñas probadas es correcta")
        print("   (Puede ser una contraseña diferente)")
    
    # Verificar si localhost está bloqueado
    ip_localhost_negra = IPListaNegra.query.filter_by(ip='127.0.0.1').first()
    ip_localhost_sospechosa = IPSospechosa.query.filter_by(ip='127.0.0.1').first()
    
    if ip_localhost_negra or (ip_localhost_sospechosa and ip_localhost_sospechosa.bloqueada):
        print("❌ Tu IP (127.0.0.1) está BLOQUEADA")
        print("   Necesitas desbloquearla para acceder")
    else:
        print("✅ Tu IP (127.0.0.1) NO está bloqueada")
    
    print("="*60 + "\n")
