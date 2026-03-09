"""
Rutas del Módulo de Monitoreo y Administración
"""

import os
import psutil
import shutil
from flask import render_template, jsonify, request, session, redirect, url_for, send_file
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from extensions import db
from . import monitoreo_bp
from .models import AlertaSeguridad, LogAccion, SesionActiva

# Importar utilidades del módulo
try:
    from .utils import formatear_duracion, obtener_tamano_carpeta, formatear_bytes, obtener_geolocalizacion_ip
    UTILS_DISPONIBLES = True
except ImportError as e:
    print(f"⚠️ ADVERTENCIA: No se pudieron importar utilidades: {e}")
    UTILS_DISPONIBLES = False
    # Funciones fallback
    def formatear_duracion(segundos):
        if segundos < 60:
            return f"{segundos}s"
        elif segundos < 3600:
            return f"{segundos // 60}m"
        else:
            return f"{segundos // 3600}h"
    
    def formatear_bytes(bytes_count):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} PB"
    
    def obtener_tamano_carpeta(ruta):
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(ruta):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total += os.path.getsize(filepath)
        except:
            pass
        return total
    
    def obtener_geolocalizacion_ip(ip):
        return {
            'pais': 'Desconocido',
            'ciudad': 'Desconocido',
            'es_local': False
        }

# Importar log_security y modelos de forma lazy para evitar importación circular
# Los modelos se importarán dentro de las funciones cuando se necesiten
def get_app_models():
    """Importación lazy de modelos de app.py para evitar circular imports"""
    import sys
    # Obtener el módulo app si ya está importado
    if 'app' in sys.modules:
        app_module = sys.modules['app']
    else:
        import app as app_module
    
    return (
        app_module.Usuario,
        app_module.Tercero,
        app_module.IPListaNegra,
        app_module.IPSospechosa,
        app_module.Acceso,
        app_module.log_security
    )


# ==============================================
# 🔒 FUNCIÓN: VALIDAR SESIÓN DE ADMINISTRADOR
# ==============================================

def validar_sesion_admin():
    """
    Valida que el usuario tenga sesión activa y sea administrador.
    """
    if 'usuario_id' not in session or 'usuario' not in session:
        return False, {"error": "Sesión no válida", "redirect": "/login"}, 401
    
    # Verificar que sea administrador (opcional: agregar campo rol a Usuario)
    usuario = session.get('usuario')
    # Por ahora permitimos acceso a cualquier usuario autenticado
    # TODO: Implementar verificación de rol de administrador
    
    return True, None, None


# ==============================================
# 🌐 RUTA: PÁGINA PRINCIPAL DE MONITOREO
# ==============================================

@monitoreo_bp.route('/')
@monitoreo_bp.route('/dashboard')
def dashboard():
    """
    Renderiza la página principal del panel de monitoreo con el nuevo template moderno.
    """
    valido, respuesta, codigo = validar_sesion_admin()
    
    if not valido:
        return redirect('/')
    
    return render_template('monitor_nuevo.html', usuario=session.get('usuario'))


# ==============================================
# � RUTA: DIAGNÓSTICO DEL SISTEMA
# ==============================================

