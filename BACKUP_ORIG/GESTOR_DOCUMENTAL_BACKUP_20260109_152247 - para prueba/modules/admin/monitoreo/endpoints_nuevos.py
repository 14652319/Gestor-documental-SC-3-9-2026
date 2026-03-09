"""
ENDPOINTS ADICIONALES PARA MONITOREO
Este archivo contiene los nuevos endpoints que se deben agregar a routes.py
Fecha: Octubre 23, 2025
"""

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
        from .models import SesionActiva
        from .utils import formatear_duracion
        
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
        from .models import SesionActiva
        
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
    
    try:
        import psutil
        from .utils import obtener_tamano_carpeta, formatear_bytes
        import psycopg2
        from dotenv import load_dotenv
        import os
        
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
            cursor = cursor.execute("""
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
        from .models import SesionActiva
        from sqlalchemy import func, cast, Date
        
        ahora = datetime.utcnow()
        hoy = ahora.date()
        hace_7_dias = ahora - timedelta(days=7)
        hace_30_dias = ahora - timedelta(days=30)
        
        # ========== 1. USUARIOS ACTIVOS POR HORA (ÚLTIMAS 24H) ==========
        usuarios_por_hora = []
        for i in range(24):
            hora_inicio = ahora - timedelta(hours=i+1)
            hora_fin = ahora - timedelta(hours=i)
            
            count = Acceso.query.filter(
                Acceso.fecha >= hora_inicio,
                Acceso.fecha < hora_fin,
                Acceso.exito == True
            ).distinct(Acceso.usuario_id).count()
            
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
        from .models import AlertaSeguridad
        
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
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}'), 500
