"""
📧 Script directo para enviar correo de prueba (SIN confirmación)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, db, Usuario
from modules.facturas_digitales.models import FacturaDigital
from modules.facturas_digitales.routes import enviar_correo_radicacion_lote

def main():
    with app.app_context():
        print("\n" + "="*70)
        print("📧 ENVIANDO CORREO DE PRUEBA...")
        print("="*70)
        
        # Obtener las 2 facturas con RFD-000005
        facturas = FacturaDigital.query.filter_by(radicado_rfd='RFD-000005').all()
        
        if not facturas:
            print("❌ No se encontraron facturas con RFD-000005")
            return
        
        print(f"\n✅ {len(facturas)} factura(s) encontradas:")
        for f in facturas:
            print(f"   - {f.numero_factura} | ${f.valor_total:,.2f}")
        
        # Obtener usuario
        usuario_obj = Usuario.query.filter_by(usuario=facturas[0].usuario_carga).first()
        
        if not usuario_obj:
            print("❌ Usuario no encontrado")
            return
        
        print(f"\n📧 Destinatario: {usuario_obj.correo}")
        
        # Preparar datos
        facturas_data = [{
            'numero_factura': f.numero_factura,
            'nit_proveedor': f.nit_proveedor,
            'razon_social': f.razon_social_proveedor,
            'valor_total': float(f.valor_total),
            'fecha_emision': f.fecha_emision.strftime('%d/%m/%Y') if f.fecha_emision else 'N/A'
        } for f in facturas]
        
        # Enviar
        print("\n📤 Enviando...")
        exito = enviar_correo_radicacion_lote(
            usuario_email=usuario_obj.correo,
            usuario_nombre=usuario_obj.usuario,
            radicado_rfd='RFD-000005',
            facturas_list=facturas_data
        )
        
        if exito:
            print("\n✅ CORREO ENVIADO EXITOSAMENTE")
            print(f"📧 Revisa: {usuario_obj.correo}")
            print("\n💡 El correo incluye:")
            print("   - Tabla horizontal con headers")
            print("   - 2 facturas listadas (FE-445 y FE-458)")
            print("   - Valor total: $100,000.00")
            print("="*70 + "\n")
        else:
            print("\n❌ ERROR al enviar correo")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
