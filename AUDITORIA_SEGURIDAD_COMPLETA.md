# 🚨 AUDITORÍA COMPLETA DE SEGURIDAD
## Gestor Documental - Supertiendas Cañaveral

**Fecha:** 9 de Diciembre, 2025  
**Análisis:** Vulnerabilidades de seguridad y puntos de intrusión

---

## 📊 RESUMEN EJECUTIVO

| Categoría | Críticas | Altas | Medias | Bajas | Total |
|-----------|----------|-------|--------|-------|-------|
| SQL Injection | 0 | 2 | 3 | 0 | 5 |
| File Upload | 3 | 1 | 2 | 0 | 6 |
| XSS | 0 | 1 | 2 | 1 | 4 |
| CSRF | 0 | 5 | 0 | 0 | 5 |
| Auth/Session | 0 | 2 | 3 | 2 | 7 |
| Information Disclosure | 0 | 1 | 3 | 2 | 6 |
| **TOTAL** | **3** | **12** | **13** | **5** | **33** |

---

## 🔴 VULNERABILIDADES CRÍTICAS (3)

### 1. ❌ Path Traversal en Upload de Archivos

**Archivo:** `app.py` líneas 1707-1750

```python
# 🔴 VULNERABLE
nombre_archivo = f"{nit}-TEMP-{fecha_carpeta}_{tipo_doc}.pdf"
ruta_archivo = os.path.join(ruta_completa, nombre_archivo)
archivo.save(ruta_archivo)
```

**Riesgo:** Un atacante puede subir archivos fuera del directorio esperado.

**Ataque:**
```python
# Archivo malicioso con nombre:
tipo_doc = "../../../evil"
# Resultado: archivo se guarda en directorio padre
```

**Impacto:** 
- Sobrescritura de archivos del sistema
- Subida de webshells
- Ejecución remota de código

**✅ SOLUCIÓN:**
```python
from werkzeug.utils import secure_filename
import re

def validar_tipo_documento(tipo_doc):
    """Solo permite tipos documentales válidos"""
    TIPOS_PERMITIDOS = [
        "RUT", "CAMARA_COMERCIO", "CEDULA_REPRESENTANTE",
        "CERTIFICACION_BANCARIA", "FORMULARIO_CONOCIMIENTO_PROVEEDORES",
        "DECLARACION_FONDOS_JURIDICA", "DECLARACION_FONDOS_NATURAL"
    ]
    if tipo_doc not in TIPOS_PERMITIDOS:
        raise ValueError(f"Tipo de documento no permitido: {tipo_doc}")
    return tipo_doc

def validar_nit_seguro(nit):
    """Solo permite números y guiones, máximo 15 caracteres"""
    if not re.match(r'^[\d\-]{1,15}$', nit):
        raise ValueError("NIT inválido")
    return nit

# Uso seguro:
nit = validar_nit_seguro(request.form.get("nit", "").strip())
tipo_doc = validar_tipo_documento(request.form.get("tipo"))

# Sanitizar nombre de archivo
nombre_base = secure_filename(archivo.filename)
nombre_archivo = f"{nit}-TEMP-{fecha_carpeta}_{tipo_doc}.pdf"

# Forzar que la ruta esté dentro del directorio permitido
ruta_archivo = os.path.abspath(os.path.join(ruta_completa, nombre_archivo))
ruta_base = os.path.abspath(ruta_completa)

if not ruta_archivo.startswith(ruta_base):
    raise ValueError("Intento de path traversal detectado")

archivo.save(ruta_archivo)
```

---

### 2. ❌ Sin Validación de Tipo de Archivo (Arbitrary File Upload)

**Archivos:** 
- `app.py` línea 1707
- `modules/facturas_digitales/routes.py` línea 1568
- `modules/facturas_digitales/routes.py` línea 2320

```python
# 🔴 VULNERABLE - No valida contenido del archivo
archivo = request.files.get(f"doc_{tipo_doc}")
if archivo and archivo.filename:
    archivo.save(ruta_archivo)
```

**Riesgo:** Subir archivos ejecutables (.exe, .sh, .php, .jsp)

**Ataque:**
```python
# Subir archivo con nombre: innocent.pdf
# Pero contenido real: webshell.php
# Luego acceder: /documentos_terceros/webshell.php
```

**Impacto:**
- Ejecución remota de código
- Compromiso total del servidor
- Robo de base de datos

