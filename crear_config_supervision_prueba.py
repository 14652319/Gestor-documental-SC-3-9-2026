"""
Script para crear una configuración de supervisión de PRUEBA
Envía documentos NO REGISTRADOS +3 días al email del supervisor
"""

from extensions import db
from app import app
from modules.dian_vs_erp.models import EnvioProgramadoDianVsErp
import json

def crear_supervision_prueba():
    """Crear configuración de supervisión de prueba"""
    
    with app.app_context():
        print("=" * 80)
        print("🔧 CREANDO CONFIGURACIÓN DE SUPERVISIÓN DE PRUEBA")
        print("=" * 80)
        print()
        
        # Email del supervisor (cambiar por el email real)
        email_supervisor = input("📧 Ingresa el email del supervisor: ").strip()
        
        if not email_supervisor or '@' not in email_supervisor:
            print("❌ Email inválido")
            return
        
        try:
            # Crear configuración de supervisión
            config_supervision = EnvioProgramadoDianVsErp(
                nombre="🔍 SUPERVISIÓN - Documentos NO REGISTRADOS +3 días",
                tipo="PENDIENTES_DIAS",  # Tipo de filtro
                
                # Criterios
                dias_minimos=3,  # Documentos con +3 días
                estados_incluidos=None,  # Todos los estados
                estados_excluidos=json.dumps([]),  # Sin exclusiones
                
                # Horario (cada 4 días a las 08:00 AM)
                hora_envio="08:00",
                frecuencia="DIARIO",  # Se ejecuta diario, pero la lógica interna usa frecuencia_dias
                dias_semana=json.dumps([1, 2, 3, 4, 5]),  # Lunes a viernes
                
                # Destinatarios
                tipo_destinatario="SUPERVISOR",  # No usado en supervisión
                email_cc=None,
                
                # 🆕 SUPERVISIÓN
                es_supervision=True,  # ✅ ESTE ES EL FLAG CLAVE
                email_supervisor=email_supervisor,
                frecuencia_dias=4,  # Cada 4 días (se puede cambiar: 1=diario, 7=semanal)
                
                # Estado
                activo=False,  # Inicia INACTIVO para que puedas revisarlo primero
                
                # Usuario creador
                usuario_creacion="SISTEMA"
            )
            
            db.session.add(config_supervision)
            db.session.commit()
            
            print()
            print("=" * 80)
            print("✅ CONFIGURACIÓN DE SUPERVISIÓN CREADA EXITOSAMENTE")
            print("=" * 80)
            print()
            print(f"📋 ID: {config_supervision.id}")
            print(f"📝 Nombre: {config_supervision.nombre}")
            print(f"📧 Email supervisor: {config_supervision.email_supervisor}")
            print(f"🔄 Frecuencia: Cada {config_supervision.frecuencia_dias} día(s)")
            print(f"⏰ Horario: {config_supervision.hora_envio}")
            print(f"📊 Criterio: Documentos NO REGISTRADOS con +{config_supervision.dias_minimos} días")
            print(f"🔴 Estado: INACTIVO (para pruebas)")
            print()
            print("=" * 80)
            print("📋 PRÓXIMOS PASOS:")
            print("=" * 80)
            print()
            print("1. 🌐 Ir a la página de configuración:")
            print("   http://127.0.0.1:8099/dian_vs_erp/configuracion")
            print()
            print("2. 👁️  Verifica que aparezca en la tabla con:")
            print("   - ✅ Tipo: SUPERVISIÓN")
            print("   - 📧 Email del supervisor visible")
            print()
            print("3. ✅ Para activarla:")
            print("   - Click en el botón de ACTIVAR (switch)")
            print("   - O ejecutar este comando SQL:")
            print(f"   UPDATE envios_programados_dian_vs_erp SET activo = TRUE WHERE id = {config_supervision.id};")
            print()
            print("4. ▶️  Para ejecutar prueba manual:")
            print("   - Click en botón ▶️ (Ejecutar Ahora)")
            print("   - Revisa el email del supervisor")
            print()
            print("5. 📊 Para ver resultado:")
            print("   - Ve a la pestaña 'Historial de Envíos'")
            print("   - Verifica estado: ENVIADO o FALLIDO")
            print()
            print("=" * 80)
            print("⚠️  IMPORTANTE:")
            print("   - Esta configuración NO agrupa por NIT")
            print("   - Envía TODOS los docs en un solo email consolidado")
            print("   - NO afecta las 5 configuraciones normales existentes")
            print("=" * 80)
            print()
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    crear_supervision_prueba()
