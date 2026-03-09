#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de exportación Excel 
del módulo de causaciones con filtros aplicados.
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8099"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
EXCEL_URL = f"{BASE_URL}/causaciones/exportar/excel"

def login():
    """Login al sistema para obtener sesión"""
    print("🔐 Iniciando sesión...")
    
    # Datos de login (usar usuario externa que está activo)
    login_data = {
        "nit": "99999999",
        "usuario": "externa", 
        "password": "123456"
    }
    
    session = requests.Session()
    
    try:
        response = session.post(LOGIN_URL, json=login_data)
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok', False):
                print("✅ Login exitoso")
                return session
            else:
                print(f"❌ Login fallido: {data.get('message', 'Error desconocido')}")
                return None
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_excel_export(session, test_name, params=None):
    """Prueba la exportación Excel con parámetros específicos"""
    print(f"\n🧪 {test_name}")
    
    url = EXCEL_URL
    if params:
        # Convertir parámetros a query string
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{EXCEL_URL}?{param_str}"
    
    print(f"📡 URL: {url}")
    
    try:
        response = session.get(url)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            # Verificar que es un archivo Excel
            content_type = response.headers.get('content-type', '')
            content_disposition = response.headers.get('content-disposition', '')
            
            print(f"📄 Content-Type: {content_type}")
            print(f"📄 Content-Disposition: {content_disposition}")
            
            if 'excel' in content_type or 'xlsx' in content_type:
                file_size = len(response.content)
                print(f"✅ Excel generado exitosamente ({file_size:,} bytes)")
                
                # Guardar archivo para verificación manual
                timestamp = datetime.now().strftime('%H%M%S')
                filename = f"test_excel_{test_name.replace(' ', '_').lower()}_{timestamp}.xlsx"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"💾 Archivo guardado: {filename}")
                return True
            else:
                print(f"❌ Respuesta no es un archivo Excel")
                print(f"📄 Contenido: {response.text[:200]}...")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"📄 Respuesta: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("=" * 60)
    print("🧪 PRUEBAS DE EXPORTACIÓN EXCEL - MÓDULO CAUSACIONES")
    print("=" * 60)
    
    # Login
    session = login()
    if not session:
        print("❌ No se pudo iniciar sesión. Abortando pruebas.")
        return
    
    # Configurar tests
    tests = [
        {
            "name": "Excel Sin Filtros (TODOS)",
            "params": None
        },
        {
            "name": "Excel Filtro Sede CYS",
            "params": {"sede": "CYS"}
        },
        {
            "name": "Excel Filtro Sede DOM",
            "params": {"sede": "DOM"}
        },
        {
            "name": "Excel Filtro Carpeta APROBADAS",
            "params": {"carpeta": "APROBADAS"}
        },
        {
            "name": "Excel Filtro Texto 'factura'",
            "params": {"filtro": "factura"}
        },
        {
            "name": "Excel Múltiples Filtros",
            "params": {
                "sede": "CYS", 
                "carpeta": "APROBADAS",
                "filtro": "20"
            }
        }
    ]
    
    # Ejecutar pruebas
    resultados = []
    for test in tests:
        resultado = test_excel_export(session, test["name"], test.get("params"))
        resultados.append((test["name"], resultado))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    exitosas = 0
    for nombre, resultado in resultados:
        estado = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{estado} {nombre}")
        if resultado:
            exitosas += 1
    
    print(f"\n🎯 Resultado Final: {exitosas}/{len(resultados)} pruebas exitosas")
    
    if exitosas == len(resultados):
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar logs.")

if __name__ == "__main__":
    main()