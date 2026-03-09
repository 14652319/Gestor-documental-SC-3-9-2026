"""
Script para verificar configuración de envío programado guardada
Consulta la tabla envios_programados_dian_vs_erp
"""

import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from modules.dian_vs_erp.models import EnvioProgramadoDianVsErp

def verificar_configuracion_reciente():
    """Consulta la configuración más reciente"""
    with app.app_context():
        # Obtener la configuración más reciente (por ID o fecha_creacion)
        config = EnvioProgramadoDianVsErp.query.order_by(
            EnvioProgramadoDianVsErp.id.desc()
        ).first()
        
        if not config:
            print("❌ No hay configuraciones en la base de datos")
            return
        
        print("\n" + "="*80)
        print(f"📋 CONFIGURACIÓN MÁS RECIENTE (ID: {config.id})")
        print("="*80)
        
        print(f"\n📌 INFORMACIÓN BÁSICA:")
        print(f"   Nombre: {config.nombre}")
        print(f"   Tipo: {config.tipo}")
        print(f"   Activo: {'✅ SÍ' if config.activo else '❌ NO'}")
        print(f"   Hora envío: {config.hora_envio}")
        print(f"   Frecuencia: {config.frecuencia}")
        
        print(f"\n🎯 CRITERIOS:")
        if config.tipo == 'PENDIENTES_DIAS':
            print(f"   Días mínimos: {config.dias_minimos}")
            print(f"   Estados excluidos: {config.estados_excluidos}")
        else:
            print(f"   Acuses mínimo: {config.requiere_acuses_minimo}")
        
        print(f"\n🏢 FILTROS DE TIPO DE TERCERO:")
        if config.tipos_tercero:
            import json
            tipos = json.loads(config.tipos_tercero)
            if tipos:
                for tipo in tipos:
                    print(f"   ✓ {tipo}")
            else:
                print("   ⚠️ Array vacío (incluirá todos los tipos)")
        else:
            print("   ⚠️ NULL (incluirá todos los tipos)")
        
        print(f"\n📅 FILTROS DE FECHA:")
        if config.fecha_inicio:
            print(f"   Fecha inicio: {config.fecha_inicio}")
        else:
            print("   Fecha inicio: ⚠️ NULL (sin filtro inferior)")
        
        if config.fecha_fin:
            print(f"   Fecha fin: {config.fecha_fin}")
        else:
            print("   Fecha fin: ⚠️ NULL (sin filtro superior)")
        
        print(f"\n🔍 SUPERVISIÓN:")
        if config.es_supervision:
            print(f"   Es supervisión: ✅ SÍ")
            print(f"   Email supervisor: {config.email_supervisor}")
            print(f"   Frecuencia (días): {config.frecuencia_dias}")
        else:
            print(f"   Es supervisión: ❌ NO")
        
        print(f"\n📧 DESTINATARIOS:")
        print(f"   Tipo destinatario: {config.tipo_destinatario}")
        
        print(f"\n⏰ PROGRAMACIÓN:")
        if config.proximo_envio:
            print(f"   Próximo envío: ✅ {config.proximo_envio}")
        else:
            print(f"   Próximo envío: ❌ NULL (NO CALCULADO)")
        
        if config.ultimo_envio:
            print(f"   Último envío: {config.ultimo_envio}")
        else:
            print(f"   Último envío: (nunca)")
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   Total ejecuciones: {config.total_ejecuciones}")
        print(f"   Total documentos procesados: {config.total_documentos_procesados}")
        print(f"   Total emails enviados: {config.total_emails_enviados}")
        
        print(f"\n📝 AUDITORÍA:")
        print(f"   Creado: {config.fecha_creacion}")
        if config.fecha_modificacion:
            print(f"   Modificado: {config.fecha_modificacion}")
        
        print("\n" + "="*80)
        
        # Verificar si hay problemas
        problemas = []
        
        if not config.proximo_envio:
            problemas.append("⚠️ proximo_envio es NULL - El scheduler no calculó la próxima fecha")
        
        if config.tipos_tercero:
            import json
            tipos = json.loads(config.tipos_tercero)
            if not tipos:
                problemas.append("ℹ️ tipos_tercero es array vacío - Se incluirán todos los tipos")
        
        if not config.fecha_inicio and not config.fecha_fin:
            problemas.append("ℹ️ Sin filtros de fecha - Se procesarán todos los documentos")
        
        if problemas:
            print("\n🔍 DIAGNÓSTICO:")
            for problema in problemas:
                print(f"   {problema}")
        
        print("\n")

if __name__ == '__main__':
    try:
        verificar_configuracion_reciente()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
