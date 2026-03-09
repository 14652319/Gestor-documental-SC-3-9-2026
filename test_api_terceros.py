#!/usr/bin/env python3
"""
Script para probar el API de terceros directamente
"""

import requests
import json

def test_api_terceros():
    """Prueba el API de listado de terceros"""
    try:
        print("🧪 Probando API de terceros...")
        
        # Hacer petición al API
        url = "http://localhost:8099/terceros/api/listar?page=1&per_page=5"
        response = requests.get(url)
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta JSON recibida correctamente")
            
            # Verificar estructura
            if data.get('success'):
                print("✅ success = True")
                
                if 'data' in data:
                    print("✅ Clave 'data' encontrada")
                    
                    # Verificar estructura interna
                    data_content = data['data']
                    
                    if 'terceros' in data_content:
                        terceros = data_content['terceros']
                        print(f"✅ Terceros encontrados: {len(terceros)}")
                        
                        # Mostrar primer tercero
                        if terceros:
                            primer_tercero = terceros[0]
                            print(f"👤 Primer tercero: {primer_tercero.get('nit')} - {primer_tercero.get('razon_social')}")
                    
                    if 'stats' in data_content:
                        stats = data_content['stats']
                        print(f"📊 Total terceros: {stats.get('total_terceros')}")
                        print(f"📄 Mostrando desde: {stats.get('mostrando_desde')} hasta: {stats.get('mostrando_hasta')}")
                    
                    if 'pagination' in data_content:
                        pagination = data_content['pagination']
                        print(f"📄 Página {pagination.get('page')} de {pagination.get('pages')}")
                        
                else:
                    print("❌ No se encontró la clave 'data' en la respuesta")
                    
            else:
                print(f"❌ success = False. Message: {data.get('message')}")
                
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Respuesta: {response.text[:200]}")
            
    except Exception as e:
        print(f"💥 Error en la prueba: {e}")

def test_api_con_autenticacion():
    """Prueba el API con sesión de login"""
    try:
        print("\n🔐 Probando con autenticación...")
        
        # Crear sesión
        session = requests.Session()
        
        # Hacer login primero
        login_url = "http://localhost:8099/api/auth/login"
        login_data = {
            "nit": "805028041",
            "usuario": "admin", 
            "contraseña": "123456"
        }
        
        login_response = session.post(login_url, json=login_data)
        print(f"🔑 Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            # Ahora hacer petición al API de terceros con sesión
            api_url = "http://localhost:8099/terceros/api/listar?page=1&per_page=5"
            api_response = session.get(api_url)
            
            print(f"📡 API Status: {api_response.status_code}")
            
            if api_response.status_code == 200:
                data = api_response.json()
                if data.get('success') and 'data' in data:
                    terceros_count = len(data['data'].get('terceros', []))
                    total_count = data['data'].get('stats', {}).get('total_terceros', 0)
                    print(f"✅ API funcionando! Mostrando {terceros_count} de {total_count} terceros")
                    return True
                    
        return False
        
    except Exception as e:
        print(f"💥 Error con autenticación: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PROBANDO API DE TERCEROS")
    print("=" * 50)
    
    # Probar sin autenticación primero
    test_api_terceros()
    
    # Probar con autenticación
    success = test_api_con_autenticacion()
    
    if success:
        print("\n🎉 ¡EL API ESTÁ FUNCIONANDO CORRECTAMENTE!")
        print("✅ Ve a http://localhost:8099/terceros/consulta para verlo en el navegador")
    else:
        print("\n❌ Hay problemas con el API")