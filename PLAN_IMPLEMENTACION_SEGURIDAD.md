# 🚀 PLAN DE IMPLEMENTACIÓN DE SEGURIDAD
## Gestor Documental - Supertiendas Cañaveral

**Fecha de inicio:** 9 de Diciembre, 2025  
**Duración estimada:** 4 semanas  
**Estado:** 📋 Planificado

---

## 📊 RESUMEN DE VULNERABILIDADES

| Prioridad | Cantidad | Estimación | Responsable |
|-----------|----------|------------|-------------|
| 🔴 **CRÍTICO** | 3 | 1 semana | Equipo completo |
| 🟠 **ALTO** | 12 | 2 semanas | Desarrollador senior |
| 🟡 **MEDIO** | 13 | 1 semana | Desarrollador junior |
| 🔵 **BAJO** | 5 | Mejora continua | QA/Testing |
| **TOTAL** | **33** | **4 semanas** | |

---

## 🎯 FASE 1: VULNERABILIDADES CRÍTICAS (Semana 1)

### 🔴 PRIORIDAD 1: File Upload Security (Días 1-2)

**Vulnerabilidad:** Arbitrary file upload sin validación de contenido  
**Impacto:** Ejecución remota de código  
**Archivos afectados:**
- `app.py` línea 1707 (api_cargar_documentos)
- `modules/facturas_digitales/routes.py` línea 1568
- `modules/notas_contables/routes.py` línea 890

**✅ IMPLEMENTACIÓN:**

```python
# 1. Instalar dependencia
# pip install python-magic-bin  # Windows
# pip install python-magic       # Linux

# 2. Agregar a app.py (INICIO DEL ARCHIVO)
from security_utils import FileValidator, SecurityValidator

# 3. Modificar TODOS los endpoints de upload
@app.route("/api/documentos/upload", methods=["POST"])
def api_cargar_documentos():
    try:
        # ... código existente ...
        
        # ✅ AGREGAR VALIDACIÓN ANTES DE GUARDAR
        for tipo_doc in TIPOS_DOCUMENTOS:
            archivo = request.files.get(f"doc_{tipo_doc}")
            
            if archivo and archivo.filename:
                # 🛡️ VALIDACIÓN CRÍTICA
                FileValidator.validar_archivo_pdf(archivo, max_mb=5)
                
                # 🛡️ SANITIZAR NOMBRE
                nombre_archivo = FileValidator.sanitizar_nombre_archivo(archivo.filename)
                nombre_final = f"{nit}-TEMP-{fecha_carpeta}_{tipo_doc}.pdf"
                
                # 🛡️ VALIDAR PATH TRAVERSAL
                ruta_archivo = os.path.join(ruta_completa, nombre_final)
                ruta_archivo = FileValidator.validar_ruta_segura(ruta_completa, ruta_archivo)
                
                # Ahora sí guardar
                archivo.save(ruta_archivo)
                log_security(f"ARCHIVO VALIDADO Y GUARDADO | tipo={tipo_doc} | tamaño={tamaño} | nit={nit}")
        
        return jsonify({"success": True})
        
    except ValueError as e:
        log_security(f"ERROR VALIDACIÓN ARCHIVO | error={str(e)} | ip={request.remote_addr}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        log_security(f"ERROR UPLOAD | error={str(e)}")
        return jsonify({"error": "Error al procesar archivo"}), 500
```

**📋 CHECKLIST:**
- [ ] Instalar python-magic
- [ ] Importar security_utils en app.py
- [ ] Modificar api_cargar_documentos() en app.py
- [ ] Modificar cargar_archivo_pdf() en facturas_digitales/routes.py
- [ ] Modificar cargar_documentos_nota() en notas_contables/routes.py
- [ ] Agregar límite global: `app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024`
- [ ] Testear upload de: PDF válido, .exe renombrado, archivo gigante
- [ ] Verificar logs de seguridad

