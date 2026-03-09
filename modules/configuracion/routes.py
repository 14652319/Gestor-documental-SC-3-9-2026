"""
Blueprint para el módulo de Configuración
Gestiona tipos de documento y centros de operación
"""
from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Importar desde extensions.py para evitar circular imports
from extensions import db
from decoradores_permisos import requiere_permiso, requiere_permiso_html

# Logging simple sin importar app para evitar conflictos de modelos
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_security(mensaje):
    """Log de seguridad sin importar app"""
    logger.info(f"[CONFIGURACION] {mensaje}")

from modules.configuracion.models import TipoDocumento, CentroOperacion, Empresa

# Crear blueprint
configuracion_bp = Blueprint('configuracion', __name__, url_prefix='/api/configuracion')

# =====================================================
# ENDPOINTS PÚBLICOS PARA SELECTS (sin permisos requeridos)
# =====================================================

@configuracion_bp.route('/empresas/opciones', methods=['GET'])
def opciones_empresas():
    """Lista empresas activas para selects (sin requerir permisos)"""
    try:
        empresas = Empresa.query.filter_by(activo=True).order_by(Empresa.sigla).all()
        return jsonify({
            'success': True,
            'data': [empresa.to_dict() for empresa in empresas]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@configuracion_bp.route('/tipos_documento/opciones', methods=['GET'])
def opciones_tipos_documento():
    """Lista tipos de documento activos para selects (sin requerir permisos)"""
    try:
        tipos = TipoDocumento.query.filter_by(estado='activo').order_by(TipoDocumento.siglas).all()
        return jsonify({
            'success': True,
            'data': [tipo.to_dict() for tipo in tipos]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@configuracion_bp.route('/centros_operacion/opciones', methods=['GET'])
def opciones_centros_operacion():
    """Lista centros de operación activos para selects (sin requerir permisos)"""
    try:
        centros = CentroOperacion.query.filter_by(activo=True).order_by(CentroOperacion.codigo).all()
        return jsonify({
            'success': True,
            'data': [centro.to_dict() for centro in centros]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# =====================================================
# ENDPOINTS PARA TIPOS DE DOCUMENTO
# =====================================================

@configuracion_bp.route('/tipos_documento/listar', methods=['GET'])
@requiere_permiso('configuracion', 'tipos_documento')
def listar_tipos_documento():
    """Lista todos los tipos de documento (activos e inactivos)"""
    try:
        tipos = TipoDocumento.query.order_by(TipoDocumento.siglas).all()
        
        log_security(f"LISTADO TIPOS DOCUMENTO | total={len(tipos)} | IP={request.remote_addr}")
        
        return jsonify({
            'success': True,
            'data': [tipo.to_dict() for tipo in tipos]
        }), 200
        
    except Exception as e:
        log_security(f"ERROR LISTAR TIPOS | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al listar tipos de documento: {str(e)}'
        }), 500

@configuracion_bp.route('/tipos_documento/crear', methods=['POST'])
@requiere_permiso('configuracion', 'tipos_documento')
def crear_tipo_documento():
    """Crea un nuevo tipo de documento"""
    try:
        data = request.get_json()
        
        # Validaciones
        if not data.get('siglas') or not data.get('nombre') or not data.get('modulo'):
            return jsonify({
                'success': False,
                'message': 'Faltan campos obligatorios: siglas, nombre, módulo'
            }), 400
        
        # Verificar que las siglas no existan
        if TipoDocumento.query.filter_by(siglas=data['siglas'].upper()).first():
            return jsonify({
                'success': False,
                'message': f'Ya existe un tipo de documento con siglas {data["siglas"]}'
            }), 400
        
        # Crear nuevo tipo
        nuevo_tipo = TipoDocumento(
            siglas=data['siglas'].upper(),
            nombre=data['nombre'],
            modulo=data['modulo'],
            estado=data.get('estado', 'activo'),
            created_by=data.get('created_by', 'sistema')
        )
        
        db.session.add(nuevo_tipo)
        db.session.flush()  # Obtener el ID antes del commit
        
        log_security(f"TIPO DOCUMENTO CREADO | id={nuevo_tipo.id} | siglas={nuevo_tipo.siglas} | usuario={nuevo_tipo.created_by}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tipo de documento creado exitosamente',
            'data': nuevo_tipo.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR CREAR TIPO | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al crear tipo de documento: {str(e)}'
        }), 500

@configuracion_bp.route('/tipos_documento/editar/<int:tipo_id>', methods=['PUT'])
@requiere_permiso('configuracion', 'tipos_documento')
def editar_tipo_documento(tipo_id):
    """Edita un tipo de documento existente (solo nombre, módulo, estado)"""
    try:
        data = request.get_json()
        
        tipo = TipoDocumento.query.get(tipo_id)
        if not tipo:
            return jsonify({
                'success': False,
                'message': f'Tipo de documento con ID {tipo_id} no encontrado'
            }), 404
        
        # Actualizar solo campos permitidos (NO siglas)
        if 'nombre' in data:
            tipo.nombre = data['nombre']
        if 'modulo' in data:
            tipo.modulo = data['modulo']
        if 'estado' in data:
            tipo.estado = data['estado']
        
        tipo.updated_by = data.get('updated_by', 'sistema')
        tipo.updated_at = datetime.utcnow()
        
        log_security(f"TIPO DOCUMENTO EDITADO | id={tipo_id} | siglas={tipo.siglas} | usuario={tipo.updated_by}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tipo de documento actualizado exitosamente',
            'data': tipo.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR EDITAR TIPO | id={tipo_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al editar tipo de documento: {str(e)}'
        }), 500

# =====================================================
# ENDPOINTS PARA CENTROS DE OPERACIÓN
# =====================================================
@configuracion_bp.route('/centros_operacion/listar', methods=['GET'])
@requiere_permiso('configuracion', 'centros_operacion')
def listar_centros_operacion():
    """Lista todos los centros de operación (activos e inactivos)"""
    try:
        centros = CentroOperacion.query.order_by(CentroOperacion.codigo).all()
        
        log_security(f"LISTADO CENTROS OPERACIÓN | total={len(centros)} | IP={request.remote_addr}")
        
        return jsonify({
            'success': True,
            'data': [centro.to_dict() for centro in centros]
        }), 200
        
    except Exception as e:
        log_security(f"ERROR LISTAR CENTROS | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al listar centros de operación: {str(e)}'
        }), 500

@configuracion_bp.route('/centros_operacion/crear', methods=['POST'])
@requiere_permiso('configuracion', 'centros_operacion')
def crear_centro_operacion():
    """Crea un nuevo centro de operación"""
    try:
        data = request.get_json()
        
        # Validaciones
        if not data.get('codigo') or not data.get('nombre'):
            return jsonify({
                'success': False,
                'message': 'Faltan campos obligatorios: código, nombre'
            }), 400
        
        # Verificar que el código no exista
        if CentroOperacion.query.filter_by(codigo=data['codigo']).first():
            return jsonify({
                'success': False,
                'message': f'Ya existe un centro de operación con código {data["codigo"]}'
            }), 400
        
        # Crear nuevo centro
        nuevo_centro = CentroOperacion(
            codigo=data['codigo'],
            nombre=data['nombre'],
            direccion=data.get('direccion'),
            ciudad=data.get('ciudad'),
            contacto=data.get('contacto'),
            telefono=data.get('telefono'),
            barrio=data.get('barrio'),
            email=data.get('email'),
            cod_depto=data.get('cod_depto'),
            cod_pais=data.get('cod_pais'),
            cod_ciudad=data.get('cod_ciudad'),
            almacen=bool(data.get('almacen', False)),
            bodega=bool(data.get('bodega', False)),
            c_comercial=bool(data.get('c_comercial', False)),
            otros=bool(data.get('otros', False)),
            mayorista=bool(data.get('mayorista', False)),
            asaderos=bool(data.get('asaderos', False)),
            panaderias=bool(data.get('panaderias', False)),
            domicilios=bool(data.get('domicilios', False)),
            estado=data.get('estado', 'ACTIVO'),
            tipo_propiedad=data.get('tipo_propiedad', 'PROPIO'),
            empresa_id=data.get('empresa_id'),
            created_by=data.get('created_by', 'sistema'),
            fecha_registro=datetime.utcnow()
        )
        
        db.session.add(nuevo_centro)
        db.session.flush()
        
        log_security(f"CENTRO OPERACIÓN CREADO | id={nuevo_centro.id} | codigo={nuevo_centro.codigo} | usuario={nuevo_centro.created_by}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Centro de operación creado exitosamente',
            'data': nuevo_centro.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR CREAR CENTRO | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al crear centro de operación: {str(e)}'
        }), 500

@configuracion_bp.route('/centros_operacion/editar/<int:centro_id>', methods=['PUT'])
@requiere_permiso('configuracion', 'centros_operacion')
def editar_centro_operacion(centro_id):
    """Edita un centro de operación existente (TODOS LOS CAMPOS editables)"""
    try:
        data = request.get_json()
        
        centro = CentroOperacion.query.get(centro_id)
        if not centro:
            return jsonify({
                'success': False,
                'message': f'Centro de operación con ID {centro_id} no encontrado'
            }), 404
        
        # Actualizar todos los campos permitidos
        if 'codigo' in data:
            # Verificar que el nuevo código no esté en uso por otro centro
            if data['codigo'] != centro.codigo:
                if CentroOperacion.query.filter_by(codigo=data['codigo']).first():
                    return jsonify({
                        'success': False,
                        'message': f'El código {data["codigo"]} ya está en uso'
                    }), 400
            centro.codigo = data['codigo']
        
        if 'nombre' in data:
            centro.nombre = data['nombre']
        if 'direccion' in data:
            centro.direccion = data['direccion']
        if 'ciudad' in data:
            centro.ciudad = data['ciudad']
        if 'contacto' in data:
            centro.contacto = data['contacto']
        if 'telefono' in data:
            centro.telefono = data['telefono']
        if 'barrio' in data:
            centro.barrio = data['barrio']
        if 'email' in data:
            centro.email = data['email']
        if 'cod_depto' in data:
            centro.cod_depto = data['cod_depto']
        if 'cod_pais' in data:
            centro.cod_pais = data['cod_pais']
        if 'cod_ciudad' in data:
            centro.cod_ciudad = data['cod_ciudad']
        if 'almacen' in data:
            centro.almacen = bool(data['almacen'])
        if 'bodega' in data:
            centro.bodega = bool(data['bodega'])
        if 'c_comercial' in data:
            centro.c_comercial = bool(data['c_comercial'])
        if 'otros' in data:
            centro.otros = bool(data['otros'])
        if 'mayorista' in data:
            centro.mayorista = bool(data['mayorista'])
        if 'asaderos' in data:
            centro.asaderos = bool(data['asaderos'])
        if 'panaderias' in data:
            centro.panaderias = bool(data['panaderias'])
        if 'domicilios' in data:
            centro.domicilios = bool(data['domicilios'])
        if 'estado' in data:
            centro.estado = data['estado']
        if 'tipo_propiedad' in data:
            centro.tipo_propiedad = data['tipo_propiedad']
        if 'empresa_id' in data:
            centro.empresa_id = data['empresa_id']
        
        centro.updated_by = data.get('updated_by', 'sistema')
        centro.updated_at = datetime.utcnow()
        
        log_security(f"CENTRO OPERACIÓN EDITADO | id={centro_id} | codigo={centro.codigo} | usuario={centro.updated_by}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Centro de operación actualizado exitosamente',
            'data': centro.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR EDITAR CENTRO | id={centro_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al editar centro de operación: {str(e)}'
        }), 500

@configuracion_bp.route('/centros_operacion/toggle/<int:centro_id>', methods=['PATCH'])
@requiere_permiso('configuracion', 'centros_operacion')
def toggle_estado_centro(centro_id):
    """Activa/Desactiva un centro de operación (cambia estado ACTIVO/INACTIVO)"""
    try:
        data = request.get_json() or {}
        nuevo_estado = data.get('estado')

        if nuevo_estado not in ('ACTIVO', 'INACTIVO'):
            return jsonify({'success': False, 'message': 'Estado inválido'}), 400

        centro = CentroOperacion.query.get(centro_id)
        if not centro:
            return jsonify({'success': False, 'message': f'Centro con ID {centro_id} no encontrado'}), 404

        centro.estado = nuevo_estado
        centro.updated_by = data.get('updated_by', 'sistema')
        centro.updated_at = datetime.utcnow()

        db.session.commit()

        log_security(f"CENTRO TOGGLE ESTADO | id={centro_id} | estado={nuevo_estado}")

        return jsonify({'success': True, 'data': centro.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR TOGGLE CENTRO | id={centro_id} | error={str(e)}")
        return jsonify({'success': False, 'message': f'Error al cambiar estado: {str(e)}'}), 500

# =====================================================
# VISTAS HTML
# =====================================================
@configuracion_bp.route('/centros_operacion_view', methods=['GET'])
@requiere_permiso_html('configuracion', 'acceder_modulo')
def centros_operacion_view():
    """Renderiza la vista HTML de gestión de centros de operación"""
    try:
        return render_template('centros_operacion.html')
    except Exception as e:
        log_security(f"ERROR VISTA CENTROS | error={str(e)}")
        return f"Error al cargar vista de centros de operación: {str(e)}", 500

@configuracion_bp.route('/tipos_documento_view', methods=['GET'])
@requiere_permiso_html('configuracion', 'acceder_modulo')
def tipos_documento_view():
    """Renderiza la vista HTML de gestión de tipos de documentos"""
    try:
        return render_template('tipos_documento.html')
    except Exception as e:
        log_security(f"ERROR VISTA TIPOS DOC | error={str(e)}")
        return f"Error al cargar vista de tipos de documentos: {str(e)}", 500

# =====================================================
# CRUD EMPRESAS
# =====================================================
@configuracion_bp.route('/empresas/listar', methods=['GET'])
@requiere_permiso('configuracion', 'parametros_sistema')
def listar_empresas():
    """Lista todas las empresas (activas e inactivas)"""
    try:
        empresas = Empresa.query.order_by(Empresa.sigla).all()
        
        log_security(f"LISTADO EMPRESAS | total={len(empresas)} | IP={request.remote_addr}")
        
        return jsonify({
            'success': True,
            'data': [empresa.to_dict() for empresa in empresas]
        }), 200
        
    except Exception as e:
        log_security(f"ERROR LISTAR EMPRESAS | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al listar empresas: {str(e)}'
        }), 500

@configuracion_bp.route('/empresas/crear', methods=['POST'])
@requiere_permiso('configuracion', 'parametros_sistema')
def crear_empresa():
    """Crea una nueva empresa"""
    try:
        data = request.get_json()
        
        # Validaciones
        if not data.get('sigla') or not data.get('nombre'):
            return jsonify({
                'success': False,
                'message': 'Sigla y nombre son requeridos'
            }), 400
        
        # Convertir a mayúsculas
        sigla = data['sigla'].strip().upper()
        nombre = data['nombre'].strip().upper()
        
        # Verificar duplicados
        existe = Empresa.query.filter_by(sigla=sigla).first()
        if existe:
            return jsonify({
                'success': False,
                'message': f'Ya existe una empresa con la sigla {sigla}'
            }), 400
        
        # Crear empresa
        nueva_empresa = Empresa(
            sigla=sigla,
            nombre=nombre,
            activo=data.get('activo', True)
        )
        
        db.session.add(nueva_empresa)
        db.session.commit()
        
        log_security(f"EMPRESA CREADA | sigla={sigla} | nombre={nombre} | IP={request.remote_addr}")
        
        return jsonify({
            'success': True,
            'message': 'Empresa creada exitosamente',
            'data': nueva_empresa.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR CREAR EMPRESA | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al crear empresa: {str(e)}'
        }), 500

@configuracion_bp.route('/empresas/editar/<int:empresa_id>', methods=['PUT'])
@requiere_permiso('configuracion', 'parametros_sistema')
def editar_empresa(empresa_id):
    """Edita una empresa existente"""
    try:
        empresa = Empresa.query.get(empresa_id)
        if not empresa:
            return jsonify({
                'success': False,
                'message': 'Empresa no encontrada'
            }), 404
        
        data = request.get_json()
        
        # Actualizar campos
        if 'sigla' in data:
            nueva_sigla = data['sigla'].strip().upper()
            # Verificar duplicados (excepto la misma empresa)
            existe = Empresa.query.filter(
                Empresa.sigla == nueva_sigla,
                Empresa.id != empresa_id
            ).first()
            if existe:
                return jsonify({
                    'success': False,
                    'message': f'Ya existe otra empresa con la sigla {nueva_sigla}'
                }), 400
            empresa.sigla = nueva_sigla
        
        if 'nombre' in data:
            empresa.nombre = data['nombre'].strip().upper()
        
        if 'activo' in data:
            empresa.activo = data['activo']
        
        empresa.fecha_actualizacion = datetime.utcnow()
        
        db.session.commit()
        
        log_security(f"EMPRESA EDITADA | id={empresa_id} | sigla={empresa.sigla} | IP={request.remote_addr}")
        
        return jsonify({
            'success': True,
            'message': 'Empresa actualizada exitosamente',
            'data': empresa.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR EDITAR EMPRESA | id={empresa_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al editar empresa: {str(e)}'
        }), 500

@configuracion_bp.route('/empresas/toggle/<int:empresa_id>', methods=['PATCH'])
@requiere_permiso('configuracion', 'parametros_sistema')
def toggle_estado_empresa(empresa_id):
    """Activa/desactiva una empresa"""
    try:
        empresa = Empresa.query.get(empresa_id)
        if not empresa:
            return jsonify({
                'success': False,
                'message': 'Empresa no encontrada'
            }), 404
        
        empresa.activo = not empresa.activo
        empresa.fecha_actualizacion = datetime.utcnow()
        
        db.session.commit()
        
        estado = 'activada' if empresa.activo else 'desactivada'
        log_security(f"EMPRESA {estado.upper()} | id={empresa_id} | sigla={empresa.sigla} | IP={request.remote_addr}")
        
        return jsonify({
            'success': True,
            'message': f'Empresa {estado} exitosamente',
            'data': empresa.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR TOGGLE EMPRESA | id={empresa_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al cambiar estado: {str(e)}'
        }), 500

# =====================================================
# VISTA HTML EMPRESAS
# =====================================================
@configuracion_bp.route('/empresas_view', methods=['GET'])
@requiere_permiso_html('configuracion', 'acceder_modulo')
def empresas_view():
    """Renderiza la vista HTML de gestión de empresas"""
    try:
        return render_template('empresas.html')
    except Exception as e:
        log_security(f"ERROR VISTA EMPRESAS | error={str(e)}")
        return f"Error al cargar vista de empresas: {str(e)}", 500

# =====================================================
# ENDPOINTS PARA FORMAS DE PAGO
# =====================================================
from modules.configuracion.models import FormaPago

@configuracion_bp.route('/formas_pago/listar', methods=['GET'])
def listar_formas_pago():
    """Lista todas las formas de pago"""
    try:
        formas = FormaPago.query.filter_by(estado='activo').order_by(FormaPago.codigo).all()
        return jsonify({
            'success': True,
            'data': [forma.to_dict() for forma in formas]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# =====================================================
# ENDPOINTS PARA TIPOS DE SERVICIO
# =====================================================
from modules.configuracion.models import TipoServicio

@configuracion_bp.route('/tipos_servicio/listar', methods=['GET'])
def listar_tipos_servicio():
    """Lista todos los tipos de servicio"""
    try:
        tipos = TipoServicio.query.filter_by(estado='activo').order_by(TipoServicio.codigo).all()
        return jsonify({
            'success': True,
            'data': [tipo.to_dict() for tipo in tipos]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# =====================================================
# ENDPOINTS PARA DEPARTAMENTOS
# =====================================================
from modules.configuracion.models import Departamento

@configuracion_bp.route('/departamentos/listar', methods=['GET'])
def listar_departamentos():
    """Lista todos los departamentos"""
    try:
        deptos = Departamento.query.filter_by(estado='activo').order_by(Departamento.codigo).all()
        return jsonify({
            'success': True,
            'data': [depto.to_dict() for depto in deptos]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# =====================================================
# VISTAS HTML (ENDPOINTS PARA RENDERIZAR TEMPLATES)
# =====================================================

@configuracion_bp.route('/formas_pago_view', methods=['GET'])
@requiere_permiso_html('configuracion', 'acceder_modulo')
def formas_pago_view():
    """Renderiza la vista HTML de gestión de formas de pago"""
    try:
        return render_template('formas_pago.html')
    except Exception as e:
        log_security(f"ERROR VISTA FORMAS PAGO | error={str(e)}")
        return f"Error al cargar vista de formas de pago: {str(e)}", 500

@configuracion_bp.route('/tipos_servicio_view', methods=['GET'])
@requiere_permiso_html('configuracion', 'acceder_modulo')
def tipos_servicio_view():
    """Renderiza la vista HTML de gestión de tipos de servicio"""
    try:
        return render_template('tipos_servicio.html')
    except Exception as e:
        log_security(f"ERROR VISTA TIPOS SERVICIO | error={str(e)}")
        return f"Error al cargar vista de tipos de servicio: {str(e)}", 500

@configuracion_bp.route('/departamentos_view', methods=['GET'])
@requiere_permiso_html('configuracion', 'acceder_modulo')
def departamentos_view():
    """Renderiza la vista HTML de gestión de departamentos"""
    try:
        return render_template('departamentos.html')
    except Exception as e:
        log_security(f"ERROR VISTA DEPARTAMENTOS | error={str(e)}")
        return f"Error al cargar vista de departamentos: {str(e)}", 500
