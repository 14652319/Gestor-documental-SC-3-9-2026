"""
Script para probar el envío de correo de recuperación de contraseña
"""
import os
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message

# Cargar variables de entorno
load_dotenv()

# Configuración básica de Flask
app = Flask(__name__)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# Inicializar Flask-Mail
mail = Mail(app)

def test_envio_recuperacion():
    """Prueba el envío de correo de recuperación"""
    
    print("\n" + "="*60)
    print("🔍 PRUEBA DE ENVÍO DE CORREO DE RECUPERACIÓN")
    print("="*60)
    
    # Mostrar configuración
    print("\n📧 Configuración de correo:")
    print(f"  ├─ Servidor: {app.config['MAIL_SERVER']}")
    print(f"  ├─ Puerto: {app.config['MAIL_PORT']}")
    print(f"  ├─ TLS: {app.config['MAIL_USE_TLS']}")
    print(f"  ├─ SSL: {app.config['MAIL_USE_SSL']}")
    print(f"  ├─ Usuario: {app.config['MAIL_USERNAME']}")
    print(f"  ├─ Password: {'*' * len(app.config['MAIL_PASSWORD']) if app.config['MAIL_PASSWORD'] else 'NO CONFIGURADO'}")
    print(f"  └─ Remitente: {app.config['MAIL_DEFAULT_SENDER']}")
    
    # Verificar configuración
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        print("\n❌ ERROR: No hay configuración de correo")
        return
    
    # Solicitar correo de destino
    destinatario = input("\n📬 Ingresa el correo de destino para la prueba: ").strip()
    
    if not destinatario or '@' not in destinatario:
        print("❌ Correo no válido")
        return
    
    # Datos de prueba
    nit = "805028041"
    nombre_usuario = "admin"
    token = "123456"
    
    print(f"\n📤 Enviando correo de prueba a: {destinatario}")
    print(f"  ├─ Usuario: {nombre_usuario}")
    print(f"  ├─ NIT: {nit}")
    print(f"  └─ Token: {token}")
    
    try:
        # HTML del correo (versión simplificada)
        html_body = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f3f4f6; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; 
                            border-radius: 12px; overflow: hidden; }}
                .header {{ background: linear-gradient(145deg, #3b82f6, #2563eb); 
                          color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .token-box {{ background: #eff6ff; border: 3px solid #3b82f6; 
                             border-radius: 12px; padding: 30px; margin: 25px 0; text-align: center; }}
                .token-number {{ color: #1e3a8a; font-size: 3em; font-weight: bold; 
                                letter-spacing: 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Recuperación de Contraseña</h1>
                </div>
                <div class="content">
                    <p>Hola, <strong>{nombre_usuario}</strong></p>
                    <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta.</p>
                    <div class="token-box">
                        <div class="token-number">{token}</div>
                    </div>
                    <p><strong>Usuario:</strong> {nombre_usuario}</p>
                    <p><strong>NIT:</strong> {nit}</p>
                    <p style="color: #dc2626;"><strong>⏱️ Este código expira en 10 minutos</strong></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Texto plano
        text_body = f"""
🔐 Recuperación de Contraseña

Hola, {nombre_usuario}

Tu Código de Verificación: {token}

Usuario: {nombre_usuario}
NIT: {nit}

Este código expira en 10 minutos.
        """
        
        # Crear mensaje
        with app.app_context():
            msg = Message(
                subject=f"Código de Recuperación - {token}",
                recipients=[destinatario],
                body=text_body,
                html=html_body
            )
            
            print("\n⏳ Enviando correo...")
            mail.send(msg)
            print("✅ CORREO ENVIADO EXITOSAMENTE")
            print(f"   Verifica la bandeja de entrada de: {destinatario}")
            print("   También revisa la carpeta de SPAM/Correo no deseado")
        
    except Exception as e:
        print(f"\n❌ ERROR al enviar correo:")
        print(f"   {str(e)}")
        import traceback
        print("\n📋 Traceback completo:")
        traceback.print_exc()

if __name__ == "__main__":
    test_envio_recuperacion()
