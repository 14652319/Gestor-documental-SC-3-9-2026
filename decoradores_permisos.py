"""
Decoradores de permisos para el Gestor Documental
Controla el acceso a endpoints y páginas basado en permisos de usuario
"""
from functools import wraps
from flask import session, jsonify, redirect, url_for, flash
from extensions import db
from sqlalchemy import text

def requiere_permiso(modulo, accion):
    """
    Decorador para endpoints API que requieren permisos específicos
    Retorna JSON con error 403 si no tiene permiso
    
    Args:
        modulo (str): Nombre del módulo (ej: 'recibir_facturas', 'relaciones')
        accion (str): Nombre de la acción (ej: 'nueva_factura', 'generar_relacion')
    
    Returns:
        function: Función decorada con validación de permisos
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar si el usuario tiene sesión activa
            if 'usuario_id' not in session:
                return jsonify({
                    "success": False,
                    "error": "No autenticado",
                    "message": "Debe iniciar sesión para acceder a este recurso"
                }), 401
            
            usuario_id = session.get('usuario_id')
            usuario = session.get('usuario', 'desconocido')
            
            # ✅ VALIDACIÓN REAL DE PERMISOS CONTRA BASE DE DATOS
            try:
                result = db.session.execute(text("""
                    SELECT permitido 
                    FROM permisos_usuarios 
                    WHERE usuario_id = :usuario_id 
                      AND modulo = :modulo 
                      AND accion = :accion
                """), {
                    'usuario_id': usuario_id,
                    'modulo': modulo,
                    'accion': accion
                })
                
                permiso = result.fetchone()
                
                # Si no existe el registro o no tiene permiso
                if not permiso or not permiso[0]:
                    return jsonify({
                        "success": False,
                        "error": "Permisos insuficientes",
                        "message": f"No tiene permisos para ejecutar la acción '{accion}' en el módulo '{modulo}'"
                    }), 403
                
                # ✅ Permiso concedido, ejecutar función
                return f(*args, **kwargs)
                
            except Exception as e:
                # En caso de error en la consulta, denegar acceso por seguridad
                return jsonify({
                    "success": False,
                    "error": "Error al verificar permisos",
                    "message": str(e)
                }), 500
                
        return decorated_function
    return decorator


def requiere_permiso_html(modulo, accion):
    """
    Decorador para páginas HTML que requieren permisos específicos
    Redirige a página de error si no tiene permiso
    
    Args:
        modulo (str): Nombre del módulo (ej: 'recibir_facturas', 'relaciones')
        accion (str): Nombre de la acción (ej: 'acceder_modulo', 'nueva_factura')
    
    Returns:
        function: Función decorada con validación de permisos
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar si el usuario tiene sesión activa
            if 'usuario_id' not in session:
                flash('Debe iniciar sesión para acceder a esta página', 'warning')
                return redirect('/')
            
            usuario_id = session.get('usuario_id')
            usuario = session.get('usuario', 'desconocido')
            
            # ✅ VALIDACIÓN REAL DE PERMISOS CONTRA BASE DE DATOS
            try:
                result = db.session.execute(text("""
                    SELECT permitido 
                    FROM permisos_usuarios 
                    WHERE usuario_id = :usuario_id 
                      AND modulo = :modulo 
                      AND accion = :accion
                """), {
                    'usuario_id': usuario_id,
                    'modulo': modulo,
                    'accion': accion
                })
                
                permiso = result.fetchone()
                
                # Si no existe el registro o no tiene permiso
                if not permiso or not permiso[0]:
                    flash(f'No tiene permisos para acceder a "{accion}" en el módulo "{modulo}"', 'error')
                    return redirect('/dashboard')
                
                # ✅ Permiso concedido, ejecutar función
                return f(*args, **kwargs)
                
            except Exception as e:
                # En caso de error en la consulta, denegar acceso por seguridad
                flash(f'Error al verificar permisos: {str(e)}', 'error')
                return redirect('/dashboard')
                
        return decorated_function
    return decorator


def requiere_rol(*roles_permitidos):
    """
    Decorador que verifica si el usuario tiene alguno de los roles permitidos
    
    Args:
        *roles_permitidos: Lista de roles que pueden acceder (ej: 'admin', 'interno', 'externo')
    
    Returns:
        function: Función decorada con validación de rol
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'usuario_id' not in session:
                return jsonify({
                    "success": False,
                    "error": "No autenticado"
                }), 401
            
            rol_usuario = session.get('rol', 'externo')
            
            if rol_usuario not in roles_permitidos:
                return jsonify({
                    "success": False,
                    "error": "Permisos insuficientes",
                    "message": f"Se requiere uno de estos roles: {', '.join(roles_permitidos)}"
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