**🧪 TESTING:**
```bash
# Test 1: PDF válido (debe pasar)
curl -X POST -F "doc_RUT=@documento_valido.pdf" http://localhost:8099/api/documentos/upload

# Test 2: EXE renombrado (debe rechazar)
copy malware.exe fake.pdf
curl -X POST -F "doc_RUT=@fake.pdf" http://localhost:8099/api/documentos/upload
# Esperado: HTTP 400 "Archivo no es un PDF válido"

# Test 3: Archivo gigante (debe rechazar)
fsutil file createnew gigante.pdf 20000000  # 20MB
curl -X POST -F "doc_RUT=@gigante.pdf" http://localhost:8099/api/documentos/upload
# Esperado: HTTP 400 "Archivo muy grande"

# Test 4: Path traversal (debe rechazar)
curl -X POST -F "doc_RUT=@../../evil.pdf" http://localhost:8099/api/documentos/upload
# Esperado: HTTP 400 "Intento de path traversal detectado"
```

---

### 🔴 PRIORIDAD 2: CSRF Protection (Días 3-4)

**Vulnerabilidad:** Sin protección CSRF en ningún endpoint POST  
**Impacto:** Ataques de falsificación de peticiones  
**Archivos afectados:** Toda la aplicación

**✅ IMPLEMENTACIÓN:**

```python
# 1. Instalar dependencia
# pip install flask-wtf

# 2. Configurar en app.py (después de crear app)
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# Configuración de cookies seguras
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # Solo HTTPS en producción
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

# Excluir solo el endpoint de login (usa su propia validación)
@csrf.exempt
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    # ... código existente
    pass

# 3. Agregar token en todos los templates
# templates/login.html (agregar en <head>)
<meta name="csrf-token" content="{{ csrf_token() }}">

# 4. Agregar en JavaScript (para fetch/AJAX)
// Función global para obtener CSRF token
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').content;
}

// Usar en todos los fetch POST
fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify(data)
});

// Para FormData
const formData = new FormData();
formData.append('csrf_token', getCSRFToken());
```

**📋 CHECKLIST:**
- [ ] Instalar flask-wtf
- [ ] Configurar CSRFProtect en app.py
- [ ] Agregar meta tag en login.html
- [ ] Agregar meta tag en nueva_factura_REFACTORED.html
- [ ] Agregar meta tag en orden_compra.html
- [ ] Agregar meta tag en generar_relacion_REFACTORED.html
- [ ] Crear función getCSRFToken() global en JavaScript
- [ ] Modificar TODOS los fetch() POST para incluir X-CSRFToken
- [ ] Testear cada formulario: login, registro, upload, etc.
- [ ] Verificar que endpoints rechacen peticiones sin CSRF token

**🧪 TESTING:**
```bash
# Test 1: Petición sin CSRF token (debe rechazar)
curl -X POST http://localhost:8099/api/registro/proveedor \
     -H "Content-Type: application/json" \
     -d '{"nit":"123456"}'
# Esperado: HTTP 400 "CSRF token missing"

# Test 2: Petición con token inválido (debe rechazar)
curl -X POST http://localhost:8099/api/registro/proveedor \
     -H "Content-Type: application/json" \
     -H "X-CSRFToken: token_falso" \
     -d '{"nit":"123456"}'
# Esperado: HTTP 400 "CSRF token invalid"

# Test 3: Login debe funcionar (exempt)
curl -X POST http://localhost:8099/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"usuario":"test","password":"test"}'
# Esperado: HTTP 200 (funciona sin CSRF)
```

---

### 🔴 PRIORIDAD 3: SQL Injection (Día 5)

**Vulnerabilidad:** F-string concatenation en queries dinámicas  
**Impacto:** Acceso/modificación no autorizada de datos  
**Archivos afectados:**
- `modules/admin/usuarios_permisos/routes.py` línea 539

**✅ IMPLEMENTACIÓN:**

