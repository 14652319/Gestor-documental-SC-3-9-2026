"""Prueba con el MISMO rango de fechas del navegador"""
import requests
import json

# Usar EXACTAMENTE el mismo rango que el navegador
print("=" * 60)
print("PRUEBA: Mismo rango que el navegador (2026-01-01 a 2026-02-16)")
print("=" * 60)

url = "http://127.0.0.1:8099/dian_vs_erp/api/dian?fecha_inicial=2026-01-01&fecha_final=2026-02-16"
try:
    response = requests.get(url, timeout=10)
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if isinstance(data, dict) and 'error' in data:
        print(f"❌ ERROR: {data['error']}")
    elif isinstance(data, list):
        print(f"✅ Registros obtenidos: {len(data)}")
        
        # Agrupar por mes
        por_mes = {}
        for reg in data:
            fecha = reg.get('fecha_emision', '')
            if fecha:
                mes = fecha[:7]  # YYYY-MM
                por_mes[mes] = por_mes.get(mes, 0) + 1
        
        print("\n📊 DISTRIBUCIÓN POR MES:")
        for mes in sorted(por_mes.keys()):
            print(f"  {mes}: {por_mes[mes]:,} registros")
        
        if len(data) > 0:
            print("\n📄 PRIMER REGISTRO:")
            primer = data[0]
            print(f"  NIT: {primer.get('nit_emisor')}")
            print(f"  Razón Social: {primer.get('nombre_emisor')}")
            print(f"  Fecha: {primer.get('fecha_emision')}")
            print(f"  Folio: {primer.get('prefijo')}-{primer.get('folio')}")
            print(f"  Valor: ${primer.get('valor'):,.0f}")
    else:
        print(f"Tipo de respuesta inesperado: {type(data)}")
        print(data)
except Exception as e:
    print(f"❌ Error al consultar: {e}")
    import traceback
    traceback.print_exc()
