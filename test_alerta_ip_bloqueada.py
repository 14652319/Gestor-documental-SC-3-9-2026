#!/usr/bin/env python3
"""
Script de Prueba: Alerta de IP Bloqueada con Listado
Simula el bloqueo de una IP y muestra cómo se verá el mensaje en Telegram
Fecha: 27 Febrero 2026
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from app import app, enviar_alerta_seguridad_telegram, IPListaNegra, IPSospechosa, log_security

def simular_bloqueo_ip():
    """Simula el bloqueo de una IP y envía alerta con listado completo"""
    print("=" * 70)
    print("🧪 PRUEBA: ALERTA DE IP BLOQUEADA CON LISTADO")
    print("=" * 70)
    print()
    
    # Verificar configuración de Telegram
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ ERROR: Telegram no configurado en .env")
        print()
        print("Este test requiere TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID")
        return
    
    print("✅ Configuración de Telegram encontrada")
    print(f"   Bot Token: {bot_token[:20]}...")
    print(f"   Chat ID: {chat_id}")
    print()
    
    with app.app_context():
        # Consultar IPs bloqueadas actuales
        print("📊 Consultando IPs bloqueadas actuales...")
        print("-" * 70)
        
        ips_negras = IPListaNegra.query.all()
        ips_sospechosas_bloq = IPSospechosa.query.filter_by(bloqueada=True).all()
        
        print(f"   IPs en lista negra: {len(ips_negras)}")
        if ips_negras:
            for ip in ips_negras[:5]:
                motivo = ip.motivo if hasattr(ip, 'motivo') else 'N/A'
                print(f"      - {ip.ip} ({motivo})")
        
        print(f"   IPs sospechosas bloqueadas: {len(ips_sospechosas_bloq)}")
        if ips_sospechosas_bloq:
            for ip in ips_sospechosas_bloq[:5]:
                intentos = ip.intentos if hasattr(ip, 'intentos') else 0
                print(f"      - {ip.ip} ({intentos} intentos)")
        
        print()
        print("📤 Enviando alerta de prueba a Telegram...")
        print("-" * 70)
        
        # Datos de prueba para la alerta
        detalles_prueba = {
            'ip': '192.168.1.100',
            'usuario': 'usuario_prueba',
            'nit': '900123456',
            'intentos': 5,
            'motivo': 'Exceso de intentos fallidos de login (PRUEBA)',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'
        }
        
        # Enviar alerta
        if enviar_alerta_seguridad_telegram('IP_BLOQUEADA', detalles_prueba):
            print("✅ Alerta enviada exitosamente a Telegram")
            print()
            print("📱 Revisa tu chat de Telegram")
            print("   Deberías ver:")
            print("   1. Detalles de la IP bloqueada (prueba)")
            print("   2. Listado de TODAS las IPs bloqueadas actualmente")
            print("   3. Sugerencia de comando /desbloquear")
        else:
            print("❌ Error enviando alerta")
            print("   Verifica logs en logs/security.log")
        
        print()
        print("=" * 70)
        print("💡 PREVIEW DEL MENSAJE")
        print("=" * 70)
        print()
        print("🚫 ALERTA DE SEGURIDAD")
        print()
        print("Tipo: IP BLOQUEADA")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print(f"IP: 192.168.1.100")
        print(f"Usuario: usuario_prueba")
        print(f"NIT: 900123456")
        print(f"Intentos fallidos: 5")
        print(f"Motivo: Exceso de intentos fallidos de login (PRUEBA)")
        print()
        
        if ips_negras or ips_sospechosas_bloq:
            total_bloqueadas = len(set([ip.ip for ip in ips_negras] + [ip.ip for ip in ips_sospechosas_bloq]))
            print("🚫 TODAS LAS IPS BLOQUEADAS ACTUALMENTE:")
            print(f"Total: {total_bloqueadas} IP(s)")
            print()
            
            count = 0
            for ip in ips_negras[:10]:
                count += 1
                motivo = ip.motivo if hasattr(ip, 'motivo') else 'No especificado'
                print(f"{count}. {ip.ip} - {motivo[:30]}")
            
            for ip in ips_sospechosas_bloq[:10-count]:
                count += 1
                motivo = ip.motivo_bloqueo if hasattr(ip, 'motivo_bloqueo') else 'Intentos fallidos'
                print(f"{count}. {ip.ip} - {motivo[:30]}")
            
            if total_bloqueadas > 10:
                print(f"\n... y {total_bloqueadas - 10} IP(s) más")
            
            print()
            print("💡 Para desbloquear: /desbloquear [IP]")
        else:
            print("✅ Esta es la única IP bloqueada actualmente")
        
        print()
        print("---")
        print("📊 Sistema de Gestión Documental")
        print()
        
    print("=" * 70)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 70)
    print()
    print("Próximos pasos:")
    print("1. Revisa tu Telegram para ver el mensaje real")
    print("2. El listado incluye todas las IPs bloqueadas")
    print("3. Usa /desbloquear para desbloquear cualquier IP")
    print()

if __name__ == '__main__':
    simular_bloqueo_ip()
