"""
Script para verificar qué envíos programados se están usando activamente
"""
import sys
from datetime import datetime, timedelta
from app import app, db

def verificar_envios_usados():
    with app.app_context():
        print("\n" + "="*80)
        print("📊 ANÁLISIS DE ENVÍOS PROGRAMADOS EN USO")
        print("="*80 + "\n")
        
        # 1. Consultar todas las configuraciones
        query_configs = """
            SELECT 
                id,
                nombre,
                tipo,
                activo,
                proximo_envio,
                frecuencia,
                hora_envio
            FROM envios_programados_dian_vs_erp
            ORDER BY activo DESC, nombre
        """
        
        configs = db.session.execute(db.text(query_configs)).fetchall()
        
        print(f"📋 TOTAL DE CONFIGURACIONES: {len(configs)}")
        print(f"   ✅ Activas: {sum(1 for c in configs if c.activo)}")
        print(f"   ⚪ Inactivas: {sum(1 for c in configs if not c.activo)}")
        print("\n" + "-"*80 + "\n")
        
        # 2. Para cada configuración, consultar su historial
        query_historial = """
            SELECT 
                COUNT(*) as total_envios,
                MAX(fecha_envio) as ultimo_envio,
                MIN(fecha_envio) as primer_envio,
                SUM(CASE WHEN exitoso = TRUE THEN 1 ELSE 0 END) as exitosos,
                SUM(CASE WHEN exitoso = FALSE THEN 1 ELSE 0 END) as fallidos
            FROM historial_envios_dian_vs_erp
            WHERE configuracion_id = :config_id
        """
        
        configs_con_uso = []
        configs_sin_uso = []
        
        for config in configs:
            historial = db.session.execute(
                db.text(query_historial), 
                {'config_id': config.id}
            ).fetchone()
            
            estado_emoji = "✅" if config.activo else "⚪"
            tipo_emoji = {
                'PENDIENTES_DIAS': '⚠️',
                'SIN_ACUSES': '📋',
                'SUPERVISION': '🔔',
                'PERSONALIZADO': '⚙️'
            }.get(config.tipo, '📊')
            
            info = {
                'id': config.id,
                'nombre': config.nombre,
                'tipo': config.tipo,
                'activo': config.activo,
                'total_envios': historial.total_envios or 0,
                'ultimo_envio': historial.ultimo_envio,
                'primer_envio': historial.primer_envio,
                'exitosos': historial.exitosos or 0,
                'fallidos': historial.fallidos or 0,
                'proximo_envio': config.proximo_envio,
                'frecuencia': config.frecuencia,
                'hora_envio': config.hora_envio
            }
            
            if info['total_envios'] > 0:
                configs_con_uso.append(info)
            else:
                configs_sin_uso.append(info)
        
        # 3. Mostrar configuraciones CON USO
        print("✅ CONFIGURACIONES CON HISTORIAL DE ENVÍOS (EN USO)")
        print("="*80)
        
        if configs_con_uso:
            for cfg in configs_con_uso:
                estado = "✅ ACTIVA" if cfg['activo'] else "⚪ INACTIVA"
                
                print(f"\n{cfg['id']}. {cfg['nombre']}")
                print(f"   Estado: {estado}")
                print(f"   Tipo: {cfg['tipo']}")
                print(f"   Total envíos: {cfg['total_envios']}")
                print(f"   ✅ Exitosos: {cfg['exitosos']} ({cfg['exitosos']*100//cfg['total_envios'] if cfg['total_envios'] > 0 else 0}%)")
                print(f"   ❌ Fallidos: {cfg['fallidos']} ({cfg['fallidos']*100//cfg['total_envios'] if cfg['total_envios'] > 0 else 0}%)")
                
                if cfg['primer_envio']:
                    print(f"   📅 Primer envío: {cfg['primer_envio'].strftime('%Y-%m-%d %H:%M:%S')}")
                if cfg['ultimo_envio']:
                    dias_desde = (datetime.now() - cfg['ultimo_envio']).days
                    print(f"   📅 Último envío: {cfg['ultimo_envio'].strftime('%Y-%m-%d %H:%M:%S')} (hace {dias_desde} días)")
                
                if cfg['proximo_envio']:
                    print(f"   ⏰ Próximo envío: {cfg['proximo_envio'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                print(f"   🔄 Frecuencia: {cfg['frecuencia']} a las {cfg['hora_envio']}")
        else:
            print("   (Ninguna configuración tiene historial de envíos)")
        
        # 4. Mostrar configuraciones SIN USO
        print("\n\n" + "="*80)
        print("⚪ CONFIGURACIONES SIN HISTORIAL (NO USADAS AÚN)")
        print("="*80)
        
        if configs_sin_uso:
            for cfg in configs_sin_uso:
                estado = "✅ ACTIVA" if cfg['activo'] else "⚪ INACTIVA"
                
                print(f"\n{cfg['id']}. {cfg['nombre']}")
                print(f"   Estado: {estado}")
                print(f"   Tipo: {cfg['tipo']}")
                print(f"   Total envíos: 0 (nunca se ha ejecutado)")
                
                if cfg['proximo_envio']:
                    print(f"   ⏰ Próximo envío programado: {cfg['proximo_envio'].strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print(f"   ⚠️ Sin próximo envío programado")
                
                print(f"   🔄 Frecuencia: {cfg['frecuencia']} a las {cfg['hora_envio']}")
        else:
            print("   (Todas las configuraciones tienen historial de envíos)")
        
        # 5. Resumen final
        print("\n\n" + "="*80)
        print("📊 RESUMEN")
        print("="*80)
        
        total_activas_con_uso = sum(1 for c in configs_con_uso if c['activo'])
        total_inactivas_con_uso = sum(1 for c in configs_con_uso if not c['activo'])
        total_activas_sin_uso = sum(1 for c in configs_sin_uso if c['activo'])
        total_inactivas_sin_uso = sum(1 for c in configs_sin_uso if not c['activo'])
        
        print(f"\n✅ Configuraciones ACTIVAS:")
        print(f"   • Con uso (se han ejecutado): {total_activas_con_uso}")
        print(f"   • Sin uso (nunca ejecutadas): {total_activas_sin_uso}")
        print(f"   • Total activas: {total_activas_con_uso + total_activas_sin_uso}")
        
        print(f"\n⚪ Configuraciones INACTIVAS:")
        print(f"   • Con uso (se ejecutaron antes): {total_inactivas_con_uso}")
        print(f"   • Sin uso (nunca usadas): {total_inactivas_sin_uso}")
        print(f"   • Total inactivas: {total_inactivas_con_uso + total_inactivas_sin_uso}")
        
        total_envios_sistema = sum(c['total_envios'] for c in configs_con_uso)
        total_exitosos_sistema = sum(c['exitosos'] for c in configs_con_uso)
        total_fallidos_sistema = sum(c['fallidos'] for c in configs_con_uso)
        
        print(f"\n📈 ESTADÍSTICAS GLOBALES:")
        print(f"   • Total envíos ejecutados: {total_envios_sistema}")
        print(f"   • ✅ Exitosos: {total_exitosos_sistema} ({total_exitosos_sistema*100//total_envios_sistema if total_envios_sistema > 0 else 0}%)")
        print(f"   • ❌ Fallidos: {total_fallidos_sistema} ({total_fallidos_sistema*100//total_envios_sistema if total_envios_sistema > 0 else 0}%)")
        
        # 6. Envíos recientes (últimos 7 días)
        fecha_hace_7_dias = datetime.now() - timedelta(days=7)
        
        query_recientes = """
            SELECT 
                he.configuracion_id,
                ep.nombre,
                he.fecha_envio,
                he.exitoso,
                he.mensaje
            FROM historial_envios_dian_vs_erp he
            JOIN envios_programados_dian_vs_erp ep ON he.configuracion_id = ep.id
            WHERE he.fecha_envio >= :fecha_limite
            ORDER BY he.fecha_envio DESC
            LIMIT 20
        """
        
        envios_recientes = db.session.execute(
            db.text(query_recientes),
            {'fecha_limite': fecha_hace_7_dias}
        ).fetchall()
        
        if envios_recientes:
            print(f"\n\n" + "="*80)
            print(f"📅 ÚLTIMOS ENVÍOS (últimos 7 días)")
            print("="*80 + "\n")
            
            for envio in envios_recientes:
                estado_emoji = "✅" if envio.exitoso else "❌"
                print(f"{estado_emoji} {envio.fecha_envio.strftime('%Y-%m-%d %H:%M:%S')} | {envio.nombre}")
                if envio.mensaje:
                    print(f"   📝 {envio.mensaje[:100]}{'...' if len(envio.mensaje) > 100 else ''}")
        
        print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    try:
        verificar_envios_usados()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
