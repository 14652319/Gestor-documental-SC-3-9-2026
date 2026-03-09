"""
Rutas para el Módulo de Gestión de Terceros
Sistema enterprise con funcionalidades avanzadas
"""

from flask import render_template, request, jsonify, session, redirect, url_for, current_app
from datetime import datetime, timedelta
import math
import time
from . import terceros_bp
from .models import TerceroStats, TerceroHelper
from extensions import db
from decoradores_permisos import requiere_permiso, requiere_permiso_html
from sqlalchemy import text, or_, and_, desc
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def validar_sesion_admin():
    """Valida sesión de administrador"""
    if 'usuario_id' not in session or 'usuario' not in session:
        return False, {"error": "Sesión no válida", "redirect": "/login"}, 401
    return True, None, None

def get_models():
    """Obtener modelos dinámicamente con importación directa"""
    try:
        from app import Tercero, DocumentoTercero, Usuario
        return Tercero, DocumentoTercero, Usuario
    except ImportError as e:
        print(f"Error importando modelos: {e}")
        return None, None, None

# ============================================================================
# 🏠 DASHBOARD PRINCIPAL DE TERCEROS
# ============================================================================

@terceros_bp.route('/')
@terceros_bp.route('/dashboard')
@requiere_permiso_html('terceros', 'acceder_modulo')
def dashboard():
    """Dashboard principal del módulo terceros"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return redirect('/')
    return render_template('terceros_dashboard.html', usuario=session.get('usuario'))

# ============================================================================
# 📊 CONSULTA GENERAL DE TERCEROS - LISTADO PAGINADO
# ============================================================================

@terceros_bp.route('/consulta')
@requiere_permiso_html('terceros', 'consultar')
def consulta():
    """Página de consulta avanzada de terceros"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return redirect('/')
    return render_template('terceros_consulta.html', usuario=session.get('usuario'))

@terceros_bp.route('/crear')
@requiere_permiso_html('terceros', 'crear')
def crear():
    """Página para crear nuevo tercero"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return redirect('/')
    return render_template('tercero_crear.html', usuario=session.get('usuario'))

@terceros_bp.route('/editar')
@requiere_permiso_html('terceros', 'editar')
def editar():
    """Página para editar tercero existente"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return redirect('/')
    return render_template('tercero_editar.html', usuario=session.get('usuario'))

@terceros_bp.route('/documentos')
@requiere_permiso_html('terceros', 'documentos')
def documentos():
    """Página de gestión de documentos de tercero"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return redirect('/')
    return render_template('tercero_documentos.html', usuario=session.get('usuario'))

@terceros_bp.route('/configuracion')
@requiere_permiso_html('terceros', 'configurar')
def configuracion():
    """Página de configuración avanzada del módulo"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return redirect('/')
    return render_template('tercero_configuracion.html', usuario=session.get('usuario'))
