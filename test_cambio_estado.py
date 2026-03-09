#!/usr/bin/env python3
"""
Script para probar el cambio de estado de terceros
"""

import requests
import json

def probar_cambio_estado():
    """Prueba el endpoint de cambio de estado"""
    
    # URL del servidor
    base_url = "http://127.0.0.1:8099"
    
    # ID de tercero para probar (usar uno de los que vimos antes)
    tercero_id = 16590  # IS INGENIERIA SAS
    
    print(f"=== PROBANDO CAMBIO DE ESTADO TERCERO ID {tercero_id} ===")
    
    try:
        # 1. Probar desactivar (cambiar a inactivo)
        print("\n1. 🔄 Probando desactivar tercero...")
        response = requests.post(
            f"{base_url}/terceros/api/cambiar_estado/{tercero_id}",
            json={'activo': False},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Respuesta: {json.dumps(data, indent=2)}")
        
        if data.get('success'):
            print("✅ Desactivación exitosa")
        else:
            print(f"❌ Error en desactivación: {data.get('message')}")
            return
        
        # 2. Probar activar (cambiar a activo)
        print("\n2. 🔄 Probando activar tercero...")
        response = requests.post(
            f"{base_url}/terceros/api/cambiar_estado/{tercero_id}",
            json={'activo': True},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Respuesta: {json.dumps(data, indent=2)}")
        
        if data.get('success'):
            print("✅ Activación exitosa")
        else:
            print(f"❌ Error en activación: {data.get('message')}")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_cambio_estado()