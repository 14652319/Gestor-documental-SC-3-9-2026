# =============================================
# 🚀 app.py — Backend seguro con Flask + PostgreSQL
# =============================================

# Configurar encoding para Windows
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from dotenv import load_dotenv
import secrets, os, logging

# Importar db desde extensions (evita importación circular)
from extensions import db
from decoradores_permisos import requiere_permiso_html, requiere_permiso
from utils_licencia import evaluate_license, build_license_notice_html

# -------------------------------------------------
# 🔧 CONFIGURACIÓN INICIAL
# -------------------------------------------------
load_dotenv()  # Carga variables del archivo .env

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "clave_fallback_2025")

# ✅ Configuración de sesión con timeout de 25 minutos
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=25)
app.config['SESSION_REFRESH_EACH_REQUEST'] = False  # Cuenta desde último request

# Base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Límite de tamaño de archivos subidos (500 MB)
# Suficiente para archivos Excel con 1M+ registros
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB

# Configuración de correo electrónico
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'  # Soporte para SSL (puerto 465)
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))
app.config['MAIL_REPLY_TO'] = os.getenv('MAIL_REPLY_TO')  # Opcional: para correos que no aceptan respuestas

# Inicializar db con la app
db.init_app(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

# =============================================
# 🎨 CONFIGURACIÓN DE MARCA (BRANDING)
# =============================================
LOGO_PATH = '/static/images/logo_supertiendas.svg'  # Ruta relativa desde la raíz web
LOGO_ALT_TEXT = 'Supertiendas Cañaveral'

# -------------------------------------------------
# 🔐 CONTROL DE LICENCIA (asociado a servidor + periodo de gracia)
# -------------------------------------------------
# - LICENSE_ENFORCE: habilita/deshabilita la verificación (por defecto: True)
# - LICENSE_FILE: ruta del archivo de licencia (por defecto: license.lic)
# - LICENSE_GRACE_DAYS: días de gracia cuando no hay licencia/autorización (por defecto: 180)
@app.route('/license/notice')
def license_notice():
    status = evaluate_license(app)
    return build_license_notice_html(status)

@app.before_request
def validar_licencia_global():
    """Bloquea el acceso si la instalación no está autorizada.

    - Si está en periodo de gracia (TRIAL), permite operar y muestra aviso sólo si se navega a /license/notice.
    - Si expiró el periodo de gracia, bloquea todo excepto recursos estáticos y /license/notice.
    - APIs devuelven 451 con JSON estándar cuando está expirado.
    """
    status = evaluate_license(app)
    if status.get('ok', True):
        return None

    # Sólo aplica bloqueo si el trial expiró
    if status.get('reason') != 'TRIAL_EXPIRED':
        return None

    path = request.path or '/'
    if (
        path.startswith('/static') or
        path == '/favicon.ico' or
        path == '/license/notice'
    ):
        return None

    # APIs → 451 (Unavailable For Legal Reasons)
    if path.startswith('/api'):
        return jsonify({
            "ok": False,
            "message": "Licencia no autorizada o expirada para este servidor",
            "reason": "TRIAL_EXPIRED",
            "redirect": "/license/notice"
        }), 451

    # Vistas HTML → redirigir a aviso
    return redirect('/license/notice')

# -------------------------------------------------
# 🚧 CONTROL GLOBAL DE SESIÓN (expiración/inactividad)
# -------------------------------------------------
@app.before_request
def validar_sesion_global():
    """Redirige o responde 401 cuando no hay sesión activa.

    - HTML (vistas): redirige a login con `?expired=1` para mostrar mensaje.
    - APIs (JSON): responde 401 con payload estándar para que el frontend maneje redirect.
    
    Rutas excluidas: login, auth, registro, consulta, estáticos.
    """
    path = request.path or '/'

    # Rutas públicas o estáticos
    if (
        path.startswith('/static') or
        path == '/' or
        path == '/favicon.ico' or
        path.startswith('/api/auth') or
        path.startswith('/api/registro') or
        path.startswith('/api/documentos') or  # 🆕 PERMITIR CARGA DE DOCUMENTOS EN REGISTRO
        path.startswith('/api/consulta') or
        path.startswith('/dian_vs_erp')  # ⚡ PERMITIR ACCESO AL MÓDULO DIAN VS ERP
    ):
        return None

    # Sesión requerida para el resto
    if 'usuario_id' not in session:
        session.clear()
        # Si es API, devolver 401 JSON
        if path.startswith('/api'):
            return jsonify({
                "ok": False,
                "message": "Sesión finalizada por inactividad",
                "expired": True,
                "redirect": "/"
            }), 401
        # Si es vista HTML, redirigir a login con bandera
        return redirect(url_for('index', expired=1))

    return None
EMPRESA_NOMBRE = 'Supertiendas Cañaveral'
EMPRESA_NIT = '805.028.041-1'

# -------------------------------------------------
# 🧾 LOGGING DE SEGURIDAD
# -------------------------------------------------
os.makedirs("logs", exist_ok=True)
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)
fh = logging.FileHandler("logs/security.log", encoding="utf-8")
fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
fh.setFormatter(fmt)
if not security_logger.handlers:
    security_logger.addHandler(fh)

def log_security(msg):
    security_logger.info(msg)

# -------------------------------------------------
# � FUNCIÓN DE ENVÍO DE CORREO
# -------------------------------------------------
def enviar_correo_confirmacion_radicado(destinatario, nit, razon_social, radicado):
    """
    Envía correo de confirmación con el número de radicado generado
    
    Args:
        destinatario: Email del tercero
        nit: NIT del tercero registrado
        razon_social: Nombre o razón social del tercero
        radicado: Número de radicado generado (ej: RAD-000027)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Verificar si hay configuración de correo
        if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
            log_security(f"ADVERTENCIA: Correo no configurado. No se envió notificación a {destinatario}")
            return (False, "Correo no configurado en el servidor")
        
        # Crear mensaje HTML con el diseño similar a la vista de éxito
        html_body = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confirmación de Registro</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    background-color: #f3f4f6;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(145deg, #16a34a, #15803d);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header-icon {{
                    font-size: 3em;
                    margin-bottom: 10px;
                }}
                .content {{
                    padding: 30px;
                }}
                .radicado-box {{
                    background-color: #f0fdf4;
                    border: 2px solid #22c55e;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: center;
                }}
                .radicado-label {{
                    color: #166534;
                    font-size: 0.9em;
                    margin-bottom: 5px;
                }}
                .radicado-number {{
                    color: #16a34a;
                    font-size: 2em;
                    font-weight: bold;
                    letter-spacing: 2px;
                }}
                .info-box {{
                    background-color: #f9fafb;
                    border-left: 4px solid #16a34a;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .steps-box {{
                    background-color: #f0fdf4;
                    border: 2px solid #22c55e;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .steps-title {{
                    color: #16a34a;
                    font-size: 1.2em;
                    font-weight: bold;
                    margin-bottom: 15px;
                    text-align: center;
                }}
                .steps-list {{
                    color: #374151;
                    line-height: 1.8;
                }}
                .steps-list li {{
                    margin-bottom: 10px;
                }}
                .warning-box {{
                    background-color: #eff6ff;
                    border: 2px solid #3b82f6;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .footer {{
                    background-color: #f9fafb;
                    padding: 20px;
                    text-align: center;
                    color: #6b7280;
                    font-size: 0.9em;
                }}
                strong {{
                    color: #16a34a;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="header-icon">✅</div>
                    <h1 style="margin: 0; font-size: 1.8em;">¡Solicitud Radicada Exitosamente!</h1>
                </div>
                
                <div class="content">
                    <div class="radicado-box">
                        <div class="radicado-label">📋 Su Número de Radicado</div>
                        <div class="radicado-number">{radicado}</div>
                    </div>
                    
                    <div class="info-box">
                        <p style="margin: 5px 0;"><strong>🏢 NIT:</strong> {nit}</p>
                        <p style="margin: 5px 0;"><strong>📄 Empresa:</strong> {razon_social}</p>
                    </div>
                    
                    <div class="steps-box">
                        <div class="steps-title">📋 Próximos Pasos</div>
                        <ul class="steps-list">
                            <li>Su solicitud será <strong>revisada por nuestro equipo</strong></li>
                            <li>En un término de <strong>5 días hábiles</strong> daremos respuesta</li>
                            <li>Nos contactaremos por el <strong>correo electrónico suministrado</strong></li>
                            <li>Una vez aprobada, recibirá sus <strong>credenciales de acceso</strong></li>
                        </ul>
                    </div>
                    
                    <div class="warning-box">
                        <p style="margin: 0; color: #1d4ed8;">
                            <strong>💡 Importante:</strong> Conserve este número de radicado para futuras consultas
                        </p>
                    </div>
                </div>
                
                <div class="footer">
                    <p style="margin: 5px 0;"><strong>Supertiendas Cañaveral SAS</strong></p>
                    <p style="margin: 5px 0;">Gestor Documental - Sistema de Registro de Proveedores</p>
                    <p style="margin: 5px 0; font-size: 0.8em; color: #9ca3af;">
                        Este es un correo automático, por favor no responda a este mensaje.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Crear mensaje de texto plano como alternativa
        text_body = f"""
¡Solicitud Radicada Exitosamente!

Su Número de Radicado: {radicado}

Información de su solicitud:
- NIT: {nit}
- Empresa: {razon_social}

Próximos Pasos:
• Su solicitud será revisada por nuestro equipo
• En un término de 5 días hábiles daremos respuesta
• Nos contactaremos por el correo electrónico suministrado
• Una vez aprobada, recibirá sus credenciales de acceso

IMPORTANTE: Conserve este número de radicado para futuras consultas

