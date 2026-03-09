"""
Consultar API de DIAN directamente
"""
import requests
import json

# Datos de búsqueda
NIT = "805003786"
PREFIJO = "LF"
FOLIO = "29065"

print("\n" + "="*80)
print(f"🔍 CONSULTANDO API: NIT={NIT} | PREFIJO={PREFIJO} | FOLIO={FOLIO}")
print("="*80)

try:
    # Consultar API con filtro de búsqueda
    url = "http://127.0.0.1:8099/dian_vs_erp/api/dian"
    params = {
        'fecha_inicial': '2025-12-01',
        'fecha_final': '2025-12-31',
        'buscar': FOLIO
    }
    
    print(f"\n📡 Consultando: {url}")
    print(f"   Parámetros: {params}")
    
    response = requests.get(url, params=params, timeout=30)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        total = len(data.get('datos', []))
        
        print(f"Total de documentos retornados: {total}")
        
        # Buscar la factura específica
        factura_encontrada = None
        for doc in data.get('datos', []):
            if (doc.get('nit_emisor') == NIT and 
                doc.get('prefijo') == PREFIJO and 
                str(doc.get('folio')) == FOLIO):
                factura_encontrada = doc
                break
        
        if factura_encontrada:
            print("\n" + "="*80)
            print("✅ FACTURA ENCONTRADA EN LA RESPUESTA DEL API")
            print("="*80)
            
            print(f"\n📊 ESTADO CONTABLE: '{factura_encontrada.get('estado_contable')}'")
            print(f"⚠️ Estado Aprobación: '{factura_encontrada.get('estado_aprobacion')}'")
            
            print(f"\n🔄 FLAGS:")
            print(f"   Recibida: {factura_encontrada.get('recibida')}")
            print(f"   Causada: {factura_encontrada.get('causada')}")
            print(f"   Rechazada: {factura_encontrada.get('rechazada')}")
            
            print(f"\n💰 DATOS FINANCIEROS:")
            print(f"   Valor: ${factura_encontrada.get('valor'):,.2f}" if factura_encontrada.get('valor') else "   Valor: N/A")
            print(f"   Forma Pago: {factura_encontrada.get('forma_pago')}")
            
            print(f"\n📅 FECHAS:")
            print(f"   Fecha Emisión: {factura_encontrada.get('fecha_emision')}")
            print(f"   Fecha Recibida: {factura_encontrada.get('fecha_recibida')}")
            
            print(f"\n👤 USUARIOS:")
            print(f"   Usuario Recibió: '{factura_encontrada.get('usuario_recibio')}'")
            
            print(f"\n📝 OTROS:")
            print(f"   Tipo Documento: '{factura_encontrada.get('tipo_documento')}'")
            print(f"   Tipo Tercero: '{factura_encontrada.get('tipo_tercero')}'")
            print(f"   Razón Social: {factura_encontrada.get('razon_social')}")
            
            print(f"\n🔍 ANÁLISIS CRÍTICO:")
            estado = factura_encontrada.get('estado_contable')
            print(f"   Estado Contable API: '{estado}'")
            print(f"   Tipo: {type(estado)}")
            print(f"   ¿Es None?: {estado is None}")
            print(f"   ¿Es vacío?: {estado == ''}")
            
            # Si el estado es "No Registrada" pero los flags dicen otra cosa
            if estado == "No Registrada":
                print(f"\n⚠️⚠️⚠️ INCONSISTENCIA DETECTADA:")
                print(f"   Estado Contable dice: 'No Registrada'")
                print(f"   Pero flag recibida={factura_encontrada.get('recibida')}")
                print(f"   Y flag causada={factura_encontrada.get('causada')}")
                
                if factura_encontrada.get('recibida'):
                    print(f"\n   🔴 PROBLEMA: Debería estar como 'Recibida' no 'No Registrada'")
                if factura_encontrada.get('causada'):
                    print(f"   🔴 PROBLEMA: Debería estar como 'Causada' no 'No Registrada'")
            
            print(f"\n📋 DOCUMENTO COMPLETO (JSON):")
            print("-" * 80)
            print(json.dumps(factura_encontrada, indent=2, ensure_ascii=False))
            
        else:
            print("\n" + "="*80)
            print("❌ FACTURA NO ENCONTRADA EN LA RESPUESTA DEL API")
            print("="*80)
            
            # Mostrar algunos documentos para debug
            if total > 0:
                print(f"\n📋 Primeros 5 documentos retornados (para debug):")
                for idx, doc in enumerate(data['datos'][:5], 1):
                    print(f"\n{idx}. {doc.get('nit_emisor')}-{doc.get('prefijo')}-{doc.get('folio')}")
                    print(f"   Razón Social: {doc.get('razon_social')}")
                    print(f"   Estado: {doc.get('estado_contable')}")
    else:
        print(f"\n❌ ERROR del servidor: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except requests.exceptions.RequestException as e:
    print(f"\n❌ ERROR DE CONEXIÓN: {str(e)}")
    print("\n💡 Asegúrate de que el servidor Flask esté corriendo en http://127.0.0.1:8099")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80 + "\n")
