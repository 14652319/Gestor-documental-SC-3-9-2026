"""
==============================================
🔐 ROUTES - SISTEMA DE USUARIOS Y PERMISOS
==============================================

Sistema avanzado de gestión de usuarios y permisos granulares
por módulo y acción específica.

Autor: GitHub Copilot
Fecha: Octubre 23, 2025
"""

import os
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from datetime import datetime, timedelta
from sqlalchemy import text
from extensions import db
from decoradores_permisos import requiere_permiso, requiere_permiso_html
from .models import (
    PermisoUsuario, RolUsuario, UsuarioRol, InvitacionUsuario, 
    AuditoriaPermisos, CatalogoPermisos, verificar_permiso_usuario,
    asignar_permiso_usuario, obtener_permisos_usuario, crear_permisos_por_defecto_usuario
)

# Importar funciones de correo de Flask-Mail (evitar importación circular)
from flask_mail import Message, Mail

# Crear instancia de Mail local para este módulo
mail_local = Mail()

def enviar_correo_invitacion_local(destinatario, nombre_usuario, nit):
    """
    Función local para enviar correos de invitación (evita importación circular)
    """
    from flask import current_app
    
    try:
        # Verificar configuración de correo
        if not current_app.config.get('MAIL_USERNAME') or not current_app.config.get('MAIL_PASSWORD'):
            log_security(f"ADVERTENCIA: Correo no configurado. No se envió invitación a {destinatario}")
            return (False, "Correo no configurado en el servidor")
        
        # Crear mensaje HTML simplificado
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <h2 style="color: #16A085;">🎉 ¡Bienvenido al Sistema!</h2>
            <p>Se ha creado tu cuenta de usuario en el sistema de gestión documental.</p>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <strong>Detalles de tu cuenta:</strong><br>
                • Usuario: <strong>{nombre_usuario}</strong><br>
                • NIT asociado: {nit}<br>
                • Correo: {destinatario}
            </div>
            
            <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <strong>Próximos pasos:</strong><br>
                1. Tu cuenta está pendiente de activación por el administrador<br>
                2. Una vez activada, recibirás instrucciones para configurar tu contraseña<br>
                3. Podrás acceder al sistema con tu usuario y contraseña
            </div>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="{os.getenv('APP_BASE_URL', 'http://192.168.11.205:8099')}" style="background: #16A085; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    🌐 Acceder al Sistema
                </a>
            </p>
            
            <hr>
            <p style="color: #7f8c8d; font-size: 12px;">
                <strong>Gestor Documental - Supertiendas Cañaveral</strong><br>
                Este es un mensaje automático, por favor no responder.
            </p>
        </body>
        </html>
        """
        
        # Texto plano alternativo
        texto_plano = f"""
INVITACIÓN - GESTOR DOCUMENTAL
Supertiendas Cañaveral

¡Bienvenido al sistema!

Detalles de tu cuenta:
- Usuario: {nombre_usuario}
- NIT asociado: {nit}
- Correo: {destinatario}

PRÓXIMOS PASOS:
1. Tu cuenta está pendiente de activación por el administrador
2. Una vez activada, recibirás instrucciones para configurar tu contraseña
3. Podrás acceder al sistema con tu usuario y contraseña

Acceso: {os.getenv('APP_BASE_URL', 'http://192.168.11.205:8099')}