---
Supertiendas Cañaveral SAS
Gestor Documental - Sistema de Registro de Proveedores
Este es un correo automático, por favor no responda a este mensaje.
        """
        
        # Crear y enviar el mensaje
        msg = Message(
            subject=f"Confirmación de Registro - Radicado {radicado}",
            recipients=[destinatario],
            body=text_body,
            html=html_body
        )
        
        # Si hay configurado un Reply-To (para correos que no aceptan respuestas)
        if app.config.get('MAIL_REPLY_TO'):
            msg.reply_to = app.config['MAIL_REPLY_TO']
        
        mail.send(msg)
        log_security(f"CORREO ENVIADO | destinatario={destinatario} | radicado={radicado}")
        return (True, "Correo enviado exitosamente")
        
    except Exception as e:
        error_msg = f"Error al enviar correo: {str(e)}"
        log_security(f"ERROR ENVÍO CORREO | destinatario={destinatario} | error={error_msg}")
        return (False, error_msg)

def enviar_correo_token_recuperacion(destinatario, nit, nombre_usuario, token):
    """
    Envía correo con el token de 6 dígitos para recuperación de contraseña
    
    Args:
        destinatario: Email del usuario
        nit: NIT del tercero
        nombre_usuario: Nombre de usuario
        token: Token de 6 dígitos
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Verificar si hay configuración de correo
        if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
            log_security(f"ADVERTENCIA: Correo no configurado. Token de recuperación no enviado a {destinatario}")
            return (False, "Correo no configurado en el servidor")
        
        # Crear mensaje HTML profesional
        html_body = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Recuperación de Contraseña</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    background-color: #f3f4f6;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(145deg, #3b82f6, #2563eb);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header-icon {{
                    font-size: 3em;
                    margin-bottom: 10px;
                }}
                .content {{
                    padding: 30px;
                }}
                .token-box {{
                    background: linear-gradient(145deg, #eff6ff, #dbeafe);
                    border: 3px solid #3b82f6;
                    border-radius: 12px;
                    padding: 30px;
                    margin: 25px 0;
                    text-align: center;
                }}
                .token-label {{
                    color: #1e40af;
                    font-size: 1em;
                    margin-bottom: 10px;
                    font-weight: 600;
                }}
                .token-number {{
                    color: #1e3a8a;
                    font-size: 3em;
                    font-weight: bold;
                    letter-spacing: 8px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                }}
                .info-box {{
                    background-color: #f9fafb;
                    border-left: 4px solid #3b82f6;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .warning-box {{
                    background-color: #fef3c7;
                    border: 2px solid #f59e0b;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .security-box {{
                    background-color: #fee2e2;
                    border: 2px solid #ef4444;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .footer {{
                    background-color: #f9fafb;
                    padding: 20px;
                    text-align: center;
                    color: #6b7280;
                    font-size: 0.9em;
                }}
                strong {{
                    color: #1e40af;
                }}
                .timer {{
                    color: #ef4444;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="header-icon">🔐</div>
                    <h1 style="margin: 0; font-size: 1.8em;">Recuperación de Contraseña</h1>
                </div>
                
                <div class="content">
                    <p style="color: #374151; font-size: 1.1em;">
                        Hola, <strong>{nombre_usuario}</strong>
                    </p>
                    
                    <p style="color: #6b7280; line-height: 1.6;">
                        Recibimos una solicitud para restablecer la contraseña de tu cuenta. 
                        Utiliza el siguiente código de verificación para continuar con el proceso:
                    </p>
                    
                    <div class="token-box">
                        <div class="token-label">🔢 Tu Código de Verificación</div>
                        <div class="token-number">{token}</div>
                    </div>
                    
                    <div class="info-box">
                        <p style="margin: 5px 0;"><strong>👤 Usuario:</strong> {nombre_usuario}</p>
                        <p style="margin: 5px 0;"><strong>🏢 NIT:</strong> {nit}</p>
                    </div>
                    
                    <div class="warning-box">
                        <p style="margin: 0; color: #92400e;">
                            <strong>⏱️ Importante:</strong> Este código expira en <span class="timer">10 minutos</span>
                        </p>
                    </div>
                    
                    <div class="warning-box">
                        <p style="margin: 0; color: #92400e;">
                            <strong>🔒 Seguridad:</strong> Tienes un máximo de <span class="timer">3 intentos</span> para ingresar el código correctamente
                        </p>
                    </div>
                    
                    <div class="security-box">
                        <p style="margin: 0; color: #991b1b;">
                            <strong>🚨 ¿No solicitaste este cambio?</strong><br>
                            Si no reconoces esta solicitud, ignora este correo y tu contraseña permanecerá sin cambios. 
                            Recomendamos cambiar tu contraseña inmediatamente si sospechas que alguien más tiene acceso a tu cuenta.
                        </p>
                    </div>
                </div>
                
                <div class="footer">
                    <p style="margin: 5px 0;"><strong>Supertiendas Cañaveral SAS</strong></p>
                    <p style="margin: 5px 0;">Gestor Documental - Sistema de Autenticación Segura</p>
                    <p style="margin: 5px 0; font-size: 0.8em; color: #9ca3af;">
                        Este es un correo automático, por favor no responda a este mensaje.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Crear mensaje de texto plano como alternativa
        text_body = f"""
🔐 Recuperación de Contraseña

Hola, {nombre_usuario}

Recibimos una solicitud para restablecer la contraseña de tu cuenta.

Tu Código de Verificación: {token}

Información de tu cuenta:
- Usuario: {nombre_usuario}
- NIT: {nit}

IMPORTANTE:
⏱️ Este código expira en 10 minutos
🔒 Tienes un máximo de 3 intentos para ingresar el código

🚨 ¿No solicitaste este cambio?
Si no reconoces esta solicitud, ignora este correo y tu contraseña permanecerá sin cambios.

---
Supertiendas Cañaveral SAS
Gestor Documental - Sistema de Autenticación Segura
Este es un correo automático, por favor no responda a este mensaje.
        """
        
        # Crear y enviar el mensaje
        msg = Message(
            subject=f"Código de Recuperación - {token}",
            recipients=[destinatario],
            body=text_body,
            html=html_body
        )
        
        # Si hay configurado un Reply-To (para correos que no aceptan respuestas)
        if app.config.get('MAIL_REPLY_TO'):
            msg.reply_to = app.config['MAIL_REPLY_TO']
        
        mail.send(msg)
        log_security(f"TOKEN RECUPERACION ENVIADO POR CORREO | destinatario={destinatario} | usuario={nombre_usuario} | nit={nit}")
        return (True, "Correo enviado exitosamente")
        
    except Exception as e:
        error_msg = f"Error al enviar correo: {str(e)}"
        log_security(f"ERROR ENVÍO TOKEN RECUPERACION | destinatario={destinatario} | error={error_msg}")
        return (False, error_msg)


# -------------------------------------------------
# 📱 FUNCIÓN: ENVIAR TELEGRAM TOKEN RECUPERACIÓN
# -------------------------------------------------
def enviar_telegram_token_recuperacion(nit, nombre_usuario, token):
    """
    Envía el token de recuperación por Telegram.
    
    Args:
        nit: NIT del tercero
        nombre_usuario: Nombre de usuario que solicita el token
        token: Token de 6 dígitos
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Verificar si Telegram está configurado
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            log_security(f"ADVERTENCIA: Telegram no configurado. Token no enviado por Telegram | usuario={nombre_usuario}")
            return (False, "Telegram no está configurado")
        
        # Importar requests solo si es necesario
        import requests
        
        # Construir mensaje con formato Markdown
        mensaje = f"""
🔐 *RECUPERACIÓN DE CONTRASEÑA*

👤 *Usuario:* {nombre_usuario}
🏢 *NIT:* {nit}
🔢 *Código de verificación:*

```
{token}
```

⏰ *Validez:* 10 minutos
🔄 *Intentos permitidos:* 3

⚠️ Si no solicitaste este código, ignora este mensaje.

---
📧 Sistema de Gestión Documental
Supertiendas Cañaveral
        """
        
        # URL de la API de Telegram
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # Datos del mensaje
        payload = {
            'chat_id': chat_id,
            'text': mensaje,
            'parse_mode': 'Markdown'
        }
        
        # Enviar mensaje
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            log_security(f"TOKEN RECUPERACION ENVIADO POR TELEGRAM | usuario={nombre_usuario} | nit={nit}")
            return (True, "Mensaje de Telegram enviado exitosamente")
        else:
            error_msg = f"Error en respuesta de Telegram: {response.status_code} - {response.text}"
            log_security(f"ERROR ENVÍO TELEGRAM | usuario={nombre_usuario} | error={error_msg}")
            return (False, error_msg)
            
    except Exception as e:
        error_msg = f"Error al enviar Telegram: {str(e)}"
        log_security(f"ERROR ENVÍO TELEGRAM | usuario={nombre_usuario} | error={error_msg}")
        return (False, error_msg)

def enviar_correo_invitacion_usuario(destinatario, nombre_usuario, nit, token_invitacion=None):
    """
    Envía correo de invitación para configurar contraseña de nuevo usuario
    
    Args:
        destinatario: Email del usuario
        nombre_usuario: Nombre de usuario asignado
        nit: NIT del tercero asociado
        token_invitacion: Token opcional para activación (futuro)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Verificar si hay configuración de correo
        if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
            log_security(f"ADVERTENCIA: Correo no configurado. No se envió invitación a {destinatario}")
            return (False, "Correo no configurado en el servidor")
        
        # Crear mensaje HTML para invitación
        html_body = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Invitación - Gestor Documental</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 20px;
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #16A085 0%, #2ECC71 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                    font-weight: 600;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .welcome {{
                    font-size: 18px;
                    color: #2c3e50;
                    margin-bottom: 20px;
                    text-align: center;
                }}
                .details {{
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 25px 0;
                    border-left: 4px solid #16A085;
                }}
                .detail-item {{
                    margin: 10px 0;
                    font-size: 16px;
                }}
                .detail-label {{
                    font-weight: 600;
                    color: #34495e;
                }}
                .detail-value {{
                    color: #2c3e50;
                    margin-left: 10px;
                }}
                .instructions {{
                    background: #e3f2fd;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 25px 0;
                    border-left: 4px solid #2196f3;
                }}
                .step {{
                    margin: 15px 0;
                    font-size: 15px;
                    color: #1565c0;
                }}
                .step strong {{
                    color: #0d47a1;
                }}
                .footer {{
                    background: #ecf0f1;
                    padding: 20px 30px;
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 14px;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #16A085 0%, #2ECC71 100%);
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(22, 160, 133, 0.3);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 ¡Bienvenido al Sistema!</h1>
                    <p>Supertiendas Cañaveral - Gestor Documental</p>
                </div>
                
                <div class="content">
                    <div class="welcome">
                        Se ha creado tu cuenta de usuario en el sistema de gestión documental.
                    </div>
                    
                    <div class="details">
                        <div class="detail-item">
                            <span class="detail-label">👤 Usuario:</span>
                            <span class="detail-value"><strong>{nombre_usuario}</strong></span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">🏢 NIT asociado:</span>
                            <span class="detail-value">{nit}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">📧 Correo:</span>
                            <span class="detail-value">{destinatario}</span>
                        </div>
                    </div>
                    
                    <div class="instructions">
                        <h3 style="color: #1565c0; margin-top: 0;">📋 Próximos pasos:</h3>
                        <div class="step">
                            <strong>1.</strong> Tu cuenta está pendiente de activación por el administrador
                        </div>
                        <div class="step">
                            <strong>2.</strong> Una vez activada, recibirás un correo con instrucciones para configurar tu contraseña
                        </div>
                        <div class="step">
                            <strong>3.</strong> Podrás acceder al sistema usando tu usuario y la contraseña que configures
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <p style="color: #7f8c8d; font-size: 14px;">
                            Una vez que tu cuenta esté activa, podrás acceder en:
                        </p>
                        <a href="https://mtlm3ljz-8099.use2.devtunnels.ms/" class="cta-button">
                            🌐 Acceder al Sistema
                        </a>
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>Gestor Documental - Supertiendas Cañaveral</strong></p>
                    <p>Este es un mensaje automático, por favor no responder.</p>
                    <p>Si tienes dudas, contacta al administrador del sistema.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Texto plano como alternativa
        texto_plano = f"""
INVITACIÓN - GESTOR DOCUMENTAL
Supertiendas Cañaveral

¡Bienvenido al sistema!

Se ha creado tu cuenta de usuario:
- Usuario: {nombre_usuario}
- NIT asociado: {nit}
- Correo: {destinatario}

PRÓXIMOS PASOS:
1. Tu cuenta está pendiente de activación por el administrador
2. Una vez activada, recibirás un correo con instrucciones para configurar tu contraseña
3. Podrás acceder al sistema usando tu usuario y la contraseña que configures

Acceso al sistema: https://mtlm3ljz-8099.use2.devtunnels.ms/

---
Gestor Documental - Supertiendas Cañaveral
Este es un mensaje automático, por favor no responder.
        """
        
        # Crear y enviar mensaje
        msg = Message(
            subject='🎉 Invitación - Gestor Documental Supertiendas Cañaveral',
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[destinatario]
        )
        
        # Configurar Reply-To si está disponible
        if app.config.get('MAIL_REPLY_TO'):
            msg.reply_to = app.config['MAIL_REPLY_TO']
        
        msg.body = texto_plano
        msg.html = html_body
        
        mail.send(msg)
        
        log_security(f"INVITACION CORREO ENVIADA | destinatario={destinatario} | usuario={nombre_usuario} | nit={nit}")
        return (True, f"Invitación enviada exitosamente a {destinatario}")
        
    except Exception as e:
        error_msg = f"Error al enviar invitación: {str(e)}"
        log_security(f"ERROR ENVÍO INVITACION | destinatario={destinatario} | error={error_msg}")
        return (False, error_msg)


# -------------------------------------------------
# � FUNCIÓN: ENVIAR ALERTA DE SEGURIDAD POR TELEGRAM
# -------------------------------------------------
def enviar_alerta_seguridad_telegram(tipo_alerta, detalles):
    """
    Envía alertas de seguridad automáticas por Telegram.
    
    Args:
        tipo_alerta: Tipo de alerta (IP_BLOQUEADA, ATAQUE_BRUTE_FORCE, USUARIO_BLOQUEADO, etc.)
        detalles: Diccionario con detalles de la alerta
        
    Returns:
        bool: True si se envió exitosamente, False en caso contrario
    """
    try:
        # Verificar si Telegram está configurado
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            return False
        
        import requests
        
        # Iconos según tipo de alerta
        iconos = {
            'IP_BLOQUEADA': '🚫',
            'ATAQUE_BRUTE_FORCE': '⚠️',
            'USUARIO_BLOQUEADO': '🔒',
            'INTENTOS_FALLIDOS': '❌',
            'ACCESO_SOSPECHOSO': '👁️'
        }
        
        icono = iconos.get(tipo_alerta, '🔔')
        
        # Construir mensaje según tipo de alerta
        mensaje = f"{icono} *ALERTA DE SEGURIDAD*\n\n"
        mensaje += f"*Tipo:* {tipo_alerta.replace('_', ' ')}\n"
        mensaje += f"*Fecha:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Agregar detalles específicos
        if 'ip' in detalles:
            mensaje += f"*IP:* `{detalles['ip']}`\n"
        if 'usuario' in detalles:
            mensaje += f"*Usuario:* {detalles['usuario']}\n"
        if 'nit' in detalles:
            mensaje += f"*NIT:* {detalles['nit']}\n"
        if 'intentos' in detalles:
            mensaje += f"*Intentos fallidos:* {detalles['intentos']}\n"
        if 'motivo' in detalles:
            mensaje += f"*Motivo:* {detalles['motivo']}\n"
        if 'user_agent' in detalles:
            mensaje += f"*Navegador:* {detalles['user_agent'][:50]}...\n"
        
        mensaje += f"\n---\n📊 Sistema de Gestión Documental"
        
        # URL de la API de Telegram
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # Datos del mensaje
        payload = {
            'chat_id': chat_id,
            'text': mensaje,
            'parse_mode': 'Markdown'
        }
        
        # Enviar mensaje (sin timeout largo para no bloquear)
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            log_security(f"ALERTA TELEGRAM ENVIADA | tipo={tipo_alerta} | ip={detalles.get('ip', 'N/A')}")
            return True
        else:
            log_security(f"ERROR ALERTA TELEGRAM | tipo={tipo_alerta} | status={response.status_code}")
            return False
            
    except Exception as e:
        log_security(f"ERROR ENVIANDO ALERTA TELEGRAM | tipo={tipo_alerta} | error={str(e)}")
        return False


# -------------------------------------------------
# �📊 MODELOS DE BASE DE DATOS
# -------------------------------------------------
class Tercero(db.Model):
    __tablename__ = "terceros"
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    nit = db.Column(db.String(20), unique=True, nullable=False)
    tipo_persona = db.Column(db.String(10), nullable=False)
    razon_social = db.Column(db.String(150))
    primer_nombre = db.Column(db.String(80))
    segundo_nombre = db.Column(db.String(80))
    primer_apellido = db.Column(db.String(80))
    segundo_apellido = db.Column(db.String(80))
    correo = db.Column(db.String(120))
    celular = db.Column(db.String(30))
    acepta_terminos = db.Column(db.Boolean, default=True)
    acepta_contacto = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default="pendiente")

class Usuario(db.Model):
    __tablename__ = "usuarios"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    tercero_id = db.Column(db.Integer, db.ForeignKey("terceros.id"))
    usuario = db.Column(db.String(60), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    rol = db.Column(db.String(30), default="externo")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

class Acceso(db.Model):
    __tablename__ = "accesos"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    ip = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    exito = db.Column(db.Boolean, default=False)
    motivo = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class TokenRecuperacion(db.Model):
    __tablename__ = "tokens_recuperacion"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    token = db.Column(db.String(64), unique=True, nullable=False)
    creado = db.Column(db.DateTime, default=datetime.utcnow)
    expira = db.Column(db.DateTime, nullable=False)
    usado = db.Column(db.Boolean, default=False)
    # Campos adicionales para mejor validación
    nit = db.Column(db.String(20))
    nombre_usuario = db.Column(db.String(60))
    intentos_validacion = db.Column(db.Integer, default=0)

class PasswordUsada(db.Model):
    __tablename__ = "contrasenas_usadas"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    password_hash = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class IPSospechosa(db.Model):
    __tablename__ = "ips_sospechosas"
    __table_args__ = {'extend_existing': True}
    ip = db.Column(db.String(45), primary_key=True)
    intentos = db.Column(db.Integer, default=0)
    ultima_actividad = db.Column(db.DateTime, default=datetime.utcnow)
    bloqueada = db.Column(db.Boolean, default=False)
    motivo_bloqueo = db.Column(db.Text)

class IPListaBlanca(db.Model):
    __tablename__ = "ips_blancas"
    __table_args__ = {'extend_existing': True}
    ip = db.Column(db.String(45), primary_key=True)

class IPListaNegra(db.Model):
    __tablename__ = "ips_negras"
    __table_args__ = {'extend_existing': True}
    ip = db.Column(db.String(45), primary_key=True)
    motivo = db.Column(db.Text)
    fecha_bloqueo = db.Column(db.DateTime, default=datetime.utcnow)

class DocumentoTercero(db.Model):
    __tablename__ = "documentos_tercero"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    tercero_id = db.Column(db.Integer, db.ForeignKey("terceros.id"))
    radicado = db.Column(db.String(20), nullable=False)
    tipo_documento = db.Column(db.String(100), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.String(500), nullable=False)
    tamaño_archivo = db.Column(db.Integer)
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default="cargado")

class SolicitudRegistro(db.Model):
    __tablename__ = "solicitudes_registro"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    tercero_id = db.Column(db.Integer, db.ForeignKey("terceros.id"))
    radicado = db.Column(db.String(20), unique=True, nullable=False)
    estado = db.Column(db.String(30), default="pendiente")
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    observaciones = db.Column(db.Text)
    documentos_completos = db.Column(db.Boolean, default=False)
    usuarios_creados = db.Column(db.Boolean, default=False)

# -------------------------------------------------
# 🔒 MIDDLEWARE: Verificar sesión antes de cada request
# -------------------------------------------------
@app.before_request
def verificar_sesion():
    """
    Hace la sesión permanente y actualiza el timeout de 25 minutos
    """
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=25)

# -------------------------------------------------
# 🌐 RUTAS FRONTEND
# -------------------------------------------------
@app.route("/")
def index():
    try:
        return render_template("login.html")
    except Exception:
        return jsonify({"message": "Endpoint no encontrado", "ok": False}), 404

@app.route("/dashboard")
def dashboard():
    """
    Dashboard principal con menú modular
    Muestra diferentes módulos según el tipo de usuario (interno/externo)
    ⚠️ NOTA: Dashboard accesible para todos los usuarios autenticados (validación manual)
    """
    # Validación manual de sesión (el dashboard es accesible para todos con sesión válida)
    if 'usuario_id' not in session:
        return redirect('/')
    
    try:
        # Obtener datos del usuario de la sesión
        user_data = session.get('user', {})
        return render_template("dashboard.html", user_data=user_data)
    except Exception as e:
        log_security(f"ERROR cargando dashboard | error={str(e)}")
        return jsonify({"message": "Error al cargar dashboard", "ok": False}), 500

# ⚠️ COMENTADO - Ahora lo maneja el blueprint recibir_facturas_bp
# @app.route("/recibir_facturas")
# def recibir_facturas():
#     """
#     Módulo de Recibir Facturas
#     Gestión completa de facturas de proveedores
#     """
#     try:
#         return render_template("recibir_facturas.html")
#     except Exception as e:
#         log_security(f"ERROR cargando módulo recibir_facturas | error={str(e)}")
#         return jsonify({"message": "Error al cargar módulo", "ok": False}), 500


# -------------------------------------------------
# 🔐 LOGIN
# -------------------------------------------------
@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(force=True, silent=True) or {}
    nit = data.get("nit", "").strip()
    usuario_alias = data.get("usuario", "").strip()
    password = data.get("password", "")
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "")

    # Bloqueo por lista negra
    if IPListaNegra.query.get(ip):
        db.session.add(Acceso(usuario_id=None, ip=ip, user_agent=ua, exito=False, motivo="ip en lista negra"))
        db.session.commit()
        log_security(f"LOGIN BLOQUEADO por lista negra | IP={ip}")
        return jsonify({"success": False, "message": "Acceso denegado."}), 403

    # Buscar usuario (case-insensitive para el nombre de usuario)
    user = Usuario.query.filter(
        (db.func.lower(Usuario.usuario) == usuario_alias.lower()) | 
        (db.func.lower(Usuario.correo) == usuario_alias.lower())
    ).first()
    
    if not user:
        db.session.add(Acceso(usuario_id=None, ip=ip, user_agent=ua, exito=False, motivo="usuario no existe"))
        db.session.commit()
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    # ✅ VALIDACIÓN DE NIT: 
    # - Administradores pueden acceder con CUALQUIER NIT (internos o proveedores)
    # - Usuarios normales solo con su NIT asociado
    if nit:
        ter = Tercero.query.filter_by(nit=nit).first()
        
        # Si NO es administrador, validar que el NIT coincida con su tercero
        if user.rol != 'admin':
            if not ter or ter.id != user.tercero_id:
                db.session.add(Acceso(usuario_id=user.id, ip=ip, user_agent=ua, exito=False, motivo="NIT no coincide"))
                db.session.commit()
                return jsonify({"success": False, "message": "NIT no coincide con el usuario"}), 401
        else:
            # Admin: Verificar que el NIT exista en sistema
            if not ter:
                return jsonify({"success": False, "message": "NIT no existe en el sistema"}), 404

    # Validar estado del usuario ANTES de validar contraseña
    if not user.activo:
        db.session.add(Acceso(usuario_id=user.id, ip=ip, user_agent=ua, exito=False, motivo="usuario inactivo"))
        db.session.commit()
        log_security(f"LOGIN BLOQUEADO - Usuario inactivo | user_id={user.id} | activo={user.activo} | IP={ip}")
        return jsonify({"success": False, "message": "Usuario inactivo. Su cuenta está pendiente de activación."}), 401

    if not bcrypt.check_password_hash(user.password_hash, password):
        s = IPSospechosa.query.get(ip) or IPSospechosa(ip=ip)
        s.intentos = (s.intentos or 0) + 1
        s.ultima_actividad = datetime.utcnow()
        
        # 🚨 ALERTA: IP bloqueada por intentos fallidos
        if s.intentos >= 5:
            s.bloqueada = True
            s.motivo_bloqueo = "Exceso de intentos fallidos"
            db.session.merge(IPListaNegra(ip=ip, motivo="Brute-force"))
            log_security(f"IP bloqueada por intentos fallidos | IP={ip}")
            
            # Enviar alerta por Telegram
            enviar_alerta_seguridad_telegram('IP_BLOQUEADA', {
                'ip': ip,
                'usuario': usuario_alias,
                'nit': nit,
                'intentos': s.intentos,
                'motivo': 'Exceso de intentos fallidos de login',
                'user_agent': ua
            })
        # 🚨 ALERTA: Intentos sospechosos (3 o más)
        elif s.intentos >= 3:
            enviar_alerta_seguridad_telegram('INTENTOS_FALLIDOS', {
                'ip': ip,
                'usuario': usuario_alias,
                'nit': nit,
                'intentos': s.intentos,
                'motivo': f'{s.intentos} intentos fallidos de login',
                'user_agent': ua
            })
        
        db.session.add(s)
        db.session.add(Acceso(usuario_id=user.id, ip=ip, user_agent=ua, exito=False, motivo="password incorrecto"))
        db.session.commit()
        return jsonify({"success": False, "message": "Contraseña incorrecta"}), 401

    s = IPSospechosa.query.get(ip)
    if s:
        s.intentos = 0
        s.bloqueada = False
        db.session.add(s)

    db.session.add(Acceso(usuario_id=user.id, ip=ip, user_agent=ua, exito=True, motivo="login ok"))
    db.session.commit()

    token_sesion = secrets.token_hex(16)
    log_security(f"LOGIN OK | user_id={user.id} | IP={ip}")
    
    # Obtener información del tercero asociado al usuario
    tercero_usuario = db.session.get(Tercero, user.tercero_id)
    
    # Para admins: usar el NIT con el que inició sesión (si es diferente al suyo)
    # Para usuarios normales: usar su NIT asociado
    if user.rol == 'admin' and nit and nit != tercero_usuario.nit:
        # Admin accediendo con NIT diferente al suyo
        tercero_trabajo = Tercero.query.filter_by(nit=nit).first()
        nit_sesion = tercero_trabajo.nit if tercero_trabajo else tercero_usuario.nit
        razon_social_sesion = tercero_trabajo.razon_social if tercero_trabajo else tercero_usuario.razon_social
    else:
        # Usuario normal o admin con su propio NIT
        nit_sesion = tercero_usuario.nit if tercero_usuario else ""
        razon_social_sesion = tercero_usuario.razon_social if tercero_usuario else ""
    
    # ✅ ESTABLECER SESIÓN EN EL SERVIDOR
    session['usuario_id'] = user.id
    session['usuario'] = user.usuario
    session['nit'] = nit_sesion  # NIT con el que está trabajando (puede ser diferente para admins)
    session['rol'] = user.rol
    session['tercero_id'] = user.tercero_id  # Tercero REAL del usuario
    
    # ✅ CRÍTICO: Calcular tipo_usuario para módulo de facturas digitales
    # - Usuarios con rol 'externo' → tipo_usuario = 'externo'
    # - Todos los demás (admin, interno, usuario) → tipo_usuario = 'interno'
    session['tipo_usuario'] = 'externo' if user.rol == 'externo' else 'interno'
    
    session.permanent = True  # Sesión persistente
    
    return jsonify({
        "success": True, 
        "sessionToken": token_sesion, 
        "redirectUrl": "/dashboard",
        "usuario": {
            "nombre": user.usuario,
            "rol": user.rol,  # 🔑 admin, usuario, etc.
            "nit": nit_sesion,  # NIT de trabajo (puede ser diferente para admins)
            "email": user.correo,
            "razon_social": razon_social_sesion
        }
    }), 200

