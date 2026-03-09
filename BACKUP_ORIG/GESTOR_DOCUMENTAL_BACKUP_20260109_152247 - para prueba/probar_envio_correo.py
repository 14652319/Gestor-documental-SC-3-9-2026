"""Probar envío de correo SMTP del sistema"""
from app import app
from modules.dian_vs_erp.scheduler_envios import scheduler_dian_vs_erp_global
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

with app.app_context():
    print("\n" + "="*80)
    print("🧪 PRUEBA DE ENVÍO DE CORREO SMTP")
    print("="*80)
    
    # 1. Verificar configuración SMTP
    print("\n📋 CONFIGURACIÓN SMTP:")
    smtp_config = scheduler_dian_vs_erp_global.smtp_config
    print(f"   Servidor: {smtp_config['server']}")
    print(f"   Puerto: {smtp_config['port']}")
    print(f"   Usuario: {smtp_config['username']}")
    print(f"   SSL: {smtp_config['use_ssl']}")
    print(f"   TLS: {smtp_config['use_tls']}")
    print(f"   Password configurado: {'✅ SÍ' if smtp_config['password'] else '❌ NO'}")
    
    # 2. Verificar usuarios en BD
    print("\n📊 USUARIOS EN BASE DE DATOS:")
    from extensions import db
    query = "SELECT nit, correo, nombres, apellidos, activo FROM usuarios_asignados WHERE activo = true"
    result = db.session.execute(db.text(query))
    usuarios = result.fetchall()
    print(f"   Total usuarios activos: {len(usuarios)}")
    for u in usuarios:
        print(f"   - NIT: {u[0]}, Correo: {u[1]}, Nombre: {u[2]} {u[3]}")
    
    # 3. Probar envío de correo de prueba
    print("\n📧 ENVIANDO CORREO DE PRUEBA...")
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_config['username']
        msg['To'] = 'ricardoriascos07@gmail.com'
        msg['Subject'] = '🧪 TEST - Sistema DIAN vs ERP'
        
        html = """
        <html>
        <body>
            <h2>✅ Prueba de Envío Exitosa</h2>
            <p>Este es un correo de prueba del sistema DIAN vs ERP.</p>
            <p>Si recibes esto, el envío SMTP está funcionando correctamente.</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(html, 'html'))
        
        # Enviar con SSL (puerto 465)
        if smtp_config['use_ssl']:
            with smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port']) as server:
                server.login(smtp_config['username'], smtp_config['password'])
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
                if smtp_config['use_tls']:
                    server.starttls()
                server.login(smtp_config['username'], smtp_config['password'])
                server.send_message(msg)
        
        print("   ✅ CORREO ENVIADO EXITOSAMENTE")
        print(f"   📬 Destinatario: ricardoriascos07@gmail.com")
        print("   ℹ️  Revisa tu bandeja de entrada o carpeta de SPAM")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*80)
