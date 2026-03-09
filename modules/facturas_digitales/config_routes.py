"""
Blueprint de Configuración de Facturas Digitales
Gestiona los catálogos: Tipo Documento, Forma Pago, Tipo Servicio, Departamentos
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from extensions import db
from sqlalchemy import text
from decoradores_permisos import requiere_permiso

# Crear blueprint
config_facturas_bp = Blueprint('config_facturas', __name__, url_prefix='/facturas-digitales/configuracion')

# ============================================================================
# VISTA PRINCIPAL
# ============================================================================
@config_facturas_bp.route('/')
def index():
    """Página principal de configuración"""
    if 'usuario' not in session:
        return redirect(url_for('index'))
    
    return render_template('facturas_digitales/configuracion_catalogos.html', usuario=session.get('usuario'))

# ============================================================================
# API: TIPO DOCUMENTO
# ============================================================================
@config_facturas_bp.route('/api/tipo-documento', methods=['GET'])
@requiere_permiso('facturas_digitales', 'configuracion')
def listar_tipo_documento():
    """Listar todos los tipos de documento"""
    try:
        resultado = db.session.execute(
            text("SELECT id, sigla, descripcion, activo FROM tipo_doc_facturacion ORDER BY sigla")
        ).fetchall()
        
        registros = []
        for row in resultado:
            registros.append({
                'id': row[0],
                'sigla': row[1],
                'descripcion': row[2],
                'activo': row[3]
            })
        
        return jsonify({'success': True, 'data': registros})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/tipo-documento', methods=['POST'])
@requiere_permiso('facturas_digitales', 'configuracion')
def crear_tipo_documento():
    """Crear un nuevo tipo de documento"""
    try:
        data = request.get_json()
        sigla = data.get('sigla', '').strip().upper()
        descripcion = data.get('descripcion', '').strip().upper()
        usuario = session.get('usuario', 'admin')
        
        if not sigla or not descripcion:
            return jsonify({'success': False, 'message': 'Sigla y descripción son obligatorios'}), 400
        
        db.session.execute(
            text("""
                INSERT INTO tipo_doc_facturacion (sigla, descripcion, usuario_creacion)
                VALUES (:sigla, :descripcion, :usuario)
            """),
            {'sigla': sigla, 'descripcion': descripcion, 'usuario': usuario}
        )
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Tipo de documento creado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/tipo-documento/<int:id>', methods=['PUT'])
@requiere_permiso('facturas_digitales', 'configuracion')
def actualizar_tipo_documento(id):
    """Actualizar un tipo de documento"""
    try:
        data = request.get_json()
        sigla = data.get('sigla', '').strip().upper()
        descripcion = data.get('descripcion', '').strip().upper()
        activo = data.get('activo', True)
        
        if not sigla or not descripcion:
            return jsonify({'success': False, 'message': 'Sigla y descripción son obligatorios'}), 400
        
        db.session.execute(
            text("""
                UPDATE tipo_doc_facturacion 
                SET sigla = :sigla, descripcion = :descripcion, activo = :activo
                WHERE id = :id
            """),
            {'id': id, 'sigla': sigla, 'descripcion': descripcion, 'activo': activo}
        )
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Tipo de documento actualizado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/tipo-documento/<int:id>', methods=['DELETE'])
@requiere_permiso('facturas_digitales', 'configuracion')
def eliminar_tipo_documento(id):
    """Eliminar (desactivar) un tipo de documento"""
    try:
        db.session.execute(
            text("UPDATE tipo_doc_facturacion SET activo = false WHERE id = :id"),
            {'id': id}
        )
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Tipo de documento desactivado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# API: FORMA DE PAGO
# ============================================================================
@config_facturas_bp.route('/api/forma-pago', methods=['GET'])
@requiere_permiso('facturas_digitales', 'configuracion')
def listar_forma_pago():
    """Listar todas las formas de pago"""
    try:
        resultado = db.session.execute(
            text("SELECT id, sigla, descripcion, activo FROM forma_pago_facturacion ORDER BY sigla")
        ).fetchall()
        
        registros = []
        for row in resultado:
            registros.append({
                'id': row[0],
                'sigla': row[1],
                'descripcion': row[2],
                'activo': row[3]
            })
        
        return jsonify({'success': True, 'data': registros})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/forma-pago', methods=['POST'])
@requiere_permiso('facturas_digitales', 'configuracion')
def crear_forma_pago():
    """Crear una nueva forma de pago"""
    try:
        data = request.get_json()
        sigla = data.get('sigla', '').strip().upper()
        descripcion = data.get('descripcion', '').strip().upper()
        usuario = session.get('usuario', 'admin')
        
        if not sigla or not descripcion:
            return jsonify({'success': False, 'message': 'Sigla y descripción son obligatorios'}), 400
        
        db.session.execute(
            text("""
                INSERT INTO forma_pago_facturacion (sigla, descripcion, usuario_creacion)
                VALUES (:sigla, :descripcion, :usuario)
            """),
            {'sigla': sigla, 'descripcion': descripcion, 'usuario': usuario}
        )
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Forma de pago creada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/forma-pago/<int:id>', methods=['PUT'])
@requiere_permiso('facturas_digitales', 'configuracion')
def actualizar_forma_pago(id):
    """Actualizar una forma de pago"""
    try:
        data = request.get_json()
        sigla = data.get('sigla', '').strip().upper()
        descripcion = data.get('descripcion', '').strip().upper()
        activo = data.get('activo', True)
        
        if not sigla or not descripcion:
            return jsonify({'success': False, 'message': 'Sigla y descripción son obligatorios'}), 400
        
        db.session.execute(
            text("""
                UPDATE forma_pago_facturacion 
                SET sigla = :sigla, descripcion = :descripcion, activo = :activo
                WHERE id = :id
            """),
            {'id': id, 'sigla': sigla, 'descripcion': descripcion, 'activo': activo}
        )
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Forma de pago actualizada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/forma-pago/<int:id>', methods=['DELETE'])
@requiere_permiso('facturas_digitales', 'configuracion')
def eliminar_forma_pago(id):
    """Eliminar (desactivar) una forma de pago"""
    try:
        db.session.execute(
            text("UPDATE forma_pago_facturacion SET activo = false WHERE id = :id"),
            {'id': id}
        )
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Forma de pago desactivada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# API: TIPO DE SERVICIO
# ============================================================================
@config_facturas_bp.route('/api/tipo-servicio', methods=['GET'])
@requiere_permiso('facturas_digitales', 'configuracion')
def listar_tipo_servicio():
    """Listar todos los tipos de servicio"""
    try:
        resultado = db.session.execute(
            text("SELECT id, sigla, descripcion, activo FROM tipo_servicio_facturacion ORDER BY sigla")
        ).fetchall()
        
        registros = []
        for row in resultado:
            registros.append({
                'id': row[0],
                'sigla': row[1],
                'descripcion': row[2],
                'activo': row[3]
            })
        
        return jsonify({'success': True, 'data': registros})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/tipo-servicio', methods=['POST'])
@requiere_permiso('facturas_digitales', 'configuracion')
def crear_tipo_servicio():
    """Crear un nuevo tipo de servicio"""
    try:
        data = request.get_json()
        sigla = data.get('sigla', '').strip().upper()
        descripcion = data.get('descripcion', '').strip().upper()
        usuario = session.get('usuario', 'admin')
        
        if not sigla or not descripcion:
            return jsonify({'success': False, 'message': 'Sigla y descripción son obligatorios'}), 400
        
        db.session.execute(
            text("""
                INSERT INTO tipo_servicio_facturacion (sigla, descripcion, usuario_creacion)
                VALUES (:sigla, :descripcion, :usuario)
            """),
            {'sigla': sigla, 'descripcion': descripcion, 'usuario': usuario}
        )
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Tipo de servicio creado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/tipo-servicio/<int:id>', methods=['PUT'])
@requiere_permiso('facturas_digitales', 'configuracion')
def actualizar_tipo_servicio(id):
    """Actualizar un tipo de servicio"""
    try:
        data = request.get_json()
        sigla = data.get('sigla', '').strip().upper()
        descripcion = data.get('descripcion', '').strip().upper()
        activo = data.get('activo', True)
        
        if not sigla or not descripcion:
            return jsonify({'success': False, 'message': 'Sigla y descripción son obligatorios'}), 400
        
        db.session.execute(
            text("""
                UPDATE tipo_servicio_facturacion 
                SET sigla = :sigla, descripcion = :descripcion, activo = :activo
                WHERE id = :id
            """),
            {'id': id, 'sigla': sigla, 'descripcion': descripcion, 'activo': activo}
        )
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Tipo de servicio actualizado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/tipo-servicio/<int:id>', methods=['DELETE'])
@requiere_permiso('facturas_digitales', 'configuracion')
def eliminar_tipo_servicio(id):
    """Eliminar (desactivar) un tipo de servicio"""
    try:
        db.session.execute(
            text("UPDATE tipo_servicio_facturacion SET activo = false WHERE id = :id"),
            {'id': id}
        )
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Tipo de servicio desactivado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# API: DEPARTAMENTOS
# ============================================================================
@config_facturas_bp.route('/api/departamento', methods=['GET'])
@requiere_permiso('facturas_digitales', 'configuracion')
def listar_departamento():
    """Listar todos los departamentos"""
    try:
        resultado = db.session.execute(
            text("SELECT id, sigla, nombre, activo FROM departamentos_facturacion ORDER BY sigla")
        ).fetchall()
        
        registros = []
        for row in resultado:
            registros.append({
                'id': row[0],
                'sigla': row[1],
                'nombre': row[2],
                'activo': row[3]
            })
        
        return jsonify({'success': True, 'data': registros})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/departamento', methods=['POST'])
@requiere_permiso('facturas_digitales', 'configuracion')
def crear_departamento():
    """Crear un nuevo departamento"""
    try:
        data = request.get_json()
        sigla = data.get('sigla', '').strip().upper()
        nombre = data.get('nombre', '').strip().upper()
        usuario = session.get('usuario', 'admin')
        
        if not sigla or not nombre:
            return jsonify({'success': False, 'message': 'Sigla y nombre son obligatorios'}), 400
        
        db.session.execute(
            text("""
                INSERT INTO departamentos_facturacion (sigla, nombre, usuario_creacion)
                VALUES (:sigla, :nombre, :usuario)
            """),
            {'sigla': sigla, 'nombre': nombre, 'usuario': usuario}
        )
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Departamento creado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/departamento/<int:id>', methods=['PUT'])
@requiere_permiso('facturas_digitales', 'configuracion')
def actualizar_departamento(id):
    """Actualizar un departamento"""
    try:
        data = request.get_json()
        sigla = data.get('sigla', '').strip().upper()
        nombre = data.get('nombre', '').strip().upper()
        activo = data.get('activo', True)
        
        if not sigla or not nombre:
            return jsonify({'success': False, 'message': 'Sigla y nombre son obligatorios'}), 400
        
        db.session.execute(
            text("""
                UPDATE departamentos_facturacion 
                SET sigla = :sigla, nombre = :nombre, activo = :activo
                WHERE id = :id
            """),
            {'id': id, 'sigla': sigla, 'nombre': nombre, 'activo': activo}
        )
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Departamento actualizado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/departamento/<int:id>', methods=['DELETE'])
@requiere_permiso('facturas_digitales', 'configuracion')
def eliminar_departamento(id):
    """Eliminar (desactivar) un departamento"""
    try:
        db.session.execute(
            text("UPDATE departamentos_facturacion SET activo = false WHERE id = :id"),
            {'id': id}
        )
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Departamento desactivado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# API: ENDPOINTS PARA FORMULARIO DE CARGA (Solo registros activos)
# ============================================================================
@config_facturas_bp.route('/api/activos/tipo-documento', methods=['GET'])
def listar_tipo_documento_activos():
    """Listar solo tipos de documento activos (para dropdowns)"""
    try:
        resultado = db.session.execute(
            text("SELECT sigla, descripcion FROM tipo_doc_facturacion WHERE activo = true ORDER BY sigla")
        ).fetchall()
        
        registros = [{'sigla': row[0], 'descripcion': row[1]} for row in resultado]
        return jsonify({'success': True, 'data': registros})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/activos/forma-pago', methods=['GET'])
def listar_forma_pago_activos():
    """Listar solo formas de pago activas (para dropdowns)"""
    try:
        resultado = db.session.execute(
            text("SELECT sigla, descripcion FROM forma_pago_facturacion WHERE activo = true ORDER BY sigla")
        ).fetchall()
        
        registros = [{'sigla': row[0], 'descripcion': row[1]} for row in resultado]
        return jsonify({'success': True, 'data': registros})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/activos/tipo-servicio', methods=['GET'])
def listar_tipo_servicio_activos():
    """Listar solo tipos de servicio activos (para dropdowns)"""
    try:
        resultado = db.session.execute(
            text("SELECT sigla, descripcion FROM tipo_servicio_facturacion WHERE activo = true ORDER BY sigla")
        ).fetchall()
        
        registros = [{'sigla': row[0], 'descripcion': row[1]} for row in resultado]
        return jsonify({'success': True, 'data': registros})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/activos/departamento', methods=['GET'])
def listar_departamento_activos():
    """Listar solo departamentos activos (para dropdowns)"""
    try:
        resultado = db.session.execute(
            text("SELECT sigla, nombre FROM departamentos_facturacion WHERE activo = true ORDER BY sigla")
        ).fetchall()
        
        registros = [{'sigla': row[0], 'nombre': row[1]} for row in resultado]
        return jsonify({'success': True, 'data': registros})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# API: GESTIÓN DE USUARIOS Y PERMISOS
# ============================================================================
@config_facturas_bp.route('/api/usuarios', methods=['GET'])
@requiere_permiso('facturas_digitales', 'configuracion')
def listar_usuarios():
    """
    Listar todos los usuarios con sus departamentos y permisos configurados
    NUEVO: Soporta múltiples departamentos por usuario
    """
    try:
        # Consulta con JOIN a usuario_departamento (muchos a muchos)
        query = text("""
            SELECT 
                u.id,
                u.usuario,
                COALESCE(u.correo, u.email_notificaciones, 'Sin correo') as email,
                COALESCE(
                    STRING_AGG(DISTINCT ud.departamento, ', ' ORDER BY ud.departamento),
                    'Sin asignar'
                ) as departamentos
            FROM usuarios u
            LEFT JOIN usuario_departamento ud ON u.id = ud.usuario_id AND ud.activo = true
            WHERE u.activo = true
            GROUP BY u.id, u.usuario, u.correo, u.email_notificaciones
            ORDER BY u.usuario
        """)
        
        resultado = db.session.execute(query).fetchall()
        
        usuarios = []
        for row in resultado:
            usuarios.append({
                'id': row[0],
                'usuario': row[1],
                'email': row[2],
                'departamentos': row[3]  # String separado por comas: "TIC, FIN, MER"
            })
        
        return jsonify({'success': True, 'data': usuarios})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/usuarios/<int:usuario_id>', methods=['GET'])
@requiere_permiso('facturas_digitales', 'configuracion')
def obtener_usuario(usuario_id):
    """
    Obtener información detallada de un usuario específico
    NUEVO: Retorna array de departamentos con permisos individuales
    """
    try:
        # 1. Obtener datos básicos del usuario
        query_usuario = text("""
            SELECT id, usuario, COALESCE(correo, email_notificaciones, 'Sin correo') as email
            FROM usuarios
            WHERE id = :usuario_id AND activo = true
        """)
        usuario_row = db.session.execute(query_usuario, {'usuario_id': usuario_id}).fetchone()
        
        if not usuario_row:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404
        
        # 2. Obtener departamentos asignados con permisos
        query_deptos = text("""
            SELECT 
                departamento,
                puede_recibir,
                puede_aprobar,
                puede_rechazar,
                puede_firmar,
                fecha_asignacion
            FROM usuario_departamento
            WHERE usuario_id = :usuario_id AND activo = true
            ORDER BY departamento
        """)
        deptos_rows = db.session.execute(query_deptos, {'usuario_id': usuario_id}).fetchall()
        
        # 3. Construir respuesta
        departamentos = []
        for row in deptos_rows:
            departamentos.append({
                'departamento': row[0],
                'puede_recibir': row[1],
                'puede_aprobar': row[2],
                'puede_rechazar': row[3],
                'puede_firmar': row[4],
                'fecha_asignacion': row[5].isoformat() if row[5] else None
            })
        
        usuario = {
            'id': usuario_row[0],
            'usuario': usuario_row[1],
            'email': usuario_row[2],
            'departamentos': departamentos  # Array de objetos
        }
        
        return jsonify({'success': True, 'data': usuario})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/usuarios/<int:usuario_id>/departamento', methods=['POST'])
@requiere_permiso('facturas_digitales', 'configuracion')
def agregar_departamento_usuario(usuario_id):
    """
    Agregar o actualizar un departamento para un usuario
    NUEVO: Soporta múltiples departamentos
    """
    try:
        data = request.get_json()
        departamento = data.get('departamento', '').strip().upper()
        puede_recibir = data.get('puede_recibir', False)
        puede_aprobar = data.get('puede_aprobar', False)
        puede_rechazar = data.get('puede_rechazar', False)
        puede_firmar = data.get('puede_firmar', False)
        
        # Validaciones
        if not departamento:
            return jsonify({'success': False, 'error': 'Departamento es obligatorio'}), 400
        
        # Lista completa de departamentos según departamentos_facturacion
        if departamento not in ['CYS', 'DOM', 'FIN', 'MER', 'MYP', 'TIC']:
            return jsonify({'success': False, 'error': 'Departamento inválido. Valores permitidos: CYS, DOM, FIN, MER, MYP, TIC'}), 400
        
        # Verificar que el usuario existe
        usuario = db.session.execute(
            text("SELECT id FROM usuarios WHERE id = :id AND activo = true"),
            {'id': usuario_id}
        ).fetchone()
        
        if not usuario:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404
        
        # INSERT or UPDATE en usuario_departamento
        db.session.execute(
            text("""
                INSERT INTO usuario_departamento 
                    (usuario_id, departamento, puede_recibir, puede_aprobar, puede_rechazar, puede_firmar, activo)
                VALUES 
                    (:usuario_id, :departamento, :puede_recibir, :puede_aprobar, :puede_rechazar, :puede_firmar, true)
                ON CONFLICT (usuario_id, departamento) 
                DO UPDATE SET
                    puede_recibir = EXCLUDED.puede_recibir,
                    puede_aprobar = EXCLUDED.puede_aprobar,
                    puede_rechazar = EXCLUDED.puede_rechazar,
                    puede_firmar = EXCLUDED.puede_firmar,
                    fecha_asignacion = CURRENT_TIMESTAMP,
                    activo = true
            """),
            {
                'usuario_id': usuario_id,
                'departamento': departamento,
                'puede_recibir': puede_recibir,
                'puede_aprobar': puede_aprobar,
                'puede_rechazar': puede_rechazar,
                'puede_firmar': puede_firmar
            }
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Departamento {departamento} asignado/actualizado exitosamente'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@config_facturas_bp.route('/api/usuarios/<int:usuario_id>/departamento/<string:departamento>', methods=['DELETE'])
@requiere_permiso('facturas_digitales', 'configuracion')
def eliminar_departamento_usuario(usuario_id, departamento):
    """
    Eliminar un departamento asignado a un usuario
    NUEVO: Permite quitar departamentos específicos
    """
    try:
        departamento = departamento.strip().upper()
        
        # Verificar que el usuario existe
        usuario = db.session.execute(
            text("SELECT id FROM usuarios WHERE id = :id AND activo = true"),
            {'id': usuario_id}
        ).fetchone()
        
        if not usuario:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404
        
        # Marcar como inactivo (soft delete) o eliminar físicamente
        db.session.execute(
            text("""
                DELETE FROM usuario_departamento
                WHERE usuario_id = :usuario_id AND departamento = :departamento
            """),
            {'usuario_id': usuario_id, 'departamento': departamento}
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Departamento {departamento} eliminado exitosamente'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