# ========================================================================
# ⚠️ SISTEMA ANTIGUO: ESTABLECER/RECUPERAR CONTRASEÑA - DESHABILITADO
# ========================================================================
# @app.route("/establecer-password/<token>", methods=["GET", "POST"])
# def establecer_password(token):
#     """
#     Ruta para establecer contraseña por primera vez o recuperarla
#     GET: Muestra el formulario
#     POST: Procesa la nueva contraseña
#     """
#     from sqlalchemy import text
#     
#     if request.method == "GET":
#        # Verificar que el token es válido
#        try:
#            result = db.session.execute(
#                text("""
#                    SELECT tp.id, tp.usuario_id, tp.expiracion, tp.usado, u.usuario, u.correo
#                    FROM tokens_password tp
#                    JOIN usuarios u ON u.id = tp.usuario_id
#                    WHERE tp.token = :token
#                """),
#                {'token': token}
#            ).fetchone()
#            
#            if not result:
#                return render_template('establecer_password.html', 
#                                     error="Token no válido o no encontrado",
#                                     token=None)
#            
#            token_id, usuario_id, expiracion, usado, nombre_usuario, correo = result
#            
#            # Verificar si ya fue usado
#            if usado:
#                return render_template('establecer_password.html', 
#                                     error="Este enlace ya fue utilizado",
#                                     token=None)
#            
#            # Verificar si está expirado
#            if datetime.now() > expiracion:
#                return render_template('establecer_password.html', 
#                                     error="Este enlace ha expirado (válido por 24 horas)",
#                                     token=None,
#                                     expirado=True,
#                                     correo=correo)
#            
#            # Todo OK - Mostrar formulario
#            return render_template('establecer_password.html', 
#                                 token=token,
#                                 usuario=nombre_usuario,
#                                 correo=correo)
#            
#        except Exception as e:
#            log_security(f"ERROR verificar token | token={token} | error={str(e)}")
#            return render_template('establecer_password.html', 
#                                 error=f"Error al verificar el enlace: {str(e)}",
#                                 token=None)
#    
#    # POST: Procesar nueva contraseña
#    elif request.method == "POST":
#        password = request.form.get('password', '').strip()
#        password_confirm = request.form.get('password_confirm', '').strip()
#        
#        # Validaciones
#        if not password or not password_confirm:
#            return jsonify({"success": False, "message": "Todos los campos son obligatorios"}), 400
#        
#        if password != password_confirm:
#            return jsonify({"success": False, "message": "Las contraseñas no coinciden"}), 400
#        
#        if len(password) < 8:
#            return jsonify({"success": False, "message": "La contraseña debe tener al menos 8 caracteres"}), 400
#        
#        try:
#            # Obtener datos del token
#            result = db.session.execute(
#                text("""
#                    SELECT tp.id, tp.usuario_id, tp.expiracion, tp.usado, u.usuario
#                    FROM tokens_password tp
#                    JOIN usuarios u ON u.id = tp.usuario_id
#                    WHERE tp.token = :token
#                """),
#                {'token': token}
#            ).fetchone()
#            
#            if not result:
#                return jsonify({"success": False, "message": "Token no válido"}), 404
#            
#            token_id, usuario_id, expiracion, usado, nombre_usuario = result
#            
#            # Verificar validez
#            if usado:
#                return jsonify({"success": False, "message": "Token ya utilizado"}), 400
#            
#            if datetime.now() > expiracion:
#                return jsonify({"success": False, "message": "Token expirado"}), 400
#            
#            # Hashear nueva contraseña
#            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
#            
#            # Actualizar contraseña del usuario
#            db.session.execute(
#                text("UPDATE usuarios SET password_hash = :password WHERE id = :usuario_id"),
#                {'password': password_hash, 'usuario_id': usuario_id}
#            )
#            
#            # Marcar token como usado
#            db.session.execute(
#                text("UPDATE tokens_password SET usado = TRUE WHERE id = :token_id"),
#                {'token_id': token_id}
#            )
#            
#            db.session.commit()
#            
#            log_security(f"PASSWORD ESTABLECIDO | usuario_id={usuario_id} | usuario={nombre_usuario}")
#            
#            return jsonify({
#                "success": True, 
#                "message": "Contraseña establecida exitosamente",
#                "redirectUrl": "/"
#            }), 200
#            
#        except Exception as e:
#            db.session.rollback()
#            log_security(f"ERROR establecer password | token={token} | error={str(e)}")
#            return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