def consulta_terceros():
    """Página de consulta con listado paginado"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return redirect('/')
    return render_template('terceros_consulta.html', usuario=session.get('usuario'))

@terceros_bp.route('/api/listar', methods=['GET'])
@requiere_permiso('terceros', 'consultar')
def listar_terceros():
    """API para listar terceros con paginación avanzada"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 200, type=int)
        search = request.args.get('search', '', type=str)
        estado_filtro = request.args.get('estado', '', type=str)
        orden = request.args.get('orden', 'fecha_desc', type=str)
        
        # Usar el helper simplificado
        terceros_paginados = TerceroHelper.listar_terceros(
            page=page, 
            per_page=per_page, 
            search=search, 
            estado=estado_filtro, 
            orden=orden
        )
        
        if not terceros_paginados:
            return jsonify({
                'success': False, 
                'message': 'Error al obtener terceros'
            }), 500
        
        # Convertir resultados a formato JSON
        terceros_data = []
        for tercero in terceros_paginados.items:
            terceros_data.append({
                'id': tercero.id,
                'nit': tercero.nit,
                'razon_social': tercero.razon_social,
                'primer_nombre': getattr(tercero, 'primer_nombre', ''),
                'primer_apellido': getattr(tercero, 'primer_apellido', ''),
                'telefono': getattr(tercero, 'telefono', ''),
                'email': getattr(tercero, 'email', ''),
                'tipo_persona': getattr(tercero, 'tipo_persona', ''),
                'fecha_registro': tercero.fecha_registro.strftime('%Y-%m-%d %H:%M') if tercero.fecha_registro else '',
                'total_documentos': 0  # Por simplicidad, por ahora 0
            })
        
        return jsonify({
            'success': True,
            'data': terceros_data,
            'pagination': {
                'page': terceros_paginados.page,
                'pages': terceros_paginados.pages,
                'per_page': terceros_paginados.per_page,
                'total': terceros_paginados.total,
                'has_next': terceros_paginados.has_next,
                'has_prev': terceros_paginados.has_prev,
                'next_num': terceros_paginados.next_num,
                'prev_num': terceros_paginados.prev_num
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error en listar_terceros: {e}")
        return jsonify({
            'success': False, 
            'message': f'Error interno: {str(e)}'
        }), 500
                Tercero.razon_social.ilike(f'%{search}%'),
                Tercero.email.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # Filtrar por estado
        if estado_filtro:
            if estado_filtro == 'activos':
                query = query.filter(Tercero.activo == True)
            elif estado_filtro == 'inactivos':
                query = query.filter(Tercero.activo == False)
        
        # Agrupar por tercero
        query = query.group_by(
            Tercero.id, Tercero.nit, Tercero.razon_social, 
            Tercero.telefono, Tercero.email, Tercero.activo,
            Tercero.fecha_registro, Tercero.fecha_actualizacion
        )
        
        # Aplicar ordenamiento
        if orden == 'nit_asc':
            query = query.order_by(Tercero.nit)
        elif orden == 'nit_desc':
            query = query.order_by(desc(Tercero.nit))
        elif orden == 'razon_asc':
            query = query.order_by(Tercero.razon_social)
        elif orden == 'razon_desc':
            query = query.order_by(desc(Tercero.razon_social))
        elif orden == 'fecha_asc':
            query = query.order_by(Tercero.fecha_registro)
        else:  # fecha_desc por defecto
            query = query.order_by(desc(Tercero.fecha_registro))
        
        # Obtener total antes de paginar
        total = query.count()
        
        # Aplicar paginación
        offset = (page - 1) * per_page
        terceros_paginados = query.offset(offset).limit(per_page).all()
        
        # Calcular estadísticas de paginación
        total_pages = math.ceil(total / per_page)
        has_prev = page > 1
        has_next = page < total_pages
        
        # Formatear resultados
        terceros_list = []
        for tercero in terceros_paginados:
            # Calcular días desde última actualización
            dias_actualizacion = (datetime.now() - tercero.fecha_actualizacion).days if tercero.fecha_actualizacion else 0
            
            terceros_list.append({
                'id': tercero.id,
                'nit': tercero.nit,
                'razon_social': tercero.razon_social,
                'telefono': tercero.telefono or 'No registrado',
                'email': tercero.email or 'No registrado',
                'activo': tercero.activo,
                'estado_texto': 'Activo' if tercero.activo else 'Inactivo',
                'estado_clase': 'success' if tercero.activo else 'danger',
                'fecha_registro': tercero.fecha_registro.strftime('%d/%m/%Y %H:%M') if tercero.fecha_registro else '',
                'fecha_actualizacion': tercero.fecha_actualizacion.strftime('%d/%m/%Y %H:%M') if tercero.fecha_actualizacion else '',
                'dias_actualizacion': dias_actualizacion,
                'requiere_actualizacion': dias_actualizacion > 365,
                'total_documentos': tercero.total_documentos or 0,
                'tiene_documentos': (tercero.total_documentos or 0) > 0
            })
        
        return jsonify({
            'success': True,
            'data': {
                'terceros': terceros_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages,
                    'has_prev': has_prev,
                    'has_next': has_next,
                    'prev_page': page - 1 if has_prev else None,
                    'next_page': page + 1 if has_next else None
                },
                'stats': {
                    'total_terceros': total,
                    'mostrando_desde': offset + 1,
                    'mostrando_hasta': min(offset + per_page, total)
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error en listar_terceros: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# ============================================================================
# 👤 GESTIÓN INDIVIDUAL DE TERCEROS
# ============================================================================

@terceros_bp.route('/crear')
@requiere_permiso_html('terceros', 'crear')
def crear_tercero():
    """Formulario para crear nuevo tercero"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return redirect('/')
    return render_template('tercero_crear.html', usuario=session.get('usuario'))

@terceros_bp.route('/editar/<int:tercero_id>')
@requiere_permiso_html('terceros', 'editar')
def editar_tercero(tercero_id):
    """Formulario para editar tercero existente"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return redirect('/')
    return render_template('tercero_editar.html', tercero_id=tercero_id, usuario=session.get('usuario'))

@terceros_bp.route('/api/obtener/<int:tercero_id>', methods=['GET'])
@requiere_permiso('terceros', 'consultar')
def obtener_tercero(tercero_id):
    """Obtener datos completos de un tercero"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        Tercero, DocumentoTercero, Usuario = get_models()
        
        tercero = Tercero.query.get_or_404(tercero_id)
        
        # Información extendida si existe
        info_extendida = TerceroExtendido.query.filter_by(tercero_id=tercero_id).first()
        
        # Estado de documentación
        estado_docs = EstadoDocumentacion.query.filter_by(tercero_id=tercero_id).first()
        
        # Contar documentos
        total_docs = DocumentoTercero.query.filter_by(tercero_id=tercero_id).count()
        
        tercero_data = {
            'id': tercero.id,
            'nit': tercero.nit,
            'razon_social': tercero.razon_social,
            'telefono': tercero.telefono,
            'email': tercero.email,
            'direccion': tercero.direccion,
            'activo': tercero.activo,
            'fecha_registro': tercero.fecha_registro.isoformat() if tercero.fecha_registro else None,
            'fecha_actualizacion': tercero.fecha_actualizacion.isoformat() if tercero.fecha_actualizacion else None,
            'total_documentos': total_docs
        }
        
        # Agregar información extendida si existe
        if info_extendida:
            tercero_data.update({
                'telefono_secundario': info_extendida.telefono_secundario,
                'contacto_principal': info_extendida.contacto_principal,
                'cargo_contacto': info_extendida.cargo_contacto,
                'categoria_tercero': info_extendida.categoria_tercero,
                'clasificacion': info_extendida.clasificacion,
                'limite_credito': float(info_extendida.limite_credito) if info_extendida.limite_credito else 0,
                'datos_adicionales': info_extendida.datos_adicionales or {}
            })
        
        return jsonify({
            'success': True,
            'data': tercero_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo tercero {tercero_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@terceros_bp.route('/api/actualizar/<int:tercero_id>', methods=['PUT'])
@requiere_permiso('terceros', 'editar')
def actualizar_tercero(tercero_id):
    """Actualizar datos de tercero existente"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        Tercero, DocumentoTercero, Usuario = get_models()
        data = request.get_json()
        
        tercero = Tercero.query.get_or_404(tercero_id)
        
        # Actualizar campos básicos
        tercero.razon_social = data.get('razon_social', tercero.razon_social)
        tercero.telefono = data.get('telefono', tercero.telefono)
        tercero.email = data.get('email', tercero.email)
        tercero.direccion = data.get('direccion', tercero.direccion)
        tercero.fecha_actualizacion = datetime.now()
        
        # Manejar información extendida
        info_extendida = TerceroExtendido.query.filter_by(tercero_id=tercero_id).first()
        if not info_extendida:
            info_extendida = TerceroExtendido(tercero_id=tercero_id)
            db.session.add(info_extendida)
        
        # Actualizar campos extendidos
        info_extendida.telefono_secundario = data.get('telefono_secundario')
        info_extendida.contacto_principal = data.get('contacto_principal')
        info_extendida.cargo_contacto = data.get('cargo_contacto')
        info_extendida.categoria_tercero = data.get('categoria_tercero')
        info_extendida.clasificacion = data.get('clasificacion')
        info_extendida.limite_credito = data.get('limite_credito', 0)
        info_extendida.datos_adicionales = data.get('datos_adicionales', {})
        info_extendida.usuario_actualizacion = session.get('usuario')
        info_extendida.fecha_actualizacion = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tercero actualizado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error actualizando tercero {tercero_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# ============================================================================
# 🔄 ACTIVACIÓN/DESACTIVACIÓN DE TERCEROS
# ============================================================================

@terceros_bp.route('/api/cambiar_estado/<int:tercero_id>', methods=['POST'])
@requiere_permiso('terceros', 'activar_desactivar')
def cambiar_estado_tercero(tercero_id):
    """Activar o desactivar tercero"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        Tercero, DocumentoTercero, Usuario = get_models()
        data = request.get_json()
        nuevo_estado = data.get('activo', True)
        
        tercero = Tercero.query.get_or_404(tercero_id)
        estado_anterior = tercero.activo
        
        tercero.activo = nuevo_estado
        tercero.fecha_actualizacion = datetime.now()
        
        db.session.commit()
        
        accion = "activado" if nuevo_estado else "desactivado"
        
        return jsonify({
            'success': True,
            'message': f'Tercero {accion} exitosamente',
            'nuevo_estado': nuevo_estado,
            'estado_anterior': estado_anterior
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error cambiando estado tercero {tercero_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# ============================================================================
# 📄 GESTIÓN DE DOCUMENTACIÓN
# ============================================================================

@terceros_bp.route('/documentos/<int:tercero_id>')
@requiere_permiso_html('terceros', 'revisar_documentos')
def revisar_documentos(tercero_id):
    """Página para revisar documentos de un tercero"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return redirect('/')
    return render_template('tercero_documentos.html', tercero_id=tercero_id, usuario=session.get('usuario'))

@terceros_bp.route('/api/documentos/<int:tercero_id>', methods=['GET'])
@requiere_permiso('terceros', 'consultar')
def listar_documentos_tercero(tercero_id):
    """Listar todos los documentos de un tercero con estado de aprobación"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        Tercero, DocumentoTercero, Usuario = get_models()
        
        # Query documentos con información de aprobación
        documentos_query = db.session.query(
            DocumentoTercero.id,
            DocumentoTercero.tipo_documento,
            DocumentoTercero.nombre_archivo,
            DocumentoTercero.ruta_archivo,
            DocumentoTercero.fecha_subida,
            AprobacionDocumentos.estado.label('estado_aprobacion'),
            AprobacionDocumentos.observaciones,
            AprobacionDocumentos.usuario_revisa,
            AprobacionDocumentos.fecha_revision
        ).outerjoin(
            AprobacionDocumentos, 
            DocumentoTercero.id == AprobacionDocumentos.documento_id
        ).filter(
            DocumentoTercero.tercero_id == tercero_id
        ).order_by(DocumentoTercero.fecha_subida.desc())
        
        documentos = documentos_query.all()
        
        documentos_list = []
        for doc in documentos:
            documentos_list.append({
                'id': doc.id,
                'tipo_documento': doc.tipo_documento,
                'nombre_archivo': doc.nombre_archivo,
                'fecha_subida': doc.fecha_subida.strftime('%d/%m/%Y %H:%M') if doc.fecha_subida else '',
                'estado_aprobacion': doc.estado_aprobacion or 'pendiente',
                'observaciones': doc.observaciones or '',
                'usuario_revisa': doc.usuario_revisa or '',
                'fecha_revision': doc.fecha_revision.strftime('%d/%m/%Y %H:%M') if doc.fecha_revision else '',
                'puede_ver': True,  # Implementar permisos específicos si es necesario
                'url_descarga': f'/api/documentos/descargar/{doc.id}'
            })
        
        return jsonify({
            'success': True,
            'data': {
                'documentos': documentos_list,
                'total_documentos': len(documentos_list)
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error listando documentos tercero {tercero_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@terceros_bp.route('/api/aprobar_documento/<int:documento_id>', methods=['POST'])
@requiere_permiso('terceros', 'aprobar_documentos')
def aprobar_documento(documento_id):
    """Aprobar o rechazar un documento específico"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        data = request.get_json()
        estado = data.get('estado')  # 'aprobado', 'rechazado'
        observaciones = data.get('observaciones', '')
        
        if estado not in ['aprobado', 'rechazado']:
            return jsonify({'success': False, 'message': 'Estado no válido'}), 400
        
        # Buscar o crear registro de aprobación
        aprobacion = AprobacionDocumentos.query.filter_by(documento_id=documento_id).first()
        if not aprobacion:
            # Obtener tercero_id del documento
            Tercero, DocumentoTercero, Usuario = get_models()
            documento = DocumentoTercero.query.get_or_404(documento_id)
            
            aprobacion = AprobacionDocumentos(
                tercero_id=documento.tercero_id,
                documento_id=documento_id
            )
            db.session.add(aprobacion)
        
        # Actualizar estado
        aprobacion.estado = estado
        aprobacion.observaciones = observaciones
        aprobacion.usuario_revisa = session.get('usuario')
        aprobacion.fecha_revision = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Documento {estado} exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error aprobando documento {documento_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# ============================================================================
# 📧 SISTEMA DE NOTIFICACIONES MASIVAS
# ============================================================================

def enviar_correo_notificacion(tercero_data, tipo_notificacion, asunto, mensaje):
    """Función auxiliar para enviar correo individual"""
    try:
        # Aquí se implementaría el envío real del correo
        # Por ahora simulamos el envío
        print(f"Enviando correo a {tercero_data['email']}: {asunto}")
        time.sleep(0.1)  # Simular tiempo de envío
        
        # Registrar en historial
        historial = HistorialNotificaciones(
            tercero_id=tercero_data['id'],
            tipo_notificacion=tipo_notificacion,
            asunto=asunto,
            mensaje=mensaje,
            estado_envio='enviado',
            correo_destinatario=tercero_data['email'],
            usuario_envia=session.get('usuario', 'sistema'),
            fecha_envio=datetime.now()
        )
        db.session.add(historial)
        db.session.commit()
        
        return True, "Enviado"
    except Exception as e:
        return False, str(e)

def envio_masivo_background(terceros_ids, asunto, mensaje, configuracion):
    """Función para envío masivo en background"""
    with current_app.app_context():
        try:
            Tercero, DocumentoTercero, Usuario = get_models()
            
            terceros = Tercero.query.filter(Tercero.id.in_(terceros_ids)).all()
            
            enviados = 0
            errores = 0
            
            for i, tercero in enumerate(terceros):
                if tercero.email:
                    exito, resultado = enviar_correo_notificacion({
                        'id': tercero.id,
                        'email': tercero.email,
                        'razon_social': tercero.razon_social
                    }, 'masiva', asunto, mensaje)
                    
                    if exito:
                        enviados += 1
                    else:
                        errores += 1
                
                # Pausa entre bloques
                if (i + 1) % configuracion['correos_por_bloque'] == 0:
                    time.sleep(configuracion['segundos_entre_bloques'])
            
            print(f"Envío masivo completado: {enviados} enviados, {errores} errores")
            
        except Exception as e:
            print(f"Error en envío masivo: {str(e)}")

@terceros_bp.route('/api/notificar_masivo', methods=['POST'])
@requiere_permiso('terceros', 'notificar_masivo')
def notificar_masivo():
    """Envío masivo de notificaciones con control de bloques"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        data = request.get_json()
        terceros_ids = data.get('terceros_ids', [])
        asunto = data.get('asunto', '')
        mensaje = data.get('mensaje', '')
        envio_inmediato = data.get('envio_inmediato', True)
        
        if not terceros_ids or not asunto or not mensaje:
            return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
        
        # Obtener configuración de envío
        config = ConfiguracionNotificaciones.query.first()
        if not config:
            config = ConfiguracionNotificaciones()
            db.session.add(config)
            db.session.commit()
        
        configuracion = {
            'correos_por_bloque': config.correos_por_bloque,
            'segundos_entre_bloques': config.segundos_entre_bloques
        }
        
        if envio_inmediato:
            # Iniciar envío en background
            thread = threading.Thread(
                target=envio_masivo_background,
                args=(terceros_ids, asunto, mensaje, configuracion)
            )
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'message': f'Envío masivo iniciado para {len(terceros_ids)} terceros',
                'configuracion': configuracion
            })
        else:
            # Solo programar para más tarde (implementar según necesidades)
            return jsonify({
                'success': True,
                'message': 'Envío programado exitosamente'
            })
        
    except Exception as e:
        current_app.logger.error(f"Error en notificar_masivo: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@terceros_bp.route('/api/historial_notificaciones/<int:tercero_id>', methods=['GET'])
@requiere_permiso('terceros', 'consultar')
def obtener_historial_notificaciones(tercero_id):
    """Obtener historial de notificaciones de un tercero"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        notificaciones = HistorialNotificaciones.query.filter_by(
            tercero_id=tercero_id
        ).order_by(desc(HistorialNotificaciones.fecha_envio)).all()
        
        historial_list = []
        for notif in notificaciones:
            historial_list.append({
                'id': notif.id,
                'tipo_notificacion': notif.tipo_notificacion,
                'asunto': notif.asunto,
                'estado_envio': notif.estado_envio,
                'fecha_envio': notif.fecha_envio.strftime('%d/%m/%Y %H:%M') if notif.fecha_envio else '',
                'usuario_envia': notif.usuario_envia,
                'error_envio': notif.error_envio
            })
        
        return jsonify({
            'success': True,
            'data': historial_list
        })
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo historial notificaciones {tercero_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# ============================================================================
# 📈 ESTADÍSTICAS Y REPORTES
# ============================================================================

@terceros_bp.route('/api/estadisticas', methods=['GET'])
@requiere_permiso('terceros', 'consultar')
def obtener_estadisticas():
    """Estadísticas generales del módulo"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        # Usar el helper de estadísticas
        stats = TerceroStats.obtener_estadisticas()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({
            'success': False, 
            'message': f'Error interno: {str(e)}'
        }), 500
        
        # Terceros con documentación
        terceros_con_docs = db.session.query(Tercero.id).join(
            DocumentoTercero, Tercero.id == DocumentoTercero.tercero_id
        ).distinct().count()
        
        # Terceros que requieren actualización (más de 365 días)
        fecha_limite = datetime.now() - timedelta(days=365)
        terceros_desactualizados = Tercero.query.filter(
            Tercero.fecha_actualizacion < fecha_limite
        ).count()
        
        # Documentos pendientes de aprobación
        docs_pendientes = AprobacionDocumentos.query.filter_by(estado='pendiente').count()
        
        # Notificaciones enviadas último mes
        fecha_mes = datetime.now() - timedelta(days=30)
        notifs_ultimo_mes = HistorialNotificaciones.query.filter(
            HistorialNotificaciones.fecha_envio >= fecha_mes
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_terceros': total_terceros,
                'terceros_activos': terceros_activos,
                'terceros_inactivos': terceros_inactivos,
                'terceros_con_documentacion': terceros_con_docs,
                'terceros_sin_documentacion': total_terceros - terceros_con_docs,
                'terceros_requieren_actualizacion': terceros_desactualizados,
                'documentos_pendientes_aprobacion': docs_pendientes,
                'notificaciones_ultimo_mes': notifs_ultimo_mes
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo estadísticas: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# ============================================================================
# 🔍 API ENDPOINTS ADICIONALES PARA NUEVAS PÁGINAS
# ============================================================================

@terceros_bp.route('/api/validar_nit', methods=['POST'])
@requiere_permiso('terceros', 'validar')
def validar_nit():
    """Validar disponibilidad de NIT para creación"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        data = request.get_json()
        nit = data.get('nit', '').strip()
        
        if not nit:
            return jsonify({"disponible": False, "message": "NIT requerido"}), 400
        
        Tercero, _, _ = get_models()
        tercero_existente = Tercero.query.filter_by(nit=nit).first()
        
        return jsonify({
            "disponible": tercero_existente is None,
            "message": "NIT disponible" if tercero_existente is None else "NIT ya registrado"
        })
        
    except Exception as e:
        current_app.logger.error(f"Error validando NIT: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500