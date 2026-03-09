"""
Buscar facturas en maestro con todas las variantes de prefijo
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from modules.dian_vs_erp.models import MaestroDianVsErp

def buscar_con_variantes(nit, prefijos_posibles, folio, nombre):
    """Busca una factura con todas las variantes de prefijo"""
    print(f"\n{'='*80}")
    print(f"🔍 BUSCANDO: {nombre}")
    print(f"   NIT: {nit} | Folios a buscar: {folio}, {folio.zfill(8)}")
    print(f"{'='*80}")
    
    # Normalizar folio a diferentes formatos
    folio_sin_ceros = folio.lstrip('0') or '0'
    folio_8_digitos = folio.zfill(8)
    
    folios_a_probar = [folio, folio_sin_ceros, folio_8_digitos]
    
    encontrada = False
    
    for prefijo_test in prefijos_posibles:
        for folio_test in folios_a_probar:
            resultado = MaestroDianVsErp.query.filter_by(
                nit_emisor=nit,
                prefijo=prefijo_test,
                folio=folio_test
            ).first()
            
            if resultado:
                print(f"\n   ✅ ENCONTRADA con:")
                print(f"      Prefijo en BD: '{resultado.prefijo}'")
                print(f"      Folio en BD: '{resultado.folio}'")
                print(f"      Estado Contable: {resultado.estado_contable}")
                print(f"      Recibida: {'✅ SÍ' if resultado.recibida else '❌ NO'}")
                print(f"      Fecha Recibida: {resultado.fecha_recibida}")
                print(f"      Usuario: {resultado.usuario_recibio}")
                print(f"      Origen: {resultado.origen_sincronizacion}")
                encontrada = True
                break
        if encontrada:
            break
    
    if not encontrada:
        print(f"\n   ❌ NO ENCONTRADA con ninguna variante")
        print(f"      Prefijos probados: {prefijos_posibles}")
        print(f"      Folios probados: {folios_a_probar}")
        
        # Buscar solo por NIT y folio (sin importar prefijo)
        print(f"\n   🔍 Buscando solo por NIT y folio...")
        resultados_nit = MaestroDianVsErp.query.filter(
            MaestroDianVsErp.nit_emisor == nit,
            MaestroDianVsErp.folio.in_(folios_a_probar)
        ).all()
        
        if resultados_nit:
            print(f"      ⚠️ Encontradas {len(resultados_nit)} facturas con ese NIT y folio:")
            for r in resultados_nit:
                print(f"         - Prefijo: '{r.prefijo}' | Folio: '{r.folio}' | Estado: {r.estado_contable}")
        else:
            print(f"      ❌ Tampoco hay facturas con ese NIT y folio en el maestro")

if __name__ == '__main__':
    with app.app_context():
        print("\n" + "="*80)
        print("🔍 BÚSQUEDA EXHAUSTIVA EN MAESTRO DIAN VS ERP")
        print("="*80)
        
        # Factura 1: BIMBO
        buscar_con_variantes(
            nit='830002366',
            prefijos_posibles=['ME40', 'E40', 'ME', 'M40', '40'],
            folio='772863',
            nombre='BIMBO - ME40-772863'
        )
        
        # Factura 2: GALERÍA
        buscar_con_variantes(
            nit='805013653',
            prefijos_posibles=['1FEA', 'FEA', 'FE', 'EA', 'A'],
            folio='77',
            nombre='GALERÍA - 1FEA-77'
        )
        
        print("\n" + "="*80)
        print("📊 CONCLUSIÓN")
        print("="*80)
        print("Si ninguna factura fue encontrada, significa que la sincronización")
        print("falló silenciosamente y NO se insertaron en el maestro.")
        print("="*80)
