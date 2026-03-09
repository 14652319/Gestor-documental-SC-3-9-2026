"""
Reparar sincronización de facturas guardadas
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from modules.recibir_facturas.models import FacturaTemporal
from modules.dian_vs_erp.models import MaestroDianVsErp
from datetime import datetime

def eliminar_temporal_duplicada():
    """Eliminar factura BIMBO de temporales (ya está en recibidas)"""
    print("\n🧹 ELIMINANDO FACTURA DUPLICADA DE TEMPORALES...")
    
    temp = FacturaTemporal.query.filter_by(
        nit='830002366',
        prefijo='ME40',
        folio='772863'
    ).first()
    
    if temp:
        print(f"   ✅ Encontrada temporal ID: {temp.id}")
        print(f"      {temp.razon_social} | {temp.prefijo}-{temp.folio}")
        db.session.delete(temp)
        db.session.commit()
        print(f"   ✅ ELIMINADA de temporales")
        return True
    else:
        print(f"   ℹ️ No hay duplicado en temporales")
        return False

def sincronizar_maestro(nit, prefijo, folio, usuario, nombre):
    """Sincronizar una factura en el maestro"""
    print(f"\n🔄 SINCRONIZANDO: {nombre}")
    print(f"   NIT: {nit} | Prefijo: {prefijo} | Folio: {folio}")
    
    factura = MaestroDianVsErp.query.filter_by(
        nit_emisor=nit,
        prefijo=prefijo,
        folio=folio
    ).first()
    
    if factura:
        print(f"   ✅ Factura encontrada en maestro (ID: {factura.id})")
        print(f"      Estado actual: {factura.estado_contable}")
        print(f"      Recibida: {'SÍ' if factura.recibida else 'NO'}")
        
        if not factura.recibida:
            # Actualizar campos de sincronización
            factura.recibida = True
            factura.fecha_recibida = datetime.now()
            factura.estado_contable = "Recibida"
            factura.usuario_recibio = usuario
            factura.origen_sincronizacion = 'RECIBIR_FACTURAS'
            
            db.session.commit()
            print(f"   ✅ SINCRONIZADA correctamente")
            print(f"      Nuevo estado: Recibida")
            print(f"      Usuario: {usuario}")
            print(f"      Origen: RECIBIR_FACTURAS")
            return True
        else:
            print(f"   ℹ️ Ya estaba sincronizada")
            return True
    else:
        print(f"   ❌ NO encontrada en maestro")
        return False

if __name__ == '__main__':
    with app.app_context():
        print("\n" + "="*80)
        print("🔧 REPARACIÓN DE SINCRONIZACIÓN")
        print("="*80)
        
        # Paso 1: Eliminar duplicado de BIMBO en temporales
        eliminado = eliminar_temporal_duplicada()
        
        # Paso 2: Sincronizar BIMBO en maestro
        sync1 = sincronizar_maestro(
            nit='830002366',
            prefijo='ME40',
            folio='772863',
            usuario='admin',
            nombre='BIMBO - ME40-772863'
        )
        
        # Paso 3: Sincronizar GALERÍA en maestro
        sync2 = sincronizar_maestro(
            nit='805013653',
            prefijo='1FEA',
            folio='77',
            usuario='admin',
            nombre='GALERÍA - 1FEA-77'
        )
        
        print("\n" + "="*80)
        print("📊 RESUMEN")
        print("="*80)
        
        if eliminado:
            print("✅ Duplicado de BIMBO eliminado de temporales")
        else:
            print("ℹ️ No había duplicado de BIMBO en temporales")
        
        if sync1:
            print("✅ BIMBO sincronizada en maestro")
        else:
            print("❌ BIMBO NO se pudo sincronizar")
        
        if sync2:
            print("✅ GALERÍA sincronizada en maestro")
        else:
            print("❌ GALERÍA NO se pudo sincronizar")
        
        # Verificar resultado
        print("\n" + "="*80)
        print("🔍 VERIFICACIÓN FINAL")
        print("="*80)
        
        # BIMBO
        maestro_bimbo = MaestroDianVsErp.query.filter_by(
            nit_emisor='830002366',
            prefijo='ME40',
            folio='772863'
        ).first()
        
        if maestro_bimbo:
            print(f"\n✅ BIMBO en Maestro:")
            print(f"   Estado: {maestro_bimbo.estado_contable}")
            print(f"   Recibida: {'✅ SÍ' if maestro_bimbo.recibida else '❌ NO'}")
            print(f"   Usuario: {maestro_bimbo.usuario_recibio}")
            print(f"   Origen: {maestro_bimbo.origen_sincronizacion}")
        
        # GALERÍA
        maestro_galeria = MaestroDianVsErp.query.filter_by(
            nit_emisor='805013653',
            prefijo='1FEA',
            folio='77'
        ).first()
        
        if maestro_galeria:
            print(f"\n✅ GALERÍA en Maestro:")
            print(f"   Estado: {maestro_galeria.estado_contable}")
            print(f"   Recibida: {'✅ SÍ' if maestro_galeria.recibida else '❌ NO'}")
            print(f"   Usuario: {maestro_galeria.usuario_recibio}")
            print(f"   Origen: {maestro_galeria.origen_sincronizacion}")
        
        # Contar temporales restantes
        total_temp = FacturaTemporal.query.count()
        print(f"\n📊 Facturas restantes en temporales: {total_temp}")
