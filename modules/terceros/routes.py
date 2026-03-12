"""
Rutas Simplificadas para el Módulo de Gestión de Terceros
Conecta directamente con la tabla terceros existente
"""

from flask import render_template, request, jsonify, session, redirect, url_for, current_app
from datetime import datetime, timedelta
import math
from . import terceros_bp
from .models import TerceroStats, TerceroHelper
from extensions import db
from decoradores_permisos import requiere_permiso, requiere_permiso_html

def validar_sesion_admin():
    """Valida sesión de administrador"""
    if 'usuario_id' not in session or 'usuario' not in session:
        return False, {"error": "Sesión no válida", "redirect": "/login"}, 401
    return True, None, None

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
    """Vista principal de consulta de terceros"""
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
        
        print(f"DEBUG: Parámetros recibidos - page: {page}, per_page: {per_page}, search: '{search}', estado: '{estado_filtro}', orden: '{orden}'")
        
        # Usar el helper simplificado
        terceros_paginados = TerceroHelper.listar_terceros(
            page=page, 
            per_page=per_page, 
            search=search, 
            estado=estado_filtro, 
            orden=orden
        )
        
        print(f"DEBUG: terceros_paginados resultado: {terceros_paginados is not None}")
        
        if not terceros_paginados:
            return jsonify({
                'success': False, 
                'message': 'Error al obtener terceros'
            }), 500
        
        print(f"DEBUG: Total de terceros: {terceros_paginados.total}, Items en página: {len(terceros_paginados.items)}")
        
        # Convertir resultados a formato JSON
        terceros_data = []
        fecha_hoy = datetime.now()
        
        for i, tercero in enumerate(terceros_paginados.items):
            try:
                # Calcular días de actualización
                fecha_actualizacion = getattr(tercero, 'fecha_actualizacion', None)
                fecha_registro = getattr(tercero, 'fecha_registro', None)
                
                # Usar fecha de actualización si existe, sino fecha de registro
                fecha_referencia = fecha_actualizacion if fecha_actualizacion else fecha_registro
                
                if fecha_referencia:
                    if isinstance(fecha_referencia, str):
                        # Si es string, intentar convertir
                        try:
                            from dateutil.parser import parse
                            fecha_referencia = parse(fecha_referencia)
                        except:
                            # Si falla, usar fecha actual menos 1000 días como fallback
                            from datetime import timedelta
                            fecha_referencia = fecha_hoy - timedelta(days=1000)
                    
                    delta = fecha_hoy - fecha_referencia
                    dias_actualizacion = delta.days
                else:
                    dias_actualizacion = 9999  # Valor alto si no hay fecha
                
                # Determinar si requiere actualización (más de 365 días)
                requiere_actualizacion = dias_actualizacion > 365
                
                # Determinar estado actual del tercero
                estado_bd = getattr(tercero, 'estado', 'activo')
                activo = estado_bd == 'activo'
                
                if estado_bd == 'activo':
                    estado_texto = 'Activo'
                    estado_clase = 'success'
                elif estado_bd == 'inactivo':
                    estado_texto = 'Inactivo'
                    estado_clase = 'danger'
                else:
                    estado_texto = estado_bd.title()
                    estado_clase = 'warning'
                
                tercero_dict = {
                    'id': tercero.id,
                    'nit': tercero.nit,
                    'razon_social': tercero.razon_social,
                    'primer_nombre': getattr(tercero, 'primer_nombre', ''),
                    'primer_apellido': getattr(tercero, 'primer_apellido', ''),
                    'telefono': getattr(tercero, 'celular', ''),  # Usar celular en lugar de telefono
                    'email': getattr(tercero, 'correo', 'No registrado'),  # Usar correo en lugar de email
                    'tipo_persona': getattr(tercero, 'tipo_persona', ''),
                    'fecha_registro': fecha_registro.strftime('%Y-%m-%d') if fecha_registro else 'No registrado',
                    'fecha_actualizacion': fecha_actualizacion.strftime('%Y-%m-%d') if fecha_actualizacion else 'No actualizado',
                    'dias_actualizacion': dias_actualizacion,
                    'requiere_actualizacion': requiere_actualizacion,
                    'total_documentos': 0,  # Por simplicidad, por ahora 0
                    'tiene_documentos': False,  # Por simplicidad, por ahora False
                    'activo': activo,  # Estado real desde BD
                    'estado_texto': estado_texto,  # Texto del estado
                    'estado_clase': estado_clase,  # Clase CSS según estado
                    'estado_bd': estado_bd  # Estado original de la BD para debug
                }
                terceros_data.append(tercero_dict)
                
                if i < 3:  # Solo loggear los primeros 3
                    print(f"DEBUG: Tercero {i+1}: {tercero.nit} - {tercero.razon_social}")
                    
            except Exception as e:
                print(f"DEBUG: Error procesando tercero {i}: {e}")
                continue
        
        print(f"DEBUG: Terceros procesados exitosamente: {len(terceros_data)}")
        
        return jsonify({
            'success': True,
            'data': {
                'terceros': terceros_data,
                'stats': {
                    'total_terceros': terceros_paginados.total,
                    'mostrando_desde': ((terceros_paginados.page - 1) * terceros_paginados.per_page) + 1,
                    'mostrando_hasta': min(terceros_paginados.page * terceros_paginados.per_page, terceros_paginados.total),
                    'pagina_actual': terceros_paginados.page,
                    'total_paginas': terceros_paginados.pages,
                    'por_pagina': terceros_paginados.per_page
                },
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
            }
        })
        
    except Exception as e:
        print(f"ERROR en listar_terceros: {e}")
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error en listar_terceros: {e}")
        return jsonify({
            'success': False, 
            'message': f'Error interno: {str(e)}'
        }), 500

