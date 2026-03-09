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
    return render_template('tercero_crear.html', usuario=session.get('usuario'))

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
                'message': 'Ya existe un tercero con este NIT'
            }), 400
        
        # Crear nuevo tercero
        from app import Tercero
        nuevo_tercero = Tercero(
            nit=data.get('nit'),
            razon_social=data.get('razon_social'),
            primer_nombre=data.get('primer_nombre', ''),
            segundo_nombre=data.get('segundo_nombre', ''),
            primer_apellido=data.get('primer_apellido', ''),
            segundo_apellido=data.get('segundo_apellido', ''),
            telefono=data.get('telefono', ''),
            email=data.get('email', ''),
            tipo_persona=data.get('tipo_persona', 'juridica'),
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
        
        return jsonify({
            'success': True,
            'tercero': {
                'id': tercero.id,
                'nit': tercero.nit,
                'razon_social': tercero.razon_social,
                'primer_nombre': getattr(tercero, 'primer_nombre', ''),
                'segundo_nombre': getattr(tercero, 'segundo_nombre', ''),
                'primer_apellido': getattr(tercero, 'primer_apellido', ''),
                'segundo_apellido': getattr(tercero, 'segundo_apellido', ''),
                'telefono': getattr(tercero, 'telefono', ''),
                'email': getattr(tercero, 'email', ''),
                'tipo_persona': getattr(tercero, 'tipo_persona', ''),
                'fecha_registro': tercero.fecha_registro.strftime('%Y-%m-%d %H:%M') if tercero.fecha_registro else ''
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

@terceros_bp.route('/configuracion')
@requiere_permiso_html('terceros', 'configurar')
def configuracion():
    """Vista de configuración del módulo"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return redirect('/')
    return render_template('tercero_configuracion.html', usuario=session.get('usuario'))