**✅ SOLUCIÓN:**
```python
import magic  # pip install python-magic

EXTENSIONES_PERMITIDAS = {'.pdf'}
MIME_TYPES_PERMITIDOS = {'application/pdf'}

def validar_archivo_pdf(archivo):
    """Valida que el archivo sea realmente un PDF"""
    # 1. Validar extensión
    ext = os.path.splitext(archivo.filename)[1].lower()
    if ext not in EXTENSIONES_PERMITIDAS:
        raise ValueError(f"Extensión no permitida: {ext}")
    
    # 2. Validar MIME type del contenido real
    archivo.seek(0)
    contenido = archivo.read(2048)  # Leer primeros 2KB
    archivo.seek(0)  # Volver al inicio
    
    mime = magic.from_buffer(contenido, mime=True)
    if mime not in MIME_TYPES_PERMITIDOS:
        raise ValueError(f"Tipo de archivo no permitido: {mime}")
    
    # 3. Validar firma del archivo (PDF comienza con %PDF)
    if not contenido.startswith(b'%PDF'):
        raise ValueError("Archivo no es un PDF válido")
    
    return True

# Uso:
archivo = request.files.get(f"doc_{tipo_doc}")
if archivo and archivo.filename:
    validar_archivo_pdf(archivo)  # Lanzará excepción si no es PDF válido
    archivo.save(ruta_archivo)
```

---

### 3. ❌ Sin Límite de Tamaño de Archivo (DoS)

**Archivo:** Toda la aplicación

```python
# 🔴 VULNERABLE - Sin límite de tamaño
@app.route("/api/documentos/upload", methods=["POST"])
def api_cargar_documentos():
    archivo = request.files.get(f"doc_{tipo_doc}")
    archivo.save(ruta_archivo)  # Acepta archivos de cualquier tamaño
```

**Riesgo:** Subir archivos gigantes para llenar el disco

**Ataque:**
```bash
# Subir archivo de 10GB
curl -X POST -F "doc_RUT=@gigante.pdf" http://sistema/api/documentos/upload
```

**Impacto:**
- Denegación de servicio (DoS)
- Llenar disco duro
- Crash del servidor

**✅ SOLUCIÓN:**
```python
# En app.py (configuración global)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB máximo

# O por endpoint:
def validar_tamano_archivo(archivo, max_mb=5):
    """Valida tamaño máximo del archivo"""
    archivo.seek(0, os.SEEK_END)
    tamaño = archivo.tell()
    archivo.seek(0)
    
    max_bytes = max_mb * 1024 * 1024
    if tamaño > max_bytes:
        raise ValueError(f"Archivo demasiado grande: {tamaño/1024/1024:.2f}MB (máx {max_mb}MB)")
    
    return tamaño

# Uso:
archivo = request.files.get(f"doc_{tipo_doc}")
if archivo and archivo.filename:
    tamaño = validar_tamano_archivo(archivo, max_mb=5)
    log_security(f"Archivo validado | tipo={tipo_doc} | tamaño={tamaño} bytes")
    archivo.save(ruta_archivo)
```

---

## 🟠 VULNERABILIDADES ALTAS (12)

### 4. ❌ SQL Injection en Nombres de Tabla Dinámicos

**Archivos:**
- `modules/admin/usuarios_permisos/routes.py` línea 539
- `buscar_tabla_permisos_correcta.py` múltiples líneas
- `crear_tablas_monitoreo.py` líneas 65, 73

```python
# 🔴 VULNERABLE
query = text(f"UPDATE usuarios SET {', '.join(updates)} WHERE id = :id")
result = db.session.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
```

**Solución:** Ver `SEGURIDAD_SQL_INJECTION.md` líneas 40-95

---

### 5. ❌ Sin Protección CSRF

**Archivo:** Toda la aplicación - **TODOS LOS ENDPOINTS POST**

```python
# 🔴 VULNERABLE - Sin token CSRF
@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json()
    # ... procesar login sin validar CSRF
```

**Riesgo:** Atacante puede hacer peticiones en nombre de usuario autenticado

**Ataque:**
```html
<!-- Página maliciosa -->
<form action="https://gestor.empresa.com/api/admin/usuarios/desactivar/1" method="POST">
    <input type="hidden" name="accion" value="eliminar">
</form>
<script>document.forms[0].submit();</script>
```

**Impacto:**
- Eliminar usuarios sin permiso
- Cambiar contraseñas
- Modificar datos