# ============================================================================
# 📊 ESTADÍSTICAS DEL MÓDULO
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

# ============================================================================
# 🆕 CREAR TERCERO
# ============================================================================

@terceros_bp.route('/crear')
@requiere_permiso_html('terceros', 'crear')
def crear():
    """Vista para crear nuevo tercero"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return redirect('/')
    
    # 🎯 Obtener radicado si viene desde SAGRILAFT
    radicado = request.args.get('radicado', None)
    return render_template('tercero_crear.html', usuario=session.get('usuario'), radicado=radicado)

@terceros_bp.route('/api/obtener_datos_radicado/<radicado>')
@requiere_permiso('terceros', 'crear')
def obtener_datos_radicado(radicado):
    """Obtiene datos del tercero asociado a un radicado"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        from app import SolicitudRegistro, Tercero
        
        # Buscar solicitud por radicado
        solicitud = SolicitudRegistro.query.filter_by(radicado=radicado).first()
        
        if not solicitud:
            return jsonify({
                'success': False,
                'message': 'Radicado no encontrado'
            }), 404
        
        # Obtener datos del tercero
        tercero = Tercero.query.get(solicitud.tercero_id)
        
        if not tercero:
            return jsonify({
                'success': False,
                'message': 'Tercero no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'radicado': radicado,
            'tercero': {
                'id': tercero.id,
                'nit': tercero.nit or '',
                'tipo_persona': tercero.tipo_persona or 'juridica',
                'razon_social': tercero.razon_social or '',
                'primer_nombre': tercero.primer_nombre or '',
                'segundo_nombre': tercero.segundo_nombre or '',
                'primer_apellido': tercero.primer_apellido or '',
                'segundo_apellido': tercero.segundo_apellido or '',
                'correo': tercero.correo or '',
                'celular': tercero.celular or '',
                'telefono': tercero.telefono or tercero.celular or '',
                'direccion': tercero.direccion or '',
                'ciudad': tercero.ciudad or '',
                'departamento': tercero.departamento or '',
                'tipo_documento': tercero.tipo_documento or ''
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error obteniendo datos de radicado {radicado}: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@terceros_bp.route('/api/crear', methods=['POST'])
@requiere_permiso('terceros', 'crear')
def crear_tercero():
    """API para crear nuevo tercero"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        data = request.get_json()
        
        # Validar NIT único
        tercero_existente = TerceroHelper.buscar_por_nit(data.get('nit'))
        if tercero_existente:
            return jsonify({
                'success': False,
                'error_code': 'NIT_DUPLICADO',
                'message': 'Ya existe un tercero con este NIT',
                'tercero_id': tercero_existente.id
            }), 400
        
        # Crear nuevo tercero
        from app import Tercero
        nuevo_tercero = Tercero(
            nit=data.get('nit'),
            razon_social=data.get('razon_social') or None,
            primer_nombre=data.get('primer_nombre') or None,
            segundo_nombre=data.get('segundo_nombre') or None,
            primer_apellido=data.get('primer_apellido') or None,
            segundo_apellido=data.get('segundo_apellido') or None,
            correo=data.get('correo') or data.get('email') or None,
            telefono=data.get('telefono') or None,
            direccion=data.get('direccion') or None,
            ciudad=data.get('ciudad') or None,
            departamento=data.get('departamento') or None,
            tipo_persona=data.get('tipo_persona', 'juridica'),
            tipo_documento=data.get('tipo_documento') or ('NIT' if data.get('tipo_persona') != 'natural' else 'CC'),
            estado=data.get('estado_inicial', 'inactivo'),
            fecha_registro=datetime.now()
        )
        
        db.session.add(nuevo_tercero)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Tercero creado exitosamente',
            'tercero_id': nuevo_tercero.id
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creando tercero: {e}")
        return jsonify({
            'success': False, 
            'message': f'Error interno: {str(e)}'
        }), 500

# ============================================================================
# ✏️ EDITAR TERCERO
# ============================================================================

@terceros_bp.route('/editar/<int:tercero_id>')
@requiere_permiso_html('terceros', 'editar')
def editar(tercero_id):
    """Vista para editar tercero"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return redirect('/')
    
    tercero = TerceroHelper.obtener_tercero_por_id(tercero_id)
    if not tercero:
        return redirect('/terceros/consulta')
    
    return render_template('tercero_editar.html', 
                         tercero=tercero, 
                         usuario=session.get('usuario'))

@terceros_bp.route('/api/cambiar_estado/<int:tercero_id>', methods=['POST'])
def cambiar_estado_tercero(tercero_id):
    """API para cambiar estado de un tercero (sin permisos por ahora)"""
    try:
        # Obtener datos del request
        data = request.get_json() if request.is_json else {}
        nuevo_activo = data.get('activo', True)
        
        # Obtener tercero desde la base de datos directamente
        from app import Tercero, db
        tercero = Tercero.query.get(tercero_id)
        
        if not tercero:
            return jsonify({
                'success': False,
                'message': 'Tercero no encontrado'
            }), 404
        
        # Cambiar el estado (convertir boolean a string)
        estado_anterior = tercero.estado
        tercero.estado = 'activo' if nuevo_activo else 'inactivo'
        
        # Guardar en base de datos
        db.session.commit()
        
        print(f"DEBUG: Tercero {tercero.nit} cambiado de '{estado_anterior}' a '{tercero.estado}'")
        
        return jsonify({
            'success': True,
            'message': f'Tercero {tercero.nit} ({tercero.razon_social}) cambiado de {estado_anterior} a {tercero.estado} exitosamente',
            'data': {
                'tercero_id': tercero_id,
                'nit': tercero.nit,
                'razon_social': tercero.razon_social,
                'estado_anterior': estado_anterior,
                'estado_nuevo': tercero.estado
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR en cambiar_estado_tercero: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error al cambiar estado del tercero: {str(e)}'
        }), 500

@terceros_bp.route('/api/obtener/<int:tercero_id>', methods=['GET'])
@requiere_permiso('terceros', 'consultar')
def obtener_tercero(tercero_id):
    """API para obtener datos de un tercero"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        tercero = TerceroHelper.obtener_tercero_por_id(tercero_id)
        if not tercero:
            return jsonify({
                'success': False, 
                'message': 'Tercero no encontrado'
            }), 404
        
        def _bool(val, default=False):
            v = getattr(tercero, val, default)
            return bool(v) if v is not None else default

        return jsonify({
            'success': True,
            'tercero': {
                'id': tercero.id,
                'nit': tercero.nit,
                'razon_social': tercero.razon_social or '',
                'primer_nombre': getattr(tercero, 'primer_nombre', '') or '',
                'segundo_nombre': getattr(tercero, 'segundo_nombre', '') or '',
                'primer_apellido': getattr(tercero, 'primer_apellido', '') or '',
                'segundo_apellido': getattr(tercero, 'segundo_apellido', '') or '',
                'telefono': getattr(tercero, 'telefono', '') or getattr(tercero, 'celular', '') or '',
                'email': getattr(tercero, 'correo', '') or '',
                'correo': getattr(tercero, 'correo', '') or '',
                'direccion': getattr(tercero, 'direccion', '') or '',
                'ciudad': getattr(tercero, 'ciudad', '') or '',
                'departamento': getattr(tercero, 'departamento', '') or '',
                'tipo_documento': getattr(tercero, 'tipo_documento', '') or '',
                'activo': getattr(tercero, 'estado', 'inactivo') == 'activo',
                'tipo_persona': getattr(tercero, 'tipo_persona', '') or '',
                'fecha_registro': tercero.fecha_registro.strftime('%Y-%m-%d %H:%M') if tercero.fecha_registro else '',
                'fecha_actualizacion': tercero.fecha_actualizacion.strftime('%Y-%m-%d %H:%M') if getattr(tercero, 'fecha_actualizacion', None) else '',
                # Contacto extendido
                'telefono_secundario': getattr(tercero, 'telefono_secundario', '') or '',
                'contacto_principal': getattr(tercero, 'contacto_principal', '') or '',
                'cargo_contacto': getattr(tercero, 'cargo_contacto', '') or '',
                # Categoría y correos
                'categoria_tercero': getattr(tercero, 'categoria_tercero', '') or '',
                'email_contabilidad': getattr(tercero, 'email_contabilidad', '') or '',
                'email_tesoreria': getattr(tercero, 'email_tesoreria', '') or '',
                'email_comercial': getattr(tercero, 'email_comercial', '') or '',
                'codigo_ciiu':   getattr(tercero, 'codigo_ciiu',   '') or '',
                'codigo_ciiu_2': getattr(tercero, 'codigo_ciiu_2', '') or '',
                'codigo_ciiu_3': getattr(tercero, 'codigo_ciiu_3', '') or '',
                # Responsabilidades tributarias
                'responsable_iva': _bool('responsable_iva'),
                'autorretenedor_renta': _bool('autorretenedor_renta'),
                'gran_contribuyente': _bool('gran_contribuyente'),
                'gran_contribuyente_ica': _bool('gran_contribuyente_ica'),
                'dept_gc_ica': getattr(tercero, 'dept_gc_ica', '') or '',
                'mun_gc_ica': getattr(tercero, 'mun_gc_ica', '') or '',
                'autorretenedor_ica': _bool('autorretenedor_ica'),
                'dept_autorretenedor_ica': getattr(tercero, 'dept_autorretenedor_ica', '') or '',
                'mun_autorretenedor_ica': getattr(tercero, 'mun_autorretenedor_ica', '') or '',
                'agente_retenedor_iva': _bool('agente_retenedor_iva'),
                'regimen_simple': _bool('regimen_simple'),
                'otras_responsabilidades': getattr(tercero, 'otras_responsabilidades', '') or '',
                # Notificaciones
                'notificaciones_activas': _bool('notificaciones_activas', True),
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo tercero: {e}")
        return jsonify({
            'success': False, 
            'message': f'Error interno: {str(e)}'
        }), 500

# ============================================================================
# 📄 DOCUMENTOS DEL TERCERO (SIMPLIFICADO)
# ============================================================================

@terceros_bp.route('/documentos/<int:tercero_id>')
@requiere_permiso_html('terceros', 'gestionar_documentos')
def documentos(tercero_id):
    """Vista de documentos del tercero"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return redirect('/')
    
    tercero = TerceroHelper.obtener_tercero_por_id(tercero_id)
    if not tercero:
        return redirect('/terceros/consulta')
    
    return render_template('tercero_documentos.html', 
                         tercero=tercero, 
                         usuario=session.get('usuario'))

# ============================================================================
# ⚙️ CONFIGURACIÓN DEL MÓDULO
# ============================================================================

# ============================================================================
# ✏️ ACTUALIZAR TERCERO
# ============================================================================

@terceros_bp.route('/api/actualizar/<int:tercero_id>', methods=['PUT'])
@requiere_permiso('terceros', 'editar')
def actualizar_tercero(tercero_id):
    """API para actualizar datos de un tercero existente"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo

    try:
        from app import Tercero
        tercero = Tercero.query.get(tercero_id)
        if not tercero:
            return jsonify({'success': False, 'message': 'Tercero no encontrado'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos'}), 400

        # --- Campos del modelo core Tercero ---
        def _str(key, upper=False):
            v = data.get(key)
            if v is None:
                return None
            v = str(v).strip()
            return v.upper() if upper else v

        def _bool_field(key, default=None):
            v = data.get(key)
            if v is None:
                return default
            return bool(v)

        # Campos core
        if 'razon_social' in data and data['razon_social']:
            tercero.razon_social = data['razon_social'].upper().strip()
        if 'email' in data:
            tercero.correo = data['email'].strip() if data['email'] else None
        if 'telefono' in data:
            tercero.telefono = _str('telefono')
        if 'direccion' in data:
            tercero.direccion = _str('direccion')
        if 'ciudad' in data:
            tercero.ciudad = _str('ciudad')
        if 'departamento' in data:
            tercero.departamento = _str('departamento')
        if 'tipo_documento' in data:
            tercero.tipo_documento = _str('tipo_documento')
        if 'activo' in data:
            tercero.estado = 'activo' if data['activo'] else 'inactivo'

        # Contacto extendido
        for campo in ('telefono_secundario', 'contacto_principal', 'cargo_contacto'):
            if campo in data:
                setattr(tercero, campo, _str(campo, upper=(campo in ('contacto_principal', 'cargo_contacto'))))

        # Categoría y correos
        if 'categoria_tercero' in data:
            tercero.categoria_tercero = _str('categoria_tercero')
        for campo in ('email_contabilidad', 'email_tesoreria', 'email_comercial'):
            if campo in data:
                setattr(tercero, campo, _str(campo))
        for campo in ('codigo_ciiu', 'codigo_ciiu_2', 'codigo_ciiu_3'):
            if campo in data:
                setattr(tercero, campo, _str(campo))

        # Responsabilidades tributarias DIAN
        bool_campos = [
            'responsable_iva', 'autorretenedor_renta', 'gran_contribuyente',
            'gran_contribuyente_ica', 'autorretenedor_ica',
            'agente_retenedor_iva', 'regimen_simple'
        ]
        for campo in bool_campos:
            v = _bool_field(campo)
            if v is not None:
                setattr(tercero, campo, v)

        # Departamento/municipio ICA
        for campo in ('dept_gc_ica', 'mun_gc_ica', 'dept_autorretenedor_ica', 'mun_autorretenedor_ica'):
            if campo in data:
                setattr(tercero, campo, _str(campo))

        # Otras responsabilidades (JSON string)
        if 'otras_responsabilidades' in data:
            tercero.otras_responsabilidades = data['otras_responsabilidades'] or None

        # Notificaciones
        v_notif = _bool_field('notificaciones_activas')
        if v_notif is not None:
            tercero.notificaciones_activas = v_notif

        # Fecha actualización
        from datetime import datetime as _dt
        tercero.fecha_actualizacion = _dt.now()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Tercero actualizado exitosamente',
            'data': {
                'id': tercero.id,
                'nit': tercero.nit,
                'razon_social': tercero.razon_social or '',
                'email': tercero.correo or '',
                'telefono': getattr(tercero, 'telefono', '') or '',
                'direccion': getattr(tercero, 'direccion', '') or '',
                'ciudad': getattr(tercero, 'ciudad', '') or '',
                'departamento': getattr(tercero, 'departamento', '') or '',
                'tipo_documento': getattr(tercero, 'tipo_documento', '') or '',
                'activo': getattr(tercero, 'estado', 'inactivo') == 'activo',
                'fecha_registro': tercero.fecha_registro.strftime('%Y-%m-%d %H:%M') if tercero.fecha_registro else ''
            }
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error actualizando tercero {tercero_id}: {e}")
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@terceros_bp.route('/configuracion')
@requiere_permiso_html('terceros', 'configurar')
def configuracion():
    """Vista de configuración del módulo"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return redirect('/')
    return render_template('tercero_configuracion.html', usuario=session.get('usuario'))