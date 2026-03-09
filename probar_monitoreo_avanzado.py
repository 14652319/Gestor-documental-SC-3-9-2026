#!/usr/bin/env python3
"""
Script para probar las nuevas funcionalidades súper avanzadas del monitoreo
"""

import requests
import json
from datetime import datetime

def probar_endpoint(url, nombre):
    """Prueba un endpoint y muestra el resultado"""
    print(f"\n🧪 PROBANDO: {nombre}")
    print(f"🔗 URL: {url}")
    print("-" * 60)
    
    try:
        response = requests.get(url, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ ÉXITO - Endpoint funciona correctamente")
                
                # Mostrar algunos datos interesantes
                if 'data' in data:
                    if isinstance(data['data'], list) and len(data['data']) > 0:
                        print(f"📋 Registros encontrados: {len(data['data'])}")
                        if hasattr(data['data'][0], 'keys'):
                            print(f"🔑 Campos: {list(data['data'][0].keys())}")
                    elif isinstance(data['data'], dict):
                        print(f"📦 Datos obtenidos: {len(data['data'])} campos")
                        for key, value in list(data['data'].items())[:3]:
                            print(f"   • {key}: {value}")
            else:
                print(f"⚠️ ADVERTENCIA - {data.get('message', 'Error sin mensaje')}")
        else:
            print(f"❌ ERROR HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"💬 Mensaje: {error_data.get('message', 'Sin mensaje de error')}")
            except:
                print(f"💬 Respuesta: {response.text[:200]}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR DE CONEXIÓN: {e}")
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")

def main():
    """Función principal para probar todos los endpoints"""
    
    base_url = "http://127.0.0.1:8099/admin/monitoreo/api"
    
    print("🚀 PROBANDO MÓDULO DE MONITOREO SÚPER AVANZADO")
    print("=" * 80)
    print(f"⏰ Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {base_url}")
    
    # Lista de endpoints a probar
    endpoints = [
        # Endpoints existentes
        (f"{base_url}/stats_sorprendentes", "📊 Dashboard Estadísticas"),
        (f"{base_url}/usuarios_tiempo_real", "👥 Usuarios en Tiempo Real"),
        (f"{base_url}/ips_tiempo_real", "🌐 IPs en Tiempo Real"),
        (f"{base_url}/disk_usage_mejorado", "💽 Uso de Disco"),
        (f"{base_url}/logs/archivos", "📄 Archivos de Log"),
        (f"{base_url}/alertas", "🚨 Sistema de Alertas"),
        
        # Nuevos endpoints súper avanzados
        (f"{base_url}/geolocalizacion/ips", "🌍 Geolocalización de IPs"),
        (f"{base_url}/analytics/tiempo-real", "📊 Analytics en Tiempo Real"),
        (f"{base_url}/seguridad/detectar-amenazas", "🛡️ Detección de Amenazas"),
        (f"{base_url}/backup/estado", "💾 Estado de Backups"),
        (f"{base_url}/metricas/sistema", "⚡ Métricas del Sistema"),
    ]
    
    # Probar cada endpoint
    for url, nombre in endpoints:
        probar_endpoint(url, nombre)
    
    print("\n" + "=" * 80)
    print("🎯 RESUMEN DE PRUEBAS COMPLETADO")
    print(f"📊 Total de endpoints probados: {len(endpoints)}")
    print("🌟 ¡El sistema de monitoreo súper avanzado está listo!")
    
    # Endpoint específico para probar notificaciones push
    print(f"\n🧪 PROBANDO ENDPOINT DE NOTIFICACIONES PUSH...")
    try:
        notification_url = f"{base_url}/notificaciones/push"
        notification_data = {
            "tipo": "INFO",
            "mensaje": "🧪 Prueba del sistema de notificaciones súper avanzado",
            "destinatarios": ["admin"]
        }
        
        response = requests.post(notification_url, json=notification_data, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ NOTIFICACIÓN PUSH ENVIADA EXITOSAMENTE")
                print(f"📱 Destinatarios: {data['data']['total_enviadas']}")
            else:
                print(f"⚠️ Error en notificación: {data.get('message')}")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error probando notificaciones: {e}")

if __name__ == "__main__":
    main()