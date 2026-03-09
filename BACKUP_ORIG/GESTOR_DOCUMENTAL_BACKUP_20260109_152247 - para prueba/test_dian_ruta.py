#!/usr/bin/env python3
"""
Test simple para verificar que la ruta /dian_vs_erp/ funciona
"""

import requests
import time

def test_dian_route():
    """Probar que la ruta del módulo DIAN vs ERP funciona"""
    try:
        # Esperar un momento para que el servidor esté listo
        print("⏳ Esperando servidor...")
        time.sleep(2)
        
        url = "http://localhost:8099/dian_vs_erp/"
        print(f"🔍 Probando: {url}")
        
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📏 Content Length: {len(response.text)}")
        
        if response.status_code == 200:
            print("✅ Respuesta exitosa")
            if "Dashboard Control de Facturas" in response.text:
                print("✅ Template DIAN vs ERP cargado correctamente")
            else:
                print("⚠️ Template parece diferente al esperado")
        elif response.status_code == 302:
            print(f"↪️ Redirect a: {response.headers.get('Location', 'Desconocido')}")
        elif response.status_code == 404:
            print("❌ Ruta no encontrada")
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
        print("🔧 Verifica que el servidor esté ejecutándose en puerto 8099")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_dian_route()