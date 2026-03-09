# -*- coding: utf-8 -*-
"""
Script para probar el envío de correo de supervisión
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("=" * 80)
print("🔍 VERIFICACIÓN DE CONFIGURACIÓN DE CORREO")
print("=" * 80)

# Verificar variables de entorno
mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
mail_port = os.getenv('MAIL_PORT', '587')
mail_username = os.getenv('MAIL_USERNAME')
mail_password = os.getenv('MAIL_PASSWORD')
mail_use_tls = os.getenv('MAIL_USE_TLS', 'True')

print(f"\n📧 Configuración de correo:")
print(f"   MAIL_SERVER: {mail_server}")
print(f"   MAIL_PORT: {mail_port}")
print(f"   MAIL_USE_TLS: {mail_use_tls}")
print(f"   MAIL_USERNAME: {'✅ Configurado' if mail_username else '❌ NO configurado'}")
print(f"   MAIL_PASSWORD: {'✅ Configurado' if mail_password else '❌ NO configurado'}")

if not mail_username or not mail_password:
    print("\n" + "=" * 80)
    print("❌ ERROR: Correo no configurado")
    print("=" * 80)
    print("\nPara configurar el correo, agrega estas líneas a tu archivo .env:")
    print("\nMAIL_SERVER=smtp.gmail.com")
    print("MAIL_PORT=587")
    print("MAIL_USE_TLS=True")
    print("MAIL_USERNAME=tu_correo@gmail.com")
    print("MAIL_PASSWORD=tu_contraseña_de_aplicacion")
    print("MAIL_DEFAULT_SENDER=tu_correo@gmail.com")
    print("\n⚠️ IMPORTANTE: Para Gmail, debes usar una contraseña de aplicación, no tu contraseña normal.")
    print("   Genera una en: https://myaccount.google.com/apppasswords")
    exit(1)

# Si llegamos aquí, el correo está configurado
print("\n✅ Correo configurado correctamente")

# Ahora intentar enviar un correo de prueba
print("\n" + "=" * 80)
print("📨 ENVIANDO CORREO DE PRUEBA...")
print("=" * 80)

try:
    from app import app, mail
    from flask_mail import Message
    
    with app.app_context():
        # Crear mensaje de prueba
        msg = Message(
            subject="🔍 Prueba de Correo de Supervisión",
            recipients=[input("\n📧 Ingresa el correo destino para la prueba: ").strip()],
            html="""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #00c875;">✅ Correo de Prueba Exitoso</h2>
                <p>Este es un correo de prueba del sistema de supervisión.</p>
                <p>Si recibes este correo, significa que la configuración está correcta.</p>
                <hr>
                <small style="color: #666;">Sistema de Supervisión - Gestor Documental</small>
            </body>
            </html>
            """
        )
        
        # Enviar
        mail.send(msg)
        print("\n✅ ¡Correo enviado exitosamente!")
        print("   Revisa la bandeja de entrada (y la carpeta de SPAM si no lo ves)")
        
except Exception as e:
    print(f"\n❌ Error al enviar correo: {e}")
    print("\nPosibles causas:")
    print("1. Contraseña incorrecta (debe ser contraseña de aplicación para Gmail)")
    print("2. Verificación en 2 pasos no habilitada en Gmail")
    print("3. Servidor SMTP bloqueado por firewall")
    print("4. Configuración incorrecta en .env")
