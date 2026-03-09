#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la consulta de radicados manualmente
"""
import requests
import json

def probar_consulta_radicado(radicado):
    url = "http://127.0.0.1:5000/api/consulta/radicado"
    data = {"radicado": radicado}
    
    try:
        response = requests.post(url, json=data)
        print(f"🔍 Consultando radicado: {radicado}")
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Respuesta:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. ¿Está corriendo la aplicación?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Probando consultas de radicados...")
    print("=" * 50)
    
    # Probar radicados existentes
    probar_consulta_radicado("RAD-000004")
    print("-" * 30)
    probar_consulta_radicado("RAD-000006") 
    print("-" * 30)
    
    # Probar radicado inexistente
    probar_consulta_radicado("RAD-000001")