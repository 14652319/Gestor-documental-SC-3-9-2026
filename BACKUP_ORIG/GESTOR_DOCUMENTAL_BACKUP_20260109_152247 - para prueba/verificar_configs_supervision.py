# -*- coding: utf-8 -*-
"""
Verifica las configuraciones de supervisión y prueba envío manual
"""
from app import app, db
from modules.dian_vs_erp.models import EnvioProgramadoDianVsErp
from modules.dian_vs_erp.scheduler_envios import EnviosProgramadosSchedulerDianVsErp

print("=" * 80)
print("🔍 VERIFICACIÓN DE CONFIGURACIONES DE SUPERVISIÓN")
print("=" * 80)

with app.app_context():
    # Buscar todas las configuraciones de supervisión activas
    configs = EnvioProgramadoDianVsErp.query.filter_by(
        es_supervision=True,
        activo=True
    ).all()
    
    print(f"\n📋 Encontradas {len(configs)} configuración(es) de supervisión activa(s):\n")
    
    for idx, config in enumerate(configs, 1):
        print(f"{'='*80}")
        print(f"📧 CONFIGURACIÓN #{idx}")
        print(f"{'='*80}")
        print(f"   ID: {config.id}")
        print(f"   Nombre: {config.nombre}")
        print(f"   Tipo: {config.tipo}")
        print(f"   Email supervisor: {config.email_supervisor}")
        print(f"   Frecuencia: {config.frecuencia}")
        print(f"   Es supervisión: {config.es_supervision}")
        print(f"   Activo: {config.activo}")
        print(f"   Días mínimos: {config.dias_minimos}")
        print(f"   Estados incluidos: {config.estados_incluidos}")
        print(f"   Estados excluidos: {config.estados_excluidos}")
        print()
        
        # Preguntar si ejecutar esta configuración
        respuesta = input(f"¿Deseas ejecutar manualmente la configuración '{config.nombre}'? (s/n): ").strip().lower()
        
        if respuesta == 's':
            print(f"\n🚀 Ejecutando configuración '{config.nombre}'...")
            print("-" * 80)
            
            try:
                # Crear instancia del scheduler
                scheduler = EnviosProgramadosSchedulerDianVsErp(app)
                
                # Ejecutar el envío
                resultado = scheduler.ejecutar_envio_programado(config.id)
                
                print("\n📊 RESULTADO DE LA EJECUCIÓN:")
                print("-" * 80)
                print(f"   Estado: {resultado.get('estado', 'N/A')}")
                print(f"   Mensaje: {resultado.get('mensaje', 'N/A')}")
                print(f"   Documentos procesados: {resultado.get('docs_procesados', 0)}")
                print(f"   Documentos enviados: {resultado.get('docs_enviados', 0)}")
                print(f"   Emails enviados: {resultado.get('emails_enviados', 0)}")
                print(f"   Emails fallidos: {resultado.get('emails_fallidos', 0)}")
                
                if resultado.get('destinatarios_ok'):
                    print(f"   ✅ Destinatarios OK: {', '.join(resultado['destinatarios_ok'])}")
                
                if resultado.get('destinatarios_error'):
                    print(f"   ❌ Destinatarios con error: {', '.join(resultado['destinatarios_error'])}")
                
                if resultado.get('estado') == 'EXITO':
                    print("\n✅ ¡CORREO ENVIADO EXITOSAMENTE!")
                    print("   Revisa la bandeja de entrada (y SPAM) del supervisor")
                else:
                    print("\n❌ EL CORREO NO SE ENVIÓ")
                    print("   Revisa el mensaje de error arriba")
                
            except Exception as e:
                print(f"\n❌ ERROR AL EJECUTAR: {e}")
                import traceback
                traceback.print_exc()
            
            print()
    
    if not configs:
        print("⚠️ No hay configuraciones de supervisión activas en la base de datos")
        print("\nVerifica que:")
        print("1. Has creado configuraciones con 'es_supervision=True'")
        print("2. Las configuraciones están activas (activo=True)")
        print("3. Tienen un email_supervisor configurado")

print("\n" + "=" * 80)
print("FIN DE LA VERIFICACIÓN")
print("=" * 80)
