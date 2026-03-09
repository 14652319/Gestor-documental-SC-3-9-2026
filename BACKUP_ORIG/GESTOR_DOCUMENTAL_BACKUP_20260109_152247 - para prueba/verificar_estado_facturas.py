"""
Verificar estado de las 2 facturas problemáticas
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from modules.recibir_facturas.models import FacturaTemporal, FacturaRecibida
from modules.dian_vs_erp.models import MaestroDianVsErp
from datetime import datetime

def verificar_factura(nit, prefijo, folio, nombre):
    """Verifica una factura en las 3 tablas"""
    print(f"\n{'='*80}")
    print(f"🔍 VERIFICANDO: {nombre}")
    print(f"   NIT: {nit} | Prefijo: {prefijo} | Folio: {folio}")
    print(f"{'='*80}")
    
    # 1. Verificar en TEMPORALES
    print("\n1️⃣ TABLA: facturas_temporales")
    temp = FacturaTemporal.query.filter_by(
        nit=nit,
        prefijo=prefijo,
        folio=folio
    ).first()
    
    if temp:
        print(f"   ✅ ENCONTRADA EN TEMPORALES")
        print(f"      ID: {temp.id}")
        print(f"      Razón Social: {temp.razon_social}")
        print(f"      Valor: ${temp.valor_neto:,.2f}")
        print(f"      Fecha Expedición: {temp.fecha_expedicion}")
    else:
        print(f"   ❌ NO ESTÁ EN TEMPORALES (ya se movió o se eliminó)")
    
    # 2. Verificar en RECIBIDAS
    print("\n2️⃣ TABLA: facturas_recibidas")
    recibida = FacturaRecibida.query.filter_by(
        nit=nit,
        prefijo=prefijo,
        folio=folio
    ).first()
    
    if recibida:
        print(f"   ✅ ENCONTRADA EN RECIBIDAS")
        print(f"      ID: {recibida.id}")
        print(f"      Razón Social: {recibida.razon_social}")
        print(f"      Valor: ${recibida.valor_neto:,.2f}")
        print(f"      Fecha Radicación: {recibida.fecha_radicacion}")
        print(f"      Usuario: {recibida.usuario_solicita}")
    else:
        print(f"   ❌ NO ESTÁ EN RECIBIDAS")
    
    # 3. Verificar en MAESTRO DIAN
    print("\n3️⃣ TABLA: maestro_dian_vs_erp")
    
    # Normalizar folio a 8 dígitos para maestro
    folio_8 = folio.zfill(8) if folio else None
    
    # Buscar con prefijo completo
    maestro1 = MaestroDianVsErp.query.filter_by(
        nit_emisor=nit,
        prefijo=prefijo,
        folio=folio_8
    ).first()
    
    # Buscar sin primer dígito del prefijo (ej: ME40 -> E40)
    prefijo_sin_primer_digito = prefijo[1:] if prefijo and len(prefijo) > 1 else None
    maestro2 = None
    if prefijo_sin_primer_digito:
        maestro2 = MaestroDianVsErp.query.filter_by(
            nit_emisor=nit,
            prefijo=prefijo_sin_primer_digito,
            folio=folio_8
        ).first()
    
    maestro = maestro1 or maestro2
    
    if maestro:
        print(f"   ✅ ENCONTRADA EN MAESTRO DIAN")
        print(f"      ID: {maestro.id}")
        print(f"      Prefijo usado: {maestro.prefijo}")
        print(f"      Folio: {maestro.folio}")
        print(f"      Estado Contable: {maestro.estado_contable}")
        print(f"      Recibida: {'✅ SÍ' if maestro.recibida else '❌ NO'}")
        print(f"      Fecha Recibida: {maestro.fecha_recibida}")
        print(f"      Usuario Recibió: {maestro.usuario_recibio}")
        print(f"      Origen Sincronización: {maestro.origen_sincronizacion}")
    else:
        print(f"   ❌ NO ESTÁ EN MAESTRO DIAN")
        print(f"      (Buscado con prefijo='{prefijo}' y prefijo='{prefijo_sin_primer_digito}')")
    
    # RESUMEN
    print(f"\n📊 RESUMEN:")
    estado = []
    if temp:
        estado.append("EN TEMPORALES ⏳")
    if recibida:
        estado.append("EN RECIBIDAS ✅")
    if maestro:
        estado.append("EN MAESTRO ✅")
    
    if not estado:
        print(f"   ⚠️ NO ENCONTRADA EN NINGUNA TABLA")
    else:
        print(f"   {' | '.join(estado)}")
    
    return {
        'temporal': temp,
        'recibida': recibida,
        'maestro': maestro
    }

if __name__ == '__main__':
    with app.app_context():
        print("\n" + "="*80)
        print("🔍 DIAGNÓSTICO DE FACTURAS")
        print("="*80)
        
        # Factura 1: BIMBO (la que NO se guardó)
        resultado1 = verificar_factura(
            nit='830002366',
            prefijo='ME40',
            folio='772863',
            nombre='BIMBO DE COLOMBIA S.A (PROBLEMA)'
        )
        
        # Factura 2: GALERÍA LALA (la que SÍ se guardó)
        resultado2 = verificar_factura(
            nit='805013653',
            prefijo='1FEA',
            folio='77',
            nombre='GALERÍA LALA (FUNCIONÓ)'
        )
        
        print("\n" + "="*80)
        print("📋 CONCLUSIONES")
        print("="*80)
        
        if resultado1['temporal'] and not resultado1['recibida']:
            print("⚠️ FACTURA BIMBO: Quedó en temporales, NO se guardó")
            print("   Posible causa: Error durante el guardado masivo")
        
        if resultado2['recibida']:
            print("✅ FACTURA GALERÍA: Se guardó correctamente")
        
        # Contar cuántas temporales hay en total
        print("\n📊 ESTADÍSTICAS:")
        total_temp = FacturaTemporal.query.count()
        print(f"   Total facturas en temporales: {total_temp}")
        
        if total_temp > 0:
            print(f"\n   Las {total_temp} facturas en temporales son:")
            temporales = FacturaTemporal.query.all()
            for t in temporales:
                print(f"      - {t.nit} | {t.prefijo}-{t.folio} | {t.razon_social} | ${t.valor_neto:,.2f}")
