"""
Prueba AUTOMÁTICA de envío de correos SAGRILAFT
NIT: 29590569 - LUZ MARINA BURGOS FIGUEROA
Email: RICARDO160883@HOTMAIL.ES
"""
from datetime import datetime, timedelta
from app import app, db, Tercero, SolicitudRegistro, mail
from modules.sagrilaft.email_sagrilaft import (
    enviar_correo_decision_radicado,
    enviar_correo_alerta_vencimiento
)

print("\n" + "="*80)
print("  PRUEBA AUTOMÁTICA DE CORREOS SAGRILAFT")
print("  NIT: 29590569 - LUZ MARINA BURGOS FIGUEROA")
print("="*80)

with app.app_context():
    # Obtener tercero
    tercero = Tercero.query.filter_by(nit='29590569').first()
    
    if not tercero:
        print("\n❌ ERROR: Tercero no encontrado")
        exit(1)
    
    # Obtener último radicado
    radicado = SolicitudRegistro.query.filter_by(
        tercero_id=tercero.id
    ).order_by(
        SolicitudRegistro.fecha_actualizacion.desc()
    ).first()
    
    if not radicado:
        print("\n❌ ERROR: No hay radicados para este tercero")
        exit(1)
    
    # Obtener email
    email = getattr(tercero, 'email', None) or getattr(tercero, 'correo', None)
    
    if not email:
        print("\n❌ ERROR: Tercero no tiene email")
        exit(1)
    
    print(f"\n📋 DATOS:")
    print(f"  NIT: {tercero.nit}")
    print(f"  Razón Social: {tercero.razon_social}")
    print(f"  Email: {email}")
    print(f"  Radicado: {radicado.radicado}")
    print(f"  Estado: {radicado.estado}")
    
    print("\n" + "="*80)
    print("  PRUEBA 1: CORREO DE DECISIÓN (APROBADO)")
    print("="*80)
    
    # Enviar correo de decisión
    success1, msg1 = enviar_correo_decision_radicado(
        mail=mail,
        destinatario=email,
        nit=tercero.nit,
        razon_social=tercero.razon_social,
        radicado=radicado.radicado,
        estado='aprobado',
        observacion='✅ Documentos COMPLETOS y verificados.\n\nBienvenido al sistema SAGRILAFT de Supertiendas Cañaveral.\n\n⚠️ NOTA: Este es un correo de PRUEBA del sistema de notificaciones automáticas.'
    )
    
    if success1:
        print(f"\n✅ ENVIADO EXITOSAMENTE")
        print(f"📧 Destinatario: {email}")
        print(f"📋 Radicado: {radicado.radicado}")
        print(f"✅ Estado: APROBADO")
        print(f"💬 Mensaje: {msg1}")
    else:
        print(f"\n❌ ERROR AL ENVIAR")
        print(f"⚠️ Mensaje: {msg1}")
    
    print("\n" + "-"*80)
    
    print("\n" + "="*80)
    print("  PRUEBA 2: CORREO DE ALERTA DE VENCIMIENTO")
    print("="*80)
    
    # Calcular fechas para alerta (simular 18 días restantes)
    fecha_ultimo_rad = radicado.fecha_actualizacion or radicado.fecha_solicitud
    fecha_vencimiento = fecha_ultimo_rad + timedelta(days=360)
    dias_restantes = 18  # Simulado
    
    print(f"\n📅 Simulación:")
    print(f"  Última actualización: {fecha_ultimo_rad.strftime('%d/%m/%Y')}")
    print(f"  Fecha vencimiento: {fecha_vencimiento.strftime('%d/%m/%Y')}")
    print(f"  ⏰ Días restantes (simulados): {dias_restantes}")
    
    # Enviar correo de alerta
    success2, msg2 = enviar_correo_alerta_vencimiento(
        mail=mail,
        destinatario=email,
        nit=tercero.nit,
        razon_social=tercero.razon_social,
        radicado=radicado.radicado,
        dias_restantes=dias_restantes,
        fecha_vencimiento=fecha_vencimiento
    )
    
    if success2:
        print(f"\n✅ ENVIADO EXITOSAMENTE")
        print(f"📧 Destinatario: {email}")
        print(f"📋 Radicado: {radicado.radicado}")
        print(f"⏰ Días restantes: {dias_restantes}")
        print(f"💬 Mensaje: {msg2}")
    else:
        print(f"\n❌ ERROR AL ENVIAR")
        print(f"⚠️ Mensaje: {msg2}")
    
    print("\n" + "="*80)
    print("  RESUMEN FINAL")
    print("="*80)
    print(f"  Correo de Decisión: {'✅ ENVIADO' if success1 else '❌ ERROR'}")
    print(f"  Correo de Alerta: {'✅ ENVIADO' if success2 else '❌ ERROR'}")
    
    if success1 and success2:
        print(f"\n🎉 AMBOS CORREOS ENVIADOS EXITOSAMENTE")
        print(f"📧 Revisa la bandeja de entrada: {email}")
        print(f"\n⚠️ IMPORTANTE: Si no aparecen, revisar SPAM/Correo no deseado")
    elif success1 or success2:
        print(f"\n⚠️ ENVÍO PARCIAL - Revisar errores arriba")
    else:
        print(f"\n❌ NINGÚN CORREO ENVIADO - Revisar configuración SMTP")
    
    print("="*80 + "\n")
