"""
Simula EXACTAMENTE la petición HTTP POST que hace el navegador
Diciembre 29, 2025
"""

import requests
from pathlib import Path

print("=" * 80)
print("🌐 SIMULANDO UPLOAD HTTP (como el navegador)")
print("=" * 80)

# Archivos a subir
archivos = {
    "dian": r"D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\Dian\Desde 01-11-2025 Hasta 29-12-2025.xlsx",
    "erp_financiero": r"D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\ERP Financiero\ERP Financiero.xlsx",
    "erp_comercial": r"D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\ERP Comercial\ERP Comercial.xlsx"
}

# URL del endpoint
url = "http://localhost:8099/dian_vs_erp/subir_archivos"

print(f"\n📡 Endpoint: {url}")
print(f"\n📁 Archivos a subir:")
for tipo, ruta in archivos.items():
    nombre = Path(ruta).name
    print(f"   • {tipo}: {nombre}")

# Preparar archivos para multipart/form-data
files = {}
for key, ruta in archivos.items():
    if Path(ruta).exists():
        files[key] = open(ruta, 'rb')
        print(f"   ✅ {key} abierto")
    else:
        print(f"   ⚠️ {key} no encontrado: {ruta}")

if len(files) == 0:
    print("\n❌ No se encontró ningún archivo")
    exit(1)

print(f"\n🚀 Enviando petición POST...")

try:
    response = requests.post(url, files=files, timeout=300)
    
    print("\n" + "=" * 80)
    print("📥 RESPUESTA DEL SERVIDOR")
    print("=" * 80)
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse Text:\n{response.text}")
    
    if response.status_code == 200:
        print("\n✅ CARGA EXITOSA")
    else:
        print(f"\n❌ ERROR {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: No se pudo conectar al servidor")
    print("   ¿Está el servidor Flask corriendo en http://localhost:8099?")
    print("   Ejecuta: python app.py")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    # Cerrar archivos
    for f in files.values():
        f.close()