# ========================================================================
# ⚠️ SISTEMA ANTIGUO DE RECUPERACIÓN DE CONTRASEÑA - DESHABILITADO
# ========================================================================
# Este sistema usaba tokens_password y enviaba enlaces por correo
# pero NO actualizaba correctamente la contraseña en la base de datos.
# Se mantiene comentado para referencia histórica.
# 
# El sistema ACTIVO es el de token de 6 dígitos (líneas 1959-2079):
# - /api/auth/forgot_request (solicitar token)
# - /api/auth/forgot_verify (verificar token)
# - /api/auth/change_password (cambiar contraseña)
# ========================================================================
#
# @app.route("/api/auth/solicitar-recuperacion", methods=["POST"])
# def solicitar_recuperacion():
#     """
#     Genera un token y envía correo para recuperar contraseña
#     Requiere NIT + Usuario + Correo para identificación única
#     (Un usuario puede tener múltiples cuentas con mismo correo pero diferentes NITs)
#     """
#     from sqlalchemy import text
#     
#     data = request.get_json(force=True, silent=True) or {}
#     correo = data.get("correo", "").strip()
#     nit = data.get("nit", "").strip()
#     usuario = data.get("usuario", "").strip()
#     
#     if not correo or not nit or not usuario:
#         return jsonify({"success": False, "message": "Todos los campos son obligatorios"}), 400
#     
#     try:
#         # Buscar tercero por NIT
#         tercero = Tercero.query.filter_by(nit=nit).first()
#         
#         if not tercero:
#             # Por seguridad, no revelar si el NIT existe o no
#             return jsonify({
#                 "success": True, 
#                 "message": "Si los datos son correctos, recibirás un enlace de recuperación"
#             }), 200
#         
#         # Buscar usuario asociado a ese tercero Y con ese nombre de usuario Y correo
#         # Esto permite diferenciar entre múltiples cuentas del mismo correo (ej: empleado + proveedor)
#         user = Usuario.query.filter_by(tercero_id=tercero.id, usuario=usuario, correo=correo).first()
#         
#         if not user:
#             # Por seguridad, no revelar si la combinación existe
#             return jsonify({
#                 "success": True, 
#                 "message": "Si los datos son correctos, recibirás un enlace de recuperación"
#             }), 200
#         
#         # Generar token
#         token = secrets.token_urlsafe(32)
#         expiracion = datetime.now() + timedelta(hours=24)
#         
#         # Eliminar token anterior si existe y crear uno nuevo
#         db.session.execute(
#             text("DELETE FROM tokens_password WHERE usuario_id = :usuario_id"),
#             {'usuario_id': user.id}
#         )
#         db.session.execute(
#             text("""
#                 INSERT INTO tokens_password (usuario_id, token, expiracion, usado)
#                 VALUES (:usuario_id, :token, :expiracion, false)
#             """),
#             {'usuario_id': user.id, 'token': token, 'expiracion': expiracion}
#         )
#         db.session.commit()
#         
#         # Obtener info del tercero para el correo
#         tercero = db.session.get(Tercero, user.tercero_id) if user.tercero_id else None
#         nit = tercero.nit if tercero else "N/A"
#         
#         # Enviar correo
#         url_recuperacion = f"https://mtlm3ljz-8099.use2.devtunnels.ms/establecer-password/{token}"
#         
#         html_body = f"""
#         <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
#             <div style="background: linear-gradient(135deg, #16A085 0%, #138D75 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center;">
#                 <h1 style="margin: 0;">🔐 Recuperación de Contraseña</h1>
#             </div>
#             <div style="padding: 20px; background-color: #f9f9f9;">
#                 <p>Hola <strong>{user.usuario}</strong>,</p>
#                 <p>Recibimos una solicitud para recuperar tu contraseña. Haz clic en el siguiente botón:</p>
#                 <p style="text-align: center; margin: 30px 0;">
#                     <a href="{url_recuperacion}" style="display: inline-block; padding: 15px 30px; background-color: #16A085; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
#                         🔐 Recuperar Contraseña
#                     </a>
#                 </p>
#                 <p style="color: #e74c3c;">⚠️ Este enlace es válido por 24 horas.</p>
#                 <p>Si no solicitaste este cambio, ignora este correo.</p>
#             </div>
#             <div style="text-align: center; padding: 15px; background-color: #ecf0f1; border-radius: 0 0 8px 8px; color: #7f8c8d; font-size: 12px;">
#                 <p>Gestor Documental - Supertiendas Cañaveral</p>
#                 <p>NIT: {nit}</p>
#             </div>
#         </div>
#         """
#         
#         msg = Message(
#             subject='🔐 Recuperación de Contraseña - Gestor Documental',
#             sender=app.config['MAIL_DEFAULT_SENDER'],
#             recipients=[correo]
#         )
#         msg.html = html_body
#         msg.body = f"Recupera tu contraseña en: {url_recuperacion} (válido 24 horas)"
#         
#         with app.app_context():
#             mail.send(msg)
#         
#         log_security(f"TOKEN RECUPERACION ENVIADO POR CORREO | destinatario={correo} | usuario={user.usuario} | nit={nit}")
#         
#         return jsonify({
#             "success": True, 
#             "message": "Si el correo existe, recibirás un enlace de recuperación"
#         }), 200
#         
#     except Exception as e:
#         db.session.rollback()
#         log_security(f"ERROR solicitar recuperación | correo={correo} | error={str(e)}")
#         return jsonify({"success": False, "message": "Error al procesar solicitud"}), 500

