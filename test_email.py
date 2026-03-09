"""
Script de prueba para verificar envío de correos con Gmail
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_gmail_connection():
    """Prueba la conexión y envío de correo con Gmail"""
    
    # Obtener configuración
    smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('MAIL_PORT', 587))
    username = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    sender = os.getenv('MAIL_DEFAULT_SENDER')
    
    print("=" * 60)
    print("🔍 VERIFICANDO CONFIGURACIÓN DE CORREO")
    print("=" * 60)
    print(f"Servidor SMTP: {smtp_server}")
    print(f"Puerto: {smtp_port}")
    print(f"Usuario: {username}")
    print(f"Password configurado: {'✅ Sí' if password else '❌ No'}")
    print(f"Remitente: {sender}")
    print("=" * 60)
    
    if not username or not password:
        print("❌ ERROR: No hay credenciales configuradas en .env")
        return False
    
    try:
        print("\n📧 Intentando conectar con Gmail...")
        
        # Correo de destino para prueba
        destino = "rriascos@supertiendascanaveral.com"
        
        # Crear mensaje de prueba
        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = destino
        message['Subject'] = "✅ Prueba de Correo - Gestor Documental"
        
        body = """
        <html>
            <body>
                <h2>🎉 Prueba de Correo Exitosa</h2>
                <p>Este es un correo de prueba del sistema Gestor Documental.</p>
                <p>Si recibes este mensaje, la configuración de Gmail está funcionando correctamente.</p>
                <hr>
                <p><small>Servidor: {}</small></p>
                <p><small>Puerto: {}</small></p>
            </body>
        </html>
        """.format(smtp_server, smtp_port)
        
        message.attach(MIMEText(body, 'html'))
        
        # Conectar con Gmail
        print(f"🔌 Conectando a {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        
        print("🔐 Iniciando TLS...")
        server.starttls()
        
        print("👤 Autenticando...")
        server.login(username, password)
        
        print("📨 Enviando correo de prueba...")
        server.send_message(message)
        
        print("🚪 Cerrando conexión...")
        server.quit()
        
        print("\n" + "=" * 60)
        print("✅ ¡CORREO ENVIADO EXITOSAMENTE!")
        print(f"📬 Revisa la bandeja de entrada de: {destino}")
        print("=" * 60)
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print("\n❌ ERROR DE AUTENTICACIÓN")
        print("La contraseña de aplicación de Gmail no es válida.")
        print(f"Detalles: {e}")
        return False
        
    except smtplib.SMTPConnectError as e:
        print("\n❌ ERROR DE CONEXIÓN")
        print("No se pudo conectar con el servidor SMTP de Gmail.")
        print(f"Detalles: {e}")
        return False
        
    except smtplib.SMTPException as e:
        print("\n❌ ERROR SMTP")
        print(f"Detalles: {e}")
        return False
        
    except Exception as e:
        print("\n❌ ERROR INESPERADO")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensaje: {e}")
        return False

if __name__ == "__main__":
    test_gmail_connection()
