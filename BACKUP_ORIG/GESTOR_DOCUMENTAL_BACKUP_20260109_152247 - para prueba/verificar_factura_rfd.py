"""
Script para verificar si la factura FE-456 tiene radicado RFD
"""
from app import app, db
from modules.facturas_digitales.models import FacturaDigital

with app.app_context():
    factura = FacturaDigital.query.filter_by(
        numero_factura='FE-456',
        nit_proveedor='14652319'
    ).first()
    
    if factura:
        print("=" * 80)
        print("✅ FACTURA ENCONTRADA")
        print("=" * 80)
        print(f"ID: {factura.id}")
        print(f"Número: {factura.numero_factura}")
        print(f"NIT: {factura.nit_proveedor}")
        print(f"Radicado RFD: {factura.radicado_rfd or 'SIN RADICADO ❌'}")
        print(f"Usuario que cargó: {factura.usuario_carga}")
        print(f"Fecha de carga: {factura.fecha_carga}")
        print(f"Estado: {factura.estado}")
        print("=" * 80)
    else:
        print("❌ FACTURA NO ENCONTRADA")
        print("Buscando facturas recientes del NIT 14652319...")
        facturas = FacturaDigital.query.filter_by(nit_proveedor='14652319').order_by(FacturaDigital.fecha_carga.desc()).limit(5).all()
        if facturas:
            print(f"\n📋 Últimas {len(facturas)} facturas del NIT 14652319:")
            for f in facturas:
                print(f"  - {f.numero_factura} | Radicado: {f.radicado_rfd or 'SIN RADICADO'} | Fecha: {f.fecha_carga}")
