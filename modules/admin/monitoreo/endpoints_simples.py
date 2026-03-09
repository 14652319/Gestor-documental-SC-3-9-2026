"""
Endpoints simplificados para el panel de monitoreo
Versión de respaldo que devuelve datos mock/vacíos en lugar de errores 500
Fecha: Octubre 23, 2025
"""

from flask import jsonify, request
from datetime import datetime, timedelta
from . import monitoreo_bp

# ========================================================================
# 📊 DASHBOARD: ESTADÍSTICAS SIMPLES
# ========================================================================

@monitoreo_bp.route('/api/stats_simple', methods=['GET'])
def stats_simple():
    """Stats básicas sin consultas complejas"""
    return jsonify({
        'success': True,
        'data': {
            'usuarios_conectados': 0,
            'total_usuarios': 0,
            'ips_bloqueadas': 0,
            'alertas_pendientes': 0,
            'usuarios_por_hora': [],
            'modulos_uso': [],
            'logins_fallidos': [],
            'top_ips': [],
            'distribucion_geo': []
        }
    })


# ========================================================================
# 👥 USUARIOS: LISTADO SIMPLE
# ========================================================================

@monitoreo_bp.route('/api/usuarios_simple', methods=['GET'])
def usuarios_simple():
    """Lista de usuarios sin geo ni sesiones"""
    try:
        from app import Usuario, Tercero
        
        usuarios = Usuario.query.join(Tercero).limit(100).all()
        resultado = []
        
        for user in usuarios:
            resultado.append({
                'usuario': user.usuario,
                'nit': user.tercero.nit if user.tercero else 'N/A',
                'razon_social': user.tercero.razon_social if user.tercero else 'N/A',
                'estado': 'Activo' if user.activo else 'Inactivo',
                'correo': user.correo or 'N/A',
                'ultima_conexion': 'Nunca',
                'ubicacion': 'Desconocido',
                'modulo_actual': 'N/A'
            })
        
        return jsonify({
            'success': True,
            'data': resultado,
            'total': len(resultado)
        })
        
    except Exception as e:
        return jsonify({
            'success': True,
            'data': [],
            'total': 0,
            'mensaje': f'Sin datos: {str(e)}'
        })


# ========================================================================
# 🌐 IPS: LISTADO SIMPLE
# ========================================================================

@monitoreo_bp.route('/api/ips_simple', methods=['GET'])
def ips_simple():
    """Lista de IPs sin geo"""
    try:
        from app import Acceso, Usuario
        from sqlalchemy import func
        
        # IPs únicas de los últimos accesos
        ips_query = Acceso.query.with_entities(
            Acceso.ip,
            func.count(Acceso.id).label('total_accesos'),
            func.max(Acceso.fecha).label('ultima_conexion')
        ).group_by(Acceso.ip).limit(50).all()
        
        resultado = []
        for ip, total, ultima in ips_query:
            resultado.append({
                'ip': ip,
                'ubicacion': 'Colombia (Red Local)' if ip.startswith('192.168') or ip == '127.0.0.1' else 'Desconocido',
                'usuarios': 1,
                'estado': 'Normal',
                'primera_conexion': ultima.strftime('%Y-%m-%d %H:%M') if ultima else 'Desconocido',
                'ultima_conexion': ultima.strftime('%Y-%m-%d %H:%M') if ultima else 'Desconocido',
                'total_accesos': total
            })
        
        return jsonify({
            'success': True,
            'data': resultado,
            'total': len(resultado)
        })
        
    except Exception as e:
        return jsonify({
            'success': True,
            'data': [],
            'total': 0,
            'mensaje': f'Sin datos: {str(e)}'
        })


# ========================================================================
# 💾 ESPACIO: INFO SIMPLE
# ========================================================================

@monitoreo_bp.route('/api/disk_simple', methods=['GET'])
def disk_simple():
    """Info de disco sin cálculos complejos"""
    import psutil
    
    try:
        discos = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                discos.append({
                    'dispositivo': partition.device,
                    'punto_montaje': partition.mountpoint,
                    'total_gb': round(usage.total / (1024 ** 3), 2),
                    'usado_gb': round(usage.used / (1024 ** 3), 2),
                    'libre_gb': round(usage.free / (1024 ** 3), 2),
                    'porcentaje_usado': usage.percent
                })
            except:
                pass
        
        return jsonify({
            'success': True,
            'data': {
                'discos': discos,
                'carpetas': [],
                'base_datos': {
                    'tamano_mb': 0,
                    'tablas': 0
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'mensaje': f'Error: {str(e)}'
        }), 500


# ========================================================================
# 🚨 ALERTAS: LISTA SIMPLE
# ========================================================================

@monitoreo_bp.route('/api/alertas_simple', methods=['GET'])
def alertas_simple():
    """Alertas sin filtros complejos"""
    try:
        from .models import AlertaSeguridad
        from sqlalchemy import desc
        
        solo_pendientes = request.args.get('solo_pendientes', 'false').lower() == 'true'
        
        query = AlertaSeguridad.query
        if solo_pendientes:
            query = query.filter_by(resuelta=False)
        
        alertas = query.order_by(desc(AlertaSeguridad.fecha_alerta)).limit(100).all()
        
        return jsonify({
            'success': True,
            'data': [alerta.to_dict() for alerta in alertas]
        })
        
    except Exception as e:
        return jsonify({
            'success': True,
            'data': [],
            'mensaje': f'Sin alertas: {str(e)}'
        })
