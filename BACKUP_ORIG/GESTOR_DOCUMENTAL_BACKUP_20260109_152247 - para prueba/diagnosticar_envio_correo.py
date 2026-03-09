"""
Verificar qué está pasando con el envío de correos
"""

import json
from app import app, db
from modules.dian_vs_erp.models import (
    EnvioProgramadoDianVsErp, 
    MaestroDianVsErp, 
    UsuarioAsignadoDianVsErp
)

with app.app_context():
    print("\n" + "=" * 80)
    print("🔍 DIAGNÓSTICO DE ENVÍO DE CORREOS")
    print("=" * 80)
    
    # Obtener configuración ID 6 (Alerta sin causar 5 dias)
    config = EnvioProgramadoDianVsErp.query.get(6)
    
    if not config:
        print("❌ No se encontró la configuración ID 6")
        exit(1)
    
    print(f"\n📋 Configuración ID {config.id}: {config.nombre}")
    print(f"   Tipo: {config.tipo}")
    print(f"   Días mínimos: {config.dias_minimos}")
    print(f"   estados_excluidos: {config.estados_excluidos}")
    
    # Parsear estados_excluidos
    estados_excl = []
    if config.estados_excluidos:
        try:
            parsed = json.loads(config.estados_excluidos)
            estados_excl = parsed if isinstance(parsed, list) else []
        except:
            pass
    
    print(f"   Estados excluidos parseados: {estados_excl}")
    
    # Buscar documentos pendientes
    print(f"\n🔍 Buscando documentos con >= {config.dias_minimos} días...")
    query = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.dias_desde_emision >= config.dias_minimos
    )
    
    if estados_excl:
        query = query.filter(~MaestroDianVsErp.estado_aprobacion.in_(estados_excl))
    
    documentos = query.all()
    
    print(f"   ✅ Encontrados {len(documentos)} documentos")
    
    if len(documentos) == 0:
        print("\n❌ NO HAY DOCUMENTOS PARA ENVIAR")
        print("   Esto explica por qué no se envía correo.")
        exit(0)
    
    # Mostrar primeros 5 documentos
    print("\n📄 Primeros 5 documentos encontrados:")
    for doc in documentos[:5]:
        print(f"   - {doc.nit_emisor} | {doc.prefijo}-{doc.folio} | {doc.dias_desde_emision} días | Estado: {doc.estado_aprobacion}")
    
    # Agrupar por NIT
    print(f"\n📊 Agrupando por NIT emisor...")
    docs_por_nit = {}
    for doc in documentos:
        nit = doc.nit_emisor
        if nit not in docs_por_nit:
            docs_por_nit[nit] = []
        docs_por_nit[nit].append(doc)
    
    print(f"   ✅ {len(docs_por_nit)} NITs diferentes")
    
    # Buscar usuarios asignados
    print(f"\n👥 Buscando usuarios asignados...")
    docs_por_usuario = {}
    total_usuarios = 0
    
    for nit, docs in docs_por_nit.items():
        usuarios = UsuarioAsignadoDianVsErp.query.filter_by(nit=nit, activo=True).all()
        print(f"\n   NIT {nit}: {len(docs)} documentos, {len(usuarios)} usuarios")
        
        if len(usuarios) == 0:
            print(f"      ⚠️ NO hay usuarios asignados para este NIT")
        
        for usuario in usuarios:
            email = usuario.correo
            print(f"      📧 {email}")
            if email not in docs_por_usuario:
                docs_por_usuario[email] = []
            docs_por_usuario[email].extend(docs)
            total_usuarios += 1
    
    print(f"\n📧 Total de destinatarios: {len(docs_por_usuario)}")
    
    if len(docs_por_usuario) == 0:
        print("\n❌ NO HAY USUARIOS ASIGNADOS CON CORREO")
        print("   Esto explica por qué no se envía correo.")
        print("\n💡 SOLUCIÓN:")
        print("   1. Ve a la pestaña 'Usuarios por NIT'")
        print(f"   2. Busca el NIT 805013653")
        print("   3. Agrega un usuario con su correo (ej: ricardoriascos07@gmail.com)")
        print("   4. Marca como 'Activo'")
        print("   5. Vuelve a ejecutar el envío")
    else:
        print("\n✅ HAY USUARIOS CONFIGURADOS:")
        for email, docs in list(docs_por_usuario.items())[:3]:
            print(f"   📧 {email}: {len(docs)} documentos")
        
        print("\n📧 Verificando configuración SMTP...")
        from flask import current_app
        
        smtp_config = {
            'server': current_app.config.get('MAIL_SERVER'),
            'port': current_app.config.get('MAIL_PORT'),
            'username': current_app.config.get('MAIL_USERNAME'),
            'password': '***' if current_app.config.get('MAIL_PASSWORD') else None,
            'use_tls': current_app.config.get('MAIL_USE_TLS'),
            'use_ssl': current_app.config.get('MAIL_USE_SSL')
        }
        
        print(f"   Server: {smtp_config['server']}")
        print(f"   Port: {smtp_config['port']}")
        print(f"   Username: {smtp_config['username']}")
        print(f"   Password: {'✅ Configurada' if smtp_config['password'] else '❌ NO configurada'}")
        print(f"   TLS: {smtp_config['use_tls']}")
        print(f"   SSL: {smtp_config['use_ssl']}")
        
        if not smtp_config['server']:
            print("\n❌ CONFIGURACIÓN SMTP FALTANTE")
            print("   Debes configurar las variables en .env:")
            print("   MAIL_SERVER=smtp.gmail.com")
            print("   MAIL_PORT=465")
            print("   MAIL_USE_SSL=True")
            print("   MAIL_USERNAME=tu@correo.com")
            print("   MAIL_PASSWORD=tu_contraseña")
    
    print("\n" + "=" * 80)
