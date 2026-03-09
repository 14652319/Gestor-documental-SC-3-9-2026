"""
Script para probar la recuperación de contraseña del usuario 14652319
"""
import requests
import json

# URL del servidor
BASE_URL = "http://localhost:8099"

# Datos del usuario según la imagen
datos_usuario = {
    "nit": "14652319",
    "usuario": "14652319",
    "correo": "RICARDO160883@HOTMAIL.ES"  # Como está en la BD
}

print("\n" + "="*80)
print("🧪 TEST DE RECUPERACIÓN DE CONTRASEÑA - Usuario 14652319")
print("="*80)

# Test 1: Solicitar código de recuperación
print("\n📧 Test 1: Solicitando código de recuperación...")
print(f"   NIT: {datos_usuario['nit']}")
print(f"   Usuario: {datos_usuario['usuario']}")
print(f"   Correo: {datos_usuario['correo']}")

response = requests.post(
    f"{BASE_URL}/api/auth/forgot_request",
    json=datos_usuario,
    headers={"Content-Type": "application/json"}
)

print(f"\n📊 Respuesta del servidor:")
print(f"   Status Code: {response.status_code}")
print(f"   Body: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

if response.status_code == 200:
    print("\n✅ ÉXITO: El código fue generado y enviado")
    print("   Revisa el terminal del servidor Flask para ver el TOKEN")
    print("   O revisa el correo RICARDO160883@HOTMAIL.ES")
else:
    print("\n❌ ERROR: No se pudo generar el código")
    print("   Posibles causas:")
    print("   - El usuario no existe en la BD")
    print("   - El correo no coincide")
    print("   - El NIT no coincide")

# Test 2: Probar con correo en lowercase (no debería funcionar sin el fix)
print("\n" + "="*80)
print("📧 Test 2: Probando con correo en minúsculas (caso común de usuario)")
print("="*80)

datos_usuario_lower = {
    "nit": "14652319",
    "usuario": "14652319",
    "correo": "ricardo160883@hotmail.es"  # En minúsculas
}

print(f"   Correo enviado: {datos_usuario_lower['correo']}")

response2 = requests.post(
    f"{BASE_URL}/api/auth/forgot_request",
    json=datos_usuario_lower,
    headers={"Content-Type": "application/json"}
)

print(f"\n📊 Respuesta del servidor:")
print(f"   Status Code: {response2.status_code}")
print(f"   Body: {json.dumps(response2.json(), indent=2, ensure_ascii=False)}")

if response2.status_code == 200:
    print("\n✅ ÉXITO: El fix funciona - comparación case-insensitive")
    print("   El usuario puede escribir su correo en minúsculas o mayúsculas")
else:
    print("\n❌ ERROR: El fix no funcionó correctamente")

print("\n" + "="*80)
print("✅ Tests completados")
print("="*80 + "\n")
