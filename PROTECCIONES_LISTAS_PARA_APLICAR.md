# 🛡️ PROTECCIONES LISTAS PARA APLICAR
## Sistema: Gestor Documental - Supertiendas Cañaveral

**Fecha de documentación:** 10 de Diciembre, 2025  
**Estado:** ✅ LISTO PARA APLICAR (cuando se solicite)

---

## ⚠️ IMPORTANTE: INSTRUCCIONES ANTES DE APLICAR

### 🔄 BACKUP OBLIGATORIO
```powershell
# Ejecutar ANTES de aplicar cualquier protección:
python backup_manager.py
# O copiar carpeta completa:
Copy-Item -Path "." -Destination "../BACKUP_ANTES_PROTECCIONES_$(Get-Date -Format 'yyyyMMdd_HHmmss')" -Recurse
```

### 📝 ORDEN DE APLICACIÓN RECOMENDADO
1. Protección 1: Rate Limiting (más simple, sin dependencias)
2. Protección 2: Validación de archivos (requiere validar python-magic)
3. Protección 3: Sanitización de inputs (modificaciones en app.py)
4. Protección 4: CSRF (requiere instalar flask-wtf)

---

## 🔒 PROTECCIÓN 1: RATE LIMITING (SIN INSTALAR NADA)

### ✅ Archivos a modificar:
- `app.py` (agregar sistema de control de intentos)

### 📝 Código a agregar en app.py:

**UBICACIÓN:** Después de las importaciones (línea ~30)

```python
# ==================== SISTEMA DE RATE LIMITING ====================
from datetime import datetime, timedelta
from collections import defaultdict

# Diccionario para rastrear intentos por IP
intentos_por_ip = defaultdict(list)

def verificar_rate_limit(ip, max_intentos=5, ventana_minutos=1):
    """
    Verifica si una IP ha excedido el límite de intentos
    
    Args:
        ip (str): Dirección IP a verificar
        max_intentos (int): Número máximo de intentos permitidos
        ventana_minutos (int): Ventana de tiempo en minutos
        
    Returns:
        tuple: (permitido: bool, intentos_restantes: int)
    """
    ahora = datetime.now()
    ventana = timedelta(minutes=ventana_minutos)
    
    # Limpiar intentos antiguos fuera de la ventana
    intentos_por_ip[ip] = [
        timestamp for timestamp in intentos_por_ip[ip]
        if ahora - timestamp < ventana
    ]
    
    # Verificar si excede el límite
    intentos_actuales = len(intentos_por_ip[ip])
    
    if intentos_actuales >= max_intentos:
        return False, 0
    
    # Registrar este intento
    intentos_por_ip[ip].append(ahora)
    
    return True, max_intentos - intentos_actuales - 1
```

### 📝 Modificaciones en endpoint de login:

**BUSCAR en app.py (línea ~1156):**
```python
@app.route('/api/auth/login', methods=['POST'])
def api_login():
```

**REEMPLAZAR con:**
```python
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    ip = request.remote_addr
    
    # 🛡️ VERIFICAR RATE LIMIT
    permitido, intentos_restantes = verificar_rate_limit(ip, max_intentos=5, ventana_minutos=1)
    
    if not permitido:
        log_security(f"RATE LIMIT EXCEDIDO | ip={ip} | endpoint=login")
        return jsonify({
            "success": False,
            "message": "Demasiados intentos. Espere 1 minuto antes de reintentar."
        }), 429
    
    # ... RESTO DEL CÓDIGO EXISTENTE (sin cambios)
```

### 📝 Aplicar también a:

**Endpoint de recuperación de contraseña (línea ~1200):**
```python
@app.route('/api/auth/forgot_request', methods=['POST'])
def forgot_request():
    ip = request.remote_addr
    
    # 🛡️ VERIFICAR RATE LIMIT (más restrictivo)
    permitido, intentos_restantes = verificar_rate_limit(ip, max_intentos=3, ventana_minutos=60)
    
    if not permitido:
        log_security(f"RATE LIMIT EXCEDIDO | ip={ip} | endpoint=forgot_request")
        return jsonify({
            "success": False,
            "message": "Demasiadas solicitudes. Espere 1 hora antes de reintentar."
        }), 429
    
    # ... RESTO DEL CÓDIGO EXISTENTE
```

