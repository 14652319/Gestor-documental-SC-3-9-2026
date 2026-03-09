"""
Consulta simple para ver envíos programados en uso
"""
import psycopg2
from datetime import datetime

def ejecutar_consulta():
    try:
        # Usar las credenciales correctas del .env
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='gestor_documental',
            user='postgres',
            password='G3st0radm$2025.'
        )
        cursor = conn.cursor()
        
        print("\n" + "="*100)
        print("📊 ANÁLISIS DE ENVÍOS PROGRAMADOS - MÓDULO DIAN VS ERP")
        print("="*100 + "\n")
        
        # Consulta 1: Configuraciones con su historial
        query1 = """
            SELECT 
                ep.id,
                ep.nombre,
                ep.tipo,
                ep.activo,
                ep.frecuencia,
                ep.hora_envio,
                ep.proximo_envio,
                COUNT(he.id) as total_envios,
                SUM(CASE WHEN he.estado = 'EXITOSO' THEN 1 ELSE 0 END) as envios_exitosos,
                SUM(CASE WHEN he.estado = 'ERROR' THEN 1 ELSE 0 END) as envios_fallidos,
                MAX(he.fecha_ejecucion) as ultimo_envio,
                MIN(he.fecha_ejecucion) as primer_envio
            FROM envios_programados_dian_vs_erp ep
            LEFT JOIN historial_envios_dian_vs_erp he ON ep.id = he.configuracion_id
            GROUP BY ep.id, ep.nombre, ep.tipo, ep.activo, ep.frecuencia, ep.hora_envio, ep.proximo_envio
            ORDER BY 
                ep.activo DESC,
                COUNT(he.id) DESC,
                ep.nombre
        """
        
        cursor.execute(query1)
        configs = cursor.fetchall()
        
        configs_con_uso = [c for c in configs if c[7] > 0]
        configs_sin_uso = [c for c in configs if c[7] == 0]
        
        # Mostrar configuraciones CON USO
        print("✅ CONFIGURACIONES CON HISTORIAL DE ENVÍOS (SE HAN USADO)")
        print("="*100)
        
        if configs_con_uso:
            for cfg in configs_con_uso:
                id_, nombre, tipo, activo, freq, hora, proximo, total, exitosos, fallidos, ultimo, primero = cfg
                
                estado = "✅ ACTIVA" if activo else "⚪ INACTIVA"
                tipo_emoji = {
                    'PENDIENTES_DIAS': '⚠️ Pendientes',
                    'SIN_ACUSES': '📋 Sin Acuses',
                    'SUPERVISION': '🔔 Supervisión'
                }.get(tipo, tipo)
                
                print(f"\n📌 ID {id_}: {nombre}")
                print(f"   Estado: {estado}")
                print(f"   Tipo: {tipo_emoji}")
                print(f"   📊 Total envíos: {total}")
                
                if total > 0:
                    tasa_exito = (exitosos * 100) // total if total > 0 else 0
                    print(f"   ✅ Exitosos: {exitosos} ({tasa_exito}%)")
                    print(f"   ❌ Fallidos: {fallidos} ({100-tasa_exito}%)")
                
                if primero:
                    print(f"   📅 Primer envío: {primero.strftime('%Y-%m-%d %H:%M')}")
                
                if ultimo:
                    dias_desde = (datetime.now() - ultimo).days
                    print(f"   📅 Último envío: {ultimo.strftime('%Y-%m-%d %H:%M')} (hace {dias_desde} días)")
                
                if proximo:
                    print(f"   ⏰ Próximo: {proximo.strftime('%Y-%m-%d %H:%M')}")
                
                print(f"   🔄 Frecuencia: {freq} a las {hora}")
        else:
            print("\n   (Ninguna configuración tiene historial)")
        
        # Mostrar configuraciones SIN USO
        print("\n\n" + "="*100)
        print("⚪ CONFIGURACIONES SIN HISTORIAL (NUNCA SE HAN EJECUTADO)")
        print("="*100)
        
        if configs_sin_uso:
            for cfg in configs_sin_uso:
                id_, nombre, tipo, activo, freq, hora, proximo, total, exitosos, fallidos, ultimo, primero = cfg
                
                estado = "✅ ACTIVA" if activo else "⚪ INACTIVA"
                tipo_emoji = {
                    'PENDIENTES_DIAS': '⚠️ Pendientes',
                    'SIN_ACUSES': '📋 Sin Acuses',
                    'SUPERVISION': '🔔 Supervisión'
                }.get(tipo, tipo)
                
                print(f"\n📌 ID {id_}: {nombre}")
                print(f"   Estado: {estado}")
                print(f"   Tipo: {tipo_emoji}")
                print(f"   📊 Total envíos: 0 (nunca ejecutada)")
                
                if proximo:
                    print(f"   ⏰ Próximo envío: {proximo.strftime('%Y-%m-%d %H:%M')}")
                else:
                    print(f"   ⚠️ Sin próximo envío programado")
                
                print(f"   🔄 Frecuencia: {freq} a las {hora}")
        else:
            print("\n   (Todas las configuraciones tienen historial)")
        
        # Resumen
        print("\n\n" + "="*100)
        print("📊 RESUMEN EJECUTIVO")
        print("="*100)
        
        total_activas = sum(1 for c in configs if c[3])
        total_inactivas = sum(1 for c in configs if not c[3])
        activas_con_uso = sum(1 for c in configs_con_uso if c[3])
        activas_sin_uso = sum(1 for c in configs_sin_uso if c[3])
        
        print(f"\n✅ Configuraciones ACTIVAS: {total_activas}")
        print(f"   • Con historial (se han ejecutado): {activas_con_uso}")
        print(f"   • Sin historial (nunca ejecutadas): {activas_sin_uso}")
        
        print(f"\n⚪ Configuraciones INACTIVAS: {total_inactivas}")
        
        total_envios = sum(c[7] for c in configs)
        total_exitosos = sum(c[8] if c[8] else 0 for c in configs)
        total_fallidos = sum(c[9] if c[9] else 0 for c in configs)
        
        print(f"\n📈 ESTADÍSTICAS GLOBALES:")
        print(f"   • Total envíos ejecutados: {total_envios}")
        if total_envios > 0:
            print(f"   • ✅ Exitosos: {total_exitosos} ({(total_exitosos*100)//total_envios}%)")
            print(f"   • ❌ Fallidos: {total_fallidos} ({(total_fallidos*100)//total_envios}%)")
        
        # Últimos envíos
        print("\n\n" + "="*100)
        print("📅 ÚLTIMOS 15 ENVÍOS EJECUTADOS")
        print("="*100 + "\n")
        
        query2 = """
            SELECT 
                he.fecha_ejecucion,
                ep.nombre,
                he.estado,
                he.mensaje
            FROM historial_envios_dian_vs_erp he
            JOIN envios_programados_dian_vs_erp ep ON he.configuracion_id = ep.id
            ORDER BY he.fecha_ejecucion DESC
            LIMIT 15
        """
        
        cursor.execute(query2)
        ultimos = cursor.fetchall()
        
        if ultimos:
            for envio in ultimos:
                fecha, nombre, estado, mensaje = envio
                estado_emoji = "✅" if estado == 'EXITOSO' else "❌" if estado == 'ERROR' else "⚠️"
                
                print(f"{estado_emoji} {fecha.strftime('%Y-%m-%d %H:%M:%S')} | {nombre}")
                if mensaje:
                    msg_corto = mensaje[:80] + "..." if len(mensaje) > 80 else mensaje
                    print(f"   📝 {msg_corto}")
        else:
            print("   (No hay historial de envíos)")
        
        print("\n" + "="*100 + "\n")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    ejecutar_consulta()
