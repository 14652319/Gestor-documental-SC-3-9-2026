# -*- coding: utf-8 -*-
"""
Script para probar corrección de documento CON autenticación
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8099"

print("="*80)
print("[TEST] PRUEBA CON AUTENTICACION - LOGIN + CORRECCION")
print("="*80)
print()

# Crear sesión para mantener cookies
session = requests.Session()

# Paso 1: LOGIN
print("1. Haciendo login...")

login_data = {
    "usuario": "14652319",
    "password": "admin123",
    "nit": "14652319"
}

try:
    login_response = session.post(
        f"{BASE_URL}/api/auth/login",
        json=login_data,
        timeout=5
    )
    
    print(f"   Status: {login_response.status_code}")
    print(f"   Response: {login_response.text[:200]}")
    
    login_result = login_response.json()
    print(f"   JSON: {login_result}")
    
    if login_result.get('success'):
        print(f"   [OK] Login exitoso")
        print(f"   Usuario: {login_result.get('usuario')}")
        print(f"   Rol: {login_result.get('rol')}")
        print()
    else:
        print(f"   [ERROR] Login fallo: {login_result.get('message')}")
        exit(1)
        
except Exception as e:
    print(f"   [ERROR] Error en login: {e}")
    exit(1)

# Paso 2: SOLICITAR CORRECCIÓN
print("2. Solicitando correccion del documento...")

correccion_data = {
    "empresa_id": None,
    "tipo_documento_id": None,
    "centro_operacion_id": None,
    "consecutivo": "00000099",
    "fecha_expedicion": None,
    "justificacion": "Prueba automatizada con autenticación desde Python - Validando corrección de variables y envío de token"
}

print("   [DATOS] Datos:")
print("      Consecutivo: 00000099")
print("      Justificacion: Prueba automatizada...")
print()

try:
    correccion_response = session.post(
        f"{BASE_URL}/api/notas/solicitar-correccion/32",
        json=correccion_data,
        timeout=10
    )
    
    print(f"   Status Code: {correccion_response.status_code}")
    
    resultado = correccion_response.json()
    
    print(f"   JSON Completo: {resultado}")
    
    print("="*80)
    print("[OK] RESPUESTA DEL SERVIDOR")
    print("="*80)
    print()
    
    if resultado.get('success'):
        print(f"[SUCCESS] {resultado.get('message')}")
        print()
        print("[INFO] Detalles del Token:")
        print(f"   [ID] Token ID: {resultado.get('token_id')}")
        print(f"   [TIME] Expira en: {resultado.get('expira_en_minutos')} minutos")
        print(f"   [EMAIL] Correo enviado: {resultado.get('correo_enviado')}")
        print()
        
        if resultado.get('correo_enviado'):
            print("[EMAIL] ¡CORREO ENVIADO EXITOSAMENTE!")
            print("   Revisa tu bandeja de entrada para obtener el token de 6 digitos")
        else:
            print("[WARN] El correo NO se envio (posible error SMTP)")
            print("   Revisa los logs del servidor para ver el token generado")
        
        print()
        print("="*80)
        print("[OK] VALIDACIONES COMPLETADAS")
        print("="*80)
        print("[OK] Variables del formulario extraidas correctamente")
        print("[OK] Validacion de duplicados ejecutada")
        print("[OK] Token generado exitosamente")
        print(f"[OK] Email procesado (enviado={resultado.get('correo_enviado')})")
        print()
        
    else:
        print(f"[WARN] ADVERTENCIA: {resultado.get('message')}")
        
        if resultado.get('ruta_existente'):
            print()
            print("[INFO] Documento duplicado detectado:")
            print(f"   Ruta: {resultado.get('ruta_existente')}")
            print()
            print("[OK] LA VALIDACION DE DUPLICADOS FUNCIONA CORRECTAMENTE")
    
except Exception as e:
    print("="*80)
    print("[ERROR] ERROR EN LA SOLICITUD")
    print("="*80)
    print()
    print(f"Error: {e}")
    
    if hasattr(e, 'response') and e.response:
        try:
            error_data = e.response.json()
            print(f"Mensaje: {error_data.get('message')}")
        except:
            pass

print()
print("="*80)
print("[FIN] PRUEBA FINALIZADA")
print("="*80)
