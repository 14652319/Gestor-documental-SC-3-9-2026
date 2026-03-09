"""
📧 Script para enviar correo de prueba del sistema de lotes RFD

Este script simula el envío de correo para las 2 últimas facturas
radicadas juntas bajo el mismo RFD.

USO:
    python enviar_correo_prueba_lote.py
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
        print("📧 ENVÍO DE CORREO DE PRUEBA - SISTEMA DE LOTES RFD")
        print("="*70)
        
        # Obtener las 2 facturas con RFD-000005
        facturas = FacturaDigital.query.filter_by(radicado_rfd='RFD-000005').all()
        
        if not facturas:
            print("❌ No se encontraron facturas con RFD-000005")
            print("   Ejecuta primero: python finalizar_lote_ids.py 13 14")
            return
        
        print(f"\n📋 Encontradas {len(facturas)} factura(s) con RFD-000005:")
        for idx, factura in enumerate(facturas, start=1):
            print(f"  {idx}. ID:{factura.id} | {factura.numero_factura} | {factura.razon_social_proveedor}")
            print(f"      Valor: ${factura.valor_total:,.2f} | Fecha: {factura.fecha_emision}")
        
        # Obtener usuario
        usuario_carga = facturas[0].usuario_carga
        usuario_obj = Usuario.query.filter_by(usuario=usuario_carga).first()
        
        if not usuario_obj or not usuario_obj.correo:
            print(f"\n❌ Usuario {usuario_carga} sin correo configurado")
            return
        
        print(f"\n📧 Destinatario:")
        print(f"   Email: {usuario_obj.correo}")
        print(f"   Nombre: {usuario_obj.usuario}")
        
        # Preparar datos para el correo
        facturas_data = []
        for factura in facturas:
            facturas_data.append({
                'numero_factura': factura.numero_factura,
                'nit_proveedor': factura.nit_proveedor,
                'razon_social': factura.razon_social_proveedor,
                'valor_total': float(factura.valor_total),
                'fecha_emision': factura.fecha_emision.strftime('%d/%m/%Y') if factura.fecha_emision else 'N/A'
            })
        
        valor_total = sum(f['valor_total'] for f in facturas_data)
        
        print(f"\n📊 Resumen del correo:")
        print(f"   Radicado: RFD-000005")
        print(f"   Facturas: {len(facturas_data)}")
        print(f"   Valor total: ${valor_total:,.2f}")
        
        print("\n📋 Facturas incluidas:")
        for idx, f in enumerate(facturas_data, start=1):
            print(f"  {idx}. {f['numero_factura']} | NIT:{f['nit_proveedor']} | {f['razon_social']}")
            print(f"      ${f['valor_total']:,.2f} | {f['fecha_emision']}")
        
        print("\n" + "⚠️ "*25)
        respuesta = input("¿Enviar correo de prueba? (S/N): ").strip().upper()
        
        if respuesta != 'S':
            print("❌ Envío cancelado")
            return
        
        print("\n📧 Enviando correo consolidado...")
        
        # Enviar correo
        envio_exitoso = enviar_correo_radicacion_lote(
            usuario_email=usuario_obj.correo,
            usuario_nombre=usuario_obj.usuario,
            radicado_rfd='RFD-000005',
            facturas_list=facturas_data
        )
        
        if envio_exitoso:
            print("\n" + "="*70)
            print("✅ CORREO ENVIADO EXITOSAMENTE")
            print("="*70)
            print(f"\n📧 Destinatario: {usuario_obj.correo}")
            print(f"📋 Asunto: ✅ Radicación Exitosa - {len(facturas_data)} Factura(s) Digital(es) - RFD-000005")
            print(f"📊 Contenido:")
            print(f"   - Tabla horizontal con {len(facturas_data)} facturas")
            print(f"   - Headers: # | Factura | NIT | Razón Social | Valor | Fecha")
            print(f"   - Valor total: ${valor_total:,.2f}")
            print("\n💡 Revisa tu bandeja de entrada (y carpeta SPAM si no aparece)")
            print("="*70 + "\n")
        else:
            print("\n❌ ERROR AL ENVIAR CORREO")
            print("   Revisa logs/security.log para más detalles")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