# -------------------------------------------------
# 🧾 REGISTRO DE TERCEROS / PROVEEDORES
# -------------------------------------------------
@app.route("/api/registro/check_nit", methods=["POST"])
def api_check_nit():
    """
    Verifica si un NIT existe y retorna datos completos del tercero + radicado si existe
    
    Respuesta:
    - exists: bool
    - tercero: {nit, razon_social, correo, celular, estado}
    - radicado: {numero, estado, fecha} (si existe solicitud)
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        nit = data.get("nit", "").strip()
        
        if not nit:
            return jsonify({"exists": False, "message": "NIT requerido"}), 400
        
        tercero = Tercero.query.filter_by(nit=nit).first()
        
        if tercero:
            # Buscar si tiene solicitud de registro (radicado)
            solicitud = SolicitudRegistro.query.filter_by(tercero_id=tercero.id).first()
            
            response_data = {
                "exists": True,
                "tercero": {
                    "nit": tercero.nit,
                    "razon_social": tercero.razon_social,
                    "correo": tercero.correo,
                    "celular": tercero.celular,
                    "estado": tercero.estado
                }
            }
            
            # Agregar información de radicado si existe
            if solicitud:
                response_data["radicado"] = {
                    "numero": solicitud.radicado,
                    "estado": solicitud.estado,
                    "fecha": solicitud.fecha_solicitud.strftime("%d/%m/%Y") if solicitud.fecha_solicitud else None
                }
            
            return jsonify(response_data), 200
        else:
            return jsonify({"exists": False}), 200
            
    except Exception as e:
        log_security(f"ERROR CHECK_NIT | nit={nit} | error={str(e)}")
        return jsonify({"exists": False, "error": "Error al verificar NIT"}), 500

@app.route("/api/registro/proveedor", methods=["POST"])
def api_registro_proveedor():
    """Valida datos del proveedor sin registrar en BD (solo preparación)"""
    data = request.get_json(force=True, silent=True) or {}
    nit = data.get("nit", "").strip()
    tipo_persona = data.get("tipoPersona")
    
    print(f"🔍 DEBUG - Datos recibidos: {data}")
    print(f"🔍 DEBUG - Tipo de persona: {tipo_persona}")
    
    if not nit or not tipo_persona:
        return jsonify({"success": False, "message": "Datos incompletos: NIT y Tipo de Persona son obligatorios"}), 400
    
    # Validar que el NIT no existe (doble verificación)
    if Tercero.query.filter_by(nit=nit).first():
        return jsonify({"success": False, "message": "El NIT ya está registrado"}), 400
    
    # Validar campos obligatorios comunes
    if not data.get("correoElectronico", "").strip():
        return jsonify({"success": False, "message": "Campo requerido: Correo Electrónico"}), 400
    
    if not data.get("numeroCelular", "").strip():
        return jsonify({"success": False, "message": "Campo requerido: Número de Celular"}), 400
    
    if not data.get("aceptaTerminos"):
        return jsonify({"success": False, "message": "Debe aceptar los Términos y Condiciones"}), 400
    
    # Validar según tipo de persona
    if tipo_persona == "natural":
        if not data.get("primerNombre", "").strip():
            return jsonify({"success": False, "message": "Campo requerido: Primer Nombre"}), 400
        if not data.get("primerApellido", "").strip():
            return jsonify({"success": False, "message": "Campo requerido: Primer Apellido"}), 400
        razon_social = f"{data.get('primerNombre', '')} {data.get('segundoNombre', '')} {data.get('primerApellido', '')} {data.get('segundoApellido', '')}".strip()
    elif tipo_persona == "juridica":
        if not data.get("razonSocial", "").strip():
            return jsonify({"success": False, "message": "Campo requerido: Razón Social"}), 400
        razon_social = data.get("razonSocial")
    else:
        return jsonify({"success": False, "message": "Tipo de Persona inválido"}), 400
    
    # Datos válidos - devolver confirmación sin guardar en BD
    log_security(f"DATOS PROVEEDOR VALIDADOS | nit={nit} | tipo={tipo_persona}")
    return jsonify({
        "success": True, 
        "data": {
            "message": "Datos del proveedor válidos",
            "nit": nit,
            "razon_social": razon_social,
            "tipo_persona": tipo_persona
        }
    }), 200

# -------------------------------------------------
# � REGISTRO DE USUARIOS PARA TERCEROS
# -------------------------------------------------
@app.route("/api/registro/usuarios", methods=["POST"])
def api_registro_usuarios():
    data = request.get_json(force=True, silent=True) or {}
    tercero_id = data.get("tercero_id")
    usuarios_data = data.get("usuarios", [])
    
    if not tercero_id or not usuarios_data:
        return jsonify({"success": False, "message": "Datos incompletos"}), 400
    
    tercero = Tercero.query.get(tercero_id)
    if not tercero:
        return jsonify({"success": False, "message": "Tercero no encontrado"}), 404
        
    try:
        usuarios_creados = []
        for usuario_data in usuarios_data:
            nombre_usuario = usuario_data.get("nombre_usuario", "").strip().upper()
            correo = usuario_data.get("correo", "").strip().lower()
            password = usuario_data.get("password", "")
            
            if not all([nombre_usuario, correo, password]):
                continue
                
            # Verificar si ya existe el usuario o correo
            if Usuario.query.filter((Usuario.usuario == nombre_usuario) | (Usuario.correo == correo)).first():
                return jsonify({"success": False, "message": f"Usuario '{nombre_usuario}' o correo '{correo}' ya existe"}), 400
            
            # Crear usuario
            nuevo_usuario = Usuario(
                tercero_id=tercero_id,
                usuario=nombre_usuario,
                correo=correo,
                password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
                activo=False,  # Usuario se crea INACTIVO hasta revisión de documentos
                rol="externo"
            )
            db.session.add(nuevo_usuario)
            usuarios_creados.append({"usuario": nombre_usuario, "correo": correo})
        
        # Actualizar solicitud de registro
        solicitud = SolicitudRegistro.query.filter_by(tercero_id=tercero_id).first()
        if solicitud:
            solicitud.usuarios_creados = True
            solicitud.fecha_actualizacion = datetime.utcnow()
        
        db.session.commit()
        log_security(f"USUARIOS CREADOS | tercero_id={tercero_id} | cantidad={len(usuarios_creados)}")
        return jsonify({"success": True, "data": {"usuarios_creados": usuarios_creados}}), 201
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR CREACION USUARIOS | tercero_id={tercero_id} | error={str(e)}")
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500

# -------------------------------------------------
# 📁 CARGA DE DOCUMENTOS
# -------------------------------------------------
@app.route("/api/documentos/upload", methods=["POST"])
def api_cargar_documentos():
    """Carga documentos temporalmente (sin registrar en BD hasta finalizar)"""
    try:
        # Obtener NIT desde formulario (no tercero_id porque aún no existe en BD)
        nit = request.form.get("nit", "").strip()
        
        if not nit:
            return jsonify({"success": False, "message": "NIT requerido"}), 400
            
        # Crear carpeta temporal para documentos: documentos_terceros/NIT-TEMP-FECHA/
        import os
        from werkzeug.utils import secure_filename
        fecha_carpeta = datetime.now().strftime("%d-%m-%Y")
        carpeta_base = "documentos_terceros"
        carpeta_tercero = f"{nit}-TEMP-{fecha_carpeta}"
        ruta_completa = os.path.join(carpeta_base, carpeta_tercero)
        
        os.makedirs(ruta_completa, exist_ok=True)
        
        documentos_guardados = []
        archivos_requeridos = ["RUT", "CAMARA_COMERCIO", "CEDULA_REPRESENTANTE", 
                             "CERTIFICACION_BANCARIA", "FORMULARIO_CONOCIMIENTO_PROVEEDORES",
                             "DECLARACION_FONDOS_JURIDICA", "DECLARACION_FONDOS_NATURAL"]
        
        # Logging de todos los archivos recibidos en la request
        log_security(f"DEBUG UPLOAD | Archivos recibidos en request: {list(request.files.keys())}")
        
        for tipo_doc in archivos_requeridos:
            archivo = request.files.get(f"doc_{tipo_doc}")
            log_security(f"DEBUG UPLOAD | Buscando doc_{tipo_doc}: {'ENCONTRADO' if archivo and archivo.filename else 'NO ENCONTRADO'}")
            if archivo and archivo.filename:
                log_security(f"DEBUG UPLOAD | Guardando {tipo_doc}: {archivo.filename}")
                # Nombre temporal del archivo: NIT-TEMP-FECHA_TIPO.pdf
                nombre_archivo = f"{nit}-TEMP-{fecha_carpeta}_{tipo_doc}.pdf"
                ruta_archivo = os.path.join(ruta_completa, nombre_archivo)
                archivo.save(ruta_archivo)
                documentos_guardados.append({
                    "tipo": tipo_doc,
                    "nombre": nombre_archivo,
                    "ruta": ruta_archivo,
                    "tamaño": os.path.getsize(ruta_archivo)
                })
        
        # Validar que se hayan cargado todos los documentos requeridos
        if len(documentos_guardados) < 7:
            documentos_faltantes = [doc for doc in archivos_requeridos if not any(d["tipo"] == doc for d in documentos_guardados)]
            log_security(f"ERROR DOCUMENTOS INCOMPLETOS | nit={nit} | cargados={len(documentos_guardados)}/7 | faltantes={documentos_faltantes}")
            return jsonify({
                "success": False, 
                "message": f"Documentos incompletos. Se cargaron {len(documentos_guardados)} de 7 requeridos. Faltan: {', '.join(documentos_faltantes)}"
            }), 400
        
        # Solo guardar archivos, NO en BD aún
        log_security(f"DOCUMENTOS TEMPORALES COMPLETOS | nit={nit} | docs={len(documentos_guardados)}")
        
        return jsonify({
            "success": True, 
            "data": {
                "documentos_cargados": len(documentos_guardados),
                "carpeta": carpeta_tercero,
                "completos": True,
                "nit": nit,
                "documentos": documentos_guardados
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR CARGA DOCUMENTOS | error={str(e)}")
        return jsonify({"success": False, "message": "Error al cargar documentos"}), 500

# -------------------------------------------------
# 🎯 FINALIZAR SOLICITUD Y GENERAR RADICADO
# -------------------------------------------------
@app.route("/api/registro/finalizar", methods=["POST"])
def api_finalizar_solicitud():
    """Registra tercero, usuarios y documentos completamente + genera radicado"""
    try:
        data = request.get_json(force=True, silent=True) or {}
        
        # Datos del tercero
        tercero_data = data.get("tercero_data", {})
        usuarios_data = data.get("usuarios_data", [])
        nit = tercero_data.get("nit", "").strip()
        
        log_security(f"DEBUG FINALIZAR | tercero_data={len(tercero_data)} | usuarios_data={len(usuarios_data)} | nit={nit}")
        
        if not nit or not tercero_data or not usuarios_data:
            log_security(f"ERROR FINALIZAR | Datos incompletos: nit={nit}, tercero_data={bool(tercero_data)}, usuarios_data={bool(usuarios_data)}")
            return jsonify({"success": False, "message": "Datos incompletos"}), 400
        
        # 🆕 VALIDAR LÍMITE DE USUARIOS (5 usuarios máximo, salvo NITs especiales)
        max_usuarios = int(os.getenv("MAX_USUARIOS_POR_TERCERO", 5))
        nits_especiales = os.getenv("NITS_ESPECIALES_SIN_LIMITE", "").split(",")
        nits_especiales = [n.strip() for n in nits_especiales if n.strip()]
        
        es_nit_especial = nit in nits_especiales
        
        if not es_nit_especial and len(usuarios_data) > max_usuarios:
            log_security(f"ERROR FINALIZAR | Demasiados usuarios: {len(usuarios_data)} > {max_usuarios} (NIT: {nit})")
            return jsonify({
                "success": False, 
                "message": f"Máximo {max_usuarios} usuarios permitidos por proveedor. Si requiere más usuarios, contacte al administrador."
            }), 400
        
        if es_nit_especial:
            log_security(f"INFO | NIT especial sin límite de usuarios: {nit} | usuarios solicitados: {len(usuarios_data)}")
        
        # Verificar que el NIT no exista (última validación)
        tercero_existente = Tercero.query.filter_by(nit=nit).first()
        if tercero_existente:
            log_security(f"ERROR FINALIZAR | NIT ya existe: {nit}")
            return jsonify({"success": False, "message": "El NIT ya está registrado"}), 400
        
        log_security(f"DEBUG FINALIZAR | NIT disponible: {nit}")
        
        # 1. REGISTRAR TERCERO
        log_security(f"DEBUG FINALIZAR | Creando tercero con datos: {tercero_data}")
        tercero = Tercero(
            nit=nit,
            tipo_persona=tercero_data.get("tipoPersona"),
            razon_social=tercero_data.get("razonSocial"),
            primer_nombre=tercero_data.get("primerNombre"),
            segundo_nombre=tercero_data.get("segundoNombre"),
            primer_apellido=tercero_data.get("primerApellido"),
            segundo_apellido=tercero_data.get("segundoApellido"),
            correo=tercero_data.get("correoElectronico"),
            celular=tercero_data.get("numeroCelular"),
            acepta_terminos=bool(tercero_data.get("aceptaTerminos")),
            acepta_contacto=bool(tercero_data.get("aceptaContacto")),
            estado="pendiente"
        )
        db.session.add(tercero)
        db.session.flush()  # Para obtener el ID
        log_security(f"DEBUG FINALIZAR | Tercero creado con ID: {tercero.id}")
        
        # 2. GENERAR RADICADO
        radicado = f"RAD-{tercero.id:06d}"
        log_security(f"DEBUG FINALIZAR | Radicado generado: {radicado}")
        
        # 3. CREAR SOLICITUD
        solicitud = SolicitudRegistro(
            tercero_id=tercero.id,
            radicado=radicado,
            estado="pendiente",
            documentos_completos=True,
            usuarios_creados=True
        )
        db.session.add(solicitud)
        
        # 4. CREAR USUARIOS
        log_security(f"DEBUG FINALIZAR | Creando usuarios: {usuarios_data}")
        usuarios_creados = []
        for usuario_data in usuarios_data:
            nombre_usuario = usuario_data.get("nombre_usuario", "").strip().upper()
            correo = usuario_data.get("correo", "").strip().lower()
            password = usuario_data.get("password", "")
            
            if not all([nombre_usuario, correo, password]):
                continue
                
            # Validar duplicados
            log_security(f"DEBUG FINALIZAR | Validando duplicados: usuario={nombre_usuario}, correo={correo}")
            duplicado = Usuario.query.filter((Usuario.usuario == nombre_usuario) | (Usuario.correo == correo)).first()
            if duplicado:
                log_security(f"ERROR FINALIZAR | Usuario duplicado encontrado: {nombre_usuario} / {correo} | ID existente: {duplicado.id}")
                db.session.rollback()
                return jsonify({"success": False, "message": f"Usuario o correo ya existe: {nombre_usuario} / {correo}"}), 400
            
            usuario = Usuario(
                tercero_id=tercero.id,
                usuario=nombre_usuario,
                correo=correo,
                password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
                activo=False  # Usuario se crea INACTIVO hasta revisión de documentos
            )
            db.session.add(usuario)
            usuarios_creados.append(nombre_usuario)
        
        # 5. REGISTRAR DOCUMENTOS DESDE ARCHIVOS TEMPORALES
        fecha_carpeta = datetime.now().strftime("%d-%m-%Y")
        carpeta_temp = f"documentos_terceros/{nit}-TEMP-{fecha_carpeta}"
        carpeta_final = f"documentos_terceros/{nit}-{radicado}-{fecha_carpeta}"
        
        documentos_procesados = []
        
        log_security(f"DEBUG FINALIZAR | Procesando documentos desde carpeta temporal: {carpeta_temp}")
        
        if os.path.exists(carpeta_temp):
            archivos_encontrados = os.listdir(carpeta_temp)
            log_security(f"DEBUG FINALIZAR | Archivos encontrados en carpeta temporal: {archivos_encontrados}")
            
            os.makedirs(carpeta_final, exist_ok=True)
            log_security(f"DEBUG FINALIZAR | Carpeta final creada: {carpeta_final}")
            
            for archivo in archivos_encontrados:
                if archivo.endswith('.pdf'):
                    log_security(f"DEBUG FINALIZAR | Procesando archivo PDF: {archivo}")
                    ruta_temp = os.path.join(carpeta_temp, archivo)
                    log_security(f"DEBUG FINALIZAR | Ruta temporal: {ruta_temp}")
                    
                    # Extraer tipo de documento del nombre
                    tipo_doc = archivo.replace(f"{nit}-TEMP-{fecha_carpeta}_", "").replace(".pdf", "")
                    log_security(f"DEBUG FINALIZAR | Tipo de documento extraído: {tipo_doc}")
                    
                    # Nuevo nombre con radicado
                    nuevo_nombre = f"{nit}-{radicado}-{fecha_carpeta}_{tipo_doc}.pdf"
                    ruta_final = os.path.join(carpeta_final, nuevo_nombre)
                    log_security(f"DEBUG FINALIZAR | Moviendo archivo: {ruta_temp} -> {ruta_final}")
                    
                    # Mover archivo
                    try:
                        os.rename(ruta_temp, ruta_final)
                        log_security(f"DEBUG FINALIZAR | Archivo movido exitosamente: {nuevo_nombre}")
                    except Exception as e:
                        log_security(f"ERROR FINALIZAR | Error moviendo archivo {archivo}: {str(e)}")
                        continue
                    
                    # Registrar en BD
                    try:
                        tamaño = os.path.getsize(ruta_final)
                        documento = DocumentoTercero(
                            tercero_id=tercero.id,
                            radicado=radicado,
                            tipo_documento=tipo_doc,
                            nombre_archivo=nuevo_nombre,
                            ruta_archivo=ruta_final,
                            tamaño_archivo=tamaño
                        )
                        db.session.add(documento)
                        documentos_procesados.append(tipo_doc)
                        log_security(f"DEBUG FINALIZAR | Documento registrado en BD: {tipo_doc} ({tamaño} bytes)")
                    except Exception as e:
                        log_security(f"ERROR FINALIZAR | Error registrando documento {tipo_doc} en BD: {str(e)}")
                        continue
            
            # Eliminar carpeta temporal vacía
            try:
                os.rmdir(carpeta_temp)
                log_security(f"DEBUG FINALIZAR | Carpeta temporal eliminada: {carpeta_temp}")
            except Exception as e:
                log_security(f"WARNING FINALIZAR | No se pudo eliminar carpeta temporal: {str(e)}")
        else:
            log_security(f"ERROR FINALIZAR | Carpeta temporal no existe: {carpeta_temp}")
        
        log_security(f"DEBUG FINALIZAR | Documentos procesados: {len(documentos_procesados)} - {documentos_procesados}")
        db.session.commit()
        
        log_security(f"REGISTRO COMPLETO | nit={nit} | tercero_id={tercero.id} | radicado={radicado} | usuarios={len(usuarios_creados)} | docs={len(documentos_procesados)}")
        
        # 📧 Enviar correo de confirmación
        correo_destinatario = tercero_data.get("correoElectronico")
        if correo_destinatario:
            razon_social_completa = tercero_data.get("razonSocial") or f"{tercero_data.get('primerNombre', '')} {tercero_data.get('primerApellido', '')}".strip()
            envio_exitoso, mensaje_envio = enviar_correo_confirmacion_radicado(
                destinatario=correo_destinatario,
                nit=nit,
                razon_social=razon_social_completa,
                radicado=radicado
            )
            if envio_exitoso:
                log_security(f"CORREO CONFIRMACIÓN ENVIADO | radicado={radicado} | destinatario={correo_destinatario}")
            else:
                log_security(f"ADVERTENCIA | No se pudo enviar correo de confirmación | radicado={radicado} | error={mensaje_envio}")
        
        return jsonify({
            "success": True,
            "data": {
                "radicado": radicado,
                "tercero_id": tercero.id,
                "usuarios_creados": usuarios_creados,
                "documentos_procesados": documentos_procesados,
                "mensaje": "Solicitud registrada exitosamente",
                "correo_enviado": correo_destinatario is not None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_detallado = traceback.format_exc()
        print(f"\n{'='*60}")
        print(f"❌ ERROR EN /api/registro/finalizar")
        print(f"{'='*60}")
        print(f"NIT: {nit if 'nit' in locals() else 'NO DISPONIBLE'}")
        print(f"Error: {str(e)}")
        print(f"Tipo: {type(e).__name__}")
        print(f"\nTraceback completo:")
        print(error_detallado)
        print(f"{'='*60}\n")
        log_security(f"ERROR FINALIZAR SOLICITUD | nit={nit if 'nit' in locals() else 'N/A'} | error={str(e)} | tipo={type(e).__name__}")
        log_security(f"TRACEBACK | {error_detallado}")
        return jsonify({"success": False, "message": "Error al procesar la solicitud. Intente nuevamente."}), 500

# -------------------------------------------------
# 📋 CONSULTA DE RADICADOS
# -------------------------------------------------
@app.route("/api/consulta/radicado", methods=["POST"])
def api_consulta_radicado():
    data = request.get_json(force=True, silent=True) or {}
    radicado = data.get("radicado", "").strip().upper()
    
    if not radicado:
        return jsonify({"success": False, "message": "Radicado requerido"}), 400
    
    try:
        # Buscar la solicitud por radicado
        solicitud = SolicitudRegistro.query.filter_by(radicado=radicado).first()
        
        if not solicitud:
            return jsonify({
                "success": False, 
                "message": "Radicado no encontrado"
            }), 404
        
        # Calcular días en el estado actual
        dias_en_estado = (datetime.utcnow() - solicitud.fecha_actualizacion).days
        
        # Preparar respuesta según el estado
        estado_info = {
            "pendiente": {
                "mensaje": "Pendiente por Revisión",
                "tipo": "info"
            },
            "en_revision": {
                "mensaje": "En Revisión",
                "tipo": "info" 
            },
            "aprobado": {
                "mensaje": "Aprobada", 
                "tipo": "success"
            },
            "rechazado": {
                "mensaje": "Rechazada",
                "tipo": "error"
            }
        }
        
        info = estado_info.get(solicitud.estado, {"mensaje": "Estado Desconocido", "tipo": "info"})
        
        response_data = {
            "success": True,
            "data": {
                "radicado": solicitud.radicado,
                "estado": info["mensaje"],
                "tipo": info["tipo"],
                "dias_en_estado": dias_en_estado,
                "fecha_solicitud": solicitud.fecha_solicitud.strftime("%d/%m/%Y"),
                "observaciones": solicitud.observaciones or None,
                "documentos_completos": solicitud.documentos_completos,
                "usuarios_creados": solicitud.usuarios_creados
            }
        }
        
        log_security(f"CONSULTA RADICADO | radicado={radicado} | estado={solicitud.estado}")
        return jsonify(response_data), 200
        
    except Exception as e:
        log_security(f"ERROR CONSULTA RADICADO | radicado={radicado} | error={str(e)}")
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500

# -------------------------------------------------
# 🔐 RECUPERACIÓN DE CONTRASEÑA MEJORADA
# -------------------------------------------------
@app.route("/api/auth/forgot_request", methods=["POST"])
def api_forgot_request():
    data = request.get_json(force=True, silent=True) or {}
    nit = data.get("nit", "").strip()
    nombre_usuario = data.get("usuario", "").strip()  # 🔧 FIX: No convertir a mayúsculas
    correo = data.get("correo", "").strip()  # No convertir a lower aquí
    
    if not all([nit, nombre_usuario, correo]):
        return jsonify({"ok": False, "message": "NIT, usuario y correo son requeridos"}), 400
    
    # Verificar que el tercero existe
    tercero = Tercero.query.filter_by(nit=nit).first()
    if not tercero:
        return jsonify({"ok": False, "message": "Los datos proporcionados no son válidos"}), 404
    
    # Verificar que el usuario existe y pertenece al tercero
    # 🔧 FIX: Comparación case-insensitive para el correo
    from sqlalchemy import func
    user = Usuario.query.filter(
        Usuario.tercero_id == tercero.id,
        Usuario.usuario == nombre_usuario,
        func.lower(Usuario.correo) == correo.lower()
    ).first()
    
    if not user:
        return jsonify({"ok": False, "message": "Los datos proporcionados no son válidos"}), 404

    # Generar token de 6 dígitos para mayor seguridad
    token = f"{secrets.randbelow(1000000):06d}"
    
    rec = TokenRecuperacion(
        usuario_id=user.id, 
        token=token, 
        expira=datetime.utcnow() + timedelta(minutes=10),
        nit=nit,
        nombre_usuario=nombre_usuario,
        intentos_validacion=0
    )
    db.session.add(rec)
    db.session.commit()

    # Enviar token por correo electrónico (usar el correo real de la BD, no el ingresado)
    correo_real = user.correo
    success_correo, mensaje_correo = enviar_correo_token_recuperacion(correo_real, nit, nombre_usuario, token)
    
    # Enviar token por Telegram (adicional)
    success_telegram, mensaje_telegram = enviar_telegram_token_recuperacion(nit, nombre_usuario, token)
    
    # Determinar respuesta basada en los envíos
    if success_correo or success_telegram:
        # Al menos un método funcionó
        mensajes = []
        if success_correo:
            mensajes.append(f"correo electrónico ({correo_real})")
        if success_telegram:
            mensajes.append("Telegram")
        
        canales = " y ".join(mensajes)
        return jsonify({"ok": True, "message": f"✅ Código de verificación enviado por {canales}"}), 200
    else:
        # Ambos métodos fallaron - imprimir en consola como fallback
        print("\n" + "="*80)
        print(f"⚠️ CÓDIGO DE RECUPERACIÓN GENERADO (Envío falló)")
        print("="*80)
        print(f"📧 Correo destino: {correo_real}")
        print(f"👤 Usuario: {nombre_usuario}")
        print(f"🏢 NIT: {nit}")
        print(f"🔑 TOKEN: {token}")
        print(f"❌ Error Correo: {mensaje_correo}")
        print(f"❌ Error Telegram: {mensaje_telegram}")
        print("="*80 + "\n")
        log_security(f"TOKEN RECUPERACION GENERADO (sin envío exitoso) | nit={nit} | user={nombre_usuario} | correo={correo_real} | TOKEN={token}")
        # Aún así retornar éxito al usuario
        return jsonify({"ok": True, "message": f"Código de verificación generado. Revisa tu correo/Telegram o contacta al administrador."}), 200

@app.route("/api/auth/forgot_verify", methods=["POST"])
def api_forgot_verify():
    data = request.get_json(force=True, silent=True) or {}
    token = data.get("token", "").strip()
    
    rec = TokenRecuperacion.query.filter_by(token=token, usado=False).first()
    if not rec:
        return jsonify({"ok": False, "message": "Código inválido"}), 400
    
    if rec.expira < datetime.utcnow():
        return jsonify({"ok": False, "message": "Código vencido. Solicite uno nuevo"}), 400
    
    # Incrementar intentos
    rec.intentos_validacion += 1
    
    # Máximo 3 intentos
    if rec.intentos_validacion > 3:
        rec.usado = True  # Bloquear token
        db.session.commit()
        return jsonify({"ok": False, "message": "Demasiados intentos. Solicite un nuevo código"}), 400
    
    db.session.commit()
    log_security(f"TOKEN VERIFICADO | nit={rec.nit} | user={rec.nombre_usuario} | intento={rec.intentos_validacion}")
    return jsonify({"ok": True, "message": "Código válido"}), 200

@app.route("/api/auth/change_password", methods=["POST"])
def api_change_password():
    data = request.get_json(force=True, silent=True) or {}
    token = data.get("token", "").strip()
    new_password = data.get("new_password", "")

    if not token or not new_password:
        return jsonify({"ok": False, "message": "Token y nueva contraseña requeridos"}), 400

    rec = TokenRecuperacion.query.filter_by(token=token, usado=False).first()
    if not rec or rec.expira < datetime.utcnow():
        return jsonify({"ok": False, "message": "Token inválido o vencido"}), 400

    user = Usuario.query.get(rec.usuario_id)
    if not user:
        return jsonify({"ok": False, "message": "Usuario no encontrado"}), 404

    # Verificar contraseñas usadas previamente
    used = PasswordUsada.query.filter_by(usuario_id=user.id).all()
    for item in used:
        if bcrypt.check_password_hash(item.password_hash, new_password):
            return jsonify({"ok": False, "message": "Contraseña ya fue usada. Elige otra."}), 400

    # Guardar contraseña anterior al historial
    db.session.add(PasswordUsada(usuario_id=user.id, password_hash=user.password_hash))
    
    # Actualizar contraseña
    user.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
    
    # Marcar token como usado
    rec.usado = True
    db.session.commit()
    log_security(f"CAMBIO DE CONTRASEÑA | user_id={user.id}")
    return jsonify({"ok": True, "message": "Contraseña actualizada"}), 200

# -------------------------------------------------
# � LOGOUT (CIERRE DE SESIÓN)
# -------------------------------------------------
@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    """
    Endpoint para cerrar sesión (manual o automático por inactividad).
    Registra el evento de logout, limpia la sesión en servidor,
    y envía notificaciones por email/Telegram cuando es por inactividad.
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        usuario = data.get("usuario", "Desconocido")
        nit = data.get("nit", "N/A")
        motivo = data.get("motivo", "manual")
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        ua = request.headers.get("User-Agent", "")
        
        # Log del evento de logout
        log_security(f"🔒 LOGOUT | Usuario: {usuario} | NIT: {nit} | Motivo: {motivo} | IP: {ip}")
        
        # Limpiar sesión del servidor
        session.clear()
        
        # Si el logout fue por inactividad, enviar notificaciones
        if motivo == "inactividad_25min":
            try:
                # Notificación por correo electrónico
                asunto = "⚠️ Alerta de Seguridad: Cierre de Sesión por Inactividad"
                mensaje_html = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                        .container {{ background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }}
                        h1 {{ color: #ff6b00; border-bottom: 3px solid #ff6b00; padding-bottom: 10px; }}
                        .info {{ background-color: #fff3cd; padding: 15px; border-left: 5px solid #ffc107; margin: 20px 0; }}
                        .detail {{ margin: 10px 0; padding: 8px; background-color: #f8f9fa; border-radius: 5px; }}
                        .label {{ font-weight: bold; color: #333; }}
                        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.9em; color: #666; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🔒 Cierre de Sesión por Inactividad</h1>
                        
                        <div class="info">
                            <p><strong>⏰ Se ha cerrado automáticamente una sesión de usuario por inactividad (25 minutos).</strong></p>
                        </div>
                        
                        <div class="detail">
                            <span class="label">👤 Usuario:</span> {usuario}
                        </div>
                        <div class="detail">
                            <span class="label">🏢 NIT:</span> {nit}
                        </div>
                        <div class="detail">
                            <span class="label">🌐 IP:</span> {ip}
                        </div>
                        <div class="detail">
                            <span class="label">📅 Fecha/Hora:</span> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        </div>
                        <div class="detail">
                            <span class="label">🖥️ User Agent:</span> {ua[:100]}...
                        </div>
                        
                        <div class="footer">
                            <p>Este es un mensaje automático del Sistema de Gestión Documental - Supertiendas Cañaveral.</p>
                            <p>Si este cierre de sesión fue inesperado, por favor contacte al administrador del sistema.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                # Enviar correo si está configurado
                if app.config.get('MAIL_SERVER'):
                    msg = Message(
                        subject=asunto,
                        recipients=[app.config.get('MAIL_DEFAULT_SENDER', 'admin@example.com')],
                        html=mensaje_html
                    )
                    mail.send(msg)
                    log_security(f"📧 Email enviado: Logout por inactividad | Usuario: {usuario}")
            except Exception as e:
                log_security(f"❌ Error enviando email de logout: {str(e)}")
            
            try:
                # Notificación por Telegram si está configurado
                bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
                chat_id = os.getenv('TELEGRAM_CHAT_ID')
                
                if bot_token and chat_id:
                    mensaje_telegram = f"""
🔒 *CIERRE DE SESIÓN POR INACTIVIDAD*

⏰ *Motivo:* 25 minutos sin actividad
👤 *Usuario:* {usuario}
🏢 *NIT:* {nit}
🌐 *IP:* {ip}
📅 *Fecha:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

_Sistema Gestor Documental - Supertiendas Cañaveral_
                    """
                    
                    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    payload = {
                        "chat_id": chat_id,
                        "text": mensaje_telegram.strip(),
                        "parse_mode": "Markdown"
                    }
                    
                    import requests
                    response = requests.post(url, json=payload, timeout=5)
                    
                    if response.status_code == 200:
                        log_security(f"📱 Telegram enviado: Logout por inactividad | Usuario: {usuario}")
                    else:
                        log_security(f"❌ Error Telegram ({response.status_code}): {response.text}")
            except Exception as e:
                log_security(f"❌ Error enviando Telegram de logout: {str(e)}")
        
        return jsonify({
            "success": True,
            "message": "Sesión cerrada correctamente",
            "redirect": "/"
        }), 200
        
    except Exception as e:
        log_security(f"❌ ERROR EN LOGOUT: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Error al cerrar sesión",
            "message": str(e)
        }), 500

# -------------------------------------------------
# �👥 ADMINISTRACIÓN DE USUARIOS
# -------------------------------------------------

@app.route("/api/admin/activar_usuario", methods=["POST"])
def api_activar_usuario():
    """Función administrativa para activar/desactivar usuarios"""
    data = request.get_json(force=True, silent=True) or {}
    usuario_id = data.get("usuario_id")
    activar = data.get("activar", True)  # True para activar, False para desactivar
    
    if not usuario_id:
        return jsonify({"success": False, "message": "ID de usuario requerido"}), 400
    
    try:
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
        
        # Actualizar estado
        usuario.activo = activar
        db.session.commit()
        
        # Log de seguridad
        accion = "ACTIVADO" if activar else "DESACTIVADO"
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        log_security(f"USUARIO {accion} | user_id={usuario_id} | usuario={usuario.usuario} | admin_ip={ip}")
        
        return jsonify({
            "success": True, 
            "message": f"Usuario {usuario.usuario} {'activado' if activar else 'desactivado'} correctamente",
            "data": {
                "usuario_id": usuario_id,
                "usuario": usuario.usuario,
                "activo": usuario.activo
            }
        }), 200
        
    except Exception as e:
        log_security(f"ERROR ADMIN ACTIVAR USUARIO | user_id={usuario_id} | error={str(e)}")
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500

@app.route("/api/admin/agregar_usuario_tercero", methods=["POST"])
def api_agregar_usuario_tercero():
    """
    🆕 Endpoint administrativo para agregar usuarios adicionales a un tercero existente
    Respeta límite de 5 usuarios, excepto para NITs especiales
    """
    data = request.get_json(force=True, silent=True) or {}
    nit = data.get("nit", "").strip()
    usuario_data = data.get("usuario", {})
    
    if not nit or not usuario_data:
        return jsonify({"success": False, "message": "Datos incompletos"}), 400
    
    try:
        # Buscar tercero por NIT
        tercero = Tercero.query.filter_by(nit=nit).first()
        if not tercero:
            return jsonify({"success": False, "message": f"Tercero con NIT {nit} no encontrado"}), 404
        
        # Validar límite de usuarios
        max_usuarios = int(os.getenv("MAX_USUARIOS_POR_TERCERO", 5))
        nits_especiales = os.getenv("NITS_ESPECIALES_SIN_LIMITE", "").split(",")
        nits_especiales = [n.strip() for n in nits_especiales if n.strip()]
        
        es_nit_especial = nit in nits_especiales
        usuarios_actuales = Usuario.query.filter_by(tercero_id=tercero.id).count()
        
        if not es_nit_especial and usuarios_actuales >= max_usuarios:
            log_security(f"ERROR AGREGAR USUARIO | NIT {nit} ya tiene {usuarios_actuales} usuarios (máx: {max_usuarios})")
            return jsonify({
                "success": False,
                "message": f"El tercero ya tiene {usuarios_actuales} usuarios (máximo {max_usuarios}). Para agregar más, contacte al administrador del sistema."
            }), 400
        
        # Extraer datos del nuevo usuario
        nombre_usuario = usuario_data.get("nombre_usuario", "").strip().upper()
        correo = usuario_data.get("correo", "").strip().lower()
        password = usuario_data.get("password", "")
        
        if not all([nombre_usuario, correo, password]):
            return jsonify({"success": False, "message": "Datos de usuario incompletos"}), 400
        
        # Validar duplicados
        if Usuario.query.filter_by(correo=correo).first():
            return jsonify({"success": False, "message": f"El correo {correo} ya está registrado"}), 400
        
        if Usuario.query.filter_by(tercero_id=tercero.id, usuario=nombre_usuario).first():
            return jsonify({"success": False, "message": f"El usuario {nombre_usuario} ya existe para este tercero"}), 400
        
        # Crear nuevo usuario
        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        nuevo_usuario = Usuario(
            tercero_id=tercero.id,
            usuario=nombre_usuario,
            correo=correo,
            password_hash=password_hash,
            activo=False,  # Inicia inactivo, requiere activación administrativa
            rol="externo"
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        log_security(f"USUARIO AGREGADO ADMIN | NIT={nit} | usuario={nombre_usuario} | total_usuarios={usuarios_actuales + 1} | admin_ip={ip}")
        
        return jsonify({
            "success": True,
            "message": f"Usuario {nombre_usuario} creado correctamente (inactivo). Total usuarios: {usuarios_actuales + 1}",
            "data": {
                "usuario_id": nuevo_usuario.id,
                "usuario": nuevo_usuario.usuario,
                "correo": nuevo_usuario.correo,
                "activo": nuevo_usuario.activo,
                "total_usuarios_tercero": usuarios_actuales + 1
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR AGREGAR USUARIO ADMIN | NIT={nit} | error={str(e)}")
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500

@app.route("/api/admin/listar_usuarios", methods=["GET"])
def api_listar_usuarios():
    """Función administrativa para listar todos los usuarios y su estado"""
    try:
        usuarios = db.session.query(Usuario, Tercero).join(Tercero, Usuario.tercero_id == Tercero.id).all()
        
        usuarios_data = []
        for usuario, tercero in usuarios:
            usuarios_data.append({
                "id": usuario.id,
                "usuario": usuario.usuario,
                "correo": usuario.correo,
                "activo": usuario.activo,
                "rol": usuario.rol,
                "fecha_creacion": usuario.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S") if usuario.fecha_creacion else None,
                "tercero": {
                    "nit": tercero.nit,
                    "razon_social": tercero.razon_social,
                    "estado": tercero.estado
                }
            })
        
        return jsonify({
            "success": True,
            "data": usuarios_data,
            "total": len(usuarios_data)
        }), 200
        
    except Exception as e:
        log_security(f"ERROR ADMIN LISTAR USUARIOS | error={str(e)}")
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500

# ==============================================
# 🤖 ENDPOINT: WEBHOOK DE TELEGRAM
# ==============================================
@app.route('/api/telegram/webhook', methods=['POST'])
def telegram_webhook():
    """
    Webhook para recibir comandos de Telegram.
    Este endpoint debe configurarse en BotFather:
    https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://tudominio.com/api/telegram/webhook
    """
    try:
        # Obtener actualización de Telegram
        update = request.get_json()
        log_security(f"TELEGRAM WEBHOOK RECIBIDO | update={update}")
        
        # Importar módulos de notificaciones y bot
        from telegram_bot import procesar_comando_telegram, enviar_respuesta_telegram
        
        # Procesar comando
        respuesta = procesar_comando_telegram(update)
        
        # Enviar respuesta
        if 'message' in update and 'chat' in update['message']:
            chat_id = update['message']['chat']['id']
            enviar_respuesta_telegram(chat_id, respuesta)
        
        return jsonify({"success": True}), 200
        
    except Exception as e:
        log_security(f"ERROR EN WEBHOOK TELEGRAM | error={str(e)}")
        return jsonify({"success": False, "message": "Error procesando webhook"}), 500


# ==============================================
# 🔧 ENDPOINT: CONFIGURAR WEBHOOK DE TELEGRAM (DESARROLLO)
# ==============================================
@app.route('/api/telegram/setup_webhook', methods=['POST'])
def setup_webhook():
    """
    Endpoint para configurar el webhook de Telegram desde la aplicación.
    Solo para desarrollo. En producción, configurar manualmente.
    """
    try:
        data = request.get_json()
        webhook_url = data.get('webhook_url')  # ej: https://tudominio.com/api/telegram/webhook
        
        if not webhook_url:
            return jsonify({"success": False, "message": "webhook_url es requerido"}), 400
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        if not bot_token:
            return jsonify({"success": False, "message": "TELEGRAM_BOT_TOKEN no configurado"}), 500
        
        import requests
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        payload = {'url': webhook_url}
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            log_security(f"TELEGRAM WEBHOOK CONFIGURADO | url={webhook_url} | result={result}")
            return jsonify({"success": True, "result": result}), 200
        else:
            log_security(f"ERROR CONFIGURANDO WEBHOOK TELEGRAM | status={response.status_code}")
            return jsonify({"success": False, "message": "Error configurando webhook"}), 500
            
    except Exception as e:
        log_security(f"ERROR SETUP WEBHOOK TELEGRAM | error={str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ==============================================
# 📊 ENDPOINT: ESTADÍSTICAS DE NOTIFICACIONES
# ==============================================
@app.route('/api/notificaciones/stats', methods=['GET'])
def notificaciones_stats():
    """Retorna estadísticas de notificaciones configuradas"""
    try:
        from notificaciones import obtener_estadisticas_notificaciones
        stats = obtener_estadisticas_notificaciones()
        return jsonify({"success": True, "data": stats}), 200
    except Exception as e:
        log_security(f"ERROR OBTENIENDO STATS NOTIFICACIONES | error={str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# -------------------------------------------------
# 🎨 FILTROS PERSONALIZADOS DE JINJA2
# -------------------------------------------------
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y %H:%M'):
    """Formatea objetos datetime para mostrar en templates"""
    if value is None:
        return ""
    if isinstance(value, str):
        return value  # Ya es string, retornar tal cual
    try:
        return value.strftime(format)
    except:
        return str(value)  # Fallback en caso de error


# -------------------------------------------------
# 📦 REGISTRO DE BLUEPRINTS (MÓDULOS)
# -------------------------------------------------
# Importar blueprints de módulos
from modules.configuracion.routes import configuracion_bp         # ✅ Configuración (Centros de Operación, Tipos Doc)
from modules.notas_contables.routes import notas_bp              # ✅ API REST Archivo Digital (Octubre 21, 2025)
from modules.notas_contables.pages import archivo_digital_pages_bp  # ✅ Páginas HTML Archivo Digital
# from modules.usuarios_internos.routes import usuarios_internos_bp
from modules.recibir_facturas.routes import recibir_facturas_bp  # ✅ Circular import RESUELTO con extensions.py
from modules.relaciones.routes import relaciones_bp              # ✅ Módulo Relaciones (Octubre 19, 2025)
from modules.causaciones.routes import causaciones_bp            # ✅ Módulo Causaciones (Octubre 23, 2025)
from modules.admin.monitoreo import monitoreo_bp                 # ✅ Módulo Monitoreo (Octubre 23, 2025)
from modules.dian_vs_erp.routes import dian_vs_erp_bp            # ✅ Módulo DIAN vs ERP (Noviembre 13, 2025)

# Importar modelos del módulo de facturas para que SQLAlchemy los registre
from modules.recibir_facturas.models import (
    FacturaTemporal, 
    FacturaRecibida, 
    ObservacionFactura, 
    ObservacionFacturaTemporal
)

# Importar modelos del módulo de relaciones
from modules.relaciones.models import (
    RelacionFactura,
    Consecutivo
)

# Importar modelos del módulo Archivo Digital
from modules.notas_contables.models import (
    DocumentoContable,
    AdjuntoDocumento,
    HistorialDocumento
)

# Importar modelos de configuración
from modules.configuracion.models import (
    TipoDocumento,
    CentroOperacion
)

# Importar modelos del módulo Causaciones
from modules.causaciones.models import (
    DocumentoCausacion,
    ObservacionCausacion
)

# Importar modelos del módulo Monitoreo
from modules.admin.monitoreo.models import (
    AlertaSeguridad,
    LogAccion,
    SesionActiva,
    LogSistema,
    LogAuditoria,
    AlertaSistema,
    MetricaRendimiento,
    IPBlanca
)

# Importar modelos del módulo Usuarios y Permisos
from modules.admin.usuarios_permisos.models import (
    PermisoUsuario,
    RolUsuario,
    UsuarioRol,
    InvitacionUsuario,
    AuditoriaPermisos,
    CatalogoPermisos
)

# Importar modelos del módulo DIAN vs ERP (Sistema Híbrido SQLite+PostgreSQL)
# TEMPORAL: Comentado hasta que se implementen los modelos
# from modules.dian_vs_erp.models import (
#     ReporteDian,
#     LogProcesamiento,
#     ConfiguracionDian,
#     DianSqliteManager,
#     obtener_estadisticas_sqlite
# )

# Registrar blueprints con prefijos
app.register_blueprint(configuracion_bp)                                      # /api/configuracion/* ⭐ ACTIVO (Oct 22, 2025)
app.register_blueprint(notas_bp)                                              # /api/notas/* ⭐ API REST (Oct 21, 2025)
app.register_blueprint(archivo_digital_pages_bp)                              # /archivo_digital/* ⭐ PÁGINAS HTML (Oct 21, 2025)
# app.register_blueprint(usuarios_internos_bp)  # /api/usuarios_internos/*
app.register_blueprint(recibir_facturas_bp, url_prefix='/recibir_facturas')   # /recibir_facturas/*
app.register_blueprint(relaciones_bp, url_prefix='/relaciones')               # /relaciones/* ⭐ NUEVO (Oct 19, 2025)
app.register_blueprint(causaciones_bp, url_prefix='/causaciones')             # /causaciones/* ⭐ NUEVO (Oct 23, 2025)
app.register_blueprint(dian_vs_erp_bp, url_prefix='/dian_vs_erp')             # /dian_vs_erp/* ⭐ NUEVO (Nov 13, 2025)
app.register_blueprint(monitoreo_bp)                                           # /admin/monitoreo/* ⭐ NUEVO (Oct 23, 2025)

# Importar blueprint de Usuarios y Permisos
from modules.admin.usuarios_permisos import usuarios_permisos_bp
app.register_blueprint(usuarios_permisos_bp, url_prefix='/admin/usuarios-permisos')  # /admin/usuarios-permisos/* ⭐ NUEVO (Oct 24, 2025)

# Importar blueprint de API de Permisos (para dashboard)
from permisos_api import permisos_api_bp
app.register_blueprint(permisos_api_bp)  # /api/mis-permisos ⭐ NUEVO (Ene 2025)

# Importar blueprint de Facturas Digitales
from modules.facturas_digitales import facturas_digitales_bp
from modules.facturas_digitales.config_routes import config_facturas_bp
app.register_blueprint(facturas_digitales_bp)  # /facturas-digitales/* ⭐ NUEVO (Ene 2025)
app.register_blueprint(config_facturas_bp)  # /facturas-digitales/configuracion/* ⭐ NUEVO (Dic 2025)

# Importar blueprint de Gestión de Terceros
from modules.terceros import terceros_bp
app.register_blueprint(terceros_bp, url_prefix='/terceros')  # /terceros/* ⭐ SÚPER NUEVO (Nov 28, 2025)

# Importar blueprint de SAGRILAFT (Gestión de Radicados)
from modules.sagrilaft import sagrilaft_bp
app.register_blueprint(sagrilaft_bp)  # /sagrilaft/* ⭐ INTEGRADO (Ene 29, 2026)

log_security("✅ SERVIDOR INICIANDO - Módulos HABILITADOS: Recibir Facturas, Relaciones, Archivo Digital, Causaciones, DIAN vs ERP, Monitoreo, Facturas Digitales, SAGRILAFT")


# =============================================
# 🎨 CONTEXT PROCESSOR - Variables Globales
# =============================================
@app.context_processor
def inject_branding():
    """
    Inyecta variables de marca en todos los templates
    Uso: {{ LOGO_PATH }}, {{ EMPRESA_NOMBRE }}, etc.
    """
    return {
        'LOGO_PATH': LOGO_PATH,
        'LOGO_ALT_TEXT': LOGO_ALT_TEXT,
        'EMPRESA_NOMBRE': EMPRESA_NOMBRE,
        'EMPRESA_NIT': EMPRESA_NIT
    }


# -------------------------------------------------
# 🔧 RUTA TEMPORAL PARA ARREGLAR ASOCIACIÓN ADMIN
# -------------------------------------------------
@app.route("/fix-admin-nit-805028041", methods=["GET"])
def fix_admin_nit():
    """Ruta temporal para arreglar asociación NIT-Usuario admin"""
    from sqlalchemy import text
    try:
        # Buscar tercero con NIT 805028041
        tercero = Tercero.query.filter_by(nit='805028041').first()
        if not tercero:
            return f"❌ No existe tercero con NIT 805028041", 404
        
        # Buscar usuario admin
        user = Usuario.query.filter(db.func.lower(Usuario.usuario) == 'admin').first()
        if not user:
            return f"❌ No existe usuario admin", 404
        
        # Verificar asociación actual
        if user.tercero_id == tercero.id:
            return f"✅ El usuario admin YA está asociado correctamente al NIT 805028041", 200
        
        # Actualizar asociación
        user.tercero_id = tercero.id
        db.session.commit()
        
        return f"""
        <h2>✅ Asociación actualizada correctamente</h2>
        <p>Usuario: {user.usuario}</p>
        <p>Nuevo Tercero ID: {tercero.id}</p>
        <p>NIT: {tercero.nit}</p>
        <p>Razón Social: {tercero.razon_social}</p>
        <br>
        <p><strong>Ahora puedes iniciar sesión con:</strong></p>
        <ul>
            <li>NIT: 805028041</li>
            <li>Usuario: admin</li>
            <li>Contraseña: Admin12345$</li>
        </ul>
        <a href="/">Ir al login</a>
        """, 200
    except Exception as e:
        db.session.rollback()
        return f"❌ Error: {str(e)}", 500

# =============================================
# 🔄 MIDDLEWARE DE TRACKING DE SESIONES
# =============================================

@app.before_request
def actualizar_sesion_activa():
    """Actualiza o crea registro de sesión activa en cada request"""
    if 'usuario_id' in session and 'usuario' in session:
        try:
            from modules.admin.monitoreo.models import SesionActiva
            from datetime import datetime
            
            # Obtener datos de la sesión
            usuario_id = session['usuario_id']
            usuario_nombre = session['usuario']
            session_id = request.session.get('session_id', session.get('_id', 'unknown'))
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
            user_agent = request.headers.get('User-Agent', '')
            ruta_actual = request.path
            
            # Determinar módulo actual basado en la ruta
            modulo_actual = "Dashboard"
            if '/recibir_facturas' in ruta_actual:
                modulo_actual = "Recibir Facturas"
            elif '/relaciones' in ruta_actual:
                modulo_actual = "Relaciones"
            elif '/causaciones' in ruta_actual:
                modulo_actual = "Causaciones"
            elif '/monitoreo' in ruta_actual:
                modulo_actual = "Monitoreo"
            elif '/admin' in ruta_actual:
                modulo_actual = "Administración"
            elif '/configuracion' in ruta_actual:
                modulo_actual = "Configuración"
            
            # Buscar sesión existente
            sesion = SesionActiva.query.filter_by(
                usuario_id=usuario_id,
                ip_address=ip_address,
                activa=True
            ).first()
            
            if sesion:
                # Actualizar sesión existente
                sesion.fecha_ultima_actividad = datetime.utcnow()
                sesion.modulo_actual = modulo_actual
                sesion.ruta_actual = ruta_actual
                sesion.user_agent = user_agent
            else:
                # Crear nueva sesión
                sesion = SesionActiva(
                    usuario_id=usuario_id,
                    usuario_nombre=usuario_nombre,
                    session_id=session_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    modulo_actual=modulo_actual,
                    ruta_actual=ruta_actual,
                    activa=True,
                    fecha_inicio=datetime.utcnow(),
                    fecha_ultima_actividad=datetime.utcnow()
                )
                db.session.add(sesion)
            
            db.session.commit()
            
        except Exception as e:
            # Log error pero no interrumpir request
            print(f"Error actualizando sesión: {e}")
            db.session.rollback()

@app.after_request  
def limpiar_sesiones_inactivas(response):
    """Limpia sesiones inactivas después de cada request"""
    try:
        from modules.admin.monitoreo.models import SesionActiva
        from datetime import datetime, timedelta
        
        # Marcar como inactivas las sesiones sin actividad > 10 minutos
        tiempo_limite = datetime.utcnow() - timedelta(minutes=10)
        
        SesionActiva.query.filter(
            SesionActiva.fecha_ultima_actividad < tiempo_limite,
            SesionActiva.conectado == True
        ).update({
            'conectado': False,
            'fecha_desconexion': datetime.utcnow()
        })
        
        db.session.commit()
        
    except Exception as e:
        print(f"Error limpiando sesiones: {e}")
        db.session.rollback()
    
    return response

# -------------------------------------------------
# 🧭 MAIN
# -------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
        # Crear tabla tokens_password si no existe
        try:
            from sqlalchemy import text
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS tokens_password (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL UNIQUE REFERENCES usuarios(id) ON DELETE CASCADE,
                    token VARCHAR(255) NOT NULL UNIQUE,
                    expiracion TIMESTAMP NOT NULL,
                    usado BOOLEAN DEFAULT FALSE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_tokens_password_token ON tokens_password(token);
                CREATE INDEX IF NOT EXISTS idx_tokens_password_usuario ON tokens_password(usuario_id);
                CREATE INDEX IF NOT EXISTS idx_tokens_password_expiracion ON tokens_password(expiracion);
            """))
            db.session.commit()
            print("[OK] Tabla tokens_password verificada/creada")
        except Exception as e:
            print(f"[INFO] Tabla tokens_password: {str(e)}")
            db.session.rollback()
    
    print("[OK] Servidor Flask iniciado correctamente en http://127.0.0.1:8099")
    print("[DEBUG] Modo debug activado - Los cambios en archivos .py se recargarán automáticamente")
    
    # ====================================
    # INICIAR SCHEDULER DE ENVÍOS PROGRAMADOS - MÓDULO DIAN VS ERP
    # ====================================
    try:
        from modules.dian_vs_erp.scheduler_envios import iniciar_scheduler_dian_vs_erp, detener_scheduler_dian_vs_erp
        import atexit
        
        print("[INFO] Iniciando scheduler de envíos programados DIAN VS ERP...")
        iniciar_scheduler_dian_vs_erp(app)  # PASAR LA INSTANCIA DE APP
        print("[OK] ✅ Scheduler DIAN VS ERP iniciado correctamente")
        
        # Registrar detención al cerrar
        atexit.register(detener_scheduler_dian_vs_erp)
        
    except ImportError as e:
        print(f"[ADVERTENCIA] Módulo scheduler no encontrado: {e}")
        print("[INFO] Instalar con: pip install apscheduler")
    except Exception as e:
        print(f"[ADVERTENCIA] No se pudo iniciar scheduler DIAN VS ERP: {e}")
        print("[INFO] El sistema funcionará sin envíos automáticos programados")
    
    app.run(host="0.0.0.0", port=8099, debug=True, use_reloader=False)
