# -*- coding: utf-8 -*-
"""
Verificar si la API V2 ahora devuelve datos de febrero 2026
"""
import requests

try:
    print("=" * 80)
    print("🔍 VERIFICANDO API V2 CON JOIN CASE-INSENSITIVE")
    print("=" * 80)
    
    # Probar API V2 con febrero 2026
    response = requests.get(
        "http://127.0.0.1:8099/dian_vs_erp/api/dian_v2",
        params={
            'fecha_inicial': '2026-02-01',
            'fecha_final': '2026-02-28',
            'size': 200
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ API V2 devolvió: {len(data)} registros")
        
        if len(data) > 0:
            print(f"\n📋 Primeros 5 registros:")
            for i, reg in enumerate(data[:5]):
                emisor = reg.get('nombre_emisor', 'N/A')[:40]
                tipo = reg.get('tipo_documento', '')
                fecha = reg.get('fecha_emision', '')
                prefijo = reg.get('prefijo', '')
                folio = reg.get('folio', '')
                print(f"  {i+1}. {emisor:40} | {tipo:30} | {fecha} | {prefijo}-{folio}")
            
            print(f"\n✅ ¡ÉXITO! El visor ahora debería mostrar los registros de 2026")
        else:
            print(f"\n⚠️  Todavía devuelve 0 registros")
            print(f"   Verifica que el servidor se haya reiniciado correctamente")
    else:
        print(f"\n❌ Error HTTP {response.status_code}")
    
    print("\n" + "=" * 80)
    print("💡 RECARGA EL VISOR:")
    print("   1. Ctrl+F5 en el navegador")
    print("   2. Fechas: 01/02/2026 - 28/02/2026")
    print("   3. Click 'Buscar'")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
