#!/usr/bin/env python3
"""
Bot de Telegram - Comandos de Administración
Implementación mínima: Comando /desbloquear
Fecha: 27 Febrero 2026
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# ============================================================================
# FUNCIONES DE TELEGRAM
# ============================================================================

def enviar_mensaje_telegram(mensaje, chat_id=None):
    """Envía un mensaje de texto por Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram no configurado")
        return False
    
    if chat_id is None:
        chat_id = TELEGRAM_CHAT_ID
    
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': mensaje,
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")
        return False


def procesar_comando_telegram(comando, parametros, chat_id):
    """
    Procesa comandos recibidos del bot de Telegram
    
    Args:
        comando (str): Comando recibido (sin el /)
        parametros (list): Lista de parámetros del comando
        chat_id (str): ID del chat que envió el comando
    
    Returns:
        str: Mensaje de respuesta
    """
    from extensions import db
    from app import app
    
    # Solo procesar si es del chat autorizado
    if str(chat_id) != str(TELEGRAM_CHAT_ID):
        return "❌ No autorizado"
    
    with app.app_context():
        # ========================================
        # COMANDO: /desbloquear [IP]
        # ========================================
        if comando == 'desbloquear':
            if not parametros or len(parametros) == 0:
                return "❌ Uso: /desbloquear [IP]\nEjemplo: /desbloquear 192.168.1.100"
            
            ip = parametros[0]
            
            try:
                from sqlalchemy import text
                
                # 1. Eliminar de lista negra
                query_negras = text("DELETE FROM ips_negras WHERE ip = :ip")
                result_negras = db.session.execute(query_negras, {'ip': ip})
                
                # 2. Eliminar de IPs sospechosas
                query_sospechosas = text("DELETE FROM ips_sospechosas WHERE ip = :ip")
                result_sospechosas = db.session.execute(query_sospechosas, {'ip': ip})
                
                # 3. Agregar a lista blanca
                query_check_blanca = text("SELECT COUNT(*) FROM ips_blancas WHERE ip = :ip")
                existe_blanca = db.session.execute(query_check_blanca, {'ip': ip}).scalar()
                
                if existe_blanca == 0:
                    query_insert_blanca = text("""
                        INSERT INTO ips_blancas (ip, descripcion, usuario_agrego, activa, fecha) 
                        VALUES (:ip, :desc, :usuario, true, :fecha)
                    """)
                    db.session.execute(query_insert_blanca, {
                        'ip': ip,
                        'desc': f'Desbloqueada via Telegram - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                        'usuario': 'telegram_bot',
                        'fecha': datetime.now()
                    })
                
                db.session.commit()
                
                # Log de seguridad
                from app import log_security
                log_security(f"IP DESBLOQUEADA VIA TELEGRAM | ip={ip} | chat_id={chat_id}")
                
                mensaje = f"""✅ *IP DESBLOQUEADA EXITOSAMENTE*

🌐 *IP:* `{ip}`
📅 *Fecha:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔓 *Acciones realizadas:*
✅ Eliminada de lista negra ({result_negras.rowcount} registros)
✅ Eliminada de IPs sospechosas ({result_sospechosas.rowcount} registros)
✅ Agregada a lista blanca

🎯 La IP ahora tiene acceso completo al sistema"""
                
                return mensaje
                
            except Exception as e:
                db.session.rollback()
                from app import log_security
                log_security(f"ERROR DESBLOQUEO TELEGRAM | ip={ip} | error={str(e)}")
                return f"❌ Error al desbloquear IP:\n`{str(e)}`"
        
        # ========================================
        # COMANDO: /ayuda
        # ========================================
        elif comando == 'ayuda' or comando == 'help':
            return """🤖 *BOT DE ADMINISTRACIÓN*
_Gestor Documental v2.0_

📋 *Comandos disponibles:*

🔓 `/desbloquear [IP]`
   Desbloquea una IP previamente bloqueada
   Ejemplo: `/desbloquear 192.168.1.100`

❓ `/ayuda`
   Muestra este mensaje

⚠️ *Nota:* Más comandos en desarrollo"""
        
        # ========================================
        # COMANDO DESCONOCIDO
        # ========================================
        else:
            return f"❌ Comando desconocido: `/{comando}`\n\nUsa /ayuda para ver comandos disponibles"


def enviar_respuesta_telegram(mensaje, chat_id=None):
    """Alias de enviar_mensaje_telegram para compatibilidad"""
    return enviar_mensaje_telegram(mensaje, chat_id)


# ============================================================================
# WEBHOOK HANDLER (para app.py)
# ============================================================================

def procesar_update_telegram(update_data):
    """
    Procesa un update recibido del webhook de Telegram
    
    Args:
        update_data (dict): Datos del update de Telegram
    
    Returns:
        bool: True si se procesó correctamente
    """
    try:
        # Extraer información del mensaje
        message = update_data.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        
        if not text.startswith('/'):
            return False
        
        # Parsear comando y parámetros
        partes = text.split()
        comando = partes[0][1:]  # Remover el /
        parametros = partes[1:] if len(partes) > 1 else []
        
        # Procesar comando
        respuesta = procesar_comando_telegram(comando, parametros, chat_id)
        
        # Enviar respuesta
        enviar_respuesta_telegram(respuesta, chat_id)
        
        return True
        
    except Exception as e:
        print(f"❌ Error procesando update de Telegram: {e}")
        return False


# ============================================================================
# CONFIGURACIÓN DEL BOT (opcional)
# ============================================================================

def configurar_comandos_bot():
    """Configura la lista de comandos del bot en Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ Telegram no configurado")
        return False
    
    try:
        url = f"{TELEGRAM_API_URL}/setMyCommands"
        comandos = [
            {
                "command": "desbloquear",
                "description": "Desbloquear una IP (uso: /desbloquear [IP])"
            },
            {
                "command": "ayuda",
                "description": "Mostrar ayuda y comandos disponibles"
            }
        ]
        
        data = {'commands': comandos}
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Comandos del bot configurados")
            return True
        else:
            print(f"⚠️ Error configurando comandos: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error configurando comandos: {e}")
        return False


# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    print("🤖 Bot de Telegram - Test")
    print("=" * 50)
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Configura TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en .env")
    else:
        print(f"✅ Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...")
        print(f"✅ Chat ID: {TELEGRAM_CHAT_ID}")
        
        # Configurar comandos
        print("\n📋 Configurando comandos del bot...")
        configurar_comandos_bot()
        
        # Enviar mensaje de prueba
        print("\n📤 Enviando mensaje de prueba...")
        mensaje_test = """🤖 *Bot de Administración Activado*

✅ El bot está funcionando correctamente
📋 Usa /ayuda para ver comandos disponibles"""
        
        if enviar_mensaje_telegram(mensaje_test):
            print("✅ Mensaje enviado exitosamente")
        else:
            print("❌ Error enviando mensaje")
