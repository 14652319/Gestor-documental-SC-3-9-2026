"""
Script de prueba para verificar el envío de correo de corrección de documentos
"""
import sys
import requests
import json

# URL del servidor
BASE_URL = "http://127.0.0.1:8099"

# Datos de prueba
documento_id = 32  # ID del documento de prueba

# Datos de corrección (cambiar solo el consecutivo para evitar duplicados)
datos_correccion = {
    "empresa_id": None,  # Mantener la misma empresa
    "tipo_documento_id": None,  # Mantener el mismo tipo
    "centro_operacion_id": None,  # Mantener el mismo centro
    "consecutivo": "00000099",  # Nuevo consecutivo
    "fecha_expedicion": None,  # Mantener la misma fecha
    "justificacion": "Prueba de envío de correo electrónico para validar corrección de documento"
}

print("="*80)
print("🧪 PRUEBA DE ENVÍO DE CORREO - CORRECCIÓN DE DOCUMENTO")
print("="*80)
print(f"📄 Documento ID: {documento_id}")
print(f"📋 Datos de corrección:")
for key, value in datos_correccion.items():
    if value:
        print(f"   - {key}: {value}")
print("="*80)

# Primero necesitamos hacer login
print("\n1️⃣ Intentando login...")

# Crear sesión para mantener cookies
session = requests.Session()

login_data = {
    "usuario": "admin",
    "clave": "admin123",
    "nit": "805028041"
}

try:
    login_response = session.post(
        f"{BASE_URL}/api/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code in [200, 302]:
        print("✅ Login exitoso")
        print(f"   Cookies: {session.cookies.get_dict()}")
    else:
        print(f"❌ Login falló: {login_response.status_code}")
        print(f"   Respuesta: {login_response.text[:200]}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error en login: {e}")
    sys.exit(1)

# Ahora solicitar la corrección
print("\n2️⃣ Solicitando corrección de documento...")

try:
    correccion_response = session.post(
        f"{BASE_URL}/api/notas/solicitar-correccion/{documento_id}",
        json=datos_correccion,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status Code: {correccion_response.status_code}")
    
    if correccion_response.status_code == 200:
        resultado = correccion_response.json()
        print("\n✅ SOLICITUD EXITOSA")
        print("="*80)
        print(f"Mensaje: {resultado.get('message')}")
        print(f"Token ID: {resultado.get('token_id')}")
        print(f"Expira en: {resultado.get('expira_en_minutos')} minutos")
        print(f"Correo enviado: {resultado.get('correo_enviado')}")
        print("="*80)
        
        if resultado.get('correo_enviado'):
            print("\n📧 ¡CORREO ENVIADO EXITOSAMENTE!")
            print("Revisa tu bandeja de entrada (puede tardar unos segundos)")
        else:
            print("\n⚠️ El correo NO se envió (revisar logs del servidor)")
            
    elif correccion_response.status_code == 409:
        resultado = correccion_response.json()
        print("\n⚠️ DOCUMENTO DUPLICADO DETECTADO")
        print("="*80)
        print(f"Mensaje: {resultado.get('message')}")
        print(f"Documento existente: {resultado.get('documento_existente')}")
        print(f"Ruta existente: {resultado.get('ruta_existente')}")
        print("="*80)
        print("\n✅ LA VALIDACIÓN DE DUPLICADOS FUNCIONA CORRECTAMENTE")
        
    else:
        print(f"\n❌ ERROR EN SOLICITUD: {correccion_response.status_code}")
        try:
            error = correccion_response.json()
            print(f"Mensaje: {error.get('message')}")
        except:
            print(f"Respuesta: {correccion_response.text[:500]}")
            
except Exception as e:
    print(f"\n❌ Error en solicitud de corrección: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("🏁 PRUEBA COMPLETADA")
print("="*80)