```python
# ANTES (VULNERABLE):
query = text(f"UPDATE usuarios SET {', '.join(updates)} WHERE id = :id")

# DESPUÉS (SEGURO):
# Opción 1: Usar ORM (RECOMENDADO)
from app import Usuario

@usuarios_permisos_bp.route('/api/admin/usuarios/<int:user_id>', methods=['PUT'])
@requiere_autenticacion
@requiere_rol('admin')
def actualizar_usuario(user_id):
    try:
        data = request.get_json()
        
        # Buscar usuario con ORM
        usuario = Usuario.query.get_or_404(user_id)
        
        # Whitelist de campos permitidos
        CAMPOS_PERMITIDOS = ['nombre', 'correo', 'telefono', 'activo', 'rol']
        
        # Actualizar solo campos permitidos
        for campo, valor in data.items():
            if campo in CAMPOS_PERMITIDOS:
                if hasattr(usuario, campo):
                    setattr(usuario, campo, valor)
        
        db.session.commit()
        log_security(f"USUARIO ACTUALIZADO | id={user_id} | campos={list(data.keys())}")
        
        return jsonify({"success": True})
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR ACTUALIZAR USUARIO | error={str(e)}")
        return jsonify({"error": "Error al actualizar usuario"}), 500

# Opción 2: Si DEBES usar SQL dinámico (NO recomendado)
CAMPOS_PERMITIDOS = {
    'nombre': str,
    'correo': str,
    'telefono': str,
    'activo': bool,
    'rol': str
}

def validar_campo_update(campo, valor):
    """Valida que el campo esté en whitelist"""
    if campo not in CAMPOS_PERMITIDOS:
        raise ValueError(f"Campo no permitido: {campo}")
    
    # Validar tipo
    tipo_esperado = CAMPOS_PERMITIDOS[campo]
    if not isinstance(valor, tipo_esperado):
        raise ValueError(f"Tipo incorrecto para {campo}")
    
    return True

# Construir query segura
updates = []
params = {'id': user_id}

for i, (campo, valor) in enumerate(data.items()):
    validar_campo_update(campo, valor)
    updates.append(f"{campo} = :val{i}")
    params[f'val{i}'] = valor

query = text(f"UPDATE usuarios SET {', '.join(updates)} WHERE id = :id")
db.session.execute(query, params)
```

**📋 CHECKLIST:**
- [ ] Refactorizar actualizar_usuario() para usar ORM
- [ ] Crear whitelist de campos permitidos
- [ ] Agregar validación de tipos de datos
- [ ] Testear actualización con campos válidos
- [ ] Testear rechazo de campos no permitidos
- [ ] Verificar logs de intentos sospechosos

**🧪 TESTING:**
```bash
# Test 1: Actualización válida (debe pasar)
curl -X PUT http://localhost:8099/api/admin/usuarios/5 \
     -H "Content-Type: application/json" \
     -d '{"nombre":"Juan Perez"}'
# Esperado: HTTP 200

# Test 2: Intento de SQL injection (debe rechazar)
curl -X PUT http://localhost:8099/api/admin/usuarios/5 \
     -H "Content-Type: application/json" \
     -d '{"rol":"admin; DROP TABLE usuarios;--"}'
# Esperado: HTTP 400 "Campo no permitido"

# Test 3: Campo no permitido (debe rechazar)
curl -X PUT http://localhost:8099/api/admin/usuarios/5 \
     -H "Content-Type: application/json" \
     -d '{"password":"nueva123"}'
# Esperado: HTTP 400 "Campo no permitido"
```

---

## 🎯 FASE 2: VULNERABILIDADES ALTAS (Semana 2-3)

### 🟠 PRIORIDAD 4: Rate Limiting (Días 6-7)

**Vulnerabilidad:** Sin límites de peticiones  
**Impacto:** Brute force de contraseñas, DoS  

**✅ IMPLEMENTACIÓN:**