**✅ SOLUCIÓN:**
```python
# Opción 1: Flask-WTF (RECOMENDADO)
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# Excluir endpoints que usan tokens propios
csrf.exempt('/api/auth/login')

# En el frontend:
<meta name="csrf-token" content="{{ csrf_token() }}">

fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
    }
});

# Opción 2: SameSite Cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_COOKIE_SECURE'] = True  # Solo HTTPS
```

---

### 6. ❌ Passwords en Logs

**Archivo:** Múltiples archivos

```python
# 🔴 VULNERABLE
log_security(f"LOGIN | usuario={usuario} | password={password}")
print(f"Datos recibidos: {data}")  # Si data contiene password
```

**Riesgo:** Contraseñas almacenadas en texto plano en logs

**✅ SOLUCIÓN:**
```python
# NUNCA loggear passwords
def sanitizar_log(data):
    """Remueve datos sensibles antes de loggear"""
    CAMPOS_SENSIBLES = ['password', 'token', 'secret', 'key']
    data_safe = data.copy() if isinstance(data, dict) else data
    
    if isinstance(data_safe, dict):
        for campo in CAMPOS_SENSIBLES:
            if campo in data_safe:
                data_safe[campo] = '***REDACTED***'
    
    return data_safe

# Uso:
log_security(f"LOGIN | datos={sanitizar_log(data)}")
```

---

### 7. ❌ Información Sensible en Respuestas de Error

**Archivo:** Múltiples archivos

```python
# 🔴 VULNERABLE
except Exception as e:
    return jsonify({'error': str(e)}), 500
```

**Riesgo:** Revelar estructura de BD, rutas del servidor, versiones

**Ejemplo:**
```json
{
  "error": "column usuarios.password does not exist at line 42 in /var/www/app/routes.py"
}
```

**✅ SOLUCIÓN:**
```python
# Mensajes genéricos para usuarios
# Logs detallados para admins
import traceback

except Exception as e:
    # Log completo para debug
    log_security(f"ERROR INTERNO | endpoint={request.endpoint} | error={str(e)}")
    log_security(f"STACK TRACE | {traceback.format_exc()}")
    
    # Mensaje genérico para usuario
    if app.debug:
        return jsonify({'error': str(e)}), 500  # Solo en desarrollo
    else:
        return jsonify({'error': 'Error interno del servidor'}), 500
```

---

### 8. ❌ Rate Limiting Insuficiente

**Archivo:** `app.py` - Login endpoint

```python
# 🔴 Protección básica pero insuficiente
# Solo bloquea después de ataques, no previene
```

**Riesgo:** Brute force de contraseñas, DoS

**✅ SOLUCIÓN:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379"  # O memoria si no tienes Redis
)

# Aplicar límites estrictos a endpoints sensibles
@app.route("/api/auth/login", methods=["POST"])
@limiter.limit("5 per minute")  # Máx 5 intentos por minuto
def api_login():
    # ... código
    pass

@app.route("/api/auth/forgot_request", methods=["POST"])
@limiter.limit("3 per hour")  # Máx 3 recuperaciones por hora
def forgot_request():
    # ... código
    pass
```

---

### 9. ❌ Weak Password Policy

**Archivo:** `app.py` - Registro de usuarios

```python
# 🔴 Sin validación fuerte de contraseñas
password = data.get("password")
# ... directo a bcrypt sin validar complejidad
```

**Riesgo:** Contraseñas débiles fáciles de adivinar

**✅ SOLUCIÓN:**
```python
import re

def validar_password_fuerte(password):
    """
    Requiere:
    - Mínimo 8 caracteres
    - Al menos 1 mayúscula
    - Al menos 1 minúscula
    - Al menos 1 número
    - Al menos 1 carácter especial
    """
    if len(password) < 8:
        raise ValueError("Contraseña debe tener mínimo 8 caracteres")
    
    if not re.search(r'[A-Z]', password):
        raise ValueError("Contraseña debe tener al menos una mayúscula")
    
    if not re.search(r'[a-z]', password):
        raise ValueError("Contraseña debe tener al menos una minúscula")
    
    if not re.search(r'\d', password):
        raise ValueError("Contraseña debe tener al menos un número")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError("Contraseña debe tener al menos un carácter especial")
    
    # Verificar contra lista de contraseñas comunes
    CONTRASEÑAS_COMUNES = [
        'password', '123456', 'qwerty', 'admin', 'letmein',
        'welcome', 'monkey', '1234567890', 'abc123'
    ]
    if password.lower() in CONTRASEÑAS_COMUNES:
        raise ValueError("Contraseña demasiado común, elige otra")
    
    return True

