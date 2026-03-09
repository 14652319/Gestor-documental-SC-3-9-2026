"""
Verificar si FE-83637 existe en DIAN
"""
from app import app, db
from modules.dian_vs_erp.models import Dian

print("\n" + "="*80)
print("🔍 VERIFICACIÓN DE FACTURA FE-83637 EN DIAN")
print("="*80)

with app.app_context():
    nit = "900161900"
    prefijo = "FE"
    folio = "83637"
    
    dian_registro = Dian.query.filter_by(
        nit_emisor=nit,
        prefijo=prefijo,
        folio=folio
    ).first()
    
    if dian_registro:
        print(f"\n✅ ENCONTRADA EN DIAN!")
        print(f"   ID: {dian_registro.id}")
        print(f"   NIT Emisor: {dian_registro.nit_emisor}")
        print(f"   Prefijo: {dian_registro.prefijo}")
        print(f"   Folio: {dian_registro.folio}")
        print(f"   Fecha Emisión: {dian_registro.fecha_emision}")
        
        print(f"\n✅ ESTA FACTURA DEBE APARECER EN EL VISOR V2")
        print(f"   Estado Contable: 'Recibida'")
        print(f"   Motivo: Está en DIAN y en facturas_temporales")
        
    else:
        print(f"\n❌ NO ENCONTRADA EN DIAN")
        print(f"\n💡 SOLUCIÓN:")
        print(f"   1. Busca el archivo Excel/CSV de DIAN que contiene esta factura")
        print(f"   2. Cárgalo usando el botón 'Cargar Datos' del visor")
        print(f"   3. Después de cargar, presiona 🔄 Sincronizar")
        print(f"   4. La factura aparecerá con estado 'Recibida'")

print("\n" + "="*80 + "\n")
