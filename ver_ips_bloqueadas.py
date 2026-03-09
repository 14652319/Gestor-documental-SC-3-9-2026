#!/usr/bin/env python3
"""
Ver IPs Bloqueadas Actualmente
Muestra listado de todas las IPs bloqueadas en el sistema
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
from app import app, IPListaNegra, IPSospechosa

def ver_ips_bloqueadas():
    """Muestra todas las IPs bloqueadas actualmente"""
    print()
    print("=" * 70)
    print("🚫 IPS BLOQUEADAS - ESTADO ACTUAL")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    with app.app_context():
        # Consultar IPs en lista negra
        ips_negras = IPListaNegra.query.all()
        
        # Consultar IPs sospechosas bloqueadas
        ips_sospechosas_bloq = IPSospechosa.query.filter_by(bloqueada=True).all()
        
        # Combinar y deduplicate
        ips_dict = {}
        
        # Agregar IPs de lista negra
        for ip in ips_negras:
            motivo = ip.motivo if hasattr(ip, 'motivo') else 'No especificado'
            fecha = ip.fecha if hasattr(ip, 'fecha') else 'N/A'
            ips_dict[ip.ip] = {
                'motivo': motivo,
                'fecha': fecha,
                'tipo': 'Lista Negra'
            }
        
        # Agregar IPs sospechosas bloqueadas (no duplicar)
        for ip in ips_sospechosas_bloq:
            if ip.ip not in ips_dict:
                motivo = ip.motivo_bloqueo if hasattr(ip, 'motivo_bloqueo') else 'Intentos fallidos'
                intentos = ip.intentos if hasattr(ip, 'intentos') else 0
                fecha = ip.ultima_actividad if hasattr(ip, 'ultima_actividad') else 'N/A'
                ips_dict[ip.ip] = {
                    'motivo': f"{motivo} ({intentos} intentos)",
                    'fecha': fecha,
                    'tipo': 'IP Sospechosa'
                }
        
        # Mostrar resultados
        if not ips_dict:
            print("✅ NO HAY IPS BLOQUEADAS ACTUALMENTE")
            print()
            print("El sistema está limpio. Todas las IPs tienen acceso.")
            print()
        else:
            print(f"📊 TOTAL: {len(ips_dict)} IP(s) bloqueada(s)")
            print()
            print("-" * 70)
            print(f"{'#':<4} {'IP':<18} {'Motivo':<30} {'Tipo':<15}")
            print("-" * 70)
            
            for idx, (ip, info) in enumerate(sorted(ips_dict.items()), 1):
                motivo_corto = info['motivo'][:28] + '..' if len(info['motivo']) > 30 else info['motivo']
                print(f"{idx:<4} {ip:<18} {motivo_corto:<30} {info['tipo']:<15}")
            
            print("-" * 70)
            print()
            
            # Mostrar detalles completos
            print("📋 DETALLES COMPLETOS:")
            print()
            
            for idx, (ip, info) in enumerate(sorted(ips_dict.items()), 1):
                print(f"{idx}. IP: {ip}")
                print(f"   Motivo: {info['motivo']}")
                print(f"   Tipo: {info['tipo']}")
                
                fecha_str = 'N/A'
                if info['fecha'] != 'N/A':
                    try:
                        if hasattr(info['fecha'], 'strftime'):
                            fecha_str = info['fecha'].strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            fecha_str = str(info['fecha'])
                    except:
                        fecha_str = 'N/A'
                
                print(f"   Fecha: {fecha_str}")
                print()
            
            # Sugerencia de desbloqueo
            print("=" * 70)
            print("💡 PARA DESBLOQUEAR:")
            print("=" * 70)
            print()
            print("Opción 1: Desde Telegram")
            print("   /desbloquear [IP]")
            print(f"   Ejemplo: /desbloquear {list(ips_dict.keys())[0]}")
            print()
            print("Opción 2: Desde consola")
            print("   python desbloquear_ip_telegram.py [IP]")
            print(f"   Ejemplo: python desbloquear_ip_telegram.py {list(ips_dict.keys())[0]}")
            print()
            print("Opción 3: Directo a base de datos")
            print("   python desbloquear_ip_directo.py")
            print()
        
        print("=" * 70)
        print()

def main():
    try:
        ver_ips_bloqueadas()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()

if __name__ == '__main__':
    main()
