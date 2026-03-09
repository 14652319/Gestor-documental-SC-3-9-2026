"""
Script de emergencia para guardar manualmente la factura ID 76
"""
from extensions import db
from modules.recibir_facturas.models import FacturaTemporal, FacturaRecibida, ObservacionFacturaTemporal, ObservacionFactura
from modules.dian_vs_erp.sync_service import sincronizar_factura_recibida
from datetime import datetime
from dotenv import load_dotenv
from app import app
import logging

load_dotenv()
logger = logging.getLogger(__name__)

print("=" * 100)
print("GUARDADO MANUAL DE FACTURA ID 76")
print("=" * 100)

with app.app_context():
    try:
        # 1. Obtener factura temporal
        factura_temp = FacturaTemporal.query.get(76)
        
        if not factura_temp:
            print("❌ Factura ID 76 no encontrada en temporales")
            exit(1)
        
        print(f"\n✅ Factura encontrada:")
        print(f"   NIT: {factura_temp.nit}")
        print(f"   Razón Social: {factura_temp.razon_social}")
        print(f"   Prefijo-Folio: {factura_temp.prefijo}-{factura_temp.folio}")
        print(f"   Valor Bruto: ${factura_temp.valor_bruto:,.0f}")
        
        # 2. Verificar duplicados
        from modules.recibir_facturas.models import FacturaRecibida
        existe, _ = FacturaRecibida.validar_clave_unica(
            factura_temp.nit,
            factura_temp.prefijo,
            factura_temp.folio
        )
        
        if existe:
            print("\n❌ Ya existe en facturas_recibidas")
            exit(1)
        
        # 3. Calcular valor neto
        valor_neto = (
            float(factura_temp.valor_bruto or 0) +
            float(factura_temp.iva or 0) -
            float(factura_temp.descuento or 0) -
            float(factura_temp.retencion_fuente or 0) -
            float(factura_temp.rete_iva or 0) -
            float(factura_temp.rete_ica or 0)
        )
        
        print(f"\n💰 Valor Neto Calculado: ${valor_neto:,.0f}")
        
        # 4. Crear factura recibida
        factura_recibida = FacturaRecibida(
            nit=factura_temp.nit,
            razon_social=factura_temp.razon_social,
            prefijo=factura_temp.prefijo or '',
            folio=factura_temp.folio,
            empresa_id=factura_temp.empresa_id,
            centro_operacion_id=factura_temp.centro_operacion_id,
            centro_operacion=factura_temp.centro_operacion or '',
            fecha_expedicion=factura_temp.fecha_expedicion,
            fecha_radicacion=factura_temp.fecha_radicacion,
            fecha_vencimiento=factura_temp.fecha_vencimiento,
            valor_bruto=factura_temp.valor_bruto,
            descuento=factura_temp.descuento or 0,
            iva=factura_temp.iva or 0,
            retencion_fuente=factura_temp.retencion_fuente or 0,
            rete_iva=factura_temp.rete_iva or 0,
            rete_ica=factura_temp.rete_ica or 0,
            valor_neto=valor_neto,
            usuario_solicita=factura_temp.usuario_solicita or 'NA',
            comprador=factura_temp.comprador or 'NA',
            quien_recibe=factura_temp.quien_recibe or 'NA',
            forma_pago=factura_temp.forma_pago or 'CREDITO',
            plazo=factura_temp.plazo or 30,
            estado='RECIBIDA',
            observaciones=factura_temp.observaciones,
            usuario_nombre=factura_temp.usuario_nombre,
            usuario_id=factura_temp.usuario_id
        )
        
        db.session.add(factura_recibida)
        db.session.flush()
        
        print(f"\n✅ Factura agregada a facturas_recibidas (ID: {factura_recibida.id})")
        
        # 5. Sincronizar con maestro
        print("\n🔄 Sincronizando con maestro_dian_vs_erp...")
        
        exito, mensaje, accion = sincronizar_factura_recibida(
            nit=factura_temp.nit,
            prefijo=factura_temp.prefijo or '',
            folio=factura_temp.folio,
            fecha_recibida=factura_recibida.fecha_radicacion or datetime.now(),
            usuario='admin',
            origen='RECIBIR_FACTURAS',
            razon_social=factura_temp.razon_social
        )
        
        if exito:
            print(f"   ✅ Sincronización exitosa: {accion}")
            print(f"   📋 {mensaje}")
        else:
            print(f"   ⚠️  Advertencia sincronización: {mensaje}")
        
        # 6. Copiar observaciones
        observaciones = ObservacionFacturaTemporal.query.filter_by(
            factura_temporal_id=factura_temp.id
        ).all()
        
        if observaciones:
            print(f"\n📝 Copiando {len(observaciones)} observación(es)...")
            for obs_temp in observaciones:
                obs_recibida = ObservacionFactura(
                    factura_id=factura_recibida.id,
                    observacion=obs_temp.observacion,
                    usuario_nombre=factura_temp.usuario_nombre,
                    usuario_id=obs_temp.usuario_id
                )
                db.session.add(obs_recibida)
                # Eliminar observación temporal
                db.session.delete(obs_temp)
            print(f"   ✅ Observaciones copiadas")
        
        # 7. Eliminar factura temporal
        print("\n🗑️  Eliminando de temporales...")
        db.session.delete(factura_temp)
        
        # 8. Commit
        db.session.commit()
        
        print("\n" + "=" * 100)
        print("✅ FACTURA GUARDADA EXITOSAMENTE")
        print("=" * 100)
        print(f"\n📊 Resumen:")
        print(f"   • Movida de temporales → recibidas")
        print(f"   • Sincronizada con maestro DIAN")
        print(f"   • Estado: Recibida")
        print(f"   • Factura: {factura_recibida.prefijo}{factura_recibida.folio}")
        print()
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        print(traceback.format_exc())
