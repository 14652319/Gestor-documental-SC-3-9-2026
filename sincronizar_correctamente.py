"""
Sincronizar correctamente las facturas BIMBO y GALERÍA
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from modules.dian_vs_erp.models import MaestroDianVsErp
from datetime import datetime

def sincronizar_factura_manual(nit, prefijo, folio, usuario, nombre):
    """Sincronizar una factura en el maestro SIN normalización"""
    print(f"\n{'='*80}")
    print(f"🔄 SINCRONIZANDO: {nombre}")
    print(f"   NIT: {nit} | Prefijo: '{prefijo}' | Folio: '{folio}'")
    print(f"{'='*80}")
    
    # Limpiar solo NIT
    nit_limpio = nit.replace('.', '').replace('-', '')
    
    factura = MaestroDianVsErp.query.filter_by(
        nit_emisor=nit_limpio,
        prefijo=prefijo,
        folio=folio
    ).first()
    
    if factura:
        print(f"\n✅ Factura encontrada en maestro (ID: {factura.id})")
        print(f"   Datos actuales:")
        print(f"      Estado Contable: {factura.estado_contable}")
        print(f"      Estado Aprobación: {factura.estado_aprobacion}")
        print(f"      Tipo Documento: {factura.tipo_documento}")
        print(f"      Tipo Tercero: {factura.tipo_tercero}")
        print(f"      Valor: ${float(factura.valor):,.2f}" if factura.valor else "N/A")
        print(f"      Recibida: {'✅ SÍ' if factura.recibida else '❌ NO'}")
        print(f"      Usuario: {factura.usuario_recibio}")
        print(f"      Origen: {factura.origen_sincronizacion}")
        
        # Actualizar SOLO los campos de sincronización
        cambios = False
        if not factura.recibida:
            print(f"\n🔄 Actualizando campos de sincronización...")
            factura.recibida = True
            factura.fecha_recibida = datetime.now()
            factura.estado_contable = "Recibida"  # ✅ SOLO este campo cambia
            factura.usuario_recibio = usuario
            factura.origen_sincronizacion = 'RECIBIR_FACTURAS'
            cambios = True
            
            # NO tocar estos campos (vienen del archivo DIAN):
            # - estado_aprobacion
            # - tipo_documento
            # - tipo_tercero
            # - valor
            # - razon_social
            # - fecha_emision
            # - cufe
            # - forma_pago
            # - etc.
        
        if cambios:
            db.session.commit()
            print(f"\n✅ SINCRONIZADA correctamente")
            print(f"   Cambios aplicados:")
            print(f"      ✅ recibida: False → True")
            print(f"      ✅ estado_contable: '{factura.estado_contable}' → 'Recibida'")
            print(f"      ✅ usuario_recibio: {usuario}")
            print(f"      ✅ origen_sincronizacion: RECIBIR_FACTURAS")
            print(f"\n   📋 Datos PRESERVADOS del archivo DIAN:")
            print(f"      ✅ estado_aprobacion: {factura.estado_aprobacion}")
            print(f"      ✅ tipo_documento: {factura.tipo_documento}")
            print(f"      ✅ tipo_tercero: {factura.tipo_tercero}")
            print(f"      ✅ valor: ${float(factura.valor):,.2f}" if factura.valor else "N/A")
            return True
        else:
            print(f"\n✅ Ya estaba sincronizada")
            return True
    else:
        print(f"\n❌ Factura NO encontrada en maestro")
        print(f"   Buscado con:")
        print(f"      NIT: '{nit_limpio}'")
        print(f"      Prefijo: '{prefijo}'")
        print(f"      Folio: '{folio}'")
        return False

if __name__ == '__main__':
    with app.app_context():
        print("\n" + "="*80)
        print("🔧 SINCRONIZACIÓN CORRECTA (SIN NORMALIZACIÓN)")
        print("="*80)
        
        # Sincronizar BIMBO
        sync1 = sincronizar_factura_manual(
            nit='830002366',
            prefijo='ME40',  # ✅ Prefijo COMPLETO
            folio='772863',  # ✅ Folio EXACTO
            usuario='admin',
            nombre='BIMBO - ME40-772863'
        )
        
        # Sincronizar GALERÍA
        sync2 = sincronizar_factura_manual(
            nit='805013653',
            prefijo='1FEA',  # ✅ Prefijo COMPLETO
            folio='77',      # ✅ Folio EXACTO
            usuario='admin',
            nombre='GALERÍA - 1FEA-77'
        )
        
        print("\n" + "="*80)
        print("📊 RESUMEN")
        print("="*80)
        
        if sync1:
            print("✅ BIMBO sincronizada correctamente")
        else:
            print("❌ BIMBO NO se pudo sincronizar")
        
        if sync2:
            print("✅ GALERÍA sincronizada correctamente")
        else:
            print("❌ GALERÍA NO se pudo sincronizar")
