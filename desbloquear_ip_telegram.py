#!/usr/bin/env python3
"""
Desbloqueo Rápido de IP via Telegram
Envía comando /desbloquear directamente al bot
Fecha: 27 Febrero 2026
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def desbloquear_ip_telegram(ip):
    """Envía comando /desbloquear al bot de Telegram"""
    print("=" * 70)
    print(f"🔓 DESBLOQUEANDO IP VIA TELEGRAM: {ip}")
    print("=" * 70)
    print()
    
    # Verificar configuración
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ ERROR: Telegram no configurado en .env")
        print()
        print("Usa el script alternativo:")
        print("   python desbloquear_ip_directo.py")
        print()
        return False
    
    try:
        # Importar módulo del bot
        from telegram_bot import procesar_comando_telegram, enviar_mensaje_telegram
        
        # Procesar comando
        print(f"📤 Enviando comando: /desbloquear {ip}")
        respuesta = procesar_comando_telegram('desbloquear', [ip], chat_id)
        
        # Mostrar respuesta
        print()
        print("📱 Respuesta del Bot:")
        print("-" * 70)
        print(respuesta)
        print("-" * 70)
        print()
        
        # Enviar también via Telegram
        print("📨 Enviando notificación a Telegram...")
        if enviar_mensaje_telegram(respuesta, chat_id):
            print("✅ Notificación enviada a tu chat de Telegram")
        else:
            print("⚠️  Comando ejecutado pero notificación no enviada")
        
        print()
        print("✅ PROCESO COMPLETADO")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()
        print("Usa el script alternativo:")
        print("   python desbloquear_ip_directo.py")
        return False

def main():
    print()
    
    if len(sys.argv) > 1:
        # IP pasada como argumento
        ip = sys.argv[1]
        desbloquear_ip_telegram(ip)
    else:
        # Modo interactivo
        print("🔓 DESBLOQUEO RÁPIDO DE IP VIA TELEGRAM")
        print("=" * 70)
        print()
        ip = input("Ingresa la IP a desbloquear: ").strip()
        
        if not ip:
            print("❌ IP no válida")
            return
        
        print()
        desbloquear_ip_telegram(ip)

if __name__ == '__main__':
    main()
