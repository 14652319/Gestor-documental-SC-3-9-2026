"""
Script para asignar radicado y enviar correo a factura FE-456
"""
from app import app, db
from modules.facturas_digitales.models import FacturaDigital
from modules.facturas_digitales.routes import generar_radicado_rfd, enviar_correo_radicacion_factura, log_security, get_usuario_model

with app.app_context():
    # 1. Buscar la factura FE-456
    factura = FacturaDigital.query.filter_by(
        numero_factura='FE-456',
        nit_proveedor='14652319'
    ).first()
    
    if not factura:
        print("❌ Factura FE-456 no encontrada")
        exit(1)
    
    print("=" * 80)
    print("📋 FACTURA ENCONTRADA")
    print("=" * 80)
    print(f"ID: {factura.id}")
    print(f"Número: {factura.numero_factura}")
    print(f"NIT: {factura.nit_proveedor}")
    print(f"Razón Social: {factura.razon_social_proveedor}")
    print(f"Valor: ${factura.valor_total:,.2f}")
    print(f"Usuario: {factura.usuario_carga}")
    print(f"Radicado actual: {factura.radicado_rfd or 'SIN RADICADO'}")
    print()
    
    # 2. Generar radicado si no tiene
    if not factura.radicado_rfd:
        print("🔄 Generando radicado RFD...")
        try:
            radicado_rfd = generar_radicado_rfd()
            factura.radicado_rfd = radicado_rfd
            db.session.commit()
            print(f"   ✅ Radicado generado: {radicado_rfd}")
            log_security(f"RADICADO ASIGNADO RETROACTIVO | factura_id={factura.id} | radicado={radicado_rfd}")
        except Exception as e:
            print(f"   ❌ Error generando radicado: {str(e)}")
            db.session.rollback()
            exit(1)
    else:
        radicado_rfd = factura.radicado_rfd
        print(f"ℹ️  Factura ya tiene radicado: {radicado_rfd}")
    
    print()
    
    # 3. Obtener datos del usuario
    print("👤 Buscando datos del usuario...")
    Usuario = get_usuario_model()
    usuario_obj = Usuario.query.filter_by(usuario=factura.usuario_carga).first()
    
    if not usuario_obj:
        print(f"   ❌ Usuario {factura.usuario_carga} no encontrado")
        exit(1)
    
    if not usuario_obj.correo:
        print(f"   ❌ Usuario {factura.usuario_carga} no tiene correo configurado")
        exit(1)
    
    usuario_email = usuario_obj.correo
    usuario_nombre = usuario_obj.usuario
    
    print(f"   ✅ Usuario: {usuario_nombre}")
    print(f"   📧 Email: {usuario_email}")
    print()
    
    # 4. Preparar datos para el correo
    factura_data = {
        'numero_factura': factura.numero_factura,
        'nit_proveedor': factura.nit_proveedor,
        'razon_social': factura.razon_social_proveedor,
        'valor_total': float(factura.valor_total),
        'fecha_emision': factura.fecha_emision.strftime('%d/%m/%Y'),
        'num_archivos': 1  # Por ahora
    }
    
    # 5. Enviar correo
    print("📧 Enviando correo...")
    try:
        envio_exitoso = enviar_correo_radicacion_factura(
            usuario_email=usuario_email,
            usuario_nombre=usuario_nombre,
            radicado_rfd=radicado_rfd,
            factura_data=factura_data
        )
        
        if envio_exitoso:
            print("   ✅ Correo enviado exitosamente")
            log_security(f"CORREO ENVIADO RETROACTIVO | factura_id={factura.id} | usuario={usuario_nombre} | email={usuario_email} | radicado={radicado_rfd}")
        else:
            print("   ⚠️  Correo no enviado (ver logs para detalles)")
            
    except Exception as e:
        print(f"   ❌ Error enviando correo: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("✅ PROCESO COMPLETADO")
    print("=" * 80)
    print(f"Radicado: {radicado_rfd}")
    print(f"Destinatario: {usuario_email}")
    print(f"Revisa tu bandeja de entrada (y spam)")
    print("=" * 80)