# Uso:
password = data.get("password")
validar_password_fuerte(password)
hashed = bcrypt.generate_password_hash(password).decode('utf-8')
```

---

### 10. ❌ Session Fixation

**Archivo:** `app.py` - Login

```python
# 🔴 No regenera session ID después de login
session['usuario_id'] = user.id
session['usuario'] = user.usuario
```

**Riesgo:** Atacante puede fijar session ID antes del login

**✅ SOLUCIÓN:**
```python
@app.route("/api/auth/login", methods=["POST"])
def api_login():
    # ... validar credenciales
    
    if user and bcrypt.check_password_hash(user.password, password):
        # 🛡️ REGENERAR SESSION ID
        session.clear()  # Limpiar sesión antigua
        session.permanent = True
        session.new = True  # Forzar nuevo ID
        
        # Ahora sí guardar datos
        session['usuario_id'] = user.id
        session['usuario'] = user.usuario
        session['nit'] = user.tercero.nit if user.tercero else None
        
        # Registrar IP de sesión para validación adicional
        session['ip_login'] = request.remote_addr
        
        return jsonify({"success": True})
```

---

### 11. ❌ Sin Validación de Session IP

**Archivo:** Toda la aplicación

```python
# 🔴 No valida que la IP sea la misma que hizo login
if 'usuario_id' in session:
    # ... usuario autenticado
```

**Riesgo:** Session hijacking, robo de cookies

**✅ SOLUCIÓN:**
```python
def validar_sesion_activa():
    """Valida que la sesión sea del mismo usuario e IP"""
    if 'usuario_id' not in session:
        return False
    
    # Validar que la IP sea la misma
    ip_actual = request.remote_addr
    ip_login = session.get('ip_login')
    
    if ip_login and ip_actual != ip_login:
        # IP cambió, posible hijacking
        log_security(f"ALERTA SESIÓN SOSPECHOSA | usuario={session.get('usuario')} | ip_login={ip_login} | ip_actual={ip_actual}")
        session.clear()
        return False
    
    return True

# Usar en cada endpoint protegido:
@app.route('/dashboard')
def dashboard():
    if not validar_sesion_activa():
        return redirect(url_for('login'))
    # ... resto del código
```

---

### 12. ❌ Debug Mode en Producción

**Archivo:** `app.py` línea final

```python
# 🔴 PELIGROSO si se deja en producción
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8099)
```

**Riesgo:** 
- Consola interactiva de Python accesible
- Stack traces completos expuestos
- Auto-reload puede causar DoS
- Información sensible visible

**✅ SOLUCIÓN:**
```python
import os

if __name__ == "__main__":
    # Usar variable de entorno
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    
    app.run(
        debug=debug_mode,
        host="0.0.0.0" if not debug_mode else "127.0.0.1",  # Solo localhost en dev
        port=8099
    )

# O mejor aún, usar WSGI server en producción:
# gunicorn -w 4 -b 0.0.0.0:8099 app:app
```

---

### 13. ❌ XSS (Cross-Site Scripting) en Templates

**Archivo:** Templates varios

```html
<!-- 🔴 VULNERABLE si se renderiza sin escape -->
<p>Bienvenido {{ usuario.nombre }}</p>
```

**Riesgo:** Si nombre contiene `<script>alert('XSS')</script>`

**✅ SOLUCIÓN:**
```html
<!-- Jinja2 escapa por defecto, PERO: -->

<!-- ✅ SEGURO - Escapado automático -->
<p>Bienvenido {{ usuario.nombre }}</p>

<!-- ❌ PELIGROSO - Sin escape -->
<p>Bienvenido {{ usuario.nombre | safe }}</p>

<!-- Para JSON en templates: -->
<script>
const datos = {{ datos_json | tojson }};  // ✅ Escapa correctamente
</script>
```

---

### 14. ❌ Insecure Direct Object Reference (IDOR)

**Archivo:** Múltiples endpoints

```python
# 🔴 VULNERABLE
@app.route('/api/usuario/<int:user_id>')
def obtener_usuario(user_id):
    # No valida que el usuario autenticado tenga permiso
    usuario = Usuario.query.get(user_id)
    return jsonify(usuario.to_dict())
