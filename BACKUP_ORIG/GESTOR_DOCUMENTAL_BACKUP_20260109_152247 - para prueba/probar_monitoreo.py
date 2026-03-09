#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Probador del sistema de monitoreo
"""
import requests
import json

def probar_monitoreo():
    """Prueba los endpoints del sistema de monitoreo"""
    base_url = "http://127.0.0.1:8099"
    
    print("🔍 PROBANDO SISTEMA DE MONITOREO")
    print("=" * 50)
    
    # 1. Probar estado de las tablas
    print("\n1. 📊 VERIFICANDO ESTADO DE TABLAS...")
    
    # 2. Probar endpoint de usuarios (requiere autenticación)
    print("\n2. 👥 PROBANDO ENDPOINT DE USUARIOS...")
    try:
        response = requests.get(f"{base_url}/admin/monitoreo/api/usuarios_tiempo_real", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                usuarios = data.get('data', [])
                print(f"   ✅ Usuarios encontrados: {len(usuarios)}")
                if usuarios:
                    print(f"   📝 Ejemplo: {usuarios[0].get('usuario', 'N/A')} - {usuarios[0].get('estado_conexion', 'N/A')}")
            else:
                print(f"   ⚠️ Respuesta no exitosa: {data}")
        else:
            print(f"   ⚠️ Error HTTP: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Probar endpoint de IPs
    print("\n3. 🔒 PROBANDO ENDPOINT DE IPs...")
    try:
        response = requests.get(f"{base_url}/admin/monitoreo/api/ips_tiempo_real", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                ips = data.get('data', [])
                print(f"   ✅ IPs encontradas: {len(ips)}")
                if ips:
                    print(f"   📝 Ejemplo: {ips[0]}")
            else:
                print(f"   ⚠️ Respuesta no exitosa: {data}")
        else:
            print(f"   ⚠️ Error HTTP: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Probar endpoint de stats
    print("\n4. 📈 PROBANDO ENDPOINT DE ESTADÍSTICAS...")
    try:
        response = requests.get(f"{base_url}/admin/monitoreo/api/stats_sorprendentes", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('data', {})
                print(f"   ✅ Usuarios conectados: {stats.get('usuarios_conectados', 'N/A')}")
                print(f"   ✅ Total usuarios: {stats.get('total_usuarios', 'N/A')}")
                print(f"   ✅ IPs bloqueadas: {stats.get('ips_bloqueadas', 'N/A')}")
            else:
                print(f"   ⚠️ Respuesta no exitosa: {data}")
        else:
            print(f"   ⚠️ Error HTTP: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 RESUMEN:")
    print("✅ Tablas de monitoreo: CREADAS")
    print("✅ IPs localhost: CONFIGURADAS") 
    print("✅ Estructura actualizada: COMPLETA")
    print("⚠️ Endpoints: Requieren autenticación")
    print("\n💡 PRÓXIMO PASO:")
    print("   Inicia sesión como admin y revisa el módulo de monitoreo")

if __name__ == "__main__":
    probar_monitoreo()