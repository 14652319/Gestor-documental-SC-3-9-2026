"""
Script de prueba para el sistema de envío masivo de facturas a firmar
Verifica que el endpoint /api/enviar-firma-masiva funcione correctamente
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8099"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
ENVIAR_URL = f"{BASE_URL}/facturas-digitales/api/enviar-firma-masiva"

# Credenciales de prueba (ajustar según tu usuario admin)
CREDENCIALES = {
    "nit": "805028041",  # NIT de Supertiendas Cañaveral
    "usuario": "admin",   # Tu usuario
    "password": "tu_password_aqui"  # Reemplazar con tu password
}

# IDs de facturas a enviar (ajustar según tus datos)
IDS_PRUEBA = [1, 2, 3]  # Reemplazar con IDs reales de tu base de datos

def main():
    session = requests.Session()
    
    print("=" * 70)
    print("🧪 TEST: ENVÍO MASIVO DE FACTURAS A FIRMAR")
    print("=" * 70)
    
    # Paso 1: Login
    print("\n1️⃣ Autenticando usuario...")
    try:
        response = session.post(LOGIN_URL, json=CREDENCIALES)
        if response.status_code == 200:
            print("   ✅ Login exitoso")
        else:
            print(f"   ❌ Error en login: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return
    
    # Paso 2: Enviar facturas
    print(f"\n2️⃣ Enviando {len(IDS_PRUEBA)} factura(s) a firmar...")
    try:
        payload = {"ids": IDS_PRUEBA}
        response = session.post(ENVIAR_URL, json=payload)
        
        print(f"\n📊 Código de respuesta: {response.status_code}")
        print("\n📋 Respuesta del servidor:")
        print("-" * 70)
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('success'):
                print("\n✅ ENVÍO EXITOSO")
                print(f"\n📧 Resumen:")
                print(f"   • Facturas actualizadas: {data.get('facturas_actualizadas', 0)}")
                print(f"   • Correos enviados: {data.get('correos_enviados', 0)}")
                print(f"   • Departamentos procesados: {data.get('departamentos_procesados', 0)}")
                
                if data.get('detalle'):
                    print(f"\n📬 Detalle de envíos:")
                    for envio in data['detalle']:
                        print(f"   • {envio['departamento']}: {envio['cantidad']} factura(s) → {envio['firmador']} ({envio['email']})")
                
                if data.get('advertencias'):
                    print(f"\n⚠️ Advertencias:")
                    for adv in data['advertencias']:
                        print(f"   • {adv}")
            else:
                print(f"\n❌ ERROR: {data.get('message', 'Error desconocido')}")
        else:
            print(response.text)
            print("\n❌ Error en el envío")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✔️ Prueba completada")
    print("=" * 70)

if __name__ == "__main__":
    print("\n⚠️ INSTRUCCIONES:")
    print("1. Edita este archivo y ajusta:")
    print("   - CREDENCIALES (tu usuario y password)")
    print("   - IDS_PRUEBA (IDs de facturas existentes en tu BD)")
    print("2. Ejecuta: python test_envio_firma_masivo.py")
    print("\n🔍 Nota: Verifica que tengas facturas en estado 'pendiente' o 'enviado_a_firmar'")
    print("         y que haya firmadores asignados a esos departamentos\n")
    
    input("Presiona Enter para continuar con la prueba...")
    main()
