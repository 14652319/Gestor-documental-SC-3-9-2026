"""Prueba la API que ahora lee de ambas tablas"""
import requests
import json

# Probar con fechas de 2026
print("=" * 60)
print("PRUEBA 1: Datos de Febrero 2026")
print("=" * 60)

url_2026 = "http://127.0.0.1:8099/dian_vs_erp/api/dian?fecha_inicial=2026-02-01&fecha_final=2026-02-28"
try:
    response = requests.get(url_2026, timeout=10)
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if isinstance(data, dict) and 'error' in data:
        print(f"❌ ERROR: {data['error']}")
    elif isinstance(data, list):
        print(f"✅ Registros obtenidos: {len(data)}")
        if len(data) > 0:
            print("\nPRIMER REGISTRO:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False))
    else:
        print(f"Tipo de respuesta inesperado: {type(data)}")
        print(data)
except Exception as e:
    print(f"❌ Error al consultar: {e}")

print("\n" + "=" * 60)
print("PRUEBA 2: Datos de 2025")
print("=" * 60)

url_2025 = "http://127.0.0.1:8099/dian_vs_erp/api/dian?fecha_inicial=2025-01-01&fecha_final=2025-12-31"
try:
    response = requests.get(url_2025, timeout=10)
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if isinstance(data, dict) and 'error' in data:
        print(f"❌ ERROR: {data['error']}")
    elif isinstance(data, list):
        print(f"✅ Registros obtenidos: {len(data)}")
        if len(data) > 0:
            print("\nPRIMER REGISTRO:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False))
    else:
        print(f"Tipo de respuesta inesperado: {type(data)}")
        print(data)
except Exception as e:
    print(f"❌ Error al consultar: {e}")
