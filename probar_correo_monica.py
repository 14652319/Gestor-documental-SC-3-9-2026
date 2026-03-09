"""
Script de Prueba - Envío de Correos SAGRILAFT
Prueba con el tercero MONICA (NIT 1130656650)
"""
import sys
from datetime import datetime, timedelta
from app import app, db, Tercero, SolicitudRegistro, mail
from modules.sagrilaft.email_sagrilaft import (
    enviar_correo_decision_radicado,
    enviar_correo_alerta_vencimiento
)

def obtener_datos_tercero(nit):
    """Obtiene datos del tercero y su último radicado"""
    with app.app_context():
        # Buscar tercero
        tercero = Tercero.query.filter_by(nit=nit).first()
        
        if not tercero:
            print(f"❌ Tercero con NIT {nit} no encontrado")
            return None
        
        print(f"\n{'='*70}")
        print(f"  DATOS DEL TERCERO")
        print(f"{'='*70}")
        print(f"  NIT: {tercero.nit}")
        print(f"  Razón Social: {tercero.razon_social}")
        
        # Verificar si tiene email
        email = getattr(tercero, 'email', None) or getattr(tercero, 'correo', None)
        print(f"  Email: {email or 'NO TIENE EMAIL REGISTRADO'}")
        print(f"  ID: {tercero.id}")
        
        # Buscar último radicado
        radicado = SolicitudRegistro.query.filter_by(
            tercero_id=tercero.id
        ).order_by(
            SolicitudRegistro.fecha_actualizacion.desc()
        ).first()
        
        if radicado:
            print(f"\n  ÚLTIMO RADICADO:")
            print(f"  Número: {radicado.radicado}")
            print(f"  Estado: {radicado.estado}")
            print(f"  Fecha Actualización: {radicado.fecha_actualizacion or radicado.fecha_solicitud}")
            # Observaciones puede no existir en el modelo
            obs = getattr(radicado, 'observaciones', None) or getattr(radicado, 'observacion', None)
            if obs:
                print(f"  Observaciones: {obs}")
        else:
            print(f"\n  ⚠️ NO tiene radicados registrados")
        
        print(f"{'='*70}\n")
        
        return {
            'tercero': tercero,
            'radicado': radicado
        }

def probar_correo_decision(datos):
    """Prueba correo de decisión de radicado"""
    tercero = datos['tercero']
    radicado = datos['radicado']
    
    # Verificar email
    email = getattr(tercero, 'email', None) or getattr(tercero, 'correo', None)
    
    if not email:
        print("❌ El tercero NO tiene email registrado")
        print("\n⚠️ SOLUCIÓN: Debes agregar un email en la tabla 'terceros' para este NIT")
        print("   Puedes ejecutar este SQL:")
        print(f"   UPDATE terceros SET email = 'test@example.com' WHERE nit = '{tercero.nit}';")
        return False
    
    if not radicado:
        print("❌ El tercero NO tiene radicados")
        return False
    
    print("\n" + "="*70)
    print("  PRUEBA 1: CORREO DE DECISIÓN")
    print("="*70)
    print("\nEnviando correo de APROBACIÓN con observaciones de prueba...")
    
    with app.app_context():
        success, msg = enviar_correo_decision_radicado(
            mail=mail,
            destinatario=email,
            nit=tercero.nit,
            razon_social=tercero.razon_social,
            radicado=radicado.radicado,
            estado='aprobado',
            observacion='Documentos correctos y completos. Bienvenido al sistema SAGRILAFT de Supertiendas Cañaveral. Este es un correo de PRUEBA del sistema.'
        )
        
        if success:
            print(f"✅ {msg}")
            print(f"📧 Correo enviado a: {email}")
            print(f"📋 Radicado: {radicado.radicado}")
            print(f"✅ Estado: APROBADO")
            return True
        else:
            print(f"❌ Error: {msg}")
            return False

