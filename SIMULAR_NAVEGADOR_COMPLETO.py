"""
Simula EXACTAMENTE el flujo completo del navegador:
1. Login
2. Upload archivos
Diciembre 29, 2025
"""

import requests
from pathlib import Path

print("=" * 80)
print("🌐 SIMULACIÓN COMPLETA: LOGIN + UPLOAD")
print("=" * 80)

# Configuración
BASE_URL = "http://localhost:8099"
session = requests.Session()  # Mantiene cookies

# ===== PASO 1: LOGIN =====
print("\n1️⃣ PASO 1: LOGIN")
print("-" * 40)

login_data = {
    "nit": "805028041",
    "usuario": "admin",
    "password": "Admin123456$"
}

print(f"Usuario: {login_data['usuario']}")
print(f"NIT: {login_data['nit']}")

try:
    login_response = session.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
    print(f"Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        print("✅ Login exitoso")
        print(f"Cookies: {session.cookies.get_dict()}")
    else:
        print(f"❌ Login falló: {login_response.text}")
        exit(1)
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: No se pudo conectar al servidor")
    print("   ¿Está el servidor Flask corriendo?")
    exit(1)

# ===== PASO 2: UPLOAD ARCHIVOS =====
print("\n2️⃣ PASO 2: UPLOAD ARCHIVOS")
print("-" * 40)

archivos = {
    "dian": r"D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\Dian\Desde 01-11-2025 Hasta 29-12-2025.xlsx",
}

print(f"\n📁 Archivo a subir:")
for tipo, ruta in archivos.items():
    nombre = Path(ruta).name
    print(f"   • {tipo}: {nombre}")

# Preparar archivos
files = {}
for key, ruta in archivos.items():
    if Path(ruta).exists():
        files[key] = open(ruta, 'rb')
    else:
        print(f"   ⚠️ {key} no encontrado")

if len(files) == 0:
    print("\n❌ No se encontró ningún archivo")
    exit(1)

print(f"\n🚀 Enviando petición POST con archivo...")

try:
    upload_response = session.post(
        f"{BASE_URL}/dian_vs_erp/subir_archivos",
        files=files,
        timeout=300  # 5 minutos
    )
    
    print("\n" + "=" * 80)
    print("📥 RESPUESTA DEL SERVIDOR")
    print("=" * 80)
    print(f"Status Code: {upload_response.status_code}")
    
    if upload_response.status_code == 200:
        print("\n✅ UPLOAD EXITOSO")
        print(f"\n{upload_response.text}")
    else:
        print(f"\n❌ ERROR {upload_response.status_code}")
        print(f"\n{upload_response.text}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    for f in files.values():
        f.close()
