"""Prueba SIMPLE de laAPI - solo contar registros"""
import requests

url = "http://127.0.0.1:8099/dian_vs_erp/api/dian?fecha_inicial=2026-01-01&fecha_final=2026-02-16"
response = requests.get(url, timeout=10)
data = response.json()

print(f"Status: {response.status_code}")
print(f"Tipo: {type(data)}")
print(f"Registros: {len(data) if isinstance(data, list) else 'N/A'}")

if isinstance(data, dict) and 'error' in data:
    print(f"ERROR: {data['error']}")