def probar_correo_alerta(datos):
    """Prueba correo de alerta de vencimiento"""
    tercero = datos['tercero']
    radicado = datos['radicado']
    
    # Verificar email
    email = getattr(tercero, 'email', None) or getattr(tercero, 'correo', None)
    
    if not email:
        print("❌ El tercero NO tiene email registrado")
        print("\n⚠️ SOLUCIÓN: Debes agregar un email en la tabla 'terceros' para este NIT")
        print("   Puedes ejecutar este SQL:")
        print(f"   UPDATE terceros SET email = 'test@example.com' WHERE nit = '{tercero.nit}';")
        return False
    
    if not radicado:
        print("❌ El tercero NO tiene radicados")
        return False
    
    print("\n" + "="*70)
    print("  PRUEBA 2: CORREO DE ALERTA DE VENCIMIENTO")
    print("="*70)
    print("\nEnviando correo de alerta (simulando 18 días restantes)...")
    
    # Simular que quedan 18 días para vencer (342 días desde última actualización)
    fecha_ultimo_rad = radicado.fecha_actualizacion or radicado.fecha_solicitud
    fecha_vencimiento = fecha_ultimo_rad + timedelta(days=360)
    dias_restantes = 18  # Simulado
    
    with app.app_context():
        success, msg = enviar_correo_alerta_vencimiento(
            mail=mail,
            destinatario=email,
            nit=tercero.nit,
            razon_social=tercero.razon_social,
            radicado=radicado.radicado,
            dias_restantes=dias_restantes,
            fecha_vencimiento=fecha_vencimiento
        )
        
        if success:
            print(f"✅ {msg}")
            print(f"📧 Correo enviado a: {email}")
            print(f"📋 Radicado: {radicado.radicado}")
            print(f"⏰ Días restantes (simulados): {dias_restantes}")
            print(f"📅 Fecha vencimiento: {fecha_vencimiento.strftime('%d/%m/%Y')}")
            return True
        else:
            print(f"❌ Error: {msg}")
            return False

def menu_principal():
    """Menú interactivo de pruebas"""
    print("\n" + "="*70)
    print("  PRUEBA DE CORREOS SAGRILAFT")
    print("  Tercero: NIT 29590569")
    print("="*70)
    
    # Obtener datos del tercero
    datos = obtener_datos_tercero('29590569')
    
    if not datos:
        print("\n❌ No se pudo obtener datos del tercero")
        return
    
    # Verificar email
    email = getattr(datos['tercero'], 'email', None) or getattr(datos['tercero'], 'correo', None)
    
    if not email:
        print("\n❌ ERROR: El tercero NO tiene email registrado en la base de datos")
        print("   Debes agregar un email primero en la tabla 'terceros'")
        print(f"\n   SQL para agregar email:")
        print(f"   UPDATE terceros SET email = 'test@example.com' WHERE nit = '29590569';")
        print(f"\n   O usa un email real del proveedor para la prueba")
        return
    
    print("\n¿Qué tipo de correo deseas probar?")
    print("\n1. Correo de DECISIÓN (Aprobado/Rechazado/Condicionado)")
    print("2. Correo de ALERTA DE VENCIMIENTO (20 días)")
    print("3. Probar AMBOS correos")
    print("0. Salir")
    
    try:
        opcion = input("\nSelecciona una opción (0-3): ").strip()
        
        if opcion == '1':
            probar_correo_decision(datos)
        elif opcion == '2':
            probar_correo_alerta(datos)
        elif opcion == '3':
            print("\n" + "="*70)
            print("  PROBANDO AMBOS CORREOS")
            print("="*70)
            exito1 = probar_correo_decision(datos)
            print("\n" + "-"*70)
            exito2 = probar_correo_alerta(datos)
            
            print("\n" + "="*70)
            print("  RESUMEN DE PRUEBAS")
            print("="*70)
            print(f"  Correo de Decisión: {'✅ Enviado' if exito1 else '❌ Error'}")
            print(f"  Correo de Alerta: {'✅ Enviado' if exito2 else '❌ Error'}")
            print("="*70)
        elif opcion == '0':
            print("\n👋 Saliendo...")
        else:
            print("\n⚠️ Opción inválida")
    
    except KeyboardInterrupt:
        print("\n\n👋 Prueba cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")

if __name__ == '__main__':
    menu_principal()
