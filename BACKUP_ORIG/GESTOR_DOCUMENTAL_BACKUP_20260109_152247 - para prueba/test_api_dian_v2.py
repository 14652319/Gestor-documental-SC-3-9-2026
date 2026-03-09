# -*- coding: utf-8 -*-
"""
Test directo de la API DIAN V2 desde el servidor
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
from datetime import date

# Test 1: Llamar a la API v2
print("\n" + "="*80)
print("TEST 1: Llamar a API DIAN V2 directamente")
print("="*80)

hoy = date.today()
fecha_inicial = f"{hoy.year}-{hoy.month:02d}-01"
fecha_final = hoy.strftime("%Y-%m-%d")

url = f"http://127.0.0.1:8099/dian_vs_erp/api/dian_v2?fecha_inicial={fecha_inicial}&fecha_final={fecha_final}"
print(f"\nURL: {url}")

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            print(f"✅ ÉXITO: API retornó {len(data)} registros")
            if len(data) > 0:
                print(f"\n📋 Primer registro:")
                print(f"   NIT: {data[0].get('nit_emisor')}")
                print(f"   Nombre: {data[0].get('nombre_emisor')}")
                print(f"   Fecha: {data[0].get('fecha_emision')}")
                print(f"   Prefijo: {data[0].get('prefijo')}")
                print(f"   Folio: {data[0].get('folio')}")
                print(f"   Valor: ${data[0].get('valor'):,.0f}")
        else:
            print(f"❌ ERROR: Respuesta no es una lista")
            print(f"   Respuesta: {data}")
    else:
        print(f"❌ ERROR: Status {response.status_code}")
        print(f"   Respuesta: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ EXCEPCIÓN: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