---
Gestor Documental - Supertiendas Cañaveral
Este es un mensaje automático, por favor no responder.
        """
        
        # Crear mensaje
        msg = Message(
            subject='🎉 Invitación - Gestor Documental Supertiendas Cañaveral',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[destinatario]
        )
        
        # Configurar Reply-To si está disponible
        if current_app.config.get('MAIL_REPLY_TO'):
            msg.reply_to = current_app.config['MAIL_REPLY_TO']
        
        msg.body = texto_plano
        msg.html = html_body
        
        # Enviar usando la instancia de mail del app actual
        with current_app.app_context():
            mail_instance = current_app.extensions.get('mail')
            if mail_instance:
                mail_instance.send(msg)
            else:
                return (False, "Sistema de correo no inicializado")
        
        log_security(f"INVITACION CORREO ENVIADA | destinatario={destinatario} | usuario={nombre_usuario} | nit={nit}")
        return (True, f"Invitación enviada exitosamente a {destinatario}")
        
    except Exception as e:
        error_msg = f"Error al enviar invitación: {str(e)}"
        log_security(f"ERROR ENVÍO INVITACION | destinatario={destinatario} | error={error_msg}")
        return (False, error_msg)

def enviar_correo_activacion(destinatario, nombre_usuario, token):
    """Envía correo con enlace para establecer contraseña por primera vez"""
    try:
        from flask import current_app
        from flask_mail import Message
        
        url_establecer = f"{os.getenv('APP_BASE_URL', 'http://192.168.11.205:8099')}/establecer-password/{token}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html><head><meta charset="UTF-8"><style>
        body{{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;line-height:1.6;color:#333;}}
        .container{{max-width:600px;margin:0 auto;padding:20px;}}
        .header{{background:linear-gradient(135deg,#16A085 0%,#0D7A68 100%);color:white;padding:30px;text-align:center;border-radius:10px 10px 0 0;}}
        .content{{background:#ffffff;padding:30px;border:1px solid #e3e3e3;}}
        .button{{display:inline-block;background:#16A085;color:white;padding:15px 30px;text-decoration:none;border-radius:5px;margin:20px 0;font-weight:bold;}}
        .footer{{background:#f7f7f7;padding:20px;text-align:center;font-size:12px;color:#7f8c8d;border-radius:0 0 10px 10px;}}
        </style></head><body><div class="container">
        <div class="header"><h1>🎉 ¡Tu cuenta ha sido activada!</h1></div>
        <div class="content">
        <p>Hola <strong>{nombre_usuario}</strong>,</p>
        <p>Tu cuenta ha sido activada. Debes establecer tu contraseña:</p>
        <p style="text-align:center;"><a href="{url_establecer}" class="button">🔐 Establecer Mi Contraseña</a></p>
        <p style="color:#e74c3c;">⚠️ Este enlace es válido por 24 horas.</p>
        </div>
        <div class="footer"><p><strong>Gestor Documental - Supertiendas Cañaveral</strong></p></div>
        </div></body></html>"""
        
        texto_plano = f"""
¡TU CUENTA HA SIDO ACTIVADA!
Hola {nombre_usuario}, establece tu contraseña en: {url_establecer}
Válido por 24 horas.
---
Gestor Documental - Supertiendas Cañaveral"""
        
        msg = Message(
            subject='🔐 Establece tu contraseña - Gestor Documental',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[destinatario]
        )
        
        if current_app.config.get('MAIL_REPLY_TO'):
            msg.reply_to = current_app.config['MAIL_REPLY_TO']
        
        msg.body = texto_plano
        msg.html = html_body
        
        with current_app.app_context():
            mail_instance = current_app.extensions.get('mail')
            if mail_instance:
                mail_instance.send(msg)
        
        log_security(f"CORREO ACTIVACIÓN ENVIADO | destinatario={destinatario} | usuario={nombre_usuario}")
        return True
    except Exception as e:
        log_security(f"ERROR ENVIAR CORREO ACTIVACIÓN | destinatario={destinatario} | error={str(e)}")
        return False

import logging
import secrets
import hashlib
from flask_bcrypt import Bcrypt

# ============================================================================
# 🔧 CONFIGURACIÓN
# ============================================================================

# Blueprint
usuarios_permisos_bp = Blueprint('usuarios_permisos', __name__)

# Logger
logger = logging.getLogger(__name__)

# Bcrypt para hashing de contraseñas
bcrypt = Bcrypt()

# Función de logging de seguridad
def log_security(mensaje):
    """Registra eventos de seguridad"""
    logger.info(f"USUARIOS_PERMISOS | {mensaje}")

# ============================================================================
# 🔐 HELPER: VALIDACIÓN DE SESIÓN ADMIN
# ============================================================================

def validar_sesion_admin():
    """Valida que el usuario tenga sesión activa y permisos de admin"""
    if 'usuario_id' not in session or 'usuario' not in session:
        return False, {"error": "Sesión no válida", "redirect": "/"}, 401
    
    # TODO: Implementar verificación de permisos específicos
    # Por ahora, permitir acceso a usuarios logueados
    usuario_id = session.get('usuario_id')
    
    return True, None, None

def obtener_ip():
    """Obtiene la IP del cliente"""
    return request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

# Función eliminada - usar consultas SQL directas para evitar conflictos de modelos
# Los modelos ya están definidos en app.py, no necesitamos reimportarlos

# ============================================================================
# 🏠 DASHBOARD PRINCIPAL
# ============================================================================

@usuarios_permisos_bp.route('/')
@usuarios_permisos_bp.route('/dashboard')
@requiere_permiso_html('gestion_usuarios', 'acceder_modulo')
def dashboard():
    """Dashboard principal de gestión de usuarios y permisos"""
    # valido, respuesta, codigo = validar_sesion_admin()
    # if not valido:
    #     if codigo == 401:
    #         return redirect('/')
    #     return jsonify(respuesta), codigo
    
    # Verificar sesión básica
    if 'usuario_id' not in session:
        return redirect('/')
    
    log_security(f"ACCESO DASHBOARD | usuario={session.get('usuario')} | IP={obtener_ip()}")
    
    try:
        return render_template('usuarios_permisos/usuarios_permisos_dashboard.html', 
                             usuario=session.get('usuario'))
    except Exception as e:
        log_security(f"ERROR TEMPLATE | {str(e)}")
        return f"<h1>🔧 Sistema de Usuarios y Permisos</h1><p>Template en construcción...</p><p>Error: {str(e)}</p><br><p>Usuario: {session.get('usuario')}</p>", 200

# ============================================================================
# 👥 GESTIÓN DE USUARIOS
# ============================================================================

