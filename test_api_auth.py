#!/usr/bin/env python3
"""
Test del API de terceros con autenticación real
"""

import requests
import json

def test_con_sesion():
    """Prueba el API con una sesión real como el navegador"""
    print("🔐 Probando API de terceros con autenticación...")
    
    # Crear sesión
    session = requests.Session()
    
    try:
        # 1. Login
        login_url = "http://localhost:8099/api/auth/login"
        login_data = {
            "nit": "805028041",  # NIT admin
            "usuario": "admin",   # Usuario admin  
            "contraseña": "123456"  # Contraseña admin
        }
        
        print(f"🔑 Haciendo login en: {login_url}")
        login_response = session.post(login_url, json=login_data)
        print(f"   Status login: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"   ✅ Login exitoso: {login_result.get('message', 'OK')}")
            
            # 2. Probar API de terceros
            api_url = "http://localhost:8099/terceros/api/listar?page=1&per_page=5"
            print(f"📡 Probando API: {api_url}")
            
            api_response = session.get(api_url)
            print(f"   Status API: {api_response.status_code}")
            
            if api_response.status_code == 200:
                data = api_response.json()
                print(f"   ✅ API respondió correctamente")
                
                # Verificar estructura
                print(f"   success: {data.get('success')}")
                
                if 'data' in data:
                    data_content = data['data']
                    print(f"   'data' key existe: ✅")
                    
                    if 'terceros' in data_content:
                        terceros = data_content['terceros']
                        print(f"   terceros count: {len(terceros)}")
                        
                        if terceros:
                            print(f"   primer tercero: {terceros[0].get('nit')} - {terceros[0].get('razon_social')}")
                    
                    if 'stats' in data_content:
                        stats = data_content['stats']
                        print(f"   stats total_terceros: {stats.get('total_terceros')}")
                else:
                    print("   ❌ No hay 'data' en la respuesta")
                    print(f"   Estructura: {list(data.keys())}")
                    
            elif api_response.status_code == 401:
                print("   ❌ API requiere autenticación - sesión no válida")
            else:
                print(f"   ❌ Error API: {api_response.status_code}")
                print(f"   Respuesta: {api_response.text[:200]}")
        else:
            print(f"   ❌ Error login: {login_response.status_code}")
            print(f"   Respuesta: {login_response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

def test_estructura_respuesta():
    """Prueba solo la estructura del API sin autenticación"""
    print("\n📋 Probando estructura del API...")
    
    try:
        url = "http://localhost:8099/terceros/api/listar?page=1&per_page=5"
        response = requests.get(url)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            data = response.json()
            print("✅ El API está funcionando (requiere auth como esperado)")
            print(f"   Mensaje: {data.get('message', data.get('error'))}")
        else:
            print(f"Response: {response.text[:100]}...")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    print("🚀 TEST COMPLETO DEL API DE TERCEROS")
    print("=" * 50)
    
    test_estructura_respuesta()
    test_con_sesion()
    
    print("\n🎯 Test completado")