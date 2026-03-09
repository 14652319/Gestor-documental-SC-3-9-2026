# Script de prueba para los nuevos endpoints
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_check_nit():
    """Probar verificación de NIT"""
    print("🔍 Probando verificación de NIT...")
    
    # Probar con NIT existente
    response = requests.post(f"{BASE_URL}/api/registro/check_nit", 
                           json={"nit": "805028041"})
    result = response.json()
    print(f"NIT existente (805028041): {result}")
    
    # Probar con NIT nuevo
    response = requests.post(f"{BASE_URL}/api/registro/check_nit", 
                           json={"nit": "999999999"})
    result = response.json()
    print(f"NIT nuevo (999999999): {result}")

def test_register_tercero():
    """Probar registro de tercero"""
    print("\n📝 Probando registro de tercero...")
    
    data = {
        "nit": "111222333",
        "tipoPersona": "juridica",
        "razonSocial": "Empresa de Prueba SAS",
        "correoElectronico": "prueba@empresa.com",
        "numeroCelular": "3001234567",
        "aceptaTerminos": True,
        "aceptaContacto": False
    }
    
    response = requests.post(f"{BASE_URL}/api/registro/proveedor", json=data)
    result = response.json()
    print(f"Registro tercero: {result}")
    
    return result.get("data", {}).get("tercero_id") if result.get("success") else None

def test_create_users(tercero_id):
    """Probar creación de usuarios"""
    print(f"\n👥 Probando creación de usuarios para tercero_id: {tercero_id}")
    
    if not tercero_id:
        print("❌ No se puede probar sin tercero_id")
        return
    
    data = {
        "tercero_id": tercero_id,
        "usuarios": [
            {
                "nombre_usuario": "USUARIO1",
                "correo": "usuario1@prueba.com",
                "password": "MiPassword123*"
            },
            {
                "nombre_usuario": "USUARIO2", 
                "correo": "usuario2@prueba.com",
                "password": "OtraPassword456*"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/registro/usuarios", json=data)
    result = response.json()
    print(f"Creación usuarios: {result}")

def test_forgot_password():
    """Probar recuperación de contraseña"""
    print("\n🔐 Probando recuperación de contraseña...")
    
    # Datos de prueba (usando admin que ya existe)
    data = {
        "nit": "123456789-0",
        "usuario": "ADMIN",
        "correo": "admin@gestor.com"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/forgot_request", json=data)
    result = response.json()
    print(f"Solicitud código: {result}")

if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBAS DE ENDPOINTS...")
    print("=" * 50)
    
    try:
        test_check_nit()
        tercero_id = test_register_tercero()
        test_create_users(tercero_id)
        test_forgot_password()
        
        print("\n✅ Pruebas completadas!")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")