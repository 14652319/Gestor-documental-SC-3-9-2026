"""
Cargar solo DIAN por bimestres
"""
import requests
from pathlib import Path

BASE_URL = "http://localhost:8099"
session = requests.Session()

# Login
session.post(f"{BASE_URL}/api/auth/login", json={"nit": "805028041", "usuario": "admin", "password": "Admin123456$"})

# Solo archivo 1 de DIAN
archivo = Path(r"D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\Dian\Desde 01-01-2025 Hasta 28-02-2025.xlsx")

print(f"📤 Cargando: {archivo.name}")
print(f"   Tamaño: {archivo.stat().st_size / (1024*1024):.2f} MB")

files = {"dian": open(archivo, 'rb')}

try:
    response = session.post(f"{BASE_URL}/dian_vs_erp/subir_archivos", files=files, timeout=300)
    print(f"\n✅ Status: {response.status_code}")
    print(response.text)
except Exception as e:
    print(f"\n❌ Error: {e}")
finally:
    files["dian"].close()