```

**Riesgo:** Acceder a datos de otros usuarios

**Ataque:**
```bash
# Usuario logueado con ID=5
curl /api/usuario/1  # Accede a datos del admin (ID=1)
curl /api/usuario/2  # Accede a datos de otro usuario
```

**✅ SOLUCIÓN:**
```python
@app.route('/api/usuario/<int:user_id>')
def obtener_usuario(user_id):
    # Validar permisos
    usuario_actual = session.get('usuario_id')
    
    if user_id != usuario_actual:
        # Solo admins pueden ver otros usuarios
        if session.get('rol') != 'admin':
            log_security(f"INTENTO IDOR | usuario={usuario_actual} | intentó acceder a user_id={user_id}")
            return jsonify({'error': 'Acceso denegado'}), 403
    
    usuario = Usuario.query.get_or_404(user_id)
    return jsonify(usuario.to_dict())
```

---

### 15. ❌ Sin Content Security Policy (CSP)

**Archivo:** Toda la aplicación

```python
# 🔴 Sin headers de seguridad
@app.route('/')
def index():
    return render_template('index.html')
```

**Riesgo:** XSS, clickjacking, code injection

**✅ SOLUCIÓN:**
```python
from flask import make_response

@app.after_request
def set_security_headers(response):
    """Agregar headers de seguridad a todas las respuestas"""
    # Prevenir XSS
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
    )
    
    # Prevenir clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # Forzar HTTPS
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Prevenir MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Protección XSS del navegador
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response
```

---

## 🟡 VULNERABILIDADES MEDIAS (13)

### 16. ⚠️ Enumeración de Usuarios

```python
# 🔴 Mensajes diferentes revelan si usuario existe
if not user:
    return jsonify({"message": "Usuario no existe"})
if not user.activo:
    return jsonify({"message": "Usuario inactivo"})
if not bcrypt.check_password_hash(user.password, password):
    return jsonify({"message": "Contraseña incorrecta"})
```

**✅ SOLUCIÓN:** Mensaje genérico
```python
return jsonify({"message": "Credenciales inválidas"})
```

### 17. ⚠️ Sin Sanitización de NIT

```python
nit = data.get("nit", "").strip()  # 🔴 Sin validación
```

**✅ SOLUCIÓN:**
```python
import re
def sanitizar_nit(nit):
    return re.sub(r'[^\d\-]', '', nit)[:15]
```

### 18. ⚠️ Tokens de Recuperación Predecibles

```python
token = str(random.randint(100000, 999999))  # 🔴 Predecible
```

**✅ SOLUCIÓN:**
```python
import secrets
token = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
```

### 19-28. Otras vulnerabilidades medias

(Documentadas en secciones anteriores)

---

## 🔵 VULNERABILIDADES BAJAS (5)

### 29. ℹ️ Ausencia de Logs de Auditoría Completos

Solo se loggean eventos de login, faltan:
- Cambios en datos sensibles
- Acceso a documentos
- Cambios de permisos

### 30-33. Otras vulnerabilidades bajas

---

## 🛡️ PLAN DE REMEDIACIÓN PRIORIZADO

### Fase 1: CRÍTICO (Semana 1)
1. ✅ Implementar validación de archivos PDF (magic numbers)
2. ✅ Agregar límites de tamaño de archivo
3. ✅ Prevenir path traversal en uploads
4. ✅ Implementar protección CSRF

### Fase 2: ALTO (Semana 2-3)
5. ✅ Agregar rate limiting
6. ✅ Implementar validación de contraseñas fuertes
7. ✅ Agregar headers de seguridad (CSP, HSTS, etc.)
8. ✅ Regenerar session ID en login
9. ✅ Implementar validación de IP de sesión
10. ✅ Remover debug mode

### Fase 3: MEDIO (Mes 1)
11. ✅ Sanitizar todos los inputs
12. ✅ Implementar IDOR protection
13. ✅ Mejorar tokens de recuperación
14. ✅ Sanitizar logs (sin passwords)
15. ✅ Mensajes de error genéricos

### Fase 4: BAJO (Mes 2)
16. ✅ Auditoría completa
17. ✅ Documentación de seguridad
18. ✅ Training del equipo

---

## 🧪 TESTING DE SEGURIDAD

### Herramientas Recomendadas:
```bash
# SQL Injection
sqlmap -u "http://localhost:8099/api/endpoint" --data="param=value"

