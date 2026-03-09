"""
Script para verificar que el endpoint /api/dian retorna valores correctos
de estado_contable y estado_aprobacion para las facturas sincronizadas
"""
import requests
import json
from datetime import datetime

print("=" * 100)
print("🔍 VERIFICACIÓN DE API /dian_vs_erp/api/dian")
print("=" * 100)

# URL del endpoint
url = "http://127.0.0.1:8099/dian_vs_erp/api/dian"

# Parámetros de búsqueda (rango amplio para encontrar las facturas de prueba)
params = {
    'fecha_inicial': '2025-01-01',  # Rango amplio
    'fecha_final': datetime.now().strftime('%Y-%m-%d'),  # Hasta hoy
    'buscar': '',  # Sin filtro de búsqueda específico
    'page': 1,
    'size': 1000  # Suficiente para encontrar nuestras facturas
}

try:
    print(f"\n📡 Consultando: {url}")
    print(f"📅 Rango: {params['fecha_inicial']} a {params['fecha_final']}")
    
    # Hacer request
    response = requests.get(url, params=params, timeout=10)
    
    if response.status_code != 200:
        print(f"\n❌ ERROR: Status code {response.status_code}")
        print(f"Respuesta: {response.text}")
        exit(1)
    
    # Parsear JSON
    facturas = response.json()
    
    print(f"\n✅ Respuesta exitosa: {len(facturas)} facturas encontradas\n")
    
    # Buscar nuestras facturas de prueba
    facturas_prueba = [
        {"nit": "900108281", "prefijo": "ME40", "folio": "772863", "nombre": "BIMBO"},
        {"nit": "890900943", "prefijo": "1FEA", "folio": "77", "nombre": "GALERÍA"}
    ]
    
    encontradas = 0
    
    for prueba in facturas_prueba:
        print(f"\n{'=' * 80}")
        print(f"🔍 Buscando: {prueba['nombre']} ({prueba['nit']}-{prueba['prefijo']}-{prueba['folio']})")
        print('=' * 80)
        
        # Buscar en resultados
        factura_encontrada = None
        for f in facturas:
            nit_match = f.get('nit_emisor', '') == prueba['nit']
            prefijo_match = f.get('prefijo', '') == prueba['prefijo']
            folio_match = str(f.get('folio', '')) == prueba['folio']
            
            if nit_match and prefijo_match and folio_match:
                factura_encontrada = f
                break
        
        if not factura_encontrada:
            print(f"❌ NO ENCONTRADA en respuesta de API")
            continue
        
        encontradas += 1
        print(f"✅ ENCONTRADA en respuesta\n")
        
        # Mostrar campos clave
        campos_importantes = [
            ('nit_emisor', 'NIT Emisor'),
            ('nombre_emisor', 'Razón Social'),
            ('prefijo', 'Prefijo'),
            ('folio', 'Folio'),
            ('fecha_emision', 'Fecha Emisión'),
            ('tipo_documento', 'Tipo Documento'),
            ('tipo_tercero', 'Tipo Tercero'),
            ('valor', 'Valor'),
            ('estado_aprobacion', '🔑 Estado Aprobación'),
            ('estado_contable', '🔑 Estado Contable')
        ]
        
        print("📋 Datos retornados por API:")
        print("-" * 80)
        for campo, etiqueta in campos_importantes:
            valor = factura_encontrada.get(campo, 'N/A')
            
            # Formatear valor si es dinero
            if campo == 'valor' and isinstance(valor, (int, float)):
                valor = f"${valor:,.2f}"
            
            # Resaltar campos clave
            if '🔑' in etiqueta:
                print(f"  {etiqueta:.<30} {valor}")
            else:
                print(f"  {etiqueta:.<30} {valor}")
        
        # Validaciones específicas
        print("\n🔍 VALIDACIONES:")
        print("-" * 80)
        
        estado_contable = factura_encontrada.get('estado_contable', '')
        estado_aprobacion = factura_encontrada.get('estado_aprobacion', '')
        tipo_tercero = factura_encontrada.get('tipo_tercero', '')
        tipo_documento = factura_encontrada.get('tipo_documento', '')
        
        # Validar estado_contable
        if estado_contable == "Recibida":
            print("  ✅ estado_contable = 'Recibida' (CORRECTO - sincronizado)")
        elif estado_contable == "No Registrada":
            print("  ❌ estado_contable = 'No Registrada' (INCORRECTO - debería ser 'Recibida')")
        else:
            print(f"  ⚠️ estado_contable = '{estado_contable}' (valor inesperado)")
        
        # Validar estado_aprobacion (debe mantener valor del DIAN)
        if estado_aprobacion and estado_aprobacion != "Recibida":
            print(f"  ✅ estado_aprobacion = '{estado_aprobacion}' (CORRECTO - dato del DIAN preservado)")
        elif estado_aprobacion == "Recibida":
            print("  ❌ estado_aprobacion = 'Recibida' (INCORRECTO - debería tener valor del DIAN)")
        else:
            print(f"  ⚠️ estado_aprobacion = '{estado_aprobacion}' (verificar)")
        
        # Validar tipo_tercero
        if tipo_tercero:
            print(f"  ✅ tipo_tercero = '{tipo_tercero}' (CORRECTO - dato del DIAN preservado)")
        else:
            print("  ❌ tipo_tercero vacío (INCORRECTO - debería tener dato del DIAN)")
        
        # Validar tipo_documento
        if tipo_documento:
            print(f"  ✅ tipo_documento = '{tipo_documento}' (CORRECTO - dato del DIAN preservado)")
        else:
            print("  ❌ tipo_documento vacío (INCORRECTO - debería tener dato del DIAN)")

    # Resumen final
    print("\n" + "=" * 100)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 100)
    print(f"✅ Facturas encontradas en API: {encontradas}/{len(facturas_prueba)}")
    
    if encontradas == len(facturas_prueba):
        print("\n🎉 ÉXITO: Todas las facturas de prueba encontradas en la respuesta de API")
        print("\n💡 Ahora recarga la página en el navegador:")
        print("   http://127.0.0.1:8099/dian_vs_erp/")
        print("   Busca por NIT 900108281 (BIMBO) o 890900943 (GALERÍA)")
        print("\n🔎 Verifica que:")
        print("   • Columna 'Estado Aprobación' muestre valores del DIAN (Pendiente, Acuse Bien/Servicio, etc.)")
        print("   • Columna 'Estado Contable' muestre 'Recibida'")
        print("   • Columna 'Tipo Tercero' muestre valores del DIAN (Proveedor, Acreedor, etc.)")
        print("   • Columna 'Tipo Documento' muestre valores del DIAN")
    else:
        print(f"\n⚠️ ADVERTENCIA: Solo se encontraron {encontradas} de {len(facturas_prueba)} facturas")
        print("   Verifica que las facturas estén en el rango de fechas consultado")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 100)