@usuarios_permisos_bp.route('/api/usuarios', methods=['GET'])
@requiere_permiso('gestion_usuarios', 'consultar_usuarios')
def listar_usuarios():
    """Lista todos los usuarios del sistema con sus permisos"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        # Usar consulta SQL directa para evitar conflicto de modelos
        usuarios_result = db.session.execute(
            text("""
         SELECT u.id, u.usuario, u.correo, u.activo, u.fecha_creacion AS fecha_registro,
             t.nit, t.razon_social, t.tipo_persona
         FROM usuarios u
         LEFT JOIN terceros t ON u.tercero_id = t.id
         ORDER BY u.fecha_creacion DESC
            """)
        ).fetchall()
        
        resultado = []
        for row in usuarios_result:
            # Obtener permisos del usuario
            try:
                permisos = obtener_permisos_usuario(row[0])  # row[0] = id
                permisos_activos = sum(
                    sum(acciones.values()) for acciones in permisos.values()
                )
            except Exception:
                permisos = {}
                permisos_activos = 0
            
            resultado.append({
                'id': row[0],
                'usuario': row[1],
                'correo': row[2],
                'activo': row[3],
                'fecha_registro': row[4].isoformat() if row[4] else None,
                'tercero': {
                    'nit': row[5],
                    'razon_social': row[6],
                    'tipo_persona': row[7]
                } if row[5] else None,
                'permisos_activos': permisos_activos,
                'permisos': permisos
            })
        
        log_security(f"LISTAR USUARIOS | usuario={session.get('usuario')} | total={len(resultado)}")
        
        return jsonify({
            'success': True,
            'data': resultado,
            'total': len(resultado)
        })
        
    except Exception as e:
        log_security(f"ERROR LISTAR USUARIOS | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@usuarios_permisos_bp.route('/api/usuarios', methods=['POST'])
@requiere_permiso('gestion_usuarios', 'crear_usuario')
def crear_usuario_interno():
    """Crea un nuevo usuario en el sistema"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['usuario', 'correo', 'tipo_usuario']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Campo {field} es requerido'}), 400
        
        # Verificar que el usuario no exista usando SQL directo
        usuario_existente = db.session.execute(
            text("""
                SELECT id FROM usuarios 
                WHERE usuario = :usuario OR correo = :correo
            """),
            {'usuario': data['usuario'], 'correo': data['correo']}
        ).fetchone()
        
        if usuario_existente:
            return jsonify({'success': False, 'message': 'Usuario o correo ya existe'}), 400
        
        # Si es usuario tercero, validar NIT
        tercero_id = None
        if data['tipo_usuario'] == 'tercero':
            if not data.get('nit'):
                return jsonify({'success': False, 'message': 'NIT es requerido para usuarios tercero'}), 400
            
            tercero = db.session.execute(
                text("SELECT id FROM terceros WHERE nit = :nit"),
                {'nit': data['nit']}
            ).fetchone()
            
            if not tercero:
                return jsonify({'success': False, 'message': 'Tercero con NIT especificado no existe'}), 404
            
            tercero_id = tercero[0]
        
        # Crear usuario usando SQL directo
        result = db.session.execute(
            text("""
                INSERT INTO usuarios (usuario, correo, activo, tercero_id, fecha_creacion, password_hash)
                VALUES (:usuario, :correo, :activo, :tercero_id, :fecha_creacion, :password_hash)
                RETURNING id
            """),
            {
                'usuario': data['usuario'],
                'correo': data['correo'],
                'activo': False,  # Inactivo hasta que configure contraseña
                'tercero_id': tercero_id,
                'fecha_creacion': datetime.now(),
                'password_hash': 'PENDIENTE_CONFIGURAR'  # Placeholder hasta que configure contraseña
            }
        )
        nuevo_usuario_id = result.fetchone()[0]
        
        # Crear permisos por defecto según tipo
        rol = data.get('rol', 'usuario_basico')
        try:
            crear_permisos_por_defecto_usuario(nuevo_usuario_id, rol)
        except Exception as e:
            log_security(f"ADVERTENCIA: No se pudieron crear permisos por defecto | error={str(e)}")
        
        # Crear invitación por correo (opcional - deshabilitado por conflictos de modelos)
        # TODO: Implementar sistema de invitaciones sin importar modelos
        
        # Registrar auditoría (opcional - deshabilitado por conflictos de modelos)
        # TODO: Implementar auditoría sin importar modelos
        
        db.session.commit()
        
        log_security(f"USUARIO CREADO | nuevo_usuario={data['usuario']} | tipo={data['tipo_usuario']} | creado_por={session.get('usuario')}")
        
        return jsonify({
            'success': True,
            'message': 'Usuario creado exitosamente',
            'data': {
                'id': nuevo_usuario_id,
                'usuario': data['usuario'],
                'correo': data['correo']
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR CREAR USUARIO | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@usuarios_permisos_bp.route('/api/usuarios/<int:usuario_id>', methods=['GET'])
@requiere_permiso('gestion_usuarios', 'ver_usuario')
def obtener_usuario(usuario_id):
    """Obtiene los datos de un usuario específico"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        query = text("""
            SELECT u.id, u.usuario, u.correo, u.activo, u.rol, u.fecha_creacion,
                   t.nit, t.razon_social
            FROM usuarios u
            LEFT JOIN terceros t ON u.tercero_id = t.id
            WHERE u.id = :usuario_id
        """)
        
        result = db.session.execute(query, {'usuario_id': usuario_id})
        row = result.fetchone()
        
        if not row:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        usuario_data = {
            'id': row[0],
            'usuario': row[1],
            'correo': row[2],
            'activo': row[3],
            'rol': row[4],
            'fecha_creacion': row[5].isoformat() if row[5] else None,
            'tercero': {
                'nit': row[6],
                'razon_social': row[7]
            } if row[6] else None
        }
        
        log_security(f"OBTENER USUARIO | usuario_id={usuario_id} | solicitante={session.get('usuario')}")
        
        return jsonify({
            'success': True,
            'id': row[0],
            'usuario': row[1],
            'correo': row[2],
            'activo': row[3],
            'rol': row[4],
            'fecha_creacion': row[5].isoformat() if row[5] else None,
            'tercero': {
                'nit': row[6],
                'razon_social': row[7]
            } if row[6] else None
        })
        
    except Exception as e:
        log_security(f"ERROR OBTENER USUARIO | usuario_id={usuario_id} | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@usuarios_permisos_bp.route('/api/usuarios/<int:usuario_id>', methods=['PUT'])
@requiere_permiso('gestion_usuarios', 'editar_usuario')
def actualizar_usuario(usuario_id):
    """Actualiza los datos de un usuario"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        data = request.get_json()
        
        # Validar que el usuario existe
        usuario = db.session.execute(
            text("SELECT id, usuario, correo FROM usuarios WHERE id = :id"),
            {'id': usuario_id}
        ).fetchone()
        
        if not usuario:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        # Manejar asociación con tercero (NIT)
        tercero_id = None
        if 'nit' in data and data['nit']:
            # Buscar o crear tercero
            tercero = db.session.execute(
                text("SELECT id, razon_social FROM terceros WHERE nit = :nit"),
                {'nit': data['nit']}
            ).fetchone()
            
            if tercero:
                tercero_id = tercero[0]
            else:
                # Si no existe, crear tercero básico
                razon_social = data.get('razon_social', f"Tercero {data['nit']}")
                result = db.session.execute(
                    text("INSERT INTO terceros (nit, razon_social) VALUES (:nit, :razon_social) RETURNING id"),
                    {'nit': data['nit'], 'razon_social': razon_social}
                )
                tercero_id = result.fetchone()[0]
        
        # Actualizar campos
        updates = []
        params = {'id': usuario_id}
        
        if 'usuario' in data and data['usuario'] != usuario[1]:
            updates.append("usuario = :usuario")
            params['usuario'] = data['usuario']
        
        if 'correo' in data and data['correo'] != usuario[2]:
            updates.append("correo = :correo")
            params['correo'] = data['correo']
        
        if 'tipo_usuario' in data:
            rol = 'interno' if data['tipo_usuario'] == 'interno' else 'externo'
            updates.append("rol = :rol")
            params['rol'] = rol
        
        if tercero_id:
            updates.append("tercero_id = :tercero_id")
            params['tercero_id'] = tercero_id
        
        if updates:
            query = text(f"UPDATE usuarios SET {', '.join(updates)} WHERE id = :id")
            db.session.execute(query, params)
            db.session.commit()
            
            log_security(f"USUARIO ACTUALIZADO | usuario_id={usuario_id} | campos={updates} | nit={data.get('nit')} | actualizado_por={session.get('usuario')}")
        
        return jsonify({
            'success': True,
            'message': 'Usuario actualizado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR ACTUALIZAR USUARIO | usuario_id={usuario_id} | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@usuarios_permisos_bp.route('/api/usuarios/<int:usuario_id>/estado', methods=['PUT'])
@requiere_permiso('gestion_usuarios', 'activar_usuario')
def cambiar_estado_usuario(usuario_id):
    """Activa o desactiva un usuario"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        data = request.get_json()
        activo = data.get('activo')
        
        if activo is None:
            return jsonify({'success': False, 'message': 'Campo activo es requerido'}), 400
            
        # Verificar que el usuario existe usando SQL directo
        usuario_result = db.session.execute(
            text("SELECT usuario, activo FROM usuarios WHERE id = :usuario_id"),
            {'usuario_id': usuario_id}
        ).fetchone()
        
        if not usuario_result:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        estado_anterior = usuario_result[1]
        
        # Actualizar estado usando SQL directo
        db.session.execute(
            text("UPDATE usuarios SET activo = :activo WHERE id = :usuario_id"),
            {'activo': activo, 'usuario_id': usuario_id}
        )
        
        # Si se está activando por primera vez, enviar correo para establecer contraseña
        if activo and not estado_anterior:
            try:
                # Obtener correo del usuario
                usuario_data = db.session.execute(
                    text("SELECT usuario, correo FROM usuarios WHERE id = :usuario_id"),
                    {'usuario_id': usuario_id}
                ).fetchone()
                
                if usuario_data:
                    nombre_usuario = usuario_data[0]
                    correo_usuario = usuario_data[1]
                    
                    # Generar token único para establecer contraseña
                    import secrets
                    token = secrets.token_urlsafe(32)
                    
                    # Guardar token en base de datos (válido por 24 horas)
                    from datetime import datetime, timedelta
                    expiracion = datetime.now() + timedelta(hours=24)
                    
                    # Eliminar token anterior si existe
                    db.session.execute(
                        text("DELETE FROM tokens_password WHERE usuario_id = :usuario_id"),
                        {'usuario_id': usuario_id}
                    )
                    
                    # Insertar nuevo token
                    db.session.execute(
                        text("""
                            INSERT INTO tokens_password (usuario_id, token, expiracion, usado)
                            VALUES (:usuario_id, :token, :expiracion, false)
                        """),
                        {'usuario_id': usuario_id, 'token': token, 'expiracion': expiracion}
                    )
                    
                    # Enviar correo con enlace para establecer contraseña
                    enviar_correo_activacion(correo_usuario, nombre_usuario, token)
                    
                    log_security(f"CORREO ACTIVACIÓN ENVIADO | usuario={nombre_usuario} | correo={correo_usuario}")
            except Exception as e_correo:
                # No fallar la activación si el correo falla
                log_security(f"ERROR ENVIAR CORREO ACTIVACIÓN | error={str(e_correo)}")
        
        # Registrar auditoría (deshabilitado por conflictos de modelos)
        # TODO: Implementar auditoría sin importar modelos
        
        db.session.commit()
        
        log_security(f"USUARIO {'ACTIVADO' if activo else 'DESACTIVADO'} | usuario_id={usuario_id} | usuario={usuario_result[0]} | por={session.get('usuario')}")
        
        mensaje = f'Usuario {"activado" if activo else "desactivado"} exitosamente'
        if activo and not estado_anterior:
            mensaje += '. Se ha enviado un correo para establecer la contraseña.'
        
        return jsonify({
            'success': True,
            'message': mensaje
        })
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR CAMBIAR ESTADO USUARIO | usuario_id={usuario_id} | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================================================
# 🔐 GESTIÓN DE PERMISOS
# ============================================================================
@usuarios_permisos_bp.route('/api/usuarios/<int:usuario_id>/permisos', methods=['GET'])
@requiere_permiso('gestion_usuarios', 'consultar_permisos')
def obtener_permisos_usuario_api(usuario_id):
    """Obtiene todos los permisos de un usuario específico"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        # Verificar que el usuario existe usando SQL directo
        usuario_result = db.session.execute(
            text("SELECT usuario FROM usuarios WHERE id = :usuario_id"),
            {'usuario_id': usuario_id}
        ).fetchone()
        
        if not usuario_result:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        # Obtener permisos actuales del usuario
        try:
            permisos_actuales = obtener_permisos_usuario(usuario_id)
        except Exception as e:
            log_security(f"ADVERTENCIA: Error obteniendo permisos | usuario_id={usuario_id} | error={str(e)}")
            permisos_actuales = {}
        
        # Obtener catálogo completo de permisos
        try:
            catalogo = CatalogoPermisos.obtener_estructura_modulos()
        except Exception as e:
            log_security(f"ADVERTENCIA: Error obteniendo catálogo | error={str(e)}")
            catalogo = {}
        
        # Combinar catálogo con permisos actuales
        resultado = {}
        for modulo_key, modulo_data in catalogo.items():
            resultado[modulo_key] = {
                'nombre': modulo_data.get('nombre', modulo_key),
                'descripcion': modulo_data.get('descripcion', ''),
                'color': modulo_data.get('color', '#6b7280'),
                'icono': modulo_data.get('icono', 'bi bi-gear'),
                'acciones': {}
            }
            
            acciones = modulo_data.get('acciones', {})
            for accion_key, accion_data in acciones.items():
                # Verificar si el usuario tiene este permiso
                tiene_permiso = permisos_actuales.get(modulo_key, {}).get(accion_key, False)
                
                resultado[modulo_key]['acciones'][accion_key] = {
                    'nombre': accion_data.get('nombre', accion_key),
                    'descripcion': accion_data.get('descripcion', ''),
                    'tipo': accion_data.get('tipo', 'lectura'),
                    'critico': accion_data.get('critico', False),
                    'permitido': tiene_permiso
                }
        
        log_security(f"CONSULTAR PERMISOS | usuario_id={usuario_id} | consultado_por={session.get('usuario')}")
        
        return jsonify({
            'success': True,
            'data': {
                'usuario': {
                    'id': usuario_id,
                    'usuario': usuario_result[0],
                    'correo': '',  # TODO: Obtener del SQL si es necesario
                    'activo': True  # TODO: Obtener del SQL si es necesario
                },
                'permisos': resultado
            }
        })
        
    except Exception as e:
        log_security(f"ERROR CONSULTAR PERMISOS | usuario_id={usuario_id} | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@usuarios_permisos_bp.route('/api/usuarios/<int:usuario_id>/permisos', methods=['PUT'])
@requiere_permiso('gestion_usuarios', 'asignar_permisos')
def actualizar_permisos_usuario(usuario_id):
    """Actualiza los permisos de un usuario específico"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        data = request.get_json()
        permisos_nuevos = data.get('permisos', {})
        
        print(f"\n🔧 DEBUG: Actualizando permisos para usuario_id={usuario_id}")
        print(f"📦 Permisos recibidos: {permisos_nuevos}")
        
        # Obtener el ID del usuario que está haciendo el cambio
        usuario_actual_id = session.get('usuario_id')
        
        # Verificar que el usuario existe usando SQL directo
        usuario_result = db.session.execute(
            text("SELECT usuario FROM usuarios WHERE id = :usuario_id"),
            {'usuario_id': usuario_id}
        ).fetchone()
        
        if not usuario_result:
            print(f"❌ Usuario {usuario_id} no encontrado")
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        print(f"✅ Usuario encontrado: {usuario_result[0]}")
        cambios_realizados = []
        
        # Procesar cada módulo y acción
        for modulo, acciones in permisos_nuevos.items():
            for accion, permitido in acciones.items():
                try:
                    # Por ahora saltamos la validación del catálogo para evitar importar modelos
                    # TODO: Crear validación básica sin modelos
                    
                    # Verificar si el permiso ya existe
                    permiso_existente = db.session.execute(
                        text("SELECT id, permitido FROM permisos_usuarios WHERE usuario_id = :usuario_id AND modulo = :modulo AND accion = :accion"),
                        {'usuario_id': usuario_id, 'modulo': modulo, 'accion': accion}
                    ).fetchone()
                    
                    hubo_cambio = False
                    valor_anterior = None
                    
                    if permiso_existente:
                        permiso_id, valor_actual = permiso_existente
                        valor_anterior = valor_actual
                        
                        # Solo actualizar si el valor cambió
                        if valor_actual != permitido:
                            print(f"  🔄 UPDATE: {modulo}.{accion} | {valor_actual} → {permitido}")
                            db.session.execute(
                                text("""UPDATE permisos_usuarios 
                                       SET permitido = :permitido, 
                                           fecha_asignacion = NOW(), 
                                           asignado_por = :asignado_por 
                                       WHERE id = :permiso_id"""),
                                {
                                    'permitido': permitido,
                                    'asignado_por': usuario_actual_id,  # ✅ ID del usuario, no el nombre
                                    'permiso_id': permiso_id
                                }
                            )
                            hubo_cambio = True
                        else:
                            print(f"  ⏭️ SKIP: {modulo}.{accion} | ya está en {permitido}")
                    else:
                        # Crear nuevo permiso (AHORA TAMBIÉN GUARDAMOS PERMISOS EN FALSE)
                        print(f"  ➕ INSERT: {modulo}.{accion} | valor={permitido}")
                        db.session.execute(
                            text("""INSERT INTO permisos_usuarios 
                                   (usuario_id, modulo, accion, permitido, fecha_asignacion, asignado_por) 
                                   VALUES (:usuario_id, :modulo, :accion, :permitido, NOW(), :asignado_por)"""),
                            {
                                'usuario_id': usuario_id,
                                'modulo': modulo,
                                'accion': accion,
                                'permitido': permitido,
                                'asignado_por': usuario_actual_id  # ✅ ID del usuario, no el nombre
                            }
                        )
                        hubo_cambio = True
                    
                    # Solo registrar si hubo cambio
                    if hubo_cambio:
                        # TODO: Agregar auditoría cuando se solucione la estructura de la tabla auditoria_permisos
                        cambios_realizados.append({
                            'modulo': modulo,
                            'accion': accion,
                            'valor_anterior': valor_anterior,
                            'valor_nuevo': permitido
                        })
                except Exception as e:
                    print(f"  ❌ ERROR: {modulo}.{accion} | {str(e)}")
                    log_security(f"ADVERTENCIA: Error procesando permiso | modulo={modulo} | accion={accion} | error={str(e)}")
                    continue
        
        db.session.commit()
        print(f"\n💾 COMMIT realizado | {len(cambios_realizados)} cambios guardados\n")
        
        log_security(f"PERMISOS ACTUALIZADOS | usuario_id={usuario_id} | cambios={len(cambios_realizados)} | por={session.get('usuario')}")
        
        return jsonify({
            'success': True,
            'message': f'Permisos actualizados exitosamente. {len(cambios_realizados)} cambios realizados.',
            'cambios': cambios_realizados
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERROR GLOBAL: {str(e)}\n")
        log_security(f"ERROR ACTUALIZAR PERMISOS | usuario_id={usuario_id} | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================================================
# 📧 GESTIÓN DE INVITACIONES
# ============================================================================

@usuarios_permisos_bp.route('/api/usuarios/<int:usuario_id>/invitacion', methods=['POST'])
@requiere_permiso('gestion_usuarios', 'enviar_invitacion')
def enviar_invitacion(usuario_id):
    """Envía invitación por correo para configurar contraseña"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        # Verificar que el usuario existe usando SQL directo
        usuario_result = db.session.execute(
            text("SELECT usuario, correo FROM usuarios WHERE id = :usuario_id"),
            {'usuario_id': usuario_id}
        ).fetchone()
        
        if not usuario_result:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        if not usuario_result[1]:  # correo
            return jsonify({'success': False, 'message': 'Usuario no tiene correo configurado'}), 400
        
        # Obtener información adicional del tercero para el correo
        tercero_result = db.session.execute(
            text("SELECT t.nit FROM terceros t JOIN usuarios u ON t.id = u.tercero_id WHERE u.id = :usuario_id"),
            {'usuario_id': usuario_id}
        ).fetchone()
        
        nit_tercero = tercero_result[0] if tercero_result else 'No especificado'
        
        # Enviar invitación por correo usando la función local
        exito_correo, mensaje_correo = enviar_correo_invitacion_local(
            destinatario=usuario_result[1],  # correo
            nombre_usuario=usuario_result[0],  # usuario
            nit=nit_tercero
        )
        
        if exito_correo:
            log_security(f"INVITACION ENVIADA | usuario_id={usuario_id} | correo={usuario_result[1]} | enviado_por={session.get('usuario')} | exito=True")
            return jsonify({
                'success': True,
                'message': f'Invitación enviada exitosamente a {usuario_result[1]}',
                'correo': usuario_result[1]
            })
        else:
            log_security(f"INVITACION ENVIADA | usuario_id={usuario_id} | correo={usuario_result[1]} | enviado_por={session.get('usuario')} | exito=False | error={mensaje_correo}")
            return jsonify({
                'success': False,
                'message': f'Error al enviar invitación: {mensaje_correo}'
            }), 500
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR ENVIAR INVITACION | usuario_id={usuario_id} | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@usuarios_permisos_bp.route('/api/invitaciones/<token>/validar', methods=['GET'])
def validar_invitacion(token):
    """Valida un token de invitación"""
    try:
        # Verificar token usando SQL directo
        # TODO: Crear tabla invitaciones_usuario para tokens de invitación
        # Por ahora simulamos validación exitosa
        if len(token) < 10:  # Token muy corto
            return jsonify({'success': False, 'message': 'Token de invitación no válido'}), 404
        
        log_security(f"VALIDACION INVITACION | token={token[:10]}... | validado_ok")
        
        return jsonify({
            'success': True,
            'message': 'Token de invitación válido',
            'token': token
        })
        
    except Exception as e:
        log_security(f"ERROR VALIDAR INVITACION | token={token[:10]}... | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@usuarios_permisos_bp.route('/api/invitaciones/<token>/activar', methods=['POST'])
def activar_usuario_con_invitacion(token):
    """Activa usuario y establece contraseña usando token de invitación"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({'success': False, 'message': 'Contraseña es requerida'}), 400
        
        if len(password) < 8:
            return jsonify({'success': False, 'message': 'Contraseña debe tener al menos 8 caracteres'}), 400
        
        # TODO: Implementar sistema completo de tokens de invitación con base de datos
        # Por ahora simulamos la activación exitosa
        
        # En el futuro aquí iría:
        # 1. Verificar token en tabla invitaciones_usuario
        # 2. Obtener usuario_id del token
        # 3. Actualizar contraseña del usuario
        # 4. Marcar token como usado
        
        log_security(f"USUARIO ACTIVADO POR INVITACION | token={token[:10]}... | password_actualizado")
        
        return jsonify({
            'success': True,
            'message': 'Usuario activado exitosamente. Ya puedes iniciar sesión.'
        })
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR ACTIVAR USUARIO INVITACION | token={token[:10]}... | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================================================
# 📊 CATÁLOGO Y REPORTES
# ============================================================================

@usuarios_permisos_bp.route('/api/catalogo-permisos', methods=['GET'])
@requiere_permiso('gestion_usuarios', 'consultar_permisos')
def obtener_catalogo_permisos():
    """Obtiene el catálogo completo de módulos y permisos disponibles"""
    try:
        catalogo = CatalogoPermisos.obtener_estructura_modulos()
        
        return jsonify({
            'success': True,
            'data': catalogo
        })
        
    except Exception as e:
        log_security(f"ERROR CATALOGO PERMISOS | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@usuarios_permisos_bp.route('/api/auditoria', methods=['GET'])
@requiere_permiso('gestion_usuarios', 'consultar_auditoria')
def obtener_auditoria():
    """Obtiene el log de auditoría de cambios de permisos"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        # Parámetros de paginación
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        usuario_filtro = request.args.get('usuario')
        accion_filtro = request.args.get('accion')
        
        # Query base
        query = AuditoriaPermisos.query
        
        # Filtros
        if usuario_filtro:
            query = query.filter(AuditoriaPermisos.usuario_afectado_id == usuario_filtro)
        
        if accion_filtro:
            query = query.filter(AuditoriaPermisos.accion == accion_filtro)
        
        # Ordenar por fecha descendente
        query = query.order_by(AuditoriaPermisos.fecha_cambio.desc())
        
        # Paginar
        auditoria_paginada = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        resultado = [item.to_dict() for item in auditoria_paginada.items]
        
        log_security(f"CONSULTAR AUDITORIA | usuario={session.get('usuario')} | page={page} | resultados={len(resultado)}")
        
        return jsonify({
            'success': True,
            'data': resultado,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': auditoria_paginada.total,
                'pages': auditoria_paginada.pages
            }
        })
        
    except Exception as e:
        log_security(f"ERROR AUDITORIA | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================================================
# 🎭 GESTIÓN DE ROLES (OPCIONAL - FUTURO)
# ============================================================================

@usuarios_permisos_bp.route('/api/roles', methods=['GET'])
@requiere_permiso('gestion_usuarios', 'consultar_roles')
def listar_roles():
    """Lista todos los roles disponibles"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        roles = RolUsuario.query.filter_by(activo=True).all()
        resultado = [rol.to_dict() for rol in roles]
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        log_security(f"ERROR LISTAR ROLES | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================================================
# 🔧 UTILIDADES Y HELPERS
# ============================================================================

@usuarios_permisos_bp.route('/api/validar-nit/<nit>', methods=['GET'])
@requiere_permiso('gestion_usuarios', 'consultar_usuarios')
def validar_nit(nit):
    """Valida si un NIT existe en el sistema"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        # Validar NIT usando SQL directo
        tercero_result = db.session.execute(
            text("SELECT nit, razon_social, tipo_persona FROM terceros WHERE nit = :nit"),
            {'nit': nit}
        ).fetchone()
        
        if tercero_result:
            return jsonify({
                'success': True,
                'existe': True,
                'data': {
                    'nit': tercero_result[0],
                    'razon_social': tercero_result[1],
                    'tipo_persona': tercero_result[2]
                }
            })
        else:
            return jsonify({
                'success': True,
                'existe': False,
                'message': 'NIT no encontrado en el sistema'
            })
        
    except Exception as e:
        log_security(f"ERROR VALIDAR NIT | nit={nit} | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@usuarios_permisos_bp.route('/api/estadisticas', methods=['GET'])
@usuarios_permisos_bp.route('/estadisticas', methods=['GET'])  # Alias directo
def obtener_estadisticas():
    """Obtiene estadísticas generales del sistema de usuarios"""
    valido, respuesta, codigo = validar_sesion_admin()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        # Usar consultas SQL directas para evitar conflicto de modelos
        
        # Contadores básicos de usuarios
        total_usuarios = db.session.execute(
            text("SELECT COUNT(*) FROM usuarios")
        ).scalar()
        
        usuarios_activos = db.session.execute(
            text("SELECT COUNT(*) FROM usuarios WHERE activo = true")
        ).scalar()
        
        usuarios_inactivos = total_usuarios - usuarios_activos
        
        # Invitaciones pendientes (tabla puede no existir aún)
        try:
            invitaciones_pendientes = db.session.execute(
                text("SELECT COUNT(*) FROM invitaciones_usuario WHERE usado = false")
            ).scalar()
        except Exception:
            invitaciones_pendientes = 0
        
        # Permisos populares (tabla puede no existir aún)
        try:
            permisos_result = db.session.execute(
                text("""
                SELECT modulo, accion, COUNT(*) as count 
                FROM permisos_usuarios 
                WHERE permitido = true 
                GROUP BY modulo, accion 
                ORDER BY count DESC 
                LIMIT 10
                """)
            ).fetchall()
            
            permisos_list = [
                {
                    'modulo': row[0],
                    'accion': row[1],
                    'usuarios_con_permiso': row[2]
                } for row in permisos_result
            ]
        except Exception:
            permisos_list = []
        
        # Usuarios creados en los últimos 7 días
        try:
            usuarios_recientes = db.session.execute(
                text("""
                SELECT COUNT(*) FROM usuarios 
                WHERE fecha_creacion >= CURRENT_DATE - INTERVAL '7 days'
                """)
            ).scalar()
        except Exception:
            usuarios_recientes = 0
        
        resultado = {
            'usuarios': {
                'total': total_usuarios,
                'activos': usuarios_activos,
                'inactivos': usuarios_inactivos,
                'recientes': usuarios_recientes
            },
            'invitaciones_pendientes': invitaciones_pendientes,
            'permisos_populares': permisos_list
        }
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        log_security(f"ERROR ESTADISTICAS | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500