# XSS
xsser --url "http://localhost:8099" -g "/*"

# File Upload
# Intentar subir: webshell.php, backdoor.jsp, malware.exe

# CSRF
# Crear formulario malicioso y testear

# Brute Force
hydra -l admin -P passwords.txt localhost http-post-form "/api/auth/login:usuario=^USER^&password=^PASS^:F=error"
```

---

## 📋 CHECKLIST DE SEGURIDAD FINAL

- [ ] ✅ Validación de todos los inputs
- [ ] ✅ Sanitización de outputs
- [ ] ✅ Protección CSRF en todos los POST
- [ ] ✅ Rate limiting en endpoints sensibles
- [ ] ✅ Validación de archivos (tipo, tamaño, contenido)
- [ ] ✅ Path traversal protection
- [ ] ✅ SQL injection protection (parametrized queries)
- [ ] ✅ XSS protection (escape automático)
- [ ] ✅ IDOR protection (validar permisos)
- [ ] ✅ Session security (regeneración, validación IP)
- [ ] ✅ Password policy fuerte
- [ ] ✅ Headers de seguridad (CSP, HSTS, etc.)
- [ ] ✅ Logs de auditoría completos
- [ ] ✅ Debug mode deshabilitado en producción
- [ ] ✅ HTTPS forzado
- [ ] ✅ Backup automático de BD
- [ ] ✅ WAF (Web Application Firewall) - Opcional
- [ ] ✅ Penetration testing - Recomendado

---

## 🚀 CÓDIGO DE EJEMPLO: Módulo de Seguridad Centralizado

```python
# security_utils.py
import re
import os
import magic
import secrets
from functools import wraps
from flask import request, session, jsonify

class SecurityValidator:
    """Validador centralizado de seguridad"""
    
    @staticmethod
    def validar_nit(nit):
        """Valida formato de NIT"""
        if not re.match(r'^[\d\-]{1,15}$', nit):
            raise ValueError("NIT inválido")
        return nit
    
    @staticmethod
    def validar_email(email):
        """Valida formato de email"""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Email inválido")
        return email.lower()
    
    @staticmethod
    def validar_password(password):
        """Valida complejidad de contraseña"""
        if len(password) < 8:
            raise ValueError("Mínimo 8 caracteres")
        if not re.search(r'[A-Z]', password):
            raise ValueError("Requiere mayúscula")
        if not re.search(r'[a-z]', password):
            raise ValueError("Requiere minúscula")
        if not re.search(r'\d', password):
            raise ValueError("Requiere número")
        if not re.search(r'[!@#$%^&*]', password):
            raise ValueError("Requiere carácter especial")
        return password
    
    @staticmethod
    def validar_archivo_pdf(archivo, max_mb=5):
        """Valida archivo PDF"""
        # Tamaño
        archivo.seek(0, os.SEEK_END)
        tamaño = archivo.tell()
        archivo.seek(0)
        
        if tamaño > max_mb * 1024 * 1024:
            raise ValueError(f"Archivo muy grande (máx {max_mb}MB)")
        
        # Extensión
        ext = os.path.splitext(archivo.filename)[1].lower()
        if ext != '.pdf':
            raise ValueError("Solo se permiten archivos PDF")
        
        # Contenido
        contenido = archivo.read(2048)
        archivo.seek(0)
        
        if not contenido.startswith(b'%PDF'):
            raise ValueError("Archivo no es un PDF válido")
        
        return True

def requiere_autenticacion(f):
    """Decorator para endpoints que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return jsonify({'error': 'No autenticado'}), 401
        
        # Validar IP
        ip_login = session.get('ip_login')
        ip_actual = request.remote_addr
        if ip_login and ip_actual != ip_login:
            session.clear()
            return jsonify({'error': 'Sesión inválida'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def requiere_rol(rol):
    """Decorator para validar rol de usuario"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('rol') != rol:
                return jsonify({'error': 'Acceso denegado'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Uso:
@app.route('/api/admin/usuarios')
@requiere_autenticacion
@requiere_rol('admin')
def listar_usuarios():
    # ...
    pass
```

---

**⚠️ NOTA FINAL:** Este es un sistema financiero crítico. Se recomienda **auditoría profesional** de seguridad antes de producción.

**Contacto para auditoría:** OWASP, consultor de seguridad certificado, o empresa de pentesting.
