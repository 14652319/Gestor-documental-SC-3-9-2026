"""
Verificar qué devuelve el API para la factura 805003786-LF-29065
"""
import requests
import json

# Datos de búsqueda
NIT = "805003786"
PREFIJO = "LF"
FOLIO = "29065"

print("\n" + "="*80)
print(f"🔍 VERIFICANDO API PARA: NIT={NIT} | PREFIJO={PREFIJO} | FOLIO={FOLIO}")
print("="*80)

# 1. Consultar API de DIAN
print("\n📡 1. CONSULTANDO API /dian_vs_erp/api/dian")
print("-" * 80)

try:
    url = "http://127.0.0.1:8099/dian_vs_erp/api/dian"
    params = {
        'fecha_inicial': '2025-12-18',
        'fecha_final': '2025-12-28',
        'buscar': FOLIO  # Buscar por folio
    }
    
    response = requests.get(url, params=params, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Buscar la factura específica
        factura_encontrada = None
        for doc in data.get('datos', []):
            if (doc.get('nit_emisor') == NIT and 
                doc.get('prefijo') == PREFIJO and 
                str(doc.get('folio')) == FOLIO):
                factura_encontrada = doc
                break
        
        if factura_encontrada:
            print("\n✅ FACTURA ENCONTRADA EN API:")
            print(f"   📊 Estado Contable: {factura_encontrada.get('estado_contable')}")
            print(f"   ⚠️ Estado Aprobación: {factura_encontrada.get('estado_aprobacion')}")
            print(f"   🔄 Recibida: {factura_encontrada.get('recibida')}")
            print(f"   🔄 Causada: {factura_encontrada.get('causada')}")
            print(f"   📝 Tipo Documento: {factura_encontrada.get('tipo_documento')}")
            print(f"   💰 Valor: ${factura_encontrada.get('valor'):,.2f}" if factura_encontrada.get('valor') else "   💰 Valor: N/A")
            print(f"   📅 Fecha Emisión: {factura_encontrada.get('fecha_emision')}")
            print(f"   👤 Usuario Recibió: {factura_encontrada.get('usuario_recibio')}")
            
            print(f"\n📋 DATOS COMPLETOS DEL DOCUMENTO:")
            print(json.dumps(factura_encontrada, indent=2, ensure_ascii=False))
        else:
            print("\n❌ FACTURA NO ENCONTRADA EN LA RESPUESTA DEL API")
            print(f"\nTotal de documentos retornados: {len(data.get('datos', []))}")
            
            # Mostrar algunos documentos para debug
            if data.get('datos'):
                print(f"\nPrimeros 3 documentos retornados:")
                for idx, doc in enumerate(data['datos'][:3], 1):
                    print(f"\n{idx}. {doc.get('nit_emisor')}-{doc.get('prefijo')}-{doc.get('folio')} | Estado: {doc.get('estado_contable')}")
    else:
        print(f"❌ ERROR: Status {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ ERROR EN PETICIÓN: {str(e)}")

# 2. Consultar directamente a la base de datos
print("\n" + "="*80)
print("📊 2. CONSULTANDO DIRECTAMENTE EN BASE DE DATOS")
print("="*80)

from app import app, db
from modules.dian_vs_erp.models import MaestroDianVsErp

with app.app_context():
    factura = MaestroDianVsErp.query.filter_by(
        nit_emisor=NIT,
        prefijo=PREFIJO,
        folio=FOLIO
    ).first()
    
    if factura:
        print(f"\n✅ FACTURA EN BASE DE DATOS:")
        print(f"   ID: {factura.id}")
        print(f"   📊 Estado Contable: '{factura.estado_contable}'")
        print(f"   ⚠️ Estado Aprobación: '{factura.estado_aprobacion}'")
        print(f"   🔄 Recibida: {factura.recibida}")
        print(f"   🔄 Causada: {factura.causada}")
        print(f"   🔄 Rechazada: {factura.rechazada}")
        print(f"   📝 Tipo Documento: '{factura.tipo_documento}'")
        print(f"   💰 Valor: ${factura.valor:,.2f}" if factura.valor else "   💰 Valor: N/A")
        print(f"   📅 Fecha Emisión: {factura.fecha_emision}")
        print(f"   👤 Usuario Recibió: '{factura.usuario_recibio}'")
        print(f"   📌 Origen Sync: '{factura.origen_sincronizacion}'")
        
        print(f"\n🔍 COMPARACIÓN:")
        print(f"   Base de Datos dice: '{factura.estado_contable}'")
        print(f"   ¿Es None?: {factura.estado_contable is None}")
        print(f"   ¿Es vacío?: {factura.estado_contable == ''}")
        print(f"   Longitud: {len(factura.estado_contable) if factura.estado_contable else 0}")
        print(f"   Repr: {repr(factura.estado_contable)}")
    else:
        print("\n❌ FACTURA NO ENCONTRADA EN BASE DE DATOS")

print("\n" + "="*80)
