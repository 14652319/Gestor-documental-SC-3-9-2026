"""
Test rápido: Consultar API para ver qué devuelve
"""
import requests

# Login
session = requests.Session()
login = session.post('http://127.0.0.1:8099/login', data={
    'usuario': 'admin',
    'password': 'Inicio2024*'
})

print("Login:", login.status_code)

# Cargar facturas
resp = session.get('http://127.0.0.1:8099/recibir_facturas/cargar_facturas_temporales')
print("\nStatus:", resp.status_code)

if resp.status_code == 200:
    facturas = resp.json()
    print(f"\nTotal facturas: {len(facturas)}")
    
    # Buscar DS-1
    ds1 = [f for f in facturas if f.get('prefijo') == 'DS' and f.get('folio') == '1']
    
    if ds1:
        print("\n" + "="*70)
        print("FACTURA DS-1:")
        print("="*70)
        factura = ds1[0]
        print(f"NIT: {factura.get('nit')}")
        print(f"Prefijo: {factura.get('prefijo')}")
        print(f"Folio: {factura.get('folio')}")
        print(f"empresa_id: {factura.get('empresa_id')}")
        print(f"centro_operacion_id: {factura.get('centro_operacion_id')}")
        print(f"\nTODAS LAS KEYS:")
        for key in sorted(factura.keys()):
            print(f"  - {key}: {factura.get(key)}")
    else:
        print("\n⚠️ No se encontró DS-1")
        print("\nPrimeras 3 facturas:")
        for f in facturas[:3]:
            print(f"  {f.get('prefijo')}{f.get('folio')} - empresa_id: {f.get('empresa_id')}")