@monitoreo_bp.route('/api/diagnostico', methods=['GET'])
def diagnostico():
    """
    Endpoint de diagnóstico para verificar el estado del sistema
    """
    try:
        Usuario, Tercero, IPListaNegra, IPSospechosa, Acceso, log_security = get_app_models()
        
        return jsonify({
            'success': True,
            'mensaje': 'Sistema funcionando correctamente',
            'datos': {
                'utils_disponibles': UTILS_DISPONIBLES,
                'total_usuarios': Usuario.query.count(),
                'total_terceros': Tercero.query.count(),
                'total_accesos': Acceso.query.count(),
                'sesion_usuario': session.get('usuario'),
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'tipo_error': type(e).__name__
        }), 500


# ==============================================
# �📊 RUTA: ESTADÍSTICAS GENERALES DEL SISTEMA
# ==============================================

@monitoreo_bp.route('/api/stats', methods=['GET'])
def obtener_estadisticas():
    """
    Retorna estadísticas generales del sistema.
    """
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    # Importar modelos para evitar circular imports
    Usuario, Tercero, IPListaNegra, IPSospechosa, Acceso, log_security = get_app_models()
    
    try:
        # Estadísticas de usuarios
        total_usuarios = Usuario.query.count()
        usuarios_activos = Usuario.query.filter_by(activo=True).count()
        usuarios_inactivos = total_usuarios - usuarios_activos
        
        # Estadísticas de terceros
        total_terceros = Tercero.query.count()
        
        # Estadísticas de IPs
        ips_bloqueadas = IPListaNegra.query.count()
        ips_sospechosas = IPSospechosa.query.filter_by(bloqueada=True).count()
        
        # Estadísticas de accesos (últimas 24 horas)
        hace_24h = datetime.utcnow() - timedelta(hours=24)
        accesos_24h = Acceso.query.filter(Acceso.fecha >= hace_24h).count()
        accesos_exitosos = Acceso.query.filter(
            Acceso.fecha >= hace_24h,
            Acceso.exito == True
        ).count()
        accesos_fallidos = accesos_24h - accesos_exitosos
        
        # Estadísticas de alertas (últimos 7 días)
        hace_7d = datetime.utcnow() - timedelta(days=7)
        alertas_totales = AlertaSeguridad.query.filter(
            AlertaSeguridad.fecha_alerta >= hace_7d
        ).count()
        alertas_pendientes = AlertaSeguridad.query.filter(
            AlertaSeguridad.fecha_alerta >= hace_7d,
            AlertaSeguridad.resuelta == False
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'usuarios': {
                    'total': total_usuarios,
                    'activos': usuarios_activos,
                    'inactivos': usuarios_inactivos
                },
                'terceros': {
                    'total': total_terceros
                },
                'seguridad': {
                    'ips_bloqueadas': ips_bloqueadas,
                    'ips_sospechosas': ips_sospechosas
                },
                'accesos_24h': {
                    'total': accesos_24h,
                    'exitosos': accesos_exitosos,
                    'fallidos': accesos_fallidos
                },
                'alertas_7d': {
                    'total': alertas_totales,
                    'pendientes': alertas_pendientes,
                    'resueltas': alertas_totales - alertas_pendientes
                }
            }
        })
    
    except Exception as e:
        log_security(f"ERROR OBTENIENDO STATS | error={str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ==============================================
# 💾 RUTA: USO DE DISCO
# ==============================================

@monitoreo_bp.route('/api/disk_usage', methods=['GET'])
def obtener_uso_disco():
    """
    Retorna información sobre el uso de disco del sistema.
    """
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    # Importar modelos para evitar circular imports
    Usuario, Tercero, IPListaNegra, IPSospechosa, Acceso, log_security = get_app_models()
    
    try:
        # Obtener ruta raíz del proyecto
        proyecto_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # Información del sistema de archivos principal
        disk_usage = psutil.disk_usage('/')
        
        # Calcular tamaño de carpetas específicas del proyecto
        carpetas_importantes = {}
        carpetas_a_analizar = [
            'documentos_terceros',
            'documentos_causacion',
            'temp_firma',
            'logs',
            'modules'
        ]
        
        for carpeta in carpetas_a_analizar:
            carpeta_path = os.path.join(proyecto_path, carpeta)
            if os.path.exists(carpeta_path):
                try:
                    # Calcular tamaño de la carpeta
                    total_size = 0
                    file_count = 0
                    for dirpath, dirnames, filenames in os.walk(carpeta_path):
                        for filename in filenames:
                            filepath = os.path.join(dirpath, filename)
                            if os.path.exists(filepath):
                                total_size += os.path.getsize(filepath)
                                file_count += 1
                    
                    carpetas_importantes[carpeta] = {
                        'size_bytes': total_size,
                        'size_mb': round(total_size / (1024 * 1024), 2),
                        'size_gb': round(total_size / (1024 * 1024 * 1024), 2),
                        'file_count': file_count
                    }
                except Exception as e:
                    carpetas_importantes[carpeta] = {'error': str(e)}
        
        return jsonify({
            'success': True,
            'data': {
                'sistema': {
                    'total_gb': round(disk_usage.total / (1024 ** 3), 2),
                    'usado_gb': round(disk_usage.used / (1024 ** 3), 2),
                    'libre_gb': round(disk_usage.free / (1024 ** 3), 2),
                    'porcentaje_usado': disk_usage.percent
                },
                'carpetas_proyecto': carpetas_importantes,
                'proyecto_path': proyecto_path
            }
        })
    
    except Exception as e:
        log_security(f"ERROR OBTENIENDO USO DISCO | error={str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ==============================================
# 🚫 RUTA: IPS BLOQUEADAS Y SOSPECHOSAS
# ==============================================

@monitoreo_bp.route('/api/ips_bloqueadas', methods=['GET'])
def listar_ips_bloqueadas():
    """
    Lista todas las IPs bloqueadas y sospechosas.
    """
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    # Importar modelos para evitar circular imports
    Usuario, Tercero, IPListaNegra, IPSospechosa, Acceso, log_security = get_app_models()
    
    try:
        # IPs en lista negra (bloqueadas permanentemente)
        ips_negras = IPListaNegra.query.all()
        lista_negra = [{
            'ip': ip.ip,
            'motivo': ip.motivo,
            'fecha_bloqueo': ip.fecha.strftime('%Y-%m-%d %H:%M:%S') if ip.fecha else None,
            'tipo': 'negra'
        } for ip in ips_negras]
        
        # IPs sospechosas
        ips_sospechosas = IPSospechosa.query.filter_by(bloqueada=True).all()
        lista_sospechosa = [{
            'ip': ip.ip,
            'intentos': ip.intentos,
            'motivo': ip.motivo_bloqueo,
            'ultima_actividad': ip.ultima_actividad.strftime('%Y-%m-%d %H:%M:%S') if ip.ultima_actividad else None,
            'tipo': 'sospechosa'
        } for ip in ips_sospechosas]
        
        # IPs con intentos pero no bloqueadas (advertencia)
        ips_advertencia = IPSospechosa.query.filter(
            IPSospechosa.bloqueada == False,
            IPSospechosa.intentos >= 2
        ).all()
        lista_advertencia = [{
            'ip': ip.ip,
            'intentos': ip.intentos,
            'ultima_actividad': ip.ultima_actividad.strftime('%Y-%m-%d %H:%M:%S') if ip.ultima_actividad else None,
            'tipo': 'advertencia'
        } for ip in ips_advertencia]
        
        return jsonify({
            'success': True,
            'data': {
                'negras': lista_negra,
                'sospechosas': lista_sospechosa,
                'advertencia': lista_advertencia,
                'totales': {
                    'negras': len(lista_negra),
                    'sospechosas': len(lista_sospechosa),
                    'advertencia': len(lista_advertencia)
                }
            }
        })
    
    except Exception as e:
        log_security(f"ERROR LISTANDO IPS BLOQUEADAS | error={str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ==============================================
# 📜 RUTA: LISTAR ARCHIVOS DE LOG DISPONIBLES
# ==============================================

@monitoreo_bp.route('/api/logs/archivos', methods=['GET'])
def listar_archivos_log():
    """
    Lista todos los archivos .log disponibles en la carpeta logs/
    """
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        logs_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'logs'
        )
        
        if not os.path.exists(logs_dir):
            return jsonify({'success': True, 'data': [], 'message': 'Carpeta de logs no encontrada'})
        
        # Listar todos los archivos .log
        archivos_log = []
        for archivo in os.listdir(logs_dir):
            if archivo.endswith('.log'):
                ruta_completa = os.path.join(logs_dir, archivo)
                stat_info = os.stat(ruta_completa)
                
                archivos_log.append({
                    'nombre': archivo,
                    'tamano_bytes': stat_info.st_size,
                    'tamano_mb': round(stat_info.st_size / (1024 * 1024), 2),
                    'fecha_modificacion': datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'lineas': sum(1 for _ in open(ruta_completa, 'r', encoding='utf-8', errors='ignore'))
                })
        
        # Ordenar por fecha de modificación (más reciente primero)
        archivos_log.sort(key=lambda x: x['fecha_modificacion'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': archivos_log,
            'total': len(archivos_log)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ==============================================
# 📜 RUTA: LOGS DE SEGURIDAD CON PAGINACIÓN
# ==============================================

@monitoreo_bp.route('/api/logs_seguridad', methods=['GET'])
def obtener_logs_seguridad():
    """
    Retorna logs de seguridad con paginación, búsqueda y filtros avanzados
    """
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    # Importar modelos para evitar circular imports
    Usuario, Tercero, IPListaNegra, IPSospechosa, Acceso, log_security = get_app_models()
    
    try:
        # Parámetros de paginación y filtros
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 50, type=int)
        filtro = request.args.get('filtro', '').upper()
        archivo_log = request.args.get('archivo', 'security.log')  # Permitir elegir archivo
        tipo_evento = request.args.get('tipo_evento', '')  # LOGIN, ERROR, REGISTRO, etc
        fecha_desde = request.args.get('fecha_desde', '')  # Formato: YYYY-MM-DD
        fecha_hasta = request.args.get('fecha_hasta', '')  # Formato: YYYY-MM-DD
        
        # Ruta al archivo de log
        log_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'logs',
            archivo_log
        )
        
        if not os.path.exists(log_path):
            return jsonify({'success': True, 'data': [], 'message': 'Archivo de logs no encontrado'})
        
        # Leer todas las líneas
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            lineas = f.readlines()
        
        # Aplicar filtros
        lineas_filtradas = []
        for linea in lineas:
            # Filtro por texto general
            if filtro and filtro not in linea.upper():
                continue
            
            # Filtro por tipo de evento
            if tipo_evento and tipo_evento.upper() not in linea.upper():
                continue
            
            # Filtro por fecha (formato típico de logs: YYYY-MM-DD HH:MM:SS)
            if fecha_desde or fecha_hasta:
                try:
                    # Extraer fecha de la línea (asumiendo formato: INFO:security:YYYY-MM-DD HH:MM:SS)
                    partes = linea.split(':')
                    if len(partes) >= 3:
                        fecha_str = partes[2].strip().split()[0]  # Obtener YYYY-MM-DD
                        
                        if fecha_desde and fecha_str < fecha_desde:
                            continue
                        if fecha_hasta and fecha_str > fecha_hasta:
                            continue
                except:
                    pass  # Si no se puede parsear la fecha, incluir la línea
            
            lineas_filtradas.append(linea.strip())
        
        # Invertir para mostrar más recientes primero
        lineas_filtradas.reverse()
        
        # Paginación
        total_lineas = len(lineas_filtradas)
        inicio = (pagina - 1) * por_pagina
        fin = inicio + por_pagina
        lineas_paginadas = lineas_filtradas[inicio:fin]
        
        return jsonify({
            'success': True,
            'data': lineas_paginadas,
            'total': total_lineas,
            'pagina': pagina,
            'por_pagina': por_pagina,
            'total_paginas': (total_lineas + por_pagina - 1) // por_pagina  # Redondeo hacia arriba
        })
    
    except Exception as e:
        log_security(f"ERROR OBTENIENDO LOGS | error={str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ==============================================
# 📥 RUTA: DESCARGAR ARCHIVO DE LOG COMPLETO
# ==============================================

@monitoreo_bp.route('/api/logs/descargar/<archivo>', methods=['GET'])
def descargar_log(archivo):
    """
    Permite descargar un archivo de log completo
    """
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    # Importar modelos para registrar la acción
    Usuario, Tercero, IPListaNegra, IPSospechosa, Acceso, log_security = get_app_models()
    
    try:
        # Validar que el archivo termine en .log (seguridad)
        if not archivo.endswith('.log'):
            return jsonify({'success': False, 'message': 'Solo se permiten archivos .log'}), 400
        
        # Evitar path traversal
        if '..' in archivo or '/' in archivo or '\\' in archivo:
            log_security(f"INTENTO DE PATH TRAVERSAL | archivo={archivo} | usuario={session.get('usuario')} | IP={request.remote_addr}")
            return jsonify({'success': False, 'message': 'Nombre de archivo inválido'}), 400
        
        # Ruta al archivo
        log_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'logs',
            archivo
        )
        
        if not os.path.exists(log_path):
            return jsonify({'success': False, 'message': 'Archivo no encontrado'}), 404
        
        # Registrar acción
        log_security(f"DESCARGA LOG | archivo={archivo} | usuario={session.get('usuario')} | IP={request.remote_addr}")
        
        return send_file(
            log_path,
            as_attachment=True,
            download_name=f"{archivo}",
            mimetype='text/plain'
        )
    
    except Exception as e:
        log_security(f"ERROR DESCARGANDO LOG | archivo={archivo} | error={str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ==============================================
# 📊 RUTA: LOGS DE ACCIONES ADMINISTRATIVAS
# ==============================================

@monitoreo_bp.route('/api/logs_acciones', methods=['GET'])
def obtener_logs_acciones():
    """
    Retorna los logs de acciones administrativas realizadas desde el panel.
    """
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    # Importar modelos para evitar circular imports
    Usuario, Tercero, IPListaNegra, IPSospechosa, Acceso, log_security = get_app_models()
    
    try:
        # Parámetros
        dias = request.args.get('dias', 7, type=int)
        
        hace_x_dias = datetime.utcnow() - timedelta(days=dias)
        logs = LogAccion.query.filter(
            LogAccion.fecha_accion >= hace_x_dias
        ).order_by(desc(LogAccion.fecha_accion)).all()
        
        return jsonify({
            'success': True,
            'data': [log.to_dict() for log in logs]
        })
    
    except Exception as e:
        log_security(f"ERROR OBTENIENDO LOGS ACCIONES | error={str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ============================================================================
# 👥 ENDPOINT: USUARIOS EN TIEMPO REAL CON SESIONES ACTIVAS
# ============================================================================

@monitoreo_bp.route('/api/usuarios_tiempo_real', methods=['GET'])
def obtener_usuarios_tiempo_real():
    """
    Retorna todos los usuarios con información de sesiones activas en tiempo real
    """
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    # Importar modelos
    Usuario, Tercero, IPListaNegra, IPSospechosa, Acceso, log_security = get_app_models()
    
    try:
        # Obtener todos los usuarios
        usuarios = Usuario.query.join(Tercero).all()
        
        resultado = []
        ahora = datetime.utcnow()
        
        for user in usuarios:
            # Buscar sesión activa más reciente
            sesion = SesionActiva.query.filter_by(
                usuario_id=user.id
            ).order_by(SesionActiva.fecha_ultima_actividad.desc()).first()
            
            # Determinar estado
            if sesion and sesion.conectado:
                # Calcular minutos de inactividad
                delta = ahora - sesion.fecha_ultima_actividad
                minutos_inactivo = int(delta.total_seconds() / 60)
                
                # Desconectar si >10 minutos sin actividad
                if minutos_inactivo >= 10:
                    conectado = False
                    estado_texto = 'Desconectado (Timeout)'
                else:
                    conectado = True
                    estado_texto = 'Conectado'
            else:
                conectado = False
                estado_texto = 'Desconectado'
            
            # Última conexión (de la tabla accesos)
            ultimo_acceso = Acceso.query.filter_by(
                usuario_id=user.id,
                exito=True
            ).order_by(Acceso.fecha.desc()).first()
            
            resultado.append({
                'usuario_id': user.id,
                'usuario': user.usuario,
                'nit': user.tercero.nit if user.tercero else 'N/A',
                'razon_social': user.tercero.razon_social if user.tercero else 'N/A',
                'activo': user.activo,
                'conectado': conectado,
                'estado_texto': estado_texto,
                'modulo_actual': sesion.modulo_actual if sesion else 'N/A',
                'ip_actual': sesion.ip_address if sesion and conectado else 'N/A',
                'pais': sesion.pais if sesion else 'N/A',
                'ciudad': sesion.ciudad if sesion else 'N/A',
                'fecha_inicio_sesion': sesion.fecha_inicio.strftime('%Y-%m-%d %H:%M:%S') if sesion and conectado else 'N/A',
                'ultima_actividad': sesion.fecha_ultima_actividad.strftime('%Y-%m-%d %H:%M:%S') if sesion else 'N/A',
                'minutos_inactivo': minutos_inactivo if sesion and conectado else None,
                'tiempo_sesion': formatear_duracion(ahora - sesion.fecha_inicio) if sesion and conectado else 'N/A',
                'ultima_conexion': ultimo_acceso.fecha.strftime('%Y-%m-%d %H:%M:%S') if ultimo_acceso else 'Nunca',
                'user_agent': sesion.user_agent if sesion else 'N/A'
            })
        
        # Ordenar: conectados primero, luego por última actividad
        resultado.sort(key=lambda x: (not x['conectado'], x['ultima_actividad']), reverse=True)
        
        # Estadísticas
        total_usuarios = len(resultado)
        usuarios_conectados = sum(1 for u in resultado if u['conectado'])
        usuarios_activos = sum(1 for u in resultado if u['activo'])
        
        return jsonify({
            'success': True,
            'data': resultado,
            'estadisticas': {
                'total_usuarios': total_usuarios,
                'conectados': usuarios_conectados,
                'activos': usuarios_activos,
                'inactivos': total_usuarios - usuarios_activos
            }
        })
    
    except Exception as e:
        log_security(f"ERROR OBTENIENDO USUARIOS TIEMPO REAL | error={str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ============================================================================
# 🌐 ENDPOINT: IPS CONECTADAS EN TIEMPO REAL CON GEOLOCALIZACIÓN
# ============================================================================

@monitoreo_bp.route('/api/ips_tiempo_real', methods=['GET'])
def obtener_ips_tiempo_real():
    """
    Lista todas las IPs conectadas en tiempo real con geolocalización
    """
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    # Importar modelos
    Usuario, Tercero, IPListaNegra, IPSospechosa, Acceso, log_security = get_app_models()
    
    try:
        # Obtener todas las sesiones activas (conectadas)
        sesiones = SesionActiva.query.filter_by(conectado=True).all()
        
        # Diccionario para agrupar por IP
        ips_dict = {}
        
        for sesion in sesiones:
            ip = sesion.ip_address
            
            if ip not in ips_dict:
                # Verificar si está bloqueada
                ip_bloqueada = IPListaNegra.query.get(ip)
                ip_sospechosa = IPSospechosa.query.get(ip)
                
                bloqueada = bool(ip_bloqueada)
                sospechosa = bool(ip_sospechosa and ip_sospechosa.bloqueada)
                
                # Primera vez que vemos esta IP
                primer_acceso = Acceso.query.filter_by(ip=ip).order_by(Acceso.fecha.asc()).first()
                ultimo_acceso = Acceso.query.filter_by(ip=ip).order_by(Acceso.fecha.desc()).first()
                
                ips_dict[ip] = {
                    'ip_address': ip,
                    'usuarios': [],
                    'pais': sesion.pais or 'Desconocido',
                    'ciudad': sesion.ciudad or 'Desconocido',
                    'latitud': float(sesion.latitud) if sesion.latitud else None,
                    'longitud': float(sesion.longitud) if sesion.longitud else None,
                    'bloqueada': bloqueada or sospechosa,
                    'estado': 'Bloqueada' if (bloqueada or sospechosa) else 'Activa',
                    'primera_conexion': primer_acceso.fecha.strftime('%Y-%m-%d %H:%M:%S') if primer_acceso else 'N/A',
                    'ultima_conexion': ultimo_acceso.fecha.strftime('%Y-%m-%d %H:%M:%S') if ultimo_acceso else 'N/A',
                    'total_accesos': Acceso.query.filter_by(ip=ip).count(),
                    'accesos_fallidos': Acceso.query.filter_by(ip=ip, exito=False).count()
                }
            
            # Agregar usuario a la lista de esta IP
            ips_dict[ip]['usuarios'].append({
                'usuario_id': sesion.usuario_id,
                'usuario_nombre': sesion.usuario_nombre,
                'modulo_actual': sesion.modulo_actual,
                'ultima_actividad': sesion.fecha_ultima_actividad.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Convertir diccionario a lista
        resultado = list(ips_dict.values())
        
        # Ordenar por última conexión (más reciente primero)
        resultado.sort(key=lambda x: x['ultima_conexion'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': resultado,
            'total_ips': len(resultado)
        })
    
    except Exception as e:
        log_security(f"ERROR OBTENIENDO IPS TIEMPO REAL | error={str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ============================================================================
# 💾 ENDPOINT: ESPACIO EN DISCO MEJORADO (MÚLTIPLES FUENTES)
# ============================================================================

@monitoreo_bp.route('/api/disk_usage_mejorado', methods=['GET'])
def obtener_disk_usage_mejorado():
    """
    Muestra espacio de múltiples fuentes: discos locales, carpetas, base de datos
    """
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    # Importar modelos
    Usuario, Tercero, IPListaNegra, IPSospechosa, Acceso, log_security = get_app_models()
    
    try:
        import psycopg2
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # ========== 1. DISCOS LOCALES ==========
        discos = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                discos.append({
                    'dispositivo': partition.device,
                    'punto_montaje': partition.mountpoint,
                    'sistema_archivos': partition.fstype,
                    'total_gb': round(usage.total / (1024 ** 3), 2),
                    'usado_gb': round(usage.used / (1024 ** 3), 2),
                    'libre_gb': round(usage.free / (1024 ** 3), 2),
                    'porcentaje_usado': round(usage.percent, 2)
                })
            except PermissionError:
                continue
        
        # ========== 2. CARPETAS DEL PROYECTO ==========
        proyecto_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        carpetas = {
            'documentos_terceros': os.path.join(proyecto_path, 'documentos_terceros'),
            'logs': os.path.join(proyecto_path, 'logs'),
            'templates': os.path.join(proyecto_path, 'templates'),
            'sql': os.path.join(proyecto_path, 'sql')
        }
        
        carpetas_info = []
        for nombre, ruta in carpetas.items():
            if os.path.exists(ruta):
                tamano_bytes = obtener_tamano_carpeta(ruta)
                carpetas_info.append({
                    'nombre': nombre,
                    'ruta': ruta,
                    'tamano_bytes': tamano_bytes,
                    'tamano_legible': formatear_bytes(tamano_bytes)
                })
        
        # ========== 3. BASE DE DATOS POSTGRESQL ==========
        try:
            DATABASE_URL = os.getenv('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pg_database_size('gestor_documental') as tamano_bytes;
            """)
            bd_tamano = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            bd_info = {
                'nombre': 'gestor_documental',
                'tamano_bytes': bd_tamano,
                'tamano_legible': formatear_bytes(bd_tamano)
            }
        except Exception as e:
            bd_info = {
                'nombre': 'gestor_documental',
                'error': str(e)
            }
        
        # ========== 4. TOTAL DEL PROYECTO ==========
        total_proyecto_bytes = sum(c['tamano_bytes'] for c in carpetas_info)
        if 'tamano_bytes' in bd_info:
            total_proyecto_bytes += bd_info['tamano_bytes']
        
        return jsonify({
            'success': True,
            'data': {
                'discos_locales': discos,
                'carpetas_proyecto': carpetas_info,
                'base_datos': bd_info,
                'total_proyecto': {
                    'tamano_bytes': total_proyecto_bytes,
                    'tamano_legible': formatear_bytes(total_proyecto_bytes)
                }
            }
        })
    
    except Exception as e:
        log_security(f"ERROR OBTENIENDO DISK USAGE MEJORADO | error={str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ============================================================================
# 📊 ENDPOINT: ESTADÍSTICAS SORPRENDENTES PARA DASHBOARD
# ============================================================================

@monitoreo_bp.route('/api/stats_sorprendentes', methods=['GET'])
def obtener_stats_sorprendentes():
    """
    Estadísticas avanzadas y visualizaciones sorprendentes para el dashboard
    """
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    # Importar modelos
    Usuario, Tercero, IPListaNegra, IPSospechosa, Acceso, log_security = get_app_models()
    
    try:
        from sqlalchemy import cast, Date
        
        ahora = datetime.utcnow()
        hoy = ahora.date()
        hace_7_dias = ahora - timedelta(days=7)
        hace_30_dias = ahora - timedelta(days=30)
        
        # ========== 1. USUARIOS ACTIVOS POR HORA (ÚLTIMAS 24H) ==========
        usuarios_por_hora = []
        for i in range(24):
            hora_inicio = ahora - timedelta(hours=i+1)
            hora_fin = ahora - timedelta(hours=i)
            
            count = db.session.query(func.count(func.distinct(Acceso.usuario_id))).filter(
                Acceso.fecha >= hora_inicio,
                Acceso.fecha < hora_fin,
                Acceso.exito == True
            ).scalar()
            
            usuarios_por_hora.append({
                'hora': hora_inicio.strftime('%H:00'),
                'usuarios_unicos': count
            })
        
        usuarios_por_hora.reverse()
        
        # ========== 2. MÓDULOS MÁS USADOS (ÚLTIMOS 7 DÍAS) ==========
        modulos_uso = db.session.query(
            SesionActiva.modulo_actual,
            func.count(SesionActiva.id).label('total_accesos')
        ).filter(
            SesionActiva.fecha_inicio >= hace_7_dias
        ).group_by(
            SesionActiva.modulo_actual
        ).order_by(
            func.count(SesionActiva.id).desc()
        ).limit(10).all()
        
        modulos_stats = [
            {'modulo': m[0] or 'Dashboard', 'accesos': m[1]}
            for m in modulos_uso
        ]
        
        # ========== 3. INTENTOS DE LOGIN FALLIDOS (ÚLTIMOS 30 DÍAS) ==========
        logins_fallidos_por_dia = []
        for i in range(30):
            dia = hoy - timedelta(days=i)
            
            count = Acceso.query.filter(
                cast(Acceso.fecha, Date) == dia,
                Acceso.exito == False
            ).count()
            
            logins_fallidos_por_dia.append({
                'fecha': dia.strftime('%Y-%m-%d'),
                'intentos_fallidos': count
            })
        
        logins_fallidos_por_dia.reverse()
        
        # ========== 4. TOP 10 IPS CON MÁS ACCESOS ==========
        top_ips = db.session.query(
            Acceso.ip,
            func.count(Acceso.id).label('total_accesos')
        ).group_by(
            Acceso.ip
        ).order_by(
            func.count(Acceso.id).desc()
        ).limit(10).all()
        
        top_ips_stats = [
            {'ip': ip[0], 'accesos': ip[1]}
            for ip in top_ips
        ]
        
        # ========== 5. DISTRIBUCIÓN GEOGRÁFICA (DE SESIONES ACTIVAS) ==========
        distribucion_geografica = db.session.query(
            SesionActiva.pais,
            func.count(SesionActiva.id).label('total_sesiones')
        ).filter(
            SesionActiva.pais.isnot(None),
            SesionActiva.pais != 'Desconocido'
        ).group_by(
            SesionActiva.pais
        ).order_by(
            func.count(SesionActiva.id).desc()
        ).all()
        
        paises_stats = [
            {'pais': p[0], 'sesiones': p[1]}
            for p in distribucion_geografica
        ]
        
        # ========== 6. ALERTAS CRÍTICAS PENDIENTES ==========
        alertas_pendientes = AlertaSeguridad.query.filter_by(
            resuelta=False
        ).order_by(
            AlertaSeguridad.fecha_alerta.desc()
        ).limit(5).all()
        
        alertas_stats = [
            {
                'tipo': a.tipo_alerta,
                'fecha': a.fecha_alerta.strftime('%Y-%m-%d %H:%M:%S'),
                'detalles': a.detalles[:100] if a.detalles else ''
            }
            for a in alertas_pendientes
        ]
        
        # ========== 7. RESUMEN GENERAL ==========
        total_usuarios_registrados = Usuario.query.count()
        usuarios_conectados_ahora = SesionActiva.query.filter_by(conectado=True).count()
        ips_bloqueadas_total = IPListaNegra.query.count()
        alertas_pendientes_total = AlertaSeguridad.query.filter_by(resuelta=False).count()
        
        return jsonify({
            'success': True,
            'data': {
                'usuarios_por_hora': usuarios_por_hora,
                'modulos_mas_usados': modulos_stats,
                'logins_fallidos_tendencia': logins_fallidos_por_dia,
                'top_ips': top_ips_stats,
                'distribucion_geografica': paises_stats,
                'alertas_criticas': alertas_stats,
                'resumen': {
                    'total_usuarios': total_usuarios_registrados,
                    'usuarios_conectados': usuarios_conectados_ahora,
                    'ips_bloqueadas': ips_bloqueadas_total,
                    'alertas_pendientes': alertas_pendientes_total
                }
            }
        })
    
    except Exception as e:
        log_security(f"ERROR OBTENIENDO STATS SORPRENDENTES | error={str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ============================================================================
# 🚨 ENDPOINT: OBTENER ALERTAS DE SEGURIDAD
# ============================================================================

@monitoreo_bp.route('/api/alertas', methods=['GET'])
def obtener_alertas():
    """
    Retorna las alertas de seguridad del sistema
    """
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    # Importar modelos
    Usuario, Tercero, IPListaNegra, IPSospechosa, Acceso, log_security = get_app_models()
    
    try:
        solo_pendientes = request.args.get('solo_pendientes', 'true').lower() == 'true'
        
        query = AlertaSeguridad.query
        if solo_pendientes:
            query = query.filter_by(resuelta=False)
        
        alertas = query.order_by(AlertaSeguridad.fecha_alerta.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [a.to_dict() for a in alertas]
        })
    
    except Exception as e:
        log_security(f"ERROR OBTENIENDO ALERTAS | error={str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ============================================================================
# ✅ ENDPOINT: RESOLVER ALERTA
# ============================================================================

@monitoreo_bp.route('/api/resolver_alerta', methods=['POST'])
def resolver_alerta():
    """
    Marca una alerta como resuelta
    """
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    # Importar modelos
    Usuario, Tercero, IPListaNegra, IPSospechosa, Acceso, log_security = get_app_models()
    
    try:
        data = request.get_json()
        alerta_id = data.get('alerta_id')
        notas = data.get('notas', '')
        
        alerta = AlertaSeguridad.query.get(alerta_id)
        if not alerta:
            return jsonify({'success': False, 'message': 'Alerta no encontrada'}), 404
        
        alerta.resuelta = True
        alerta.fecha_resolucion = datetime.utcnow()
        alerta.usuario_resolucion = session.get('usuario')
        alerta.notas_resolucion = notas
        
        db.session.commit()
        
        log_security(f"ALERTA RESUELTA | id={alerta_id} | usuario={session.get('usuario')}")
        
        return jsonify({'success': True, 'message': 'Alerta resuelta exitosamente'})
    
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR RESOLVIENDO ALERTA | error={str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ============================================================================
# 🔒 ENDPOINT: BLOQUEAR IP
# ============================================================================

@monitoreo_bp.route('/api/bloquear_ip', methods=['POST'])
def bloquear_ip():
    """
    Bloquea una IP sospechosa
    """
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    # Importar modelos
    Usuario, Tercero, IPListaNegra, IPSospechosa, Acceso, log_security = get_app_models()
    
    try:
        data = request.get_json()
        ip = data.get('ip')
        
        # Agregar a lista negra
        if not IPListaNegra.query.get(ip):
            nueva_ip_bloqueada = IPListaNegra(
                ip_address=ip,
                motivo='Bloqueada desde panel de monitoreo',
                fecha_bloqueo=datetime.utcnow(),
                admin_usuario=session.get('usuario')
            )
            db.session.add(nueva_ip_bloqueada)
        
        # Actualizar en ips_sospechosas
        ip_sospechosa = IPSospechosa.query.get(ip)
        if ip_sospechosa:
            ip_sospechosa.bloqueada = True
        
        db.session.commit()
        
        log_security(f"IP BLOQUEADA MANUAL | ip={ip} | admin={session.get('usuario')}")
        
        return jsonify({'success': True, 'message': f'IP {ip} bloqueada exitosamente'})
    
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR BLOQUEANDO IP | ip={ip} | error={str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ============================================================================
# 🔓 ENDPOINT: DESBLOQUEAR IP
# ============================================================================

@monitoreo_bp.route('/api/desbloquear_ip', methods=['POST'])
def desbloquear_ip():
    """
    Desbloquea una IP previamente bloqueada
    """
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    # Importar modelos
    Usuario, Tercero, IPListaNegra, IPSospechosa, Acceso, log_security = get_app_models()
    
    try:
        data = request.get_json()
        ip = data.get('ip')
        
        # Eliminar de lista negra
        ip_bloqueada = IPListaNegra.query.get(ip)
        if ip_bloqueada:
            db.session.delete(ip_bloqueada)
        
        # Actualizar en ips_sospechosas
        ip_sospechosa = IPSospechosa.query.get(ip)
        if ip_sospechosa:
            ip_sospechosa.bloqueada = False
        
        db.session.commit()
        
        log_security(f"IP DESBLOQUEADA MANUAL | ip={ip} | admin={session.get('usuario')}")
        
        return jsonify({'success': True, 'message': f'IP {ip} desbloqueada exitosamente'})
    
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR DESBLOQUEANDO IP | ip={ip} | error={str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

