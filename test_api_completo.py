"""
Test directo del API - Ver qué devuelve cargar_facturas_temporales
"""
import requests
import json

# Login
session = requests.Session()
login_data = {
    'usuario': 'admin',
    'password': 'Inicio2024*'
}

print("="*70)
print("🔐 HACIENDO LOGIN...")
print("="*70)

try:
    login_resp = session.post('http://127.0.0.1:8099/login', data=login_data, timeout=5)
    print(f"Status: {login_resp.status_code}")
    
    if login_resp.status_code == 200:
        print("✅ Login exitoso\n")
        
        # Cargar facturas
        print("="*70)
        print("📋 CONSULTANDO API: /recibir_facturas/cargar_facturas_temporales")
        print("="*70)
        
        api_resp = session.get('http://127.0.0.1:8099/recibir_facturas/cargar_facturas_temporales', timeout=5)
        print(f"Status: {api_resp.status_code}\n")
        
        if api_resp.status_code == 200:
            facturas = api_resp.json()
            print(f"Total facturas recibidas: {len(facturas)}\n")
            
            # Mostrar las primeras 3 facturas con TODOS sus campos
            print("="*70)
            print("📊 PRIMERAS 3 FACTURAS (TODOS LOS CAMPOS)")
            print("="*70)
            
            for i, factura in enumerate(facturas[:3], 1):
                print(f"\n--- FACTURA {i}: {factura.get('prefijo', '')}{factura.get('folio', '')} ---")
                for key, value in sorted(factura.items()):
                    print(f"  {key:30s}: {value}")
            
            # Verificar si empresa_id existe
            print("\n" + "="*70)
            print("🔍 VERIFICACIÓN CAMPO 'empresa_id'")
            print("="*70)
            
            con_empresa = sum(1 for f in facturas if 'empresa_id' in f)
            sin_empresa = len(facturas) - con_empresa
            
            print(f"✅ Facturas CON campo 'empresa_id': {con_empresa}")
            print(f"❌ Facturas SIN campo 'empresa_id': {sin_empresa}")
            
            # Mostrar valores de empresa_id
            if con_empresa > 0:
                print("\n📌 VALORES DE empresa_id:")
                for f in facturas[:5]:
                    emp = f.get('empresa_id', 'CAMPO NO EXISTE')
                    print(f"  {f.get('prefijo', '')}{f.get('folio', ''):4s} -> empresa_id: {emp}")
        else:
            print(f"❌ Error en API: {api_resp.status_code}")
            print(api_resp.text)
    else:
        print(f"❌ Error en login: {login_resp.status_code}")

except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "="*70)
