import requests
from datetime import datetime

# URL de la API v2
base_url = "http://127.0.0.1:8099"
api_url = f"{base_url}/dian_vs_erp/api/dian_v2"

# Parámetros: mismo rango que estás usando en el navegador
params = {
    'fecha_inicial': '2026-01-01',
    'fecha_final': '2026-02-26'
}

print("=" * 80)
print("🔍 PROBANDO API V2 DIRECTAMENTE")
print("=" * 80)
print(f"\n📡 URL: {api_url}")
print(f"📅 Parámetros: {params}")

try:
    response = requests.get(api_url, params=params, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        
        # La API puede retornar lista directa o dict con 'registros'
        if isinstance(data, list):
            registros = data
        else:
            registros = data.get('registros', data.get('data', []))
        
        print(f"\n✅ Respuesta exitosa - {len(registros)} registros recibidos")
        
        # Contar forma_pago_texto
        contado_count = sum(1 for r in registros if r.get('forma_pago_texto') == 'Contado')
        credito_count = sum(1 for r in registros if r.get('forma_pago_texto') == 'Crédito')
        otros_count = len(registros) - contado_count - credito_count
        
        print(f"\n📊 DISTRIBUCIÓN DE FORMA_PAGO_TEXTO EN LA RESPUESTA:")
        print(f"   Contado:  {contado_count:>6,} registros ({contado_count/len(registros)*100:.2f}%)")
        print(f"   Crédito:  {credito_count:>6,} registros ({credito_count/len(registros)*100:.2f}%)")
        print(f"   Otros:    {otros_count:>6,} registros ({otros_count/len(registros)*100:.2f}%)")
        print(f"   TOTAL:    {len(registros):>6,} registros")
        
        # Mostrar primeros 5 registros con Contado
        contado_registros = [r for r in registros if r.get('forma_pago_texto') == 'Contado']
        if contado_registros:
            print(f"\n💰 PRIMEROS 5 REGISTROS CON 'CONTADO' (de {len(contado_registros)}):")
            print("-" * 120)
            for i, reg in enumerate(contado_registros[:5], 1):
                print(f"{i}. NIT: {reg.get('nit_emisor')} | Fecha: {reg.get('fecha_emision')} | "
                      f"Folio: {reg.get('prefijo', '')}-{reg.get('folio')} | "
                      f"Valor: ${reg.get('valor', 0):,.2f} | "
                      f"forma_pago_texto: '{reg.get('forma_pago_texto')}'")
        else:
            print("\n❌ NO HAY REGISTROS CON 'CONTADO' EN LA RESPUESTA DE LA API")
            print("   Esto significa que el backend NO está devolviendo los registros Contado")
            print("   aunque existen en la base de datos.")
        
        # Mostrar primeros 3 registros Crédito para comparar
        credito_registros = [r for r in registros if r.get('forma_pago_texto') == 'Crédito']
        if credito_registros:
            print(f"\n💳 PRIMEROS 3 REGISTROS CON 'CRÉDITO' (de {len(credito_registros)}):")
            print("-" * 120)
            for i, reg in enumerate(credito_registros[:3], 1):
                print(f"{i}. NIT: {reg.get('nit_emisor')} | Fecha: {reg.get('fecha_emision')} | "
                      f"Folio: {reg.get('prefijo', '')}-{reg.get('folio')} | "
                      f"Valor: ${reg.get('valor', 0):,.2f} | "
                      f"forma_pago_texto: '{reg.get('forma_pago_texto')}'")
        
    else:
        print(f"\n❌ Error HTTP {response.status_code}")
        print(f"   Respuesta: {response.text[:500]}")

except Exception as e:
    print(f"\n❌ Error al consultar la API:")
    print(f"   {type(e).__name__}: {e}")

print("\n" + "=" * 80)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 80)
