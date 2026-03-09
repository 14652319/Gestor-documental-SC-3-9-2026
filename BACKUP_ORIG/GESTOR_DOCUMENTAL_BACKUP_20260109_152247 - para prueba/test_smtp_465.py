"""
Test SMTP con puerto 465 (SSL)
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*80)
print("🔍 TEST SMTP - PUERTO 465 (SSL)")
print("="*80)

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465  # Puerto SSL
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

print(f"\n📧 Configuración:")
print(f"  ├─ Servidor: {MAIL_SERVER}")
print(f"  ├─ Puerto: {MAIL_PORT} (SSL)")
print(f"  ├─ Usuario: {MAIL_USERNAME}")
print(f"  └─ Password: {'*' * len(MAIL_PASSWORD) if MAIL_PASSWORD else 'NO CONFIGURADO'}")

if not MAIL_USERNAME or not MAIL_PASSWORD:
    print("\n❌ ERROR: Credenciales no configuradas")
    exit(1)

destinatario = input("\n📬 Ingresa el correo de destino: ").strip()

if not destinatario or '@' not in destinatario:
    print("❌ Correo no válido")
    exit(1)

print(f"\n⏳ Conectando a {MAIL_SERVER}:{MAIL_PORT} con SSL...")

try:
    # Usar SMTP_SSL en lugar de SMTP para puerto 465
    server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT, timeout=10)
    print("✅ Conexión SSL establecida")
    
    # Login
    print(f"⏳ Autenticando como {MAIL_USERNAME}...")
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    print("✅ Autenticación exitosa")
    
    # Crear mensaje
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '🔐 Código de Recuperación - 123456'
    msg['From'] = MAIL_USERNAME
    msg['To'] = destinatario
    
    texto = """
🔐 Recuperación de Contraseña

Tu Código de Verificación: 123456

Este es un correo de prueba del sistema (Puerto 465/SSL).
"""
    
    html = """
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px;">
                <h1 style="color: #3b82f6;">🔐 Recuperación de Contraseña</h1>
                <p>Tu Código de Verificación:</p>
                <div style="background: #eff6ff; border: 3px solid #3b82f6; border-radius: 10px; padding: 20px; text-align: center;">
                    <div style="font-size: 3em; font-weight: bold; color: #1e3a8a; letter-spacing: 8px;">123456</div>
                </div>
                <p style="color: #6b7280; margin-top: 20px;">Este es un correo de prueba del sistema (Puerto 465/SSL).</p>
            </div>
        </body>
    </html>
    """
    
    parte_texto = MIMEText(texto, 'plain', 'utf-8')
    parte_html = MIMEText(html, 'html', 'utf-8')
    
    msg.attach(parte_texto)
    msg.attach(parte_html)
    
    print(f"\n⏳ Enviando correo a {destinatario}...")
    server.send_message(msg)
    print("✅ CORREO ENVIADO EXITOSAMENTE")
    print(f"\n📬 Revisa la bandeja de entrada de: {destinatario}")
    print("   También revisa la carpeta de SPAM/Correo no deseado")
    
    server.quit()
    print("\n✅ Prueba completada - Puerto 465 funciona correctamente")
    
except Exception as e:
    print(f"\n❌ ERROR:")
    print(f"   {str(e)}")
    print(f"   Tipo: {type(e).__name__}")
    
    import traceback
    print("\n📋 Traceback:")
    traceback.print_exc()
    
    print("\n💡 El puerto 465 también está bloqueado.")
    print("   Necesitas configurar el firewall/antivirus para permitir:")
    print("   - Puerto 587 (TLS)")
    print("   - Puerto 465 (SSL)")

print("\n" + "="*80)
