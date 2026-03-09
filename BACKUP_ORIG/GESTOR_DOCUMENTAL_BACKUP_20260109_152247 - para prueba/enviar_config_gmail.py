#!/usr/bin/env python3
"""
Script para enviar configuración Gmail del Gestor Documental
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def enviar_configuracion_gmail():
    """Envía la configuración Gmail por correo electrónico"""
    
    # Configuración del correo
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    smtp_ssl = True
    
    # Credenciales del sistema
    remitente = os.getenv('MAIL_USERNAME', 'gestordocumentalsc01@gmail.com')
    password = os.getenv('MAIL_PASSWORD', 'urjrkjlogcfdtynq')
    
    # Destinatario
    destinatario = "ricardoriascso07@gmail.com"
    
    # Crear mensaje
    mensaje = MIMEMultipart('alternative')
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = "🔧 Configuración Gmail - Gestor Documental Supertiendas Cañaveral"
    
    # Contenido HTML del correo
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: linear-gradient(135deg, #20c997, #17a2b8); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f8f9fa; padding: 20px; }}
        .config-box {{ background: white; border-left: 4px solid #20c997; padding: 15px; margin: 15px 0; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .config-title {{ font-weight: bold; color: #20c997; margin-bottom: 10px; }}
        .config-item {{ margin: 8px 0; font-family: 'Courier New', monospace; background: #f1f3f4; padding: 8px; border-radius: 4px; }}
        .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 15px 0; border-radius: 4px; }}
        .success {{ background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 15px 0; border-radius: 4px; }}
        .footer {{ text-align: center; padding: 20px; color: #6c757d; font-size: 12px; }}
        .code {{ background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 6px; overflow-x: auto; font-family: 'Courier New', monospace; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📧 Configuración Gmail</h1>
        <p>Gestor Documental - Supertiendas Cañaveral</p>
    </div>
    
    <div class="content">
        <div class="success">
            <strong>✅ Estado:</strong> Correo configurado y funcionando correctamente<br>
            <strong>📅 Fecha:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            <strong>🎯 Propósito:</strong> Envío de confirmaciones de registro y tokens de recuperación
        </div>

        <div class="config-box">
            <div class="config-title">📋 Datos de la Cuenta Gmail</div>
            <div class="config-item"><strong>Correo:</strong> gestordocumentalsc01@gmail.com</div>
            <div class="config-item"><strong>Contraseña de App:</strong> urjrkjlogcfdtynq</div>
            <div class="config-item"><strong>2FA:</strong> Habilitado ✅</div>
        </div>

        <div class="config-box">
            <div class="config-title">⚙️ Configuración SMTP</div>
            <div class="config-item"><strong>Servidor:</strong> smtp.gmail.com</div>
            <div class="config-item"><strong>Puerto:</strong> 465 (SSL) / 587 (TLS)</div>
            <div class="config-item"><strong>Cifrado:</strong> SSL habilitado</div>
            <div class="config-item"><strong>TLS:</strong> Opcional (puerto 587)</div>
        </div>

        <div class="config-box">
            <div class="config-title">🔧 Variables de Entorno (.env)</div>
            <div class="code">
MAIL_PROVIDER=gmail
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True
MAIL_USERNAME=gestordocumentalsc01@gmail.com
MAIL_PASSWORD=urjrkjlogcfdtynq
MAIL_DEFAULT_SENDER=gestordocumentalsc01@gmail.com
            </div>
        </div>

        <div class="config-box">
            <div class="config-title">🐍 Configuración Python (Flask-Mail)</div>
            <div class="code">
from flask_mail import Mail, Message
from flask import Flask

app = Flask(__name__)

# Configuración
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'gestordocumentalsc01@gmail.com'
app.config['MAIL_PASSWORD'] = 'urjrkjlogcfdtynq'
app.config['MAIL_DEFAULT_SENDER'] = 'gestordocumentalsc01@gmail.com'

mail = Mail(app)
            </div>
        </div>

        <div class="config-box">
            <div class="config-title">🔐 Información de Seguridad</div>
            <div class="config-item"><strong>Tipo de Contraseña:</strong> Contraseña de Aplicación (App Password)</div>
            <div class="config-item"><strong>2FA Requerido:</strong> Sí, debe estar habilitado en Gmail</div>
            <div class="config-item"><strong>Validez:</strong> La contraseña de app no expira automáticamente</div>
            <div class="config-item"><strong>Revocación:</strong> Se puede revocar desde configuración de Google</div>
        </div>

        <div class="warning">
            <strong>⚠️ Importante:</strong><br>
            • Esta es una <strong>contraseña de aplicación</strong>, NO la contraseña personal de Gmail<br>
            • Se generó específicamente para el Gestor Documental<br>
            • Mantener esta información confidencial<br>
            • No compartir con terceros no autorizados
        </div>

        <div class="config-box">
            <div class="config-title">🧪 Test de Conexión</div>
            <div class="code">
# Script de prueba
import smtplib
from email.mime.text import MIMEText

server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.login('gestordocumentalsc01@gmail.com', 'urjrkjlogcfdtynq')

msg = MIMEText('Prueba de conexión exitosa')
msg['Subject'] = 'Test Gmail'
msg['From'] = 'gestordocumentalsc01@gmail.com'
msg['To'] = 'destino@ejemplo.com'

server.send_message(msg)
server.quit()
print("✅ Conexión exitosa")
            </div>
        </div>

        <div class="config-box">
            <div class="config-title">📞 Soporte y Contacto</div>
            <div class="config-item"><strong>Sistema:</strong> Gestor Documental v2.0</div>
            <div class="config-item"><strong>Desarrollador:</strong> Sistema Interno</div>
            <div class="config-item"><strong>Servidor:</strong> http://127.0.0.1:8099</div>
            <div class="config-item"><strong>Base de Datos:</strong> PostgreSQL 18</div>
        </div>
    </div>
    
    <div class="footer">
        <p>📧 Correo generado automáticamente por el Gestor Documental</p>
        <p>🏢 Supertiendas Cañaveral - Sistema de Gestión Documental</p>
        <p>🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
    """
    
    # Crear parte HTML
    html_part = MIMEText(html_content, 'html', 'utf-8')
    mensaje.attach(html_part)
    
    try:
        print("📧 Enviando configuración Gmail...")
        print(f"📨 Remitente: {remitente}")
        print(f"📬 Destinatario: {destinatario}")
        
        # Conectar y enviar
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as servidor:
            servidor.login(remitente, password)
            servidor.send_message(mensaje)
        
        print("✅ ¡Configuración enviada exitosamente!")
        print(f"📧 Revisa tu bandeja de entrada: {destinatario}")
        
    except Exception as e:
        print(f"❌ Error al enviar: {e}")
        return False
    
    return True

def mostrar_resumen_local():
    """Muestra resumen local de la configuración"""
    print("\n" + "="*60)
    print("📧 CONFIGURACIÓN GMAIL - GESTOR DOCUMENTAL")
    print("="*60)
    print(f"📧 Correo del Sistema: gestordocumentalsc01@gmail.com")
    print(f"🔐 Contraseña de App:  urjrkjlogcfdtynq")
    print(f"🌐 Servidor SMTP:      smtp.gmail.com")
    print(f"🔌 Puerto:             465 (SSL) / 587 (TLS)")
    print(f"🔒 Cifrado:            SSL Habilitado")
    print(f"✅ Estado:             Configurado y Funcionando")
    print("="*60)

if __name__ == "__main__":
    print("🔧 Enviador de Configuración Gmail - Gestor Documental")
    print("🎯 Destinatario: ricardoriascso07@gmail.com")
    
    # Mostrar resumen local
    mostrar_resumen_local()
    
    # Enviar por correo
    resultado = enviar_configuracion_gmail()
    
    if resultado:
        print("\n🎉 ¡Configuración enviada correctamente!")
        print("📱 Revisa tu correo electrónico")
    else:
        print("\n❌ Error en el envío")
        print("💡 La configuración se mostró arriba de todas formas")