# -*- coding: utf-8 -*-
"""
Script de diagnóstico completo para correos de supervisión
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("=" * 80)
print("🔍 DIAGNÓSTICO COMPLETO DE CORREOS DE SUPERVISIÓN")
print("=" * 80)

# 1. VERIFICAR CONFIGURACIÓN
print("\n📧 PASO 1: Verificar configuración en .env")
print("-" * 80)

mail_server = os.getenv('MAIL_SERVER')
mail_port = os.getenv('MAIL_PORT')
mail_username = os.getenv('MAIL_USERNAME')
mail_password = os.getenv('MAIL_PASSWORD')
mail_use_tls = os.getenv('MAIL_USE_TLS', 'False')
mail_use_ssl = os.getenv('MAIL_USE_SSL', 'True')

print(f"   MAIL_SERVER: {mail_server}")
print(f"   MAIL_PORT: {mail_port}")
print(f"   MAIL_USE_TLS: {mail_use_tls}")
print(f"   MAIL_USE_SSL: {mail_use_ssl}")
print(f"   MAIL_USERNAME: {mail_username}")
print(f"   MAIL_PASSWORD: {'✅ Configurado (' + str(len(mail_password)) + ' chars)' if mail_password else '❌ NO configurado'}")

if not mail_username or not mail_password:
    print("\n❌ ERROR: Correo no configurado correctamente")
    sys.exit(1)

print("\n✅ Configuración del correo OK")

# 2. PROBAR CONEXIÓN SMTP
print("\n🔌 PASO 2: Probar conexión SMTP")
print("-" * 80)

try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # Intentar conectar
    if mail_use_ssl == 'True':
        print(f"   Conectando con SSL a {mail_server}:{mail_port}...")
        server = smtplib.SMTP_SSL(mail_server, int(mail_port), timeout=10)
    else:
        print(f"   Conectando con TLS a {mail_server}:{mail_port}...")
        server = smtplib.SMTP(mail_server, int(mail_port), timeout=10)
        if mail_use_tls == 'True':
            server.starttls()
    
    print("   ✅ Conexión establecida")
    
    # Intentar autenticarse
    print(f"   Autenticando como {mail_username}...")
    server.login(mail_username, mail_password)
    print("   ✅ Autenticación exitosa")
    
    # Preguntar si enviar correo de prueba
    print("\n" + "=" * 80)
    respuesta = input("¿Deseas enviar un correo de prueba? (s/n): ").strip().lower()
    
    if respuesta == 's':
        email_destino = input("📧 Ingresa el correo destino: ").strip()
        
        print(f"\n📨 Enviando correo de prueba a {email_destino}...")
        
        # Crear mensaje de prueba
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🔍 Prueba de Supervisión - Sistema OK"
        msg['From'] = mail_username
        msg['To'] = email_destino
        
        html = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #00c875; border-bottom: 3px solid #00c875; padding-bottom: 10px;">
                    ✅ Correo de Prueba Exitoso
                </h2>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    Este es un correo de prueba del <strong>Sistema de Supervisión</strong>.
                </p>
                <p style="font-size: 14px; color: #666; line-height: 1.6;">
                    Si recibiste este correo, significa que:
                </p>
                <ul style="font-size: 14px; color: #666; line-height: 1.8;">
                    <li>✅ La configuración SMTP está correcta</li>
                    <li>✅ Las credenciales de Gmail funcionan</li>
                    <li>✅ El servidor puede enviar correos</li>
                    <li>✅ Los correos de supervisión deberían funcionar</li>
                </ul>
                <div style="margin-top: 30px; padding: 15px; background-color: #e8f5e9; border-left: 4px solid #4caf50; border-radius: 5px;">
                    <p style="margin: 0; font-size: 14px; color: #2e7d32;">
                        <strong>📊 Datos de configuración:</strong><br>
                        Servidor: """ + mail_server + """<br>
                        Puerto: """ + mail_port + """<br>
                        Usuario: """ + mail_username + """<br>
                        Fecha: """ + """<script>document.write(new Date().toLocaleString('es-CO'));</script>
                    </p>
                </div>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #999; text-align: center; margin: 0;">
                    Sistema de Supervisión - Gestor Documental<br>
                    Supertiendas Cañaveral
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        # Enviar
        server.sendmail(mail_username, [email_destino], msg.as_string())
        print("   ✅ ¡Correo enviado exitosamente!")
        print(f"\n   Revisa la bandeja de entrada de {email_destino}")
        print("   (También revisa la carpeta de SPAM si no lo ves)")
    
    server.quit()
    print("\n✅ Conexión cerrada correctamente")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ ERROR DE AUTENTICACIÓN: {e}")
    print("\nPosibles causas:")
    print("1. Contraseña de aplicación incorrecta")
    print("2. Verificación en 2 pasos no habilitada en Gmail")
    print("3. Contraseña de aplicación revocada")
    print("\nSolución:")
    print("1. Ve a https://myaccount.google.com/apppasswords")
    print("2. Genera una nueva contraseña de aplicación")
    print("3. Actualiza MAIL_PASSWORD en el archivo .env")
    sys.exit(1)
    
except smtplib.SMTPConnectError as e:
    print(f"\n❌ ERROR DE CONEXIÓN: {e}")
    print("\nPosibles causas:")
    print("1. Puerto bloqueado por firewall")
    print("2. Servidor SMTP incorrecto")
    print("3. Sin conexión a Internet")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ ERROR INESPERADO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. VERIFICAR CONFIGURACIONES DE SUPERVISIÓN
print("\n" + "=" * 80)
print("📋 PASO 3: Verificar configuraciones de supervisión en BD")
print("-" * 80)

try:
    from app import app, db
    from modules.dian_vs_erp.models import EnvioProgramadoDianVsErp
    
    with app.app_context():
        configs_supervision = EnvioProgramadoDianVsErp.query.filter_by(
            es_supervision=True,
            activo=True
        ).all()
        
        if not configs_supervision:
            print("   ⚠️ No hay configuraciones de supervisión activas")
        else:
            print(f"   ✅ {len(configs_supervision)} configuración(es) de supervisión activa(s):\n")
            for config in configs_supervision:
                print(f"   📧 ID: {config.id}")
                print(f"      Nombre: {config.nombre}")
                print(f"      Email supervisor: {config.email_supervisor}")
                print(f"      Frecuencia: Cada {config.frecuencia_dias} días")
                print(f"      Próxima ejecución: {config.proxima_ejecucion}")
                print()
        
except Exception as e:
    print(f"   ⚠️ No se pudo verificar BD: {e}")

print("\n" + "=" * 80)
print("✅ DIAGNÓSTICO COMPLETO")
print("=" * 80)
print("\nSi el correo de prueba llegó correctamente, el problema podría ser:")
print("1. El scheduler no está ejecutando la función de supervisión")
print("2. Hay un error en la función _enviar_supervision_general()")
print("3. Los correos se están enviando pero van a SPAM")
print("\nRevisa también:")
print("- La tabla 'historial_envios_dian_vs_erp' en la base de datos")
print("- Los logs del servidor Flask cuando ejecutas manualmente")
