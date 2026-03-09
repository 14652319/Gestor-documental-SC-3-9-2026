"""
Test directo de conexión SMTP sin Flask
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*80)
print("🔍 DIAGNÓSTICO DE CONEXIÓN SMTP")
print("="*80)

# Configuración
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

print(f"\n📧 Configuración:")
print(f"  ├─ Servidor: {MAIL_SERVER}")
print(f"  ├─ Puerto: {MAIL_PORT}")
print(f"  ├─ Usuario: {MAIL_USERNAME}")
print(f"  └─ Password: {'*' * len(MAIL_PASSWORD) if MAIL_PASSWORD else 'NO CONFIGURADO'}")

if not MAIL_USERNAME or not MAIL_PASSWORD:
    print("\n❌ ERROR: Credenciales de correo no configuradas en .env")
    exit(1)

# Solicitar destinatario
destinatario = input("\n📬 Ingresa el correo de destino: ").strip()

if not destinatario or '@' not in destinatario:
    print("❌ Correo no válido")
    exit(1)

print(f"\n⏳ Conectando a {MAIL_SERVER}:{MAIL_PORT}...")

try:
    # Crear conexión SMTP
    server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=10)
    print("✅ Conexión establecida")
    
    # Iniciar TLS
    print("⏳ Iniciando TLS...")
    server.starttls()
    print("✅ TLS activado")
    
    # Login
    print(f"⏳ Autenticando como {MAIL_USERNAME}...")
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    print("✅ Autenticación exitosa")
    
    # Crear mensaje
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '🔐 Código de Recuperación - 123456'
    msg['From'] = MAIL_USERNAME
    msg['To'] = destinatario
    
    # Texto plano
    texto = """
🔐 Recuperación de Contraseña

Tu Código de Verificación: 123456

Este es un correo de prueba del sistema.
"""
    
    # HTML
    html = """
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px;">
                <h1 style="color: #3b82f6;">🔐 Recuperación de Contraseña</h1>
                <p>Tu Código de Verificación:</p>
                <div style="background: #eff6ff; border: 3px solid #3b82f6; border-radius: 10px; padding: 20px; text-align: center;">
                    <div style="font-size: 3em; font-weight: bold; color: #1e3a8a; letter-spacing: 8px;">123456</div>
                </div>
                <p style="color: #6b7280; margin-top: 20px;">Este es un correo de prueba del sistema.</p>
            </div>
        </body>
    </html>
    """
    
    parte_texto = MIMEText(texto, 'plain', 'utf-8')
    parte_html = MIMEText(html, 'html', 'utf-8')
    
    msg.attach(parte_texto)
    msg.attach(parte_html)
    
    # Enviar
    print(f"\n⏳ Enviando correo a {destinatario}...")
    server.send_message(msg)
    print("✅ CORREO ENVIADO EXITOSAMENTE")
    print(f"\n📬 Revisa la bandeja de entrada de: {destinatario}")
    print("   También revisa la carpeta de SPAM/Correo no deseado")
    
    # Cerrar conexión
    server.quit()
    print("\n✅ Prueba completada exitosamente")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ ERROR DE AUTENTICACIÓN:")
    print(f"   {str(e)}")
    print("\n💡 Posibles soluciones:")
    print("   1. Verifica que el correo y contraseña sean correctos")
    print("   2. Si es Gmail, asegúrate de usar una 'Contraseña de aplicación'")
    print("   3. Habilita 'Acceso de apps menos seguras' (no recomendado)")
    print("   4. Verifica que la verificación en 2 pasos esté configurada")
    
except smtplib.SMTPConnectError as e:
    print(f"\n❌ ERROR DE CONEXIÓN:")
    print(f"   {str(e)}")
    print("\n💡 Posibles soluciones:")
    print("   1. Verifica tu conexión a internet")
    print("   2. Verifica que el servidor y puerto sean correctos")
    print("   3. Revisa el firewall/antivirus")
    
except Exception as e:
    print(f"\n❌ ERROR INESPERADO:")
    print(f"   {str(e)}")
    print(f"   Tipo: {type(e).__name__}")
    
    import traceback
    print("\n📋 Traceback completo:")
    traceback.print_exc()

print("\n" + "="*80)