```python
# 1. Instalar dependencia
# pip install flask-limiter redis  # O sin Redis: flask-limiter[memcached]

# 2. Configurar en app.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # O redis://localhost:6379 si tienes Redis
)

# 3. Aplicar límites estrictos a endpoints sensibles
@app.route("/api/auth/login", methods=["POST"])
@limiter.limit("5 per minute")
@limiter.limit("20 per hour")
def api_login():
    # ... código existente
    pass

@app.route("/api/auth/forgot_request", methods=["POST"])
@limiter.limit("3 per hour")
@limiter.limit("10 per day")
def forgot_request():
    # ... código existente
    pass

@app.route("/api/registro/proveedor", methods=["POST"])
@limiter.limit("10 per hour")
def registro_proveedor():
    # ... código existente
    pass

@app.route("/api/documentos/upload", methods=["POST"])
@limiter.limit("50 per hour")
def api_cargar_documentos():
    # ... código existente
    pass

# 4. Personalizar respuesta de límite excedido
@app.errorhandler(429)
def ratelimit_handler(e):
    log_security(f"RATE LIMIT EXCEDIDO | ip={request.remote_addr} | endpoint={request.endpoint}")
    return jsonify({
        "error": "Demasiadas peticiones. Intente de nuevo en unos minutos."
    }), 429
```

