"""
EJECUTA LA CARGA REAL DE ARCHIVOS
Simula la petición HTTP que hace el navegador al endpoint real
"""

import requests
import json

print("=" * 80)
print("🚀 EJECUTANDO CARGA REAL DE ARCHIVOS")
print("=" * 80)

# URL del endpoint real - FORZAR PROCESAR desde archivos en disco
url = "http://127.0.0.1:8099/dian_vs_erp/api/forzar_procesar"

print(f"\n📡 Enviando petición GET a: {url}")
print("   (Reprocesa los archivos que ya están en uploads/)")

try:
    # Llamar al endpoint que procesa archivos existentes en disco
    response = requests.get(
        url,
        timeout=300  # 5 minutos de timeout
    )
    
    print(f"\n📊 Código de respuesta: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Respuesta exitosa")
        try:
            data = response.json()
            print("\n📋 Respuesta JSON:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            print("\n📋 Respuesta (texto):")
            print(response.text[:500])
    else:
        print(f"❌ Error HTTP {response.status_code}")
        print("\n📋 Respuesta de error:")
        print(response.text[:1000])
        
except requests.exceptions.Timeout:
    print("\n⏱️  TIMEOUT - El proceso tardó más de 5 minutos")
    print("   Esto puede ser normal para archivos grandes")
    print("   Verifica la terminal del servidor Flask para ver el progreso")
    
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR DE CONEXIÓN")
    print("   El servidor Flask no está corriendo en http://127.0.0.1:8099")
    print("   Ejecuta: .\\1_iniciar_gestor.bat")
    
except Exception as e:
    print(f"\n❌ ERROR INESPERADO: {e}")
    print(f"   Tipo: {type(e).__name__}")

print("\n" + "=" * 80)
print("💡 IMPORTANTE: Revisa la terminal de VS Code donde corre Flask")
print("   Ahí verás los mensajes detallados de lo que está pasando")
print("=" * 80)
