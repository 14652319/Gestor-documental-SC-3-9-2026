"""
Middleware para tracking de sesiones activas
Este código debe agregarse a app.py
Fecha: Octubre 23, 2025
"""

# ============================================================================
# 🔄 MIDDLEWARE: ACTUALIZAR SESIÓN ACTIVA EN CADA REQUEST
# ============================================================================

from modules.admin.monitoreo.models import SesionActiva
from modules.admin.monitoreo.utils import detectar_modulo_desde_url, obtener_geolocalizacion_ip, generar_session_id
from datetime import datetime
from extensions import db

@app.before_request
def actualizar_sesion_activa():
    """
    Middleware que se ejecuta ANTES de cada request para actualizar
    la sesión activa del usuario en la base de datos
    """
    # Solo trackear si el usuario está logueado
    if 'usuario_id' not in session or 'usuario' not in session:
        return  # No hacer nada si no hay sesión
    
    # Ignorar ciertos endpoints (para evitar overhead innecesario)
    endpoints_ignorar = [
        '/static/',
        '/favicon.ico',
        '/__debug',
        '/api/monitoreo/heartbeat'  # Endpoint de heartbeat propio
    ]
    
    if any(request.path.startswith(ep) for ep in endpoints_ignorar):
        return
    
    try:
        usuario_id = session.get('usuario_id')
        usuario_nombre = session.get('usuario')
        ip_address = request.remote_addr
        user_agent = request.user_agent.string
        ruta_actual = request.path
        modulo_actual = detectar_modulo_desde_url(ruta_actual)
        
        # Generar un session_id único basado en el SID de Flask
        session_id = session.get('_id', None)
        if not session_id:
            # Si no existe, generarlo
            session_id = generar_session_id(usuario_id, ip_address, str(datetime.utcnow()))
            session['_id'] = session_id
        
        # Buscar sesión existente por session_id
        sesion = SesionActiva.query.filter_by(session_id=session_id).first()
        
        if sesion:
            # Actualizar sesión existente
            sesion.fecha_ultima_actividad = datetime.utcnow()
            sesion.modulo_actual = modulo_actual
            sesion.ruta_actual = ruta_actual
            sesion.conectado = True
        else:
            # Crear nueva sesión
            # Obtener geolocalización de la IP (solo en la primera vez)
            geo_info = obtener_geolocalizacion_ip(ip_address)
            
            sesion = SesionActiva(
                usuario_id=usuario_id,
                usuario_nombre=usuario_nombre,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                modulo_actual=modulo_actual,
                ruta_actual=ruta_actual,
                conectado=True,
                pais=geo_info.get('pais'),
                ciudad=geo_info.get('ciudad'),
                latitud=geo_info.get('latitud'),
                longitud=geo_info.get('longitud')
            )
            db.session.add(sesion)
        
        db.session.commit()
    
    except Exception as e:
        # Si falla el tracking de sesión, NO romper el request
        print(f"❌ Error actualizando sesión activa: {str(e)}")
        db.session.rollback()


# ============================================================================
# 📡 ENDPOINT: HEARTBEAT PARA MANTENER SESIÓN VIVA
# ============================================================================
# Este endpoint debe llamarse cada 30 segundos desde el frontend

@app.route('/api/monitoreo/heartbeat', methods=['POST'])
def heartbeat_sesion():
    """
    Endpoint ligero que actualiza el timestamp de última actividad
    Se llama cada 30 segundos desde el frontend para mantener la sesión activa
    """
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'Sin sesión'}), 401
    
    try:
        session_id = session.get('_id')
        if session_id:
            sesion = SesionActiva.query.filter_by(session_id=session_id).first()
            if sesion:
                sesion.fecha_ultima_actividad = datetime.utcnow()
                db.session.commit()
        
        return jsonify({'success': True, 'timestamp': datetime.utcnow().isoformat()})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# 🚪 HOOK: MARCAR SESIÓN COMO DESCONECTADA AL HACER LOGOUT
# ============================================================================
# Agregar esto a la función de logout en app.py

def marcar_sesion_desconectada():
    """
    Marca la sesión actual como desconectada en la base de datos
    Llamar esto en el logout
    """
    try:
        session_id = session.get('_id')
        if session_id:
            sesion = SesionActiva.query.filter_by(session_id=session_id).first()
            if sesion:
                sesion.conectado = False
                sesion.fecha_desconexion = datetime.utcnow()
                db.session.commit()
    except Exception as e:
        print(f"❌ Error marcando sesión como desconectada: {str(e)}")


# ============================================================================
# INSTRUCCIONES DE INSTALACIÓN
# ============================================================================
"""
PASO 1: Agregar imports al inicio de app.py
-----------------------------------------------
from modules.admin.monitoreo.models import SesionActiva
from modules.admin.monitoreo.utils import detectar_modulo_desde_url, obtener_geolocalizacion_ip, generar_session_id

PASO 2: Agregar el middleware ANTES de cualquier ruta
-----------------------------------------------
Copiar la función actualizar_sesion_activa() completa

PASO 3: Agregar el endpoint de heartbeat
-----------------------------------------------
Copiar la función heartbeat_sesion() completa

PASO 4: Modificar la función de logout existente
-----------------------------------------------
Al final de la función de logout (antes del return), agregar:
    marcar_sesion_desconectada()

PASO 5: Agregar JavaScript al frontend (dashboard.html y otros templates)
-----------------------------------------------
Agregar al final del <script>:

// Heartbeat para mantener sesión viva
setInterval(() => {
    fetch('/api/monitoreo/heartbeat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    }).catch(err => console.error('Heartbeat failed:', err));
}, 30000);  // Cada 30 segundos
"""