**Endpoint de registro (línea ~1500):**
```python
@app.route('/api/registro/proveedor', methods=['POST'])
def registro_proveedor():
    ip = request.remote_addr
    
    # 🛡️ VERIFICAR RATE LIMIT
    permitido, intentos_restantes = verificar_rate_limit(ip, max_intentos=10, ventana_minutos=60)
    
    if not permitido:
        log_security(f"RATE LIMIT EXCEDIDO | ip={ip} | endpoint=registro")
        return jsonify({
            "success": False,
            "message": "Demasiados registros desde esta IP. Espere 1 hora."
        }), 429
    
    # ... RESTO DEL CÓDIGO EXISTENTE
```

### ✅ Testing después de aplicar:
```powershell
# Test 1: Login normal (debe funcionar)
curl -X POST http://localhost:8099/api/auth/login -H "Content-Type: application/json" -d '{\"usuario\":\"test\",\"password\":\"test\"}'

# Test 2: 6 intentos rápidos (6to debe fallar)
for ($i=1; $i -le 6; $i++) {
    Write-Host "Intento $i"
    curl -X POST http://localhost:8099/api/auth/login -H "Content-Type: application/json" -d '{\"usuario\":\"test\",\"password\":\"test\"}'
}
# Esperado: Primeros 5 funcionan, 6to retorna HTTP 429
```

---

## 🔒 PROTECCIÓN 2: VALIDACIÓN DE ARCHIVOS PDF (SIN LIBRERÍAS EXTERNAS)

### ✅ Archivos a modificar:
- `app.py` (función de validación + endpoint de upload)

### 📝 Código a agregar en app.py:

**UBICACIÓN:** Después del sistema de rate limiting (línea ~100)

```python
# ==================== VALIDACIÓN DE ARCHIVOS ====================
def validar_archivo_pdf_seguro(archivo, max_mb=5):
    """
    Valida que un archivo sea realmente un PDF válido
    
    Args:
        archivo (FileStorage): Archivo subido
        max_mb (int): Tamaño máximo en MB
        
    Returns:
        tuple: (valido: bool, error: str, tamaño: int)
    """
    try:
        # 1. Verificar que el archivo existe
        if not archivo or not archivo.filename:
            return False, "Archivo no proporcionado", 0
        
        # 2. Verificar extensión
        if not archivo.filename.lower().endswith('.pdf'):
            return False, "Solo se permiten archivos PDF", 0
        
        # 3. Verificar tamaño
        archivo.seek(0, 2)  # Ir al final
        tamaño = archivo.tell()
        archivo.seek(0)  # Volver al inicio
        
        if tamaño == 0:
            return False, "Archivo vacío", 0
        
        max_bytes = max_mb * 1024 * 1024
        if tamaño > max_bytes:
            tamaño_mb = tamaño / 1024 / 1024
            return False, f"Archivo muy grande: {tamaño_mb:.2f}MB (máx {max_mb}MB)", tamaño
        
        # 4. Verificar firma PDF (magic number)
        contenido_inicio = archivo.read(2048)
        archivo.seek(0)
        
        if not contenido_inicio.startswith(b'%PDF'):
            return False, "Archivo no es un PDF válido (firma incorrecta)", tamaño
        
        # 5. Verificar que no contenga JavaScript malicioso
        contenido_muestra = contenido_inicio.lower()
        if b'/js' in contenido_muestra or b'/javascript' in contenido_muestra:
            return False, "PDF contiene JavaScript (no permitido por seguridad)", tamaño
        
        return True, "OK", tamaño
        
    except Exception as e:
        return False, f"Error al validar archivo: {str(e)}", 0

def sanitizar_nombre_archivo(nombre_archivo):
    """
    Sanitiza nombre de archivo para prevenir path traversal
    
    Args:
        nombre_archivo (str): Nombre original del archivo
        
    Returns:
        str: Nombre sanitizado
    """
    import re
    
    # Remover caracteres peligrosos
    nombre = os.path.basename(nombre_archivo)  # Quitar path
    nombre = re.sub(r'[^\w\s\-\.]', '_', nombre)  # Solo alfanuméricos, espacios, guiones, puntos
    nombre = nombre[:255]  # Limitar longitud
    
    return nombre

def validar_ruta_segura(ruta_base, ruta_archivo):
    """
    Previene path traversal validando que la ruta esté dentro del directorio permitido
    
    Args:
        ruta_base (str): Directorio base permitido
        ruta_archivo (str): Ruta del archivo a validar
        
    Returns:
        tuple: (valido: bool, ruta_absoluta: str)
    """
    # Convertir a rutas absolutas
    ruta_base_abs = os.path.abspath(ruta_base)
    ruta_archivo_abs = os.path.abspath(ruta_archivo)
    
    # Verificar que la ruta del archivo esté dentro de la ruta base
    if not ruta_archivo_abs.startswith(ruta_base_abs):
        return False, None
    
    return True, ruta_archivo_abs
```

