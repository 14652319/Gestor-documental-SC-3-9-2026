"""
Verificar qué datos tiene la factura 1FEA-77 en el maestro
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from modules.dian_vs_erp.models import MaestroDianVsErp

if __name__ == '__main__':
    with app.app_context():
        print("\n" + "="*80)
        print("🔍 VERIFICANDO DATOS DE FACTURA 1FEA-77")
        print("="*80)
        
        factura = MaestroDianVsErp.query.filter_by(
            nit_emisor='805013653',
            prefijo='1FEA',
            folio='77'
        ).first()
        
        if factura:
            print(f"\n📋 TODOS LOS CAMPOS:")
            print(f"   ID: {factura.id}")
            print(f"   NIT Emisor: {factura.nit_emisor}")
            print(f"   Razón Social: {factura.razon_social}")
            print(f"   Prefijo: {factura.prefijo}")
            print(f"   Folio: {factura.folio}")
            print(f"   Tipo Documento: {factura.tipo_documento}")
            print(f"   Tipo Tercero: {factura.tipo_tercero}")
            print(f"   Fecha Emisión: {factura.fecha_emision}")
            print(f"   Valor: {factura.valor}")
            print(f"   Estado Contable: {factura.estado_contable}")
            print(f"   Estado Aprobación: {factura.estado_aprobacion}")
            print(f"   Recibida: {'✅ SÍ' if factura.recibida else '❌ NO'}")
            print(f"   Fecha Recibida: {factura.fecha_recibida}")
            print(f"   Usuario Recibió: {factura.usuario_recibio}")
            print(f"   Origen Sincronización: {factura.origen_sincronizacion}")
            
            # Verificar si se perdieron datos
            print(f"\n⚠️ VERIFICACIÓN DE DATOS:")
            if not factura.tipo_documento:
                print(f"   ❌ FALTA tipo_documento")
            else:
                print(f"   ✅ tipo_documento: {factura.tipo_documento}")
            
            if not factura.tipo_tercero:
                print(f"   ❌ FALTA tipo_tercero")
            else:
                print(f"   ✅ tipo_tercero: {factura.tipo_tercero}")
            
            if not factura.valor:
                print(f"   ❌ FALTA valor")
            else:
                print(f"   ✅ valor: ${float(factura.valor):,.2f}")
        else:
            print("❌ Factura NO encontrada")
