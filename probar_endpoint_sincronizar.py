"""
Probar endpoint de sincronización directamente
"""
import requests
import json

print("\n" + "="*80)
print("🧪 PRUEBA DEL ENDPOINT /api/sincronizar")
print("="*80)

url = "http://localhost:8099/dian_vs_erp/api/sincronizar"

try:
    print(f"\n📡 Enviando petición POST a: {url}")
    response = requests.post(url, headers={'Content-Type': 'application/json'}, timeout=30)
    
    print(f"\n📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ RESPUESTA EXITOSA:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if data.get('exito'):
            print(f"\n🎉 SINCRONIZACIÓN EXITOSA")
            print(f"   Fecha: {data.get('fecha_sincronizacion')}")
            
            if 'resumen' in data:
                resumen = data['resumen']
                print(f"\n📊 RESUMEN:")
                print(f"   Total DIAN: {resumen.get('total_dian', 0):,}")
                print(f"   Total ERP Comercial: {resumen.get('total_erp_comercial', 0):,}")
                print(f"   Total ERP Financiero: {resumen.get('total_erp_financiero', 0):,}")
                print(f"   Total Acuses: {resumen.get('total_acuses', 0):,}")
                print(f"   Total Temporales: {resumen.get('total_temporales', 0):,}")
                print(f"   Total Recibidas: {resumen.get('total_recibidas', 0):,}")
                print(f"   Temporales en DIAN: {resumen.get('temporales_en_dian', 0):,}")
                print(f"   Recibidas en DIAN: {resumen.get('recibidas_en_dian', 0):,}")
        else:
            print(f"\n❌ SINCRONIZACIÓN FALLÓ")
            print(f"   Mensaje: {data.get('mensaje')}")
            
    else:
        print(f"\n❌ ERROR {response.status_code}")
        print(f"   Respuesta: {response.text[:500]}")
        
except requests.exceptions.ConnectionError:
    print(f"\n❌ ERROR DE CONEXIÓN")
    print(f"   ¿El servidor está corriendo en localhost:8099?")
    print(f"   Ejecuta: .\\1_iniciar_gestor.bat")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "="*80 + "\n")