### 📝 Modificar endpoint de carga de documentos:

**BUSCAR en app.py (línea ~1707):**
```python
@app.route('/api/documentos/upload', methods=['POST'])
@app.route('/api/registro/cargar_documentos', methods=['POST'])
def api_cargar_documentos():
```

**BUSCAR el bloque donde se guardan archivos (línea ~1740):**
```python
for tipo_doc in TIPOS_DOCUMENTOS:
    archivo = request.files.get(f"doc_{tipo_doc}")
    if archivo and archivo.filename:
        nombre_archivo = f"{nit}-TEMP-{fecha_carpeta}_{tipo_doc}.pdf"
        ruta_archivo = os.path.join(ruta_completa, nombre_archivo)
        archivo.save(ruta_archivo)
```

**REEMPLAZAR con:**
```python
for tipo_doc in TIPOS_DOCUMENTOS:
    archivo = request.files.get(f"doc_{tipo_doc}")
    if archivo and archivo.filename:
        # 🛡️ VALIDAR ARCHIVO PDF
        valido, error, tamaño = validar_archivo_pdf_seguro(archivo, max_mb=5)
        
        if not valido:
            log_security(f"ARCHIVO RECHAZADO | tipo={tipo_doc} | error={error} | ip={request.remote_addr} | nit={nit}")
            return jsonify({
                "success": False,
                "message": f"Error en {tipo_doc}: {error}"
            }), 400
        
        # 🛡️ SANITIZAR NOMBRE
        nombre_original_seguro = sanitizar_nombre_archivo(archivo.filename)
        nombre_archivo = f"{nit}-TEMP-{fecha_carpeta}_{tipo_doc}.pdf"
        
        # 🛡️ VALIDAR PATH TRAVERSAL
        ruta_archivo = os.path.join(ruta_completa, nombre_archivo)
        valido_path, ruta_segura = validar_ruta_segura(ruta_completa, ruta_archivo)
        
        if not valido_path:
            log_security(f"INTENTO PATH TRAVERSAL | tipo={tipo_doc} | ip={request.remote_addr} | nit={nit}")
            return jsonify({
                "success": False,
                "message": "Intento de acceso no autorizado detectado"
            }), 403
        
        # 🛡️ GUARDAR ARCHIVO (ahora es seguro)
        archivo.save(ruta_segura)
        log_security(f"ARCHIVO VALIDADO Y GUARDADO | tipo={tipo_doc} | tamaño={tamaño} bytes | nit={nit}")
        
        # Resto del código existente...
```

### ✅ Testing después de aplicar:
```powershell
# Test 1: PDF válido (debe funcionar)
curl -X POST http://localhost:8099/api/documentos/upload -F "doc_RUT=@documento_valido.pdf"
# Esperado: HTTP 200

# Test 2: Archivo .exe renombrado (debe rechazar)
Copy-Item "C:\Windows\System32\notepad.exe" "fake.pdf"
curl -X POST http://localhost:8099/api/documentos/upload -F "doc_RUT=@fake.pdf"
# Esperado: HTTP 400 "Archivo no es un PDF válido"

# Test 3: Archivo muy grande (debe rechazar)
fsutil file createnew gigante.pdf 10485760  # 10MB
curl -X POST http://localhost:8099/api/documentos/upload -F "doc_RUT=@gigante.pdf"
# Esperado: HTTP 400 "Archivo muy grande"

# Test 4: Path traversal (debe rechazar)
curl -X POST http://localhost:8099/api/documentos/upload -F "doc_RUT=@../../sistema.pdf"
# Esperado: HTTP 403 "Intento de acceso no autorizado"
```

---

## 🔒 PROTECCIÓN 3: SANITIZACIÓN DE INPUTS

### ✅ Archivos a modificar:
- `app.py` (agregar funciones de validación)

### 📝 Código a agregar en app.py:

**UBICACIÓN:** Después de las funciones de validación de archivos (línea ~200)

