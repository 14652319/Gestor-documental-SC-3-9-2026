"""
🛡️ MÓDULO DE SEGURIDAD CENTRALIZADO
Gestor Documental - Supertiendas Cañaveral

Validadores y utilidades de seguridad reutilizables.
Usar en TODOS los endpoints que reciban input de usuario.
"""

import re
import os
import hashlib
import secrets
from functools import wraps
from datetime import datetime, timedelta
from flask import request, session, jsonify, abort
from werkzeug.utils import secure_filename


class SecurityValidator:
    """Validador centralizado de inputs de usuario"""
    
    @staticmethod
    def validar_nit(nit):
        """
        Valida formato de NIT colombiano
        
        Args:
            nit (str): NIT a validar
            
        Returns:
            str: NIT sanitizado
            
        Raises:
            ValueError: Si NIT es inválido
            
        Ejemplos:
            >>> SecurityValidator.validar_nit("805028041-2")
            "805028041-2"
            >>> SecurityValidator.validar_nit("abc123")
            ValueError: NIT inválido
        """
        if not nit:
            raise ValueError("NIT no puede estar vacío")
        
        # Remover espacios
        nit = str(nit).strip()
        
        # Solo números y guiones
        if not re.match(r'^[\d\-]{1,15}$', nit):
            raise ValueError("NIT debe contener solo números y guiones (máx 15 caracteres)")
        
        # Al menos 5 dígitos
        digitos = re.sub(r'[^\d]', '', nit)
        if len(digitos) < 5:
            raise ValueError("NIT debe tener al menos 5 dígitos")
        
        return nit
    
    @staticmethod
    def validar_email(email):
        """
        Valida formato de email
        
        Args:
            email (str): Email a validar
            
        Returns:
            str: Email sanitizado (lowercase)
            
        Raises:
            ValueError: Si email es inválido
        """
        if not email:
            raise ValueError("Email no puede estar vacío")
        
        email = str(email).strip().lower()
        
        # Patrón básico de email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Formato de email inválido")
        
        # Longitud máxima
        if len(email) > 254:
            raise ValueError("Email demasiado largo")
        
        return email
    
    @staticmethod
    def validar_password(password):
        """
        Valida complejidad de contraseña
        
        Requisitos:
        - Mínimo 8 caracteres
        - Al menos 1 mayúscula
        - Al menos 1 minúscula
        - Al menos 1 número
        - Al menos 1 carácter especial
        
        Args:
            password (str): Contraseña a validar
            
        Returns:
            str: Password validado
            
        Raises:
            ValueError: Si password no cumple requisitos
        """
        if not password:
            raise ValueError("Contraseña no puede estar vacía")
        
        if len(password) < 8:
            raise ValueError("Contraseña debe tener mínimo 8 caracteres")
        
        if len(password) > 128:
            raise ValueError("Contraseña demasiado larga (máx 128 caracteres)")
        
        if not re.search(r'[A-Z]', password):
            raise ValueError("Contraseña debe tener al menos una mayúscula")
        
        if not re.search(r'[a-z]', password):
            raise ValueError("Contraseña debe tener al menos una minúscula")
        
        if not re.search(r'\d', password):
            raise ValueError("Contraseña debe tener al menos un número")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/`~]', password):
            raise ValueError("Contraseña debe tener al menos un carácter especial")
        
        # Verificar contra lista de contraseñas comunes
        CONTRASEÑAS_COMUNES = [
            'password', '123456', 'qwerty', 'admin', 'letmein',
            'welcome', 'monkey', '1234567890', 'abc123', 'password123',
            'qwerty123', 'admin123', '12345678', 'password1', 'pass123'
        ]
        if password.lower() in CONTRASEÑAS_COMUNES:
            raise ValueError("Contraseña demasiado común, elige otra más segura")
        
        return password
    
    @staticmethod
    def validar_nombre(nombre, max_length=255):
        """
        Valida nombre de persona/empresa
        
        Args:
            nombre (str): Nombre a validar
            max_length (int): Longitud máxima
            
        Returns:
            str: Nombre sanitizado
            
        Raises:
            ValueError: Si nombre es inválido
        """
        if not nombre:
            raise ValueError("Nombre no puede estar vacío")
        
        nombre = str(nombre).strip()
        
        # Solo letras, espacios, tildes y algunos caracteres especiales
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\.\-\']+$', nombre):
            raise ValueError("Nombre contiene caracteres no permitidos")
        
        if len(nombre) < 2:
            raise ValueError("Nombre demasiado corto (mín 2 caracteres)")
        
        if len(nombre) > max_length:
            raise ValueError(f"Nombre demasiado largo (máx {max_length} caracteres)")
        
        return nombre
    
    @staticmethod
    def validar_telefono(telefono):
        """
        Valida número de teléfono colombiano
        
        Args:
            telefono (str): Teléfono a validar
            
        Returns:
            str: Teléfono sanitizado
            
        Raises:
            ValueError: Si teléfono es inválido
        """
        if not telefono:
            raise ValueError("Teléfono no puede estar vacío")
        
        telefono = str(telefono).strip()
        
        # Remover caracteres no numéricos excepto + al inicio
        telefono = re.sub(r'[^\d\+]', '', telefono)
        
        # Validar formato colombiano
        # Formato: +57XXXXXXXXXX o XXXXXXXXXX (7-10 dígitos)
        if telefono.startswith('+57'):
            telefono = telefono[3:]
        
        if not re.match(r'^\d{7,10}$', telefono):
            raise ValueError("Teléfono debe tener entre 7 y 10 dígitos")
        
        return telefono
    
    @staticmethod
    def validar_id(id_value, nombre_campo="ID"):
        """
        Valida que un ID sea un entero positivo
        
        Args:
            id_value: Valor a validar
            nombre_campo (str): Nombre del campo para mensaje de error
            
        Returns:
            int: ID validado
            
        Raises:
            ValueError: Si ID es inválido
        """
        try:
            id_int = int(id_value)
        except (TypeError, ValueError):
            raise ValueError(f"{nombre_campo} debe ser un número entero")
        
        if id_int <= 0:
            raise ValueError(f"{nombre_campo} debe ser mayor a 0")
        
        if id_int > 2147483647:  # Max INT en PostgreSQL
            raise ValueError(f"{nombre_campo} demasiado grande")
        
        return id_int
    
    @staticmethod
    def validar_fecha(fecha_str, formato='%Y-%m-%d'):
        """
        Valida formato de fecha
        
        Args:
            fecha_str (str): Fecha en formato string
            formato (str): Formato esperado (default: YYYY-MM-DD)
            
        Returns:
            datetime: Objeto datetime validado
            
        Raises:
            ValueError: Si fecha es inválida
        """
        if not fecha_str:
            raise ValueError("Fecha no puede estar vacía")
        
        try:
            fecha = datetime.strptime(str(fecha_str).strip(), formato)
        except ValueError as e:
            raise ValueError(f"Formato de fecha inválido. Use {formato}")
        
        # Validar rango razonable (1900 - 2100)
        if fecha.year < 1900 or fecha.year > 2100:
            raise ValueError("Año fuera de rango válido (1900-2100)")
        
        return fecha
    
    @staticmethod
    def validar_url(url):
        """
        Valida formato básico de URL
        
        Args:
            url (str): URL a validar
            
        Returns:
            str: URL validada
            
        Raises:
            ValueError: Si URL es inválida
        """
        if not url:
            raise ValueError("URL no puede estar vacía")
        
        url = str(url).strip()
        
        # Solo HTTP/HTTPS
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL debe comenzar con http:// o https://")
        
        # Patrón básico
        pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        if not re.match(pattern, url):
            raise ValueError("Formato de URL inválido")
        
        return url
    
    @staticmethod
    def sanitizar_sql_like(valor):
        """
        Sanitiza valor para uso en cláusulas SQL LIKE
        Escapa caracteres especiales: % _ [ ]
        
        Args:
            valor (str): Valor a sanitizar
            
        Returns:
            str: Valor sanitizado
        """
        if not valor:
            return ''
        
        # Escapar caracteres especiales de LIKE
        valor = str(valor).replace('\\', '\\\\')
        valor = valor.replace('%', '\\%')
        valor = valor.replace('_', '\\_')
        valor = valor.replace('[', '\\[')
        valor = valor.replace(']', '\\]')
        
        return valor


class FileValidator:
    """Validador de archivos subidos"""
    
    # Tipos MIME permitidos por categoría
    MIME_TYPES = {
        'pdf': {'application/pdf'},
        'excel': {
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        },
        'word': {
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        },
        'imagen': {
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/webp'
        }
    }
    
    @staticmethod
    def validar_archivo_pdf(archivo, max_mb=5):
        """
        Valida que un archivo sea realmente un PDF
        
        Args:
            archivo (FileStorage): Archivo subido
            max_mb (int): Tamaño máximo en MB
            
        Returns:
            tuple: (True, tamaño_bytes)
            
        Raises:
            ValueError: Si archivo es inválido
        """
        if not archivo or not archivo.filename:
            raise ValueError("Archivo no proporcionado")
        
        # 1. Validar extensión
        ext = os.path.splitext(archivo.filename)[1].lower()
        if ext != '.pdf':
            raise ValueError("Solo se permiten archivos PDF")
        
        # 2. Validar tamaño
        archivo.seek(0, os.SEEK_END)
        tamaño = archivo.tell()
        archivo.seek(0)
        
        max_bytes = max_mb * 1024 * 1024
        if tamaño > max_bytes:
            raise ValueError(f"Archivo muy grande: {tamaño/1024/1024:.2f}MB (máx {max_mb}MB)")
        
        if tamaño == 0:
            raise ValueError("Archivo vacío")
        
        # 3. Validar firma del archivo (magic number)
        contenido_inicio = archivo.read(1024)
        archivo.seek(0)
        
        # PDF debe comenzar con %PDF
        if not contenido_inicio.startswith(b'%PDF'):
            raise ValueError("Archivo no es un PDF válido (firma incorrecta)")
        
        # Verificar que no sea PDF malicioso
        if b'/JS' in contenido_inicio or b'/JavaScript' in contenido_inicio:
            raise ValueError("PDF contiene JavaScript (no permitido)")
        
        return True, tamaño
    
    @staticmethod
    def sanitizar_nombre_archivo(nombre_archivo):
        """
        Sanitiza nombre de archivo
        
        Args:
            nombre_archivo (str): Nombre original del archivo
            
        Returns:
            str: Nombre sanitizado
        """
        # Usar secure_filename de Werkzeug
        nombre_seguro = secure_filename(nombre_archivo)
        
        # Límite de longitud
        nombre, ext = os.path.splitext(nombre_seguro)
        if len(nombre) > 100:
            nombre = nombre[:100]
        
        return nombre + ext
    
    @staticmethod
    def validar_ruta_segura(ruta_base, ruta_archivo):
        """
        Previene path traversal validando que la ruta esté dentro del directorio permitido
        
        Args:
            ruta_base (str): Directorio base permitido
            ruta_archivo (str): Ruta del archivo a validar
            
        Returns:
            str: Ruta absoluta validada
            
        Raises:
            ValueError: Si se detecta intento de path traversal
        """
        # Obtener rutas absolutas
        ruta_base = os.path.abspath(ruta_base)
        ruta_archivo = os.path.abspath(ruta_archivo)
        
        # Verificar que la ruta del archivo esté dentro de la ruta base
        if not ruta_archivo.startswith(ruta_base):
            raise ValueError("Intento de path traversal detectado")
        
        return ruta_archivo


class TokenGenerator:
    """Generador de tokens seguros"""
    
    @staticmethod
    def generar_token_numerico(longitud=6):
        """
        Genera token numérico seguro
        
        Args:
            longitud (int): Longitud del token
            
        Returns:
            str: Token numérico
        """
        return ''.join([str(secrets.randbelow(10)) for _ in range(longitud)])
    
    @staticmethod
    def generar_token_alfanumerico(longitud=32):
        """
        Genera token alfanumérico seguro
        
        Args:
            longitud (int): Longitud del token
            
        Returns:
            str: Token alfanumérico
        """
        return secrets.token_urlsafe(longitud)
    
    @staticmethod
    def generar_hash_seguro(datos):
        """
        Genera hash SHA256 de datos
        
        Args:
            datos (str): Datos a hashear
            
        Returns:
            str: Hash hexadecimal
        """
        return hashlib.sha256(str(datos).encode()).hexdigest()


class LogSanitizer:
    """Sanitizador de logs para prevenir exposición de datos sensibles"""
    
    CAMPOS_SENSIBLES = [
        'password', 'contraseña', 'token', 'secret', 'key',
        'api_key', 'access_token', 'refresh_token', 'authorization',
        'credit_card', 'tarjeta', 'cvv', 'pin'
    ]
    
    @staticmethod
    def sanitizar_dict(datos):
        """
        Remueve datos sensibles de diccionario
        
        Args:
            datos (dict): Diccionario con posibles datos sensibles
            
        Returns:
            dict: Diccionario con datos sensibles censurados
        """
        if not isinstance(datos, dict):
            return datos
        
        datos_safe = datos.copy()
        
        for campo in LogSanitizer.CAMPOS_SENSIBLES:
            # Buscar key exacta o que contenga el término
            for key in list(datos_safe.keys()):
                if campo.lower() in key.lower():
                    datos_safe[key] = '***REDACTED***'
        
        return datos_safe
    
    @staticmethod
    def sanitizar_string(texto):
        """
        Remueve información sensible de strings
        
        Args:
            texto (str): Texto a sanitizar
            
        Returns:
            str: Texto sanitizado
        """
        if not isinstance(texto, str):
            return texto
        
        # Censurar números de tarjeta (16 dígitos)
        texto = re.sub(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b', '****-****-****-****', texto)
        
        # Censurar emails parcialmente (mantener dominio)
        texto = re.sub(r'([a-zA-Z0-9._%+-]{1,3})[a-zA-Z0-9._%+-]*@', r'\1***@', texto)
        
        return texto


# ==================== DECORADORES DE SEGURIDAD ====================

def requiere_autenticacion(f):
    """
    Decorator para endpoints que requieren usuario autenticado
    
    Valida:
    - Sesión activa
    - IP de sesión (previene hijacking)
    - Usuario activo en BD
    
    Uso:
        @app.route('/dashboard')
        @requiere_autenticacion
        def dashboard():
            # ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Validar sesión activa
        if 'usuario_id' not in session:
            return jsonify({'error': 'No autenticado'}), 401
        
        # Validar que la IP sea la misma que hizo login
        ip_login = session.get('ip_login')
        ip_actual = request.remote_addr
        
        if ip_login and ip_actual != ip_login:
            from app import log_security  # Import lazy para evitar circular
            log_security(f"ALERTA SESIÓN SOSPECHOSA | usuario={session.get('usuario')} | ip_login={ip_login} | ip_actual={ip_actual}")
            session.clear()
            return jsonify({'error': 'Sesión inválida'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def requiere_rol(*roles_permitidos):
    """
    Decorator para validar rol de usuario
    
    Args:
        *roles_permitidos: Lista de roles permitidos ('admin', 'interno', 'externo')
    
    Uso:
        @app.route('/admin/usuarios')
        @requiere_autenticacion
        @requiere_rol('admin')
        def listar_usuarios():
            # ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            rol_usuario = session.get('rol')
            
            if rol_usuario not in roles_permitidos:
                return jsonify({'error': 'Acceso denegado'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def validar_idor(modelo, campo_id='id', campo_propietario=None):
    """
    Decorator para prevenir Insecure Direct Object Reference
    
    Valida que el usuario solo pueda acceder a sus propios recursos
    
    Args:
        modelo: Clase del modelo SQLAlchemy
        campo_id (str): Nombre del parámetro en la ruta
        campo_propietario (str): Campo que indica el propietario (ej: 'usuario_id', 'nit')
    
    Uso:
        @app.route('/api/factura/<int:factura_id>')
        @requiere_autenticacion
        @validar_idor(Factura, campo_id='factura_id', campo_propietario='usuario_id')
        def obtener_factura(factura_id):
            # ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obtener ID del recurso
            recurso_id = kwargs.get(campo_id)
            
            if not recurso_id:
                return jsonify({'error': 'ID no proporcionado'}), 400
            
            # Buscar recurso
            recurso = modelo.query.get(recurso_id)
            
            if not recurso:
                return jsonify({'error': 'Recurso no encontrado'}), 404
            
            # Validar propiedad (excepto admins)
            if session.get('rol') != 'admin' and campo_propietario:
                propietario = getattr(recurso, campo_propietario, None)
                usuario_actual = session.get('usuario_id') if campo_propietario == 'usuario_id' else session.get('nit')
                
                if propietario != usuario_actual:
                    from app import log_security
                    log_security(f"INTENTO IDOR | usuario={session.get('usuario')} | recurso={modelo.__name__}#{recurso_id}")
                    return jsonify({'error': 'Acceso denegado'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


# ==================== FUNCIONES DE UTILIDAD ====================

def sanitizar_para_log(datos):
    """
    Wrapper para sanitizar datos antes de loggear
    
    Args:
        datos: Dict, string u objeto a sanitizar
        
    Returns:
        Datos sanitizados
    """
    if isinstance(datos, dict):
        return LogSanitizer.sanitizar_dict(datos)
    elif isinstance(datos, str):
        return LogSanitizer.sanitizar_string(datos)
    else:
        return datos


def generar_nombre_archivo_seguro(nit, prefijo, extension='.pdf'):
    """
    Genera nombre de archivo seguro con timestamp
    
    Args:
        nit (str): NIT del tercero
        prefijo (str): Prefijo descriptivo
        extension (str): Extensión del archivo
        
    Returns:
        str: Nombre de archivo sanitizado
    """
    # Validar NIT
    nit = SecurityValidator.validar_nit(nit)
    
    # Timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Sanitizar prefijo
    prefijo = re.sub(r'[^\w\-]', '_', prefijo)
    
    # Generar nombre
    nombre = f"{nit}_{prefijo}_{timestamp}{extension}"
    
    return FileValidator.sanitizar_nombre_archivo(nombre)


# ==================== EJEMPLO DE USO ====================

if __name__ == '__main__':
    print("🛡️ Módulo de seguridad cargado")
    print("\n📋 Ejemplos de uso:")
    
    # Validar NIT
    try:
        nit = SecurityValidator.validar_nit("805028041-2")
        print(f"✅ NIT válido: {nit}")
    except ValueError as e:
        print(f"❌ Error: {e}")
    
    # Validar email
    try:
        email = SecurityValidator.validar_email("usuario@empresa.com")
        print(f"✅ Email válido: {email}")
    except ValueError as e:
        print(f"❌ Error: {e}")
    
    # Validar password
    try:
        pwd = SecurityValidator.validar_password("Admin123!@#")
        print(f"✅ Password válido")
    except ValueError as e:
        print(f"❌ Error: {e}")
    
    # Generar token
    token = TokenGenerator.generar_token_numerico(6)
    print(f"✅ Token generado: {token}")
    
    # Sanitizar log
    datos_sensibles = {
        "usuario": "admin",
        "password": "secreto123",
        "nit": "805028041"
    }
    datos_seguros = LogSanitizer.sanitizar_dict(datos_sensibles)
    print(f"✅ Datos sanitizados: {datos_seguros}")
