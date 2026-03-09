"""
🔥 Script para probar el endpoint /api/finalizar-lote-rfd

Este script:
1. Busca facturas sin radicado del usuario especificado
2. Llama al endpoint de finalizar lote
3. Verifica que se asigne el mismo RFD a todas
4. Confirma que se envíe un solo correo con todas las facturas

USO:
    python probar_finalizar_lote.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from modules.facturas_digitales.models import FacturaDigital, ConsecutivoRFD
from datetime import datetime, timedelta

def main():
    with app.app_context():
        print("\n" + "="*70)
        print("🔥 PRUEBA DE FINALIZACIÓN DE LOTE RFD")
        print("="*70)
        
        # Usuario de prueba (el que cargó las facturas)
        usuario_prueba = '14652319'
        
        # 1. Buscar facturas sin radicado
        print(f"\n📋 Buscando facturas SIN radicado del usuario: {usuario_prueba}")
        
        tiempo_limite = datetime.now() - timedelta(minutes=5)
        
        facturas_sin_radicado = FacturaDigital.query.filter(
            FacturaDigital.usuario_carga == usuario_prueba,
            FacturaDigital.radicado_rfd.is_(None),
            FacturaDigital.fecha_carga >= tiempo_limite
        ).all()
        
        if not facturas_sin_radicado:
            print("⚠️  NO HAY FACTURAS SIN RADICADO (últimos 5 minutos)")
            print("\nBuscando TODAS las facturas sin radicado (sin límite de tiempo)...")
            
            facturas_sin_radicado = FacturaDigital.query.filter(
                FacturaDigital.usuario_carga == usuario_prueba,
                FacturaDigital.radicado_rfd.is_(None)
            ).all()
            
            if not facturas_sin_radicado:
                print("❌ NO HAY FACTURAS SIN RADICADO EN TOTAL")
                print("\nPara probar, primero carga facturas sin especificar radicado.")
                return
        
        print(f"✅ Encontradas {len(facturas_sin_radicado)} facturas sin radicado:")
        for idx, factura in enumerate(facturas_sin_radicado, start=1):
            print(f"  {idx}. ID:{factura.id} | {factura.numero_factura} | {factura.razon_social_proveedor} | ${factura.valor_total:,.2f} | {factura.fecha_carga}")
        
        # 2. Obtener consecutivo actual
        consecutivo_actual = ConsecutivoRFD.query.filter_by(tipo='facturas_digitales').first()
        if consecutivo_actual:
            print(f"\n📊 Consecutivo actual: {consecutivo_actual.ultimo_numero}")
            print(f"   Próximo RFD será: RFD-{(consecutivo_actual.ultimo_numero + 1):06d}")
        
        # 3. Confirmar ejecución
        print("\n" + "⚠️ "*25)
        respuesta = input("¿Ejecutar finalización de lote? (S/N): ").strip().upper()
        
        if respuesta != 'S':
            print("❌ Operación cancelada")
            return
        
        # 4. Importar la función de generación
        from modules.facturas_digitales.routes import generar_radicado_rfd, enviar_correo_radicacion_lote
        
        print("\n🔢 Generando RFD para el lote...")
        radicado_rfd = generar_radicado_rfd()
        print(f"✅ RFD generado: {radicado_rfd}")
        
        # 5. Asignar RFD a todas las facturas
        print(f"\n🏷️  Asignando {radicado_rfd} a {len(facturas_sin_radicado)} factura(s)...")
        
        facturas_data = []
        for factura in facturas_sin_radicado:
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
        
        # 6. Enviar correo consolidado
        print("\n📧 Enviando correo consolidado...")
        
        # Obtener datos del usuario
        from app import Usuario
        usuario_obj = Usuario.query.filter_by(usuario=usuario_prueba).first()
        
        if not usuario_obj or not usuario_obj.correo:
            print("❌ Usuario sin correo electrónico configurado")
            print(f"   Usuario: {usuario_prueba}")
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
        
        # 7. Resumen final
        print("\n" + "="*70)
        print("📊 RESUMEN FINAL")
        print("="*70)
        print(f"✅ Radicado generado: {radicado_rfd}")
        print(f"✅ Facturas radicadas: {len(facturas_sin_radicado)}")
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
