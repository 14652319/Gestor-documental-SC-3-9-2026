"""
🔥 Script SIMPLIFICADO para finalizar lote RFD especificando IDs de facturas

USO:
    python finalizar_lote_ids.py 13 14
    (Asignará mismo RFD a facturas 13 y 14, y enviará un solo correo)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, db, Usuario
from modules.facturas_digitales.models import FacturaDigital
from modules.facturas_digitales.routes import generar_radicado_rfd, enviar_correo_radicacion_lote

def main():
    if len(sys.argv) < 2:
        print("❌ ERROR: Debes especificar al menos una ID de factura")
        print("USO: python finalizar_lote_ids.py 13 14")
        return
    
    # Obtener IDs de facturas desde argumentos
    ids_facturas = [int(id_str) for id_str in sys.argv[1:]]
    
    with app.app_context():
        print("\n" + "="*70)
        print("🔥 FINALIZACIÓN DE LOTE RFD POR IDs")
        print("="*70)
        
        print(f"\n📋 IDs de facturas a radicar: {ids_facturas}")
        
        # 1. Buscar las facturas
        facturas = FacturaDigital.query.filter(
            FacturaDigital.id.in_(ids_facturas)
        ).all()
        
        if not facturas:
            print("❌ No se encontraron facturas con esos IDs")
            return
        
        if len(facturas) != len(ids_facturas):
            print(f"⚠️  ADVERTENCIA: Se encontraron {len(facturas)} facturas de {len(ids_facturas)} solicitadas")
        
        print(f"\n✅ Encontradas {len(facturas)} factura(s):")
        for idx, factura in enumerate(facturas, start=1):
            print(f"  {idx}. ID:{factura.id} | {factura.numero_factura} | {factura.razon_social_proveedor}")
            print(f"      Valor: ${factura.valor_total:,.2f} | Usuario: {factura.usuario_carga}")
            if factura.radicado_rfd:
                print(f"      ⚠️  YA TIENE RADICADO: {factura.radicado_rfd}")
        
        # 2. Generar RFD
        print(f"\n🔢 Generando RFD para el lote...")
        radicado_rfd = generar_radicado_rfd()
        print(f"✅ RFD generado: {radicado_rfd}")
        
        # 3. Asignar RFD a todas las facturas
        print(f"\n🏷️  Asignando {radicado_rfd} a {len(facturas)} factura(s)...")
        
        facturas_data = []
        for factura in facturas:
            factura.radicado_rfd = radicado_rfd
            
            facturas_data.append({
                'numero_factura': factura.numero_factura,
                'nit_proveedor': factura.nit_proveedor,
                'razon_social': factura.razon_social_proveedor,
                'valor_total': float(factura.valor_total),
                'fecha_emision': factura.fecha_emision.strftime('%d/%m/%Y') if factura.fecha_emision else 'N/A'
            })
            
            print(f"  ✅ {factura.numero_factura} → {radicado_rfd}")
        
        db.session.commit()
        print("\n💾 Cambios guardados en BD")
        
        # 4. Enviar correo consolidado
        print("\n📧 Enviando correo consolidado...")
        
        # Obtener usuario de la primera factura
        usuario_carga = facturas[0].usuario_carga
        usuario_obj = Usuario.query.filter_by(usuario=usuario_carga).first()
        
        if not usuario_obj or not usuario_obj.correo:
            print(f"❌ Usuario sin correo electrónico configurado: {usuario_carga}")
            return
        
        print(f"   Destinatario: {usuario_obj.correo}")
        print(f"   Nombre: {usuario_obj.usuario}")
        print(f"   Facturas: {len(facturas_data)}")
        
        envio_exitoso = enviar_correo_radicacion_lote(
            usuario_email=usuario_obj.correo,
            usuario_nombre=usuario_obj.usuario,
            radicado_rfd=radicado_rfd,
            facturas_list=facturas_data
        )
        
        if envio_exitoso:
            print("✅ CORREO ENVIADO EXITOSAMENTE")
        else:
            print("❌ ERROR ENVIANDO CORREO (ver logs/security.log)")
        
        # 5. Resumen final
        print("\n" + "="*70)
        print("📊 RESUMEN FINAL")
        print("="*70)
        print(f"✅ Radicado generado: {radicado_rfd}")
        print(f"✅ Facturas radicadas: {len(facturas)}")
        print(f"✅ Correo enviado: {'Sí' if envio_exitoso else 'No'}")
        
        valor_total = sum(f['valor_total'] for f in facturas_data)
        print(f"💰 Valor total del lote: ${valor_total:,.2f}")
        
        print("\n📋 Facturas incluidas en el correo:")
        for idx, f in enumerate(facturas_data, start=1):
            print(f"  {idx}. {f['numero_factura']} | {f['nit_proveedor']} | {f['razon_social']}")
            print(f"      Valor: ${f['valor_total']:,.2f} | Fecha: {f['fecha_emision']}")
        
        print("\n🎉 FINALIZACIÓN DE LOTE COMPLETADA")
        print(f"📧 Revisa el correo: {usuario_obj.correo}")
        print("="*70 + "\n")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
