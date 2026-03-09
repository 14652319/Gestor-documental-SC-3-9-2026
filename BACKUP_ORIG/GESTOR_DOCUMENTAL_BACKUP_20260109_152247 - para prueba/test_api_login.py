#!/usr/bin/env python3
"""
Test directo del API de terceros con autenticación
"""

import requests
import json

def test_api_autenticado():
    """Prueba el API con login real"""
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    print("🔐 Haciendo login...")
    
    # Login con credenciales reales
    login_url = "http://localhost:8099/api/auth/login"
    login_data = {
        "nit": "805028041",
        "usuario": "admin",
        "contraseña": "123456"
    }
    
    try:
        login_response = session.post(login_url, json=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login exitoso")
            
            # Probar API de terceros
            print("\n📋 Probando API de terceros...")
            
            api_url = "http://localhost:8099/terceros/api/listar"
            params = {
                'page': 1,
                'per_page': 5,
                'search': '',
                'estado': '',
                'orden': 'fecha_desc'
            }
            
            api_response = session.get(api_url, params=params)
            print(f"API Status: {api_response.status_code}")
            
            if api_response.status_code == 200:
                data = api_response.json()
                print(f"✅ API Response: success = {data.get('success')}")
                
                if data.get('success'):
                    api_data = data.get('data', {})
                    terceros = api_data.get('terceros', [])
                    stats = api_data.get('stats', {})
                    
                    print(f"📊 Total terceros: {stats.get('total_terceros', 'N/A')}")
                    print(f"📄 Terceros en respuesta: {len(terceros)}")
                    
                    if terceros:
                        print("\n👥 Primeros terceros:")
                        for i, tercero in enumerate(terceros[:3]):
                            print(f"  {i+1}. {tercero.get('nit')} - {tercero.get('razon_social')}")
                    
                    return True
                else:
                    print(f"❌ API Error: {data.get('message')}")
            else:
                print(f"❌ HTTP Error: {api_response.status_code}")
                print(f"Response: {api_response.text[:200]}")
                
        else:
            print(f"❌ Login falló: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")
        
    return False

if __name__ == "__main__":
    print("🧪 PROBANDO API DE TERCEROS CON AUTENTICACIÓN")
    print("=" * 60)
    
    if test_api_autenticado():
        print("\n🎉 ¡API funcionando correctamente!")
        print("✅ El problema debe ser en el frontend")
    else:
        print("\n❌ Problemas en el API")
        print("🔍 Revisar logs del servidor")