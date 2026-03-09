"""
Sistema de Monitoreo y Alertas Automáticas - SAGRILAFT
Monitorea radicados y envía alertas de vencimiento automáticamente

LÓGICA:
- Alerta inicial: Cuando quedan 20 días para vencer (340 días desde última actualización)
- Recordatorio: Si no hay nuevo radicado después de 8 días del primer correo
- Vencimiento: 360 días desde la última actualización del radicado
"""
from datetime import datetime, timedelta
from flask import current_app
from extensions import db
from modules.sagrilaft.email_sagrilaft import enviar_correo_alerta_vencimiento
import logging

# Logger para monitoreo
monitor_logger = logging.getLogger('sagrilaft_monitor')

class MonitorVencimientos:
    """Clase para monitorear vencimientos y enviar alertas"""
    
    @staticmethod
    def obtener_radicados_proximos_vencer():
        """
        Obtiene radicados que están próximos a vencer (20 días o menos)
        
        Returns:
            list: Lista de tuplas (radicado, tercero, dias_restantes, fecha_vencimiento)
        """
        from app import SolicitudRegistro, Tercero
        
        try:
            # Fecha actual
            hoy = datetime.now()
            
            # Obtener último radicado APROBADO de cada tercero
            # Subconsulta para obtener el último radicado por tercero
            subquery = db.session.query(
                SolicitudRegistro.tercero_id,
                db.func.max(SolicitudRegistro.fecha_actualizacion).label('ultima_fecha')
            ).filter(
                SolicitudRegistro.estado == 'aprobado'
            ).group_by(
                SolicitudRegistro.tercero_id
            ).subquery()
            
            # Query principal: obtener radicados que coincidan con la última fecha
            radicados_ultimos = db.session.query(
                SolicitudRegistro,
                Tercero
            ).join(
                Tercero, Tercero.id == SolicitudRegistro.tercero_id
            ).join(
                subquery,
                db.and_(
                    SolicitudRegistro.tercero_id == subquery.c.tercero_id,
                    SolicitudRegistro.fecha_actualizacion == subquery.c.ultima_fecha
                )
            ).filter(
                SolicitudRegistro.estado == 'aprobado',
                Tercero.email.isnot(None),  # Solo terceros con email
                Tercero.email != ''
            ).all()
            
            resultados = []
            
            for solicitud, tercero in radicados_ultimos:
                # Calcular días desde última actualización
                fecha_ultimo_rad = solicitud.fecha_actualizacion or solicitud.fecha_registro
                dias_transcurridos = (hoy - fecha_ultimo_rad).days
                
                # Calcular días restantes para los 360 días
                dias_restantes = 360 - dias_transcurridos
                fecha_vencimiento = fecha_ultimo_rad + timedelta(days=360)
                
                # Solo incluir si quedan 20 días o menos
                if dias_restantes <= 20 and dias_restantes > 0:
                    resultados.append({
                        'radicado': solicitud.radicado,
                        'tercero_id': tercero.id,
                        'nit': tercero.nit,
                        'razon_social': tercero.razon_social,
                        'email': tercero.email,
                        'dias_restantes': dias_restantes,
                        'fecha_vencimiento': fecha_vencimiento,
                        'fecha_ultimo_radicado': fecha_ultimo_rad
                    })
            
            return resultados
            
        except Exception as e:
            monitor_logger.error(f"Error obteniendo radicados próximos a vencer: {e}")
            return []
    
    @staticmethod
    def registrar_envio_alerta(tercero_id, radicado, tipo_envio='alerta_inicial'):
        """
        Registra el envío de una alerta en la base de datos
        
        Args:
            tercero_id: ID del tercero
            radicado: Número de radicado
            tipo_envio: 'alerta_inicial' o 'recordatorio'
        
        Returns:
            bool: True si se registró correctamente
        """
        from app import AlertaVencimiento
        
        try:
            # Buscar si ya existe registro de alerta para este tercero
            alerta = AlertaVencimiento.query.filter_by(
                tercero_id=tercero_id,
                radicado=radicado
            ).first()
            
            if alerta:
                # Actualizar registro existente
                if tipo_envio == 'alerta_inicial':
                    alerta.fecha_primera_alerta = datetime.now()
                elif tipo_envio == 'recordatorio':
                    alerta.fecha_recordatorio = datetime.now()
                    alerta.recordatorio_enviado = True
            else:
                # Crear nuevo registro
                alerta = AlertaVencimiento(
                    tercero_id=tercero_id,
                    radicado=radicado,
                    fecha_primera_alerta=datetime.now() if tipo_envio == 'alerta_inicial' else None,
                    fecha_recordatorio=datetime.now() if tipo_envio == 'recordatorio' else None,
                    recordatorio_enviado=(tipo_envio == 'recordatorio')
                )
                db.session.add(alerta)
            
            db.session.commit()
            return True
            
        except Exception as e:
            monitor_logger.error(f"Error registrando envío de alerta: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def necesita_recordatorio(tercero_id, radicado):
        """
        Verifica si un tercero necesita recordatorio (8 días después de primera alerta)
        
        Args:
            tercero_id: ID del tercero
            radicado: Número de radicado
        
        Returns:
            bool: True si necesita recordatorio
        """
        from app import AlertaVencimiento, SolicitudRegistro
        
        try:
            # Buscar registro de alerta
            alerta = AlertaVencimiento.query.filter_by(
                tercero_id=tercero_id,
                radicado=radicado
            ).first()
            
            if not alerta or not alerta.fecha_primera_alerta:
                return False  # No hay alerta inicial
            
            if alerta.recordatorio_enviado:
                return False  # Ya se envió recordatorio
            
            # Verificar si han pasado 8 días desde primera alerta
            dias_desde_alerta = (datetime.now() - alerta.fecha_primera_alerta).days
            
            if dias_desde_alerta < 8:
                return False  # Aún no han pasado 8 días
            
            # Verificar si el tercero NO ha generado nuevo radicado
            nuevo_radicado = SolicitudRegistro.query.filter(
                SolicitudRegistro.tercero_id == tercero_id,
                SolicitudRegistro.fecha_registro > alerta.fecha_primera_alerta
            ).first()
            
            if nuevo_radicado:
                return False  # Ya generó nuevo radicado
            
            return True  # Necesita recordatorio
            
        except Exception as e:
            monitor_logger.error(f"Error verificando recordatorio: {e}")
            return False
    
    @staticmethod
    def enviar_alertas_automaticas():
        """
        Proceso principal: Envía alertas y recordatorios automáticamente
        
        Returns:
            dict: Estadísticas del proceso
        """
        with current_app.app_context():
            from app import mail
            
            stats = {
                'alertas_enviadas': 0,
                'recordatorios_enviados': 0,
                'errores': 0,
                'procesados': 0
            }
            
            try:
                # 1. Obtener radicados próximos a vencer
                radicados_vencer = MonitorVencimientos.obtener_radicados_proximos_vencer()
                
                monitor_logger.info(f"📊 Radicados próximos a vencer: {len(radicados_vencer)}")
                
                for item in radicados_vencer:
                    stats['procesados'] += 1
                    
                    try:
                        # 2. Verificar si necesita recordatorio
                        if MonitorVencimientos.necesita_recordatorio(item['tercero_id'], item['radicado']):
                            # Enviar recordatorio
                            success, msg = enviar_correo_alerta_vencimiento(
                                mail=mail,
                                destinatario=item['email'],
                                nit=item['nit'],
                                razon_social=item['razon_social'],
                                radicado=item['radicado'],
                                dias_restantes=item['dias_restantes'],
                                fecha_vencimiento=item['fecha_vencimiento']
                            )
                            
                            if success:
                                MonitorVencimientos.registrar_envio_alerta(
                                    item['tercero_id'],
                                    item['radicado'],
                                    'recordatorio'
                                )
                                stats['recordatorios_enviados'] += 1
                                monitor_logger.info(f"🔔 Recordatorio enviado: {item['radicado']} - {item['email']}")
                            else:
                                stats['errores'] += 1
                                monitor_logger.error(f"❌ Error recordatorio {item['radicado']}: {msg}")
                        
                        else:
                            # 3. Verificar si ya se envió alerta inicial
                            from app import AlertaVencimiento
                            alerta_existente = AlertaVencimiento.query.filter_by(
                                tercero_id=item['tercero_id'],
                                radicado=item['radicado']
                            ).first()
                            
                            if not alerta_existente or not alerta_existente.fecha_primera_alerta:
                                # Enviar alerta inicial
                                success, msg = enviar_correo_alerta_vencimiento(
                                    mail=mail,
                                    destinatario=item['email'],
                                    nit=item['nit'],
                                    razon_social=item['razon_social'],
                                    radicado=item['radicado'],
                                    dias_restantes=item['dias_restantes'],
                                    fecha_vencimiento=item['fecha_vencimiento']
                                )
                                
                                if success:
                                    MonitorVencimientos.registrar_envio_alerta(
                                        item['tercero_id'],
                                        item['radicado'],
                                        'alerta_inicial'
                                    )
                                    stats['alertas_enviadas'] += 1
                                    monitor_logger.info(f"📧 Alerta inicial enviada: {item['radicado']} - {item['email']}")
                                else:
                                    stats['errores'] += 1
                                    monitor_logger.error(f"❌ Error alerta {item['radicado']}: {msg}")
                    
                    except Exception as e:
                        stats['errores'] += 1
                        monitor_logger.error(f"❌ Error procesando {item['radicado']}: {e}")
                
                # Log del resumen
                monitor_logger.info(f"""
📊 RESUMEN MONITOREO SAGRILAFT:
   - Procesados: {stats['procesados']}
   - Alertas enviadas: {stats['alertas_enviadas']}
   - Recordatorios enviados: {stats['recordatorios_enviados']}
   - Errores: {stats['errores']}
""")
                
                return stats
                
            except Exception as e:
                monitor_logger.error(f"❌ Error en proceso de alertas automáticas: {e}")
                return stats


# Función para ejecutar desde línea de comandos o cron
def ejecutar_monitoreo():
    """Ejecuta el monitoreo de vencimientos"""
    from app import app
    
    with app.app_context():
        monitor = MonitorVencimientos()
        stats = monitor.enviar_alertas_automaticas()
        print(f"\n{'='*60}")
        print(f"  MONITOREO SAGRILAFT - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print(f"{'='*60}")
        print(f"  Radicados procesados: {stats['procesados']}")
        print(f"  Alertas enviadas: {stats['alertas_enviadas']}")
        print(f"  Recordatorios enviados: {stats['recordatorios_enviados']}")
        print(f"  Errores: {stats['errores']}")
        print(f"{'='*60}\n")


if __name__ == '__main__':
    ejecutar_monitoreo()
