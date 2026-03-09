"""
Script para listar TODAS las facturas temporales del NIT 900161900
"""
from app import app, db
from modules.recibir_facturas.models import FacturaTemporal

print("\n" + "="*80)
print("📋 FACTURAS TEMPORALES DEL NIT 900161900")
print("="*80)

with app.app_context():
    nit = "900161900"
    
    facturas = FacturaTemporal.query.filter_by(nit=nit).all()
    
    print(f"\n🔍 Total de facturas encontradas: {len(facturas)}")
    
    if facturas:
        print("\n" + "-"*80)
        for i, factura in enumerate(facturas, 1):
            print(f"\n{i}. Factura ID: {factura.id}")
            print(f"   NIT: {factura.nit}")
            print(f"   Prefijo: {factura.prefijo}")
            print(f"   Folio: {factura.folio}")
            print(f"   Clave: {factura.prefijo}-{factura.folio}")
            print(f"   Usuario: {factura.usuario_id}")
    else:
        print(f"\n❌ NO hay facturas temporales del NIT {nit}")
        print(f"   Esto significa que:")
        print(f"   • No se guardó la factura FE-8367")
        print(f"   • O se guardó con un NIT diferente")
        print(f"   • O se movió a facturas_recibidas")

print("\n" + "="*80 + "\n")
