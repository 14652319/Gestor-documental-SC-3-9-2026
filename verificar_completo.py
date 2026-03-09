# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Usuario, Tercero, IPListaNegra, IPSospechosa, Acceso

with app.app_context():
    print(f"\n{'='*60}")
    print(f"VERIFICACIÓN COMPLETA - USUARIO ADMIN")
    print(f"{'='*60}\n")
    
    # 1. Buscar usuario admin con NIT 805028041
    tercero = Tercero.query.filter_by(nit='805028041').first()
    
    if not tercero:
        print("❌ No se encontró el tercero con NIT 805028041")
        sys.exit(1)
    
    print(f"✅ Tercero encontrado:")
    print(f"   NIT: {tercero.nit}")
    print(f"   Razón Social: {tercero.razon_social}")
    print(f"   Correo: {tercero.correo}")
    print(f"   Estado: {tercero.estado}\n")
    
    # Buscar usuario admin asociado a este tercero
    user = Usuario.query.filter_by(tercero_id=tercero.id, usuario='admin').first()
    
    if not user:
        print("❌ No se encontró usuario 'admin' asociado a este tercero")
        # Buscar todos los usuarios de este tercero
        usuarios = Usuario.query.filter_by(tercero_id=tercero.id).all()
        if usuarios:
            print(f"\nUsuarios asociados al NIT {tercero.nit}:")
            for u in usuarios:
                print(f"  - {u.usuario} (ID: {u.id}, Activo: {u.activo})")
        sys.exit(1)
    
    print(f"✅ Usuario encontrado:")
    print(f"   ID: {user.id}")
    print(f"   Usuario: {user.usuario}")
    print(f"   Correo: {user.correo}")
    print(f"   Activo: {'✅ SÍ' if user.activo else '❌ NO'}")
    print(f"   Rol: {user.rol}")
    print(f"   Tiene password: {'✅ SÍ' if user.password_hash else '❌ NO'}\n")
    
    # 2. Verificar IPs en lista negra
    print(f"{'='*60}")
    print(f"VERIFICACIÓN DE IPS")
    print(f"{'='*60}\n")
    
    ips_bloqueadas = IPListaNegra.query.all()
    if ips_bloqueadas:
        print(f"⚠️  IPs en LISTA NEGRA ({len(ips_bloqueadas)}):")
        for ip_negra in ips_bloqueadas:
            print(f"   - {ip_negra.ip} | Motivo: {ip_negra.motivo}")
    else:
        print("✅ No hay IPs en lista negra")
    
    print()
    
    ips_sospechosas = IPSospechosa.query.filter(IPSospechosa.bloqueada == True).all()
    if ips_sospechosas:
        print(f"⚠️  IPs SOSPECHOSAS BLOQUEADAS ({len(ips_sospechosas)}):")
        for ip_sosp in ips_sospechosas:
            print(f"   - {ip_sosp.ip} | Intentos: {ip_sosp.intentos} | Motivo: {ip_sosp.motivo_bloqueo}")
    else:
        print("✅ No hay IPs sospechosas bloqueadas")
    
    print()
    
    # 3. Últimos intentos de acceso del usuario
    print(f"{'='*60}")
    print(f"ÚLTIMOS INTENTOS DE ACCESO")
    print(f"{'='*60}\n")
    
    accesos = Acceso.query.filter_by(usuario_id=user.id).order_by(Acceso.timestamp.desc()).limit(5).all()
    if accesos:
        for acc in accesos:
            status = "✅ EXITOSO" if acc.exito else "❌ FALLIDO"
            print(f"{status} | {acc.timestamp} | IP: {acc.ip}")
            if not acc.exito and acc.motivo:
                print(f"         Motivo: {acc.motivo}")
    else:
        print("No hay registros de acceso para este usuario")
    
    print(f"\n{'='*60}")
    print(f"RESUMEN DEL PROBLEMA")
    print(f"{'='*60}\n")
    
    if not user.activo:
        print("❌ PROBLEMA PRINCIPAL: Usuario INACTIVO")
        print("   Solución: Activar el usuario desde el panel de administración")
        print(f"   O ejecutar: UPDATE usuarios SET activo = true WHERE id = {user.id};\n")
    
    if not user.password_hash:
        print("❌ El usuario NO TIENE contraseña establecida")
        print("   Solución: Enviar enlace de recuperación de contraseña\n")
    else:
        print("✅ El usuario tiene contraseña establecida")
        print(f"   Hash: {user.password_hash[:60]}...\n")
        print("⚠️  No puedo descifrar la contraseña (está hasheada con bcrypt)")
        print("   Si no recuerdas la contraseña, debes usar recuperación de contraseña\n")
