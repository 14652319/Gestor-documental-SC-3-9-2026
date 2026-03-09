"""
Buscar directamente en maestro con normalización
"""
from extensions import db
from modules.dian_vs_erp.models import MaestroDianVsErp
from dotenv import load_dotenv
from app import app

load_dotenv()

print("=" * 100)
print("BÚSQUEDA DIRECTA EN MAESTRO_DIAN_VS_ERP")
print("=" * 100)

with app.app_context():
    # Buscar con diferentes variaciones del prefijo
    variaciones = [
        ('805013653', '1FEA', '00000077'),
        ('805013653', 'FEA', '00000077'),
        ('805013653', '1FEA', '77'),
        ('805013653', 'FEA', '77'),
    ]
    
    for nit, prefijo, folio in variaciones:
        print(f"\n🔍 Buscando: NIT={nit} | PREFIJO={prefijo} | FOLIO={folio}")
        
        factura = MaestroDianVsErp.query.filter_by(
            nit_emisor=nit,
            prefijo=prefijo,
            folio=folio
        ).first()
        
        if factura:
            print(f"   ✅ ENCONTRADA!")
            print(f"      ID: {factura.id}")
            print(f"      Estado Contable: {factura.estado_contable}")
            print(f"      Recibida: {factura.recibida}")
            print(f"      Usuario Recibió: {factura.usuario_recibio}")
            print(f"      Origen Sincronización: {factura.origen_sincronizacion}")
            print(f"      Fecha Emisión: {factura.fecha_emision}")
            print(f"      Valor: ${factura.valor:,.0f}")
            break
    else:
        print("\n❌ NO encontrada con ninguna variación")
        
        # Buscar cualquier factura de ese NIT
        print(f"\n📊 Otras facturas del NIT {variaciones[0][0]}:")
        facturas_nit = MaestroDianVsErp.query.filter_by(
            nit_emisor=variaciones[0][0]
        ).limit(5).all()
        
        for f in facturas_nit:
            print(f"   • {f.prefijo}-{f.folio} | Estado: {f.estado_contable}")

print("\n" + "=" * 100)
