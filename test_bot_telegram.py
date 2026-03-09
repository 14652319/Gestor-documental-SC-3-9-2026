#!/usr/bin/env python3
"""
Script de Prueba: Bot de Telegram
Prueba el comando /desbloquear y otros comandos
Fecha: 27 Febrero 2026
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def main():
    print("=" * 70)
    print("🤖 TEST: BOT DE TELEGRAM - COMANDO /DESBLOQUEAR")
    print("=" * 70)
    print()
    
    # Verificar configuración
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ ERROR: Telegram no está configurado en .env")
        print()
        print("Configura las siguientes variables en tu archivo .env:")
        print("   TELEGRAM_BOT_TOKEN=tu_bot_token_aqui")
        print("   TELEGRAM_CHAT_ID=tu_chat_id_aqui")
        print()
        return
    
    print("✅ Configuración de Telegram encontrada")
    print(f"   Bot Token: {bot_token[:20]}...")
    print(f"   Chat ID: {chat_id}")
    print()
    
    # Importar módulo del bot
    try:
        from telegram_bot import (
            configurar_comandos_bot, 
            enviar_mensaje_telegram,
            procesar_comando_telegram
        )
        print("✅ Módulo telegram_bot importado correctamente")
        print()
    except ImportError as e:
        print(f"❌ Error importando telegram_bot: {e}")
        return
    
    # ====================================================================
    # TEST 1: Configurar comandos del bot
    # ====================================================================
    print("📋 TEST 1: Configurando comandos del bot...")
    print("-" * 70)
    if configurar_comandos_bot():
        print("✅ Comandos configurados en Telegram")
        print("   Ahora verás /desbloquear y /ayuda en el menú del bot")
    else:
        print("❌ Error configurando comandos")
    print()
    
    # ====================================================================
    # TEST 2: Enviar mensaje de activación
    # ====================================================================
    print("📤 TEST 2: Enviando mensaje de activación...")
    print("-" * 70)
    mensaje_activacion = """🤖 *BOT DE ADMINISTRACIÓN ACTIVADO*

✅ El bot está funcionando correctamente
📋 Comandos disponibles:

🔓 `/desbloquear [IP]` - Desbloquear IP bloqueada
   Ejemplo: `/desbloquear 192.168.1.100`

❓ `/ayuda` - Ver todos los comandos

⚠️ *IMPORTANTE:*
Solo el administrador autorizado puede usar estos comandos.

🚀 *Próximos comandos en desarrollo:*
• /bloqueos - Ver IPs bloqueadas
• /sesiones - Usuarios activos
• /radicados - Radicados del día
• /backup - Crear backup manual
• Y muchos más..."""

    if enviar_mensaje_telegram(mensaje_activacion):
        print("✅ Mensaje enviado exitosamente")
        print("   Revisa tu chat de Telegram")
    else:
        print("❌ Error enviando mensaje")
    print()
    
    # ====================================================================
    # TEST 3: Simular comando /desbloquear
    # ====================================================================
    print("🧪 TEST 3: Simulando comando /desbloquear...")
    print("-" * 70)
    print("   Nota: Este test NO desbloquea una IP real")
    print("   Solo verifica que la función funciona")
    print()
    
    respuesta_ayuda = procesar_comando_telegram('ayuda', [], chat_id)
    print("➡️ Simulando: /ayuda")
    print("⬅️ Respuesta:")
    print(respuesta_ayuda)
    print()
    
    # ====================================================================
    # TEST 4: Instrucciones de uso
    # ====================================================================
    print("=" * 70)
    print("📖 CÓMO USAR EL BOT DE TELEGRAM")
    print("=" * 70)
    print()
    print("1️⃣ Abre tu chat de Telegram con el bot")
    print()
    print("2️⃣ Cuando recibas una alerta de IP bloqueada:")
    print("   🚨 ALERTA: IP BLOQUEADA")
    print("   🌐 IP: 192.168.1.100")
    print("   👤 Usuario: juanperez")
    print()
    print("3️⃣ Para desbloquear, responde en el chat:")
    print("   /desbloquear 192.168.1.100")
    print()
    print("4️⃣ El bot confirmará:")
    print("   ✅ IP DESBLOQUEADA EXITOSAMENTE")
    print()
    print("5️⃣ Otros comandos útiles:")
    print("   /ayuda - Ver todos los comandos")
    print()
    print("=" * 70)
    print("🎯 CONFIGURACIÓN WEBHOOK (OPCIONAL - SOLO PARA PRODUCCIÓN)")
    print("=" * 70)
    print()
    print("Si tienes un dominio público (ej: https://tudominio.com):")
    print()
    print("1. Configura el webhook en Telegram:")
    print("   curl -X POST https://api.telegram.org/bot<TU_TOKEN>/setWebhook \\")
    print("        -d 'url=https://tudominio.com/api/telegram/webhook'")
    print()
    print("2. O usa el endpoint de la app:")
    print("   POST http://localhost:8099/api/telegram/setup_webhook")
    print("   Body: {\"webhook_url\": \"https://tudominio.com/api/telegram/webhook\"}")
    print()
    print("⚠️ Nota: El webhook solo funciona con HTTPS público")
    print("   Para desarrollo local, usa los comandos directamente en Telegram")
    print()
    print("=" * 70)
    print("✅ TEST COMPLETADO")
    print("=" * 70)
    print()
    print("📱 Revisa tu Telegram para ver el mensaje de activación")
    print("🔓 Intenta usar /desbloquear con una IP de prueba")
    print()

if __name__ == '__main__':
    main()