```python
# ==================== VALIDACIÓN DE INPUTS ====================
import re

def validar_nit_seguro(nit):
    """Valida formato de NIT colombiano"""
    if not nit:
        raise ValueError("NIT no puede estar vacío")
    
    nit = str(nit).strip()
    
    # Solo números y guiones
    if not re.match(r'^[\d\-]{1,15}$', nit):
        raise ValueError("NIT debe contener solo números y guiones (máx 15 caracteres)")
    
    # Al menos 5 dígitos
    digitos = re.sub(r'[^\d]', '', nit)
    if len(digitos) < 5:
        raise ValueError("NIT debe tener al menos 5 dígitos")
    
    return nit

def validar_email_seguro(email):
    """Valida formato de email"""
    if not email:
        raise ValueError("Email no puede estar vacío")
    
    email = str(email).strip().lower()
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError("Formato de email inválido")
    
    if len(email) > 254:
        raise ValueError("Email demasiado largo")
    
    return email

def validar_telefono_seguro(telefono):
    """Valida número de teléfono"""
    if not telefono:
        raise ValueError("Teléfono no puede estar vacío")
    
    telefono = str(telefono).strip()
    telefono = re.sub(r'[^\d\+]', '', telefono)
    
    if telefono.startswith('+57'):
        telefono = telefono[3:]
    
    if not re.match(r'^\d{7,10}$', telefono):
        raise ValueError("Teléfono debe tener entre 7 y 10 dígitos")
    
    return telefono

def validar_nombre_seguro(nombre, max_length=255):
    """Valida nombre de persona/empresa"""
    if not nombre:
        raise ValueError("Nombre no puede estar vacío")
    
    nombre = str(nombre).strip()
    
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\.\-\']+$', nombre):
        raise ValueError("Nombre contiene caracteres no permitidos")
    
    if len(nombre) < 2:
        raise ValueError("Nombre demasiado corto (mín 2 caracteres)")
    
    if len(nombre) > max_length:
        raise ValueError(f"Nombre demasiado largo (máx {max_length} caracteres)")
    
    return nombre

def validar_id_seguro(id_value, nombre_campo="ID"):
    """Valida que un ID sea un entero positivo"""
    try:
        id_int = int(id_value)
    except (TypeError, ValueError):
        raise ValueError(f"{nombre_campo} debe ser un número entero")
    
    if id_int <= 0:
        raise ValueError(f"{nombre_campo} debe ser mayor a 0")
    
    if id_int > 2147483647:
        raise ValueError(f"{nombre_campo} demasiado grande")
    
    return id_int
```

### 📝 Modificar endpoint de registro:

**BUSCAR en app.py (línea ~1500):**
```python
@app.route('/api/registro/proveedor', methods=['POST'])
def registro_proveedor():
    data = request.get_json()
    nit = data.get('nit', '').strip()
    razon_social = data.get('razon_social', '').strip()
    correo = data.get('correo', '').strip()
```

**REEMPLAZAR con:**
```python
@app.route('/api/registro/proveedor', methods=['POST'])
def registro_proveedor():
    try:
        data = request.get_json()
        
        # 🛡️ VALIDAR TODOS LOS INPUTS
        nit = validar_nit_seguro(data.get('nit', ''))
        razon_social = validar_nombre_seguro(data.get('razon_social', ''))
        correo = validar_email_seguro(data.get('correo', ''))
        
        if data.get('celular'):
            celular = validar_telefono_seguro(data.get('celular', ''))
        else:
            celular = None
        
        # ... RESTO DEL CÓDIGO EXISTENTE (usar variables validadas)
        
    except ValueError as e:
        log_security(f"INPUT INVÁLIDO | endpoint=registro | error={str(e)} | ip={request.remote_addr}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
```

### 📝 Modificar endpoint de login:

**BUSCAR en app.py (línea ~1156, después del rate limit):**
```python
data = request.get_json()
nit_input = data.get("nit", "").strip()
usuario_alias = data.get("usuario", "").strip().lower()
```

**REEMPLAZAR con:**
```python
try:
    data = request.get_json()
    
    # 🛡️ VALIDAR INPUTS
    nit_input = validar_nit_seguro(data.get("nit", ""))
    usuario_alias = str(data.get("usuario", "")).strip().lower()
    
    if not usuario_alias or len(usuario_alias) < 3:
        raise ValueError("Usuario debe tener al menos 3 caracteres")
    
    if len(usuario_alias) > 50:
        raise ValueError("Usuario demasiado largo")
    
except ValueError as e:
    log_security(f"INPUT INVÁLIDO | endpoint=login | error={str(e)} | ip={request.remote_addr}")
    return jsonify({
        "success": False,
        "message": "Datos de entrada inválidos"
    }), 400

# ... RESTO DEL CÓDIGO EXISTENTE
```