**📋 CHECKLIST:**
- [ ] Instalar flask-limiter
- [ ] Configurar Limiter en app.py
- [ ] Aplicar límites a /api/auth/login
- [ ] Aplicar límites a /api/auth/forgot_request
- [ ] Aplicar límites a /api/registro/*
- [ ] Aplicar límites a /api/documentos/upload
- [ ] Configurar handler de error 429
- [ ] Testear con script de peticiones masivas
- [ ] Verificar logs de rate limiting

---

### 🟠 PRIORIDAD 5: Session Security (Días 8-9)

**Vulnerabilidad:** Session fixation, sin validación de IP  
**Impacto:** Session hijacking  

**✅ IMPLEMENTACIÓN:**

```python
# 1. Regenerar session ID en login
@app.route("/api/auth/login", methods=["POST"])
def api_login():
    # ... validar credenciales ...
    
    if user and bcrypt.check_password_hash(user.password, password):
        # 🛡️ LIMPIAR SESIÓN ANTIGUA
        session.clear()
        
        # 🛡️ REGENERAR SESSION ID
        session.permanent = True
        session.new = True
        
        # Guardar datos de sesión
        session['usuario_id'] = user.id
        session['usuario'] = user.usuario
        session['nit'] = user.tercero.nit if user.tercero else None
        session['rol'] = user.rol
        
        # 🛡️ GUARDAR IP DE LOGIN
        session['ip_login'] = request.remote_addr
        session['user_agent'] = request.headers.get('User-Agent', '')
        
        log_security(f"LOGIN EXITOSO | usuario={user.usuario} | ip={request.remote_addr}")
        return jsonify({"success": True})

# 2. Crear decorator de validación de sesión
from security_utils import requiere_autenticacion

# 3. Aplicar a TODOS los endpoints protegidos
@app.route('/dashboard')
@requiere_autenticacion
def dashboard():
    # ... código existente
    pass

@app.route('/api/facturas/nueva')
@requiere_autenticacion
def nueva_factura():
    # ... código existente
    pass

# El decorator ya valida:
# - Sesión activa
# - IP no cambió
# - Usuario activo en BD
```

**📋 CHECKLIST:**
- [ ] Modificar api_login() para regenerar session
- [ ] Guardar ip_login y user_agent en session
- [ ] Importar requiere_autenticacion de security_utils
- [ ] Aplicar decorator a todos los endpoints protegidos (50+)
- [ ] Testear login + acceso a dashboard
- [ ] Testear que cambio de IP cierre sesión
- [ ] Verificar logs de sesiones sospechosas

---

### 🟠 PRIORIDAD 6-15: Otras vulnerabilidades altas

(Seguir patrón similar para las 10 vulnerabilidades altas restantes)

---

## 🎯 FASE 3: VULNERABILIDADES MEDIAS (Semana 3)

### 🟡 Input Sanitization (Días 15-17)

**Implementar validación en TODOS los endpoints que reciban datos de usuario:**

```python
from security_utils import SecurityValidator

@app.route('/api/registro/proveedor', methods=['POST'])
def registro_proveedor():
    try:
        data = request.get_json()
        
        # 🛡️ VALIDAR TODOS LOS INPUTS
        nit = SecurityValidator.validar_nit(data.get('nit', ''))
        email = SecurityValidator.validar_email(data.get('correo', ''))
        nombre = SecurityValidator.validar_nombre(data.get('razon_social', ''))
        telefono = SecurityValidator.validar_telefono(data.get('celular', ''))
        
        # Procesar con datos validados
        # ...
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
```

**📋 CHECKLIST:**
- [ ] Validar NITs en TODOS los endpoints
- [ ] Validar emails en TODOS los endpoints
- [ ] Validar teléfonos
- [ ] Validar nombres/razones sociales
- [ ] Validar fechas
- [ ] Validar IDs (enteros positivos)
- [ ] Testear cada validación

---

## 🎯 FASE 4: VULNERABILIDADES BAJAS (Semana 4)

### 🔵 Auditoría y Mejoras Continuas

- [ ] Implementar auditoría completa de acciones
- [ ] Agregar Content Security Policy headers
- [ ] Implementar HSTS (HTTPS forzado)
- [ ] Crear dashboard de seguridad
- [ ] Training del equipo

---

## 📊 TRACKING DE PROGRESO

| Semana | Fase | Tareas | Completado | Pendiente |
|--------|------|--------|------------|-----------|
| 1 | CRÍTICO | File Upload, CSRF, SQL Injection | 0/3 | 3 |
| 2 | ALTO (1-6) | Rate Limit, Session, etc. | 0/6 | 6 |
| 3 | ALTO (7-12) + MEDIO | Input validation, etc. | 0/13 | 13 |
| 4 | BAJO | Auditoría, training | 0/5 | 5 |
| **TOTAL** | | | **0/27** | **27** |

---

## 🧪 TESTING FINAL

```bash
# Script de testing completo
python test_security.py

# Tests individuales:
pytest tests/test_file_upload_security.py
pytest tests/test_csrf_protection.py
pytest tests/test_sql_injection.py
pytest tests/test_rate_limiting.py
pytest tests/test_session_security.py
pytest tests/test_input_validation.py
```

---

## 📝 DOCUMENTACIÓN GENERADA

1. ✅ `AUDITORIA_SEGURIDAD_COMPLETA.md` - Análisis completo
2. ✅ `security_utils.py` - Módulo de utilidades
3. ✅ `PLAN_IMPLEMENTACION_SEGURIDAD.md` - Este archivo
4. 📋 `TESTING_SEGURIDAD.md` - Suite de tests (por crear)
5. 📋 `MANUAL_SEGURIDAD_EQUIPO.md` - Training (por crear)

---

## 🚨 NOTAS IMPORTANTES

1. **NO hacer cambios masivos sin testing:** Implementar prioridad por prioridad
2. **Backup antes de cada cambio:** `python backup_manager.py`
3. **Testing en desarrollo primero:** NO tocar producción sin validar
4. **Logs de auditoría:** Verificar logs después de cada cambio
5. **Comunicar al equipo:** Coordinar despliegues

---

## 👥 RESPONSABLES

| Tarea | Responsable | Contacto |
|-------|-------------|----------|
| File Upload Security | Developer Senior | |
| CSRF Protection | Developer Senior | |
| SQL Injection Fix | Developer Senior | |
| Rate Limiting | Developer Mid | |
| Session Security | Developer Mid | |
| Input Validation | Developer Junior | |
| Testing | QA Team | |
| Documentación | Tech Lead | |

---

## 📞 CONTACTO

**Dudas o problemas durante implementación:**
- Revisar `AUDITORIA_SEGURIDAD_COMPLETA.md`
- Consultar ejemplos en `security_utils.py`
- Verificar logs en `logs/security.log`

---

**⚠️ URGENTE:** Sistema maneja datos financieros sensibles. Priorizar semana 1 (CRÍTICO).
