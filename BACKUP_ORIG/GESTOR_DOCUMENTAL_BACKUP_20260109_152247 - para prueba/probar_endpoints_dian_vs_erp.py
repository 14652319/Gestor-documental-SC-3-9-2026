#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que los endpoints del módulo DIAN vs ERP funcionan correctamente
"""

import requests
import json

# URL base del servidor
BASE_URL = "http://127.0.0.1:8099"

def probar_endpoint(endpoint, metodo="GET", datos=None):
    """Prueba un endpoint específico"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 Probando: {metodo} {endpoint}")
    
    try:
        if metodo == "GET":
            response = requests.get(url, timeout=5)
        elif metodo == "POST":
            response = requests.post(url, json=datos, timeout=5)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ EXITOSO")
            # Si es JSON, mostrar la estructura
            if 'application/json' in response.headers.get('Content-Type', ''):
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   📊 Retorna lista con {len(data)} elementos")
                    elif isinstance(data, dict):
                        print(f"   📊 Retorna diccionario con claves: {list(data.keys())[:5]}")
                except:
                    pass
        else:
            print(f"   ❌ ERROR: {response.status_code}")
            print(f"   Mensaje: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ ERROR DE CONEXIÓN: {e}")

def main():
    print("🚀 PRUEBAS DE ENDPOINTS - MÓDULO DIAN vs ERP")
    print("=" * 50)
    
    # 1. Probar el dashboard principal
    probar_endpoint("/dian_vs_erp")
    
    # 2. Probar la página de configuración (nuevo endpoint sin conflictos)
    probar_endpoint("/dian_vs_erp/config")
    
    # 3. Probar API de datos
    probar_endpoint("/dian_vs_erp/api/dian")
    
    # 4. Probar API de usuarios por NIT (nuevo endpoint sin conflictos)
    probar_endpoint("/dian_vs_erp/api/dian_usuarios/por_nit/805028041")
    
    # 5. Probar API de envío de emails individual
    datos_email = {
        "cufe": "test-cufe-123",
        "destinatarios": [
            {"correo": "test@example.com", "nombre": "Usuario Test"}
        ]
    }
    probar_endpoint("/dian_vs_erp/api/enviar_emails", "POST", datos_email)
    
    # 6. Probar API de envío de emails agrupado
    datos_email_agrupado = {
        "destinatarios": [
            {"correo": "test@example.com", "nombre": "Usuario Test"}
        ],
        "cufes": ["test-cufe-1", "test-cufe-2", "test-cufe-3"]
    }
    probar_endpoint("/dian_vs_erp/api/enviar_email_agrupado", "POST", datos_email_agrupado)
    
    print(f"\n🎉 PRUEBAS COMPLETADAS")
    print("=" * 50)

if __name__ == "__main__":
    main()