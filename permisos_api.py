"""
API de Permisos - Endpoint para consultar permisos del usuario actual
"""
from flask import Blueprint, session, jsonify
from extensions import db

permisos_api_bp = Blueprint('permisos_api', __name__)

@permisos_api_bp.route('/api/mis-permisos', methods=['GET'])
def obtener_mis_permisos():
    """
    Retorna los permisos del usuario autenticado
    
    Returns:
        JSON con lista de permisos del usuario + email
    """
    if 'usuario_id' not in session:
        return jsonify({
            "success": False,
            "error": "No autenticado"
        }), 401
    
    usuario_id = session.get('usuario_id')
    rol = session.get('rol', 'externo')
    
    # Obtener email del usuario desde la sesión o base de datos
    email_usuario = session.get('email', '')
    
    # Si no está en sesión, intentar obtener de BD
    if not email_usuario:
        try:
            # Importar modelo Usuario
            from app import Usuario
            usuario = Usuario.query.get(usuario_id)
            if usuario and usuario.tercero:
                email_usuario = usuario.tercero.correo_electronico or ''
        except Exception as e:
            email_usuario = ''
    
    # TODO: Consultar permisos reales desde la base de datos
    # Por ahora, retornar permisos por defecto basados en el rol
    
    permisos_default = {
        "usuario_id": usuario_id,
        "rol": rol,
        "email": email_usuario,
        "permisos": []
    }
    
    # Permisos básicos para todos los usuarios autenticados
    if rol == 'externo':
        permisos_default["permisos"] = [
            {"modulo": "recibir_facturas", "accion": "acceder_modulo", "permitido": True},
            {"modulo": "recibir_facturas", "accion": "nueva_factura", "permitido": True},
            {"modulo": "relaciones", "accion": "acceder_modulo", "permitido": True},
            {"modulo": "relaciones", "accion": "generar_relacion", "permitido": True}
        ]
    elif rol == 'interno':
        permisos_default["permisos"] = [
            {"modulo": "recibir_facturas", "accion": "acceder_modulo", "permitido": True},
            {"modulo": "recibir_facturas", "accion": "nueva_factura", "permitido": True},
            {"modulo": "relaciones", "accion": "acceder_modulo", "permitido": True},
            {"modulo": "relaciones", "accion": "generar_relacion", "permitido": True},
            {"modulo": "notas_contables", "accion": "acceder_modulo", "permitido": True},
            {"modulo": "causaciones", "accion": "acceder_modulo", "permitido": True},
            {"modulo": "configuracion", "accion": "tipos_documento", "permitido": True}
        ]
    elif rol == 'admin':
        # Administradores tienen todos los permisos
        permisos_default["permisos"] = [
            {"modulo": "*", "accion": "*", "permitido": True}
        ]
    
    return jsonify({
        "success": True,
        "data": permisos_default
    }), 200