### ✅ Testing después de aplicar:
```powershell
# Test 1: Registro con datos válidos (debe funcionar)
curl -X POST http://localhost:8099/api/registro/proveedor -H "Content-Type: application/json" -d '{\"nit\":\"805028041\",\"razon_social\":\"Empresa Test\",\"correo\":\"test@test.com\"}'

# Test 2: NIT con SQL injection (debe rechazar)
curl -X POST http://localhost:8099/api/registro/proveedor -H "Content-Type: application/json" -d '{\"nit\":\"123\\'; DROP TABLE usuarios;--\",\"razon_social\":\"Test\"}'
# Esperado: HTTP 400 "NIT debe contener solo números"

# Test 3: Email inválido (debe rechazar)
curl -X POST http://localhost:8099/api/registro/proveedor -H "Content-Type: application/json" -d '{\"nit\":\"123456\",\"correo\":\"no-es-email\"}'
# Esperado: HTTP 400 "Formato de email inválido"
```

---

## 🔒 PROTECCIÓN 4: CSRF (REQUIERE INSTALAR FLASK-WTF)

### ⚠️ IMPORTANTE: Solo aplicar si están dispuestos a instalar una librería

### 📦 Instalación requerida:
```powershell
pip install flask-wtf
```

### ✅ Archivos a modificar:
- `app.py` (configuración CSRF)
- `templates/login.html` (agregar meta tag)
- `templates/facturas_digitales/nueva_factura_REFACTORED.html` (agregar meta tag)
- `templates/facturas_digitales/orden_compra.html` (agregar meta tag)
- Todos los archivos JavaScript que hagan fetch POST

### 📝 Código a agregar en app.py:

**UBICACIÓN:** Después de crear la app (línea ~50)

```python
# ==================== PROTECCIÓN CSRF ====================
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# Configuración de cookies seguras
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
# Solo en producción con HTTPS:
# app.config['SESSION_COOKIE_SECURE'] = True

# Excluir solo el endpoint de login (usa validación propia)
@csrf.exempt
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    # ... código existente
    pass
```

### 📝 Agregar en templates:

**En `templates/login.html`** (dentro de `<head>`):
```html
<meta name="csrf-token" content="{{ csrf_token() }}">
```

**En todos los archivos JavaScript** (buscar todos los `fetch` con método POST):

**BUSCAR:**
```javascript
fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});
```

**REEMPLAZAR con:**
```javascript
// Función global para obtener CSRF token
function getCSRFToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : '';
}

fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify(data)
});
```

### ✅ Testing después de aplicar:
```powershell
# Test 1: Petición con token válido (debe funcionar)
# Abrir navegador → hacer login → crear factura
# Esperado: Funciona normal

# Test 2: Petición sin token (debe rechazar)
curl -X POST http://localhost:8099/api/registro/proveedor -H "Content-Type: application/json" -d '{\"nit\":\"123\"}'
# Esperado: HTTP 400 "CSRF token missing"
```

---

## 📊 RESUMEN DE PROTECCIONES DOCUMENTADAS

| # | Protección | Instalar algo | Complejidad | Impacto |
|---|-----------|---------------|-------------|---------|
| 1 | Rate Limiting | ❌ NO | 🟢 Baja | Previene fuerza bruta |
| 2 | Validación PDFs | ❌ NO | 🟡 Media | Previene malware |
| 3 | Sanitización | ❌ NO | 🟡 Media | Previene injections |
| 4 | CSRF | ✅ flask-wtf | 🔴 Alta | Previene ataques externos |

---

## 🚀 COMANDO PARA APLICAR TODO (CUANDO LO SOLICITES)

```powershell
# 1. Hacer backup
python backup_manager.py

# 2. Aplicar protecciones 1, 2 y 3 (sin instalar nada)
# Te daré los comandos específicos cuando lo solicites

# 3. Si quieres CSRF, instalar y aplicar:
pip install flask-wtf
# Luego aplicar cambios documentados arriba
```

---

## ✅ CHECKLIST DE VERIFICACIÓN POST-APLICACIÓN

- [ ] Backup creado exitosamente
- [ ] Rate limiting funciona (probar 6 logins rápidos)
- [ ] Validación PDF funciona (probar .exe renombrado)
- [ ] Sanitización funciona (probar SQL injection en NIT)
- [ ] Login sigue funcionando normal
- [ ] Registro sigue funcionando normal
- [ ] Upload de documentos sigue funcionando
- [ ] Logs muestran intentos bloqueados
- [ ] No hay errores en consola del navegador

---

**📌 NOTA FINAL:** Este documento contiene TODO lo necesario para aplicar las protecciones. Cuando digas "apliquemos la protección", tomaré este documento y aplicaré los cambios exactos aquí documentados.
