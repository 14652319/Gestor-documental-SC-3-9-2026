# 🔒 SEGURIDAD: Protección contra SQL Injection

**Fecha:** 9 de Diciembre, 2025  
**Sistema:** Gestor Documental - Supertiendas Cañaveral

---

## ✅ CÓDIGO SEGURO ACTUAL (Lo que está bien)

### 1. **Uso de Parámetros Nombrados** ⭐ CORRECTO

**Archivo:** `modules/facturas_digitales/routes.py`

```python
# ✅ SEGURO: Uso de parámetros nombrados con :parametro
@facturas_digitales_bp.route('/api/ordenes-compra/buscar-tercero/<nit>')
def buscar_tercero_ocr(nit):
    tercero = Tercero.query.filter_by(nit=nit).first()  # ✅ ORM seguro
```

**¿Por qué es seguro?**
- SQLAlchemy ORM escapa automáticamente los valores
- `filter_by()` usa parámetros internos que previenen inyección

---

### 2. **Text() con Parámetros Explícitos** ⭐ CORRECTO

```python
# ✅ SEGURO: Parámetros nombrados
result = db.session.execute(text("""
    SELECT id, codigo, nombre 
    FROM centros_operacion
    WHERE codigo = :codigo
"""), {'codigo': codigo_usuario})
```

**¿Por qué es seguro?**
- Los valores se pasan por separado del SQL
- SQLAlchemy escapa automáticamente los valores
- No hay concatenación de strings

---

## 🔴 VULNERABILIDADES ENCONTRADAS

### ❌ VULNERABILIDAD #1: Concatenación con f-strings

**Archivo:** `modules/admin/usuarios_permisos/routes.py` (línea 539)

```python
# 🔴 VULNERABLE
query = text(f"UPDATE usuarios SET {', '.join(updates)} WHERE id = :id")
```

**Ataque posible:**
```python
# Si un atacante controla el contenido de 'updates':
updates = ["password = 'hacked'); DROP TABLE usuarios; --"]

# Query resultante:
"UPDATE usuarios SET password = 'hacked'); DROP TABLE usuarios; -- WHERE id = :id"
```

**✅ SOLUCIÓN:**
```python
# Validar columnas permitidas
COLUMNAS_PERMITIDAS = ['nombre', 'email', 'activo', 'tipo_usuario']
updates_seguros = []
params = {'id': user_id}

for key, value in datos.items():
    if key in COLUMNAS_PERMITIDAS:
        updates_seguros.append(f"{key} = :{key}")
        params[key] = value

query = text(f"UPDATE usuarios SET {', '.join(updates_seguros)} WHERE id = :id")
db.session.execute(query, params)
```

---

### ❌ VULNERABILIDAD #2: Nombres de Tabla Dinámicos

**Archivos:** Múltiples scripts de migración

```python
# 🔴 VULNERABLE
result = db.session.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
```

**Ataque posible:**
```python
# Si 'tabla' viene del usuario:
tabla = "usuarios; DROP TABLE terceros; --"

# Query resultante:
"SELECT COUNT(*) FROM usuarios; DROP TABLE terceros; --"
```

**✅ SOLUCIÓN:**
```python
# Whitelist de tablas válidas
TABLAS_VALIDAS = ['usuarios', 'terceros', 'centros_operacion']

def consultar_tabla_segura(nombre_tabla):
    if nombre_tabla not in TABLAS_VALIDAS:
        raise ValueError(f"Tabla no permitida: {nombre_tabla}")
    
    # Usar comillas dobles para identifiers en PostgreSQL
    query = text(f'SELECT COUNT(*) FROM "{nombre_tabla}"')
    return db.session.execute(query)
```

---

### ❌ VULNERABILIDAD #3: Input del Usuario sin Validar

**Ejemplo genérico:**
```python
# 🔴 VULNERABLE
nit_usuario = request.args.get('nit')
query = text(f"SELECT * FROM terceros WHERE nit = '{nit_usuario}'")
```

**Ataque posible:**
```
GET /api/buscar?nit=' OR '1'='1
Query: SELECT * FROM terceros WHERE nit = '' OR '1'='1'
Resultado: Retorna TODOS los terceros
```

**✅ SOLUCIÓN:**
```python
# Usar parámetros nombrados
nit_usuario = request.args.get('nit')
query = text("SELECT * FROM terceros WHERE nit = :nit")
result = db.session.execute(query, {'nit': nit_usuario})
```

---

## 🛡️ REGLAS DE ORO PARA PREVENCIÓN

### 1. ⭐ **NUNCA concatenar input del usuario directamente**

```python
# ❌ NUNCA HACER ESTO
query = f"SELECT * FROM usuarios WHERE id = {user_id}"

# ✅ HACER ESTO
query = text("SELECT * FROM usuarios WHERE id = :id")
db.session.execute(query, {'id': user_id})
```

---

### 2. ⭐ **Usar ORM cuando sea posible**

```python
# ✅ PREFERIR ORM
usuario = Usuario.query.filter_by(nit=nit).first()

# En lugar de SQL crudo:
# ❌ query = text(f"SELECT * FROM usuarios WHERE nit = '{nit}'")
```

---

### 3. ⭐ **Validar SIEMPRE los inputs**

```python
import re

def validar_nit(nit):
    # Solo números y guiones
    if not re.match(r'^[\d\-]+$', nit):
        raise ValueError("NIT inválido")
    return nit

# Uso:
nit = validar_nit(request.args.get('nit'))
```

---

### 4. ⭐ **Usar Whitelist para nombres de tabla/columna**

```python
# Si necesitas nombres dinámicos:
COLUMNAS_PERMITIDAS = ['nombre', 'email', 'activo']

def validar_columna(columna):
    if columna not in COLUMNAS_PERMITIDAS:
        raise ValueError(f"Columna no permitida: {columna}")
    return columna
```

---

## 🔍 AUDITORÍA DEL CÓDIGO ACTUAL

### Archivos a revisar URGENTEMENTE:

1. **`modules/admin/usuarios_permisos/routes.py`**
   - Línea 539: Concatenación con f-string en UPDATE
   - ⚠️ **PRIORIDAD ALTA**

2. **Scripts de migración:**
   - `buscar_tabla_permisos_correcta.py`
   - `crear_tablas_monitoreo.py`
   - `verificar_tablas_monitoreo.py`
   - ⚠️ **PRIORIDAD MEDIA** (son scripts administrativos, no endpoints públicos)

3. **`agregar_columnas_permisos_usuarios.py`**
   - Línea 41: Nombres de columna dinámicos
   - ⚠️ **PRIORIDAD MEDIA**

---

## 🧪 CÓMO PROBAR VULNERABILIDADES

### Test 1: SQL Injection básico
```bash
# Intenta buscar con:
NIT: ' OR '1'='1

# Si el sistema retorna datos sin validar el NIT, es vulnerable
```

### Test 2: Comentario SQL
```bash
# Intenta:
NIT: 123456789--

# Si el -- comenta el resto de la query, es vulnerable
```

### Test 3: UNION Attack
```bash
# Intenta:
NIT: 123' UNION SELECT password FROM usuarios--

# Si retorna passwords, es MUY vulnerable
```

---

## ✅ CÓDIGO DE EJEMPLO SEGURO COMPLETO

```python
from sqlalchemy import text
import re

# 1. Validación de inputs
def validar_nit(nit):
    """Solo permite números y guiones"""
    if not re.match(r'^[\d\-]+$', nit):
        raise ValueError("Formato de NIT inválido")
    return nit

def validar_email(email):
    """Valida formato de email"""
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise ValueError("Formato de email inválido")
    return email

# 2. Endpoint seguro
@app.route('/api/buscar-tercero')
def buscar_tercero_seguro():
    try:
        # Validar input
        nit = validar_nit(request.args.get('nit', ''))
        
        # Opción 1: Usar ORM (PREFERIDO)
        tercero = Tercero.query.filter_by(nit=nit).first()
        
        # Opción 2: SQL con parámetros nombrados
        result = db.session.execute(
            text("SELECT * FROM terceros WHERE nit = :nit"),
            {'nit': nit}
        )
        
        return jsonify({'success': True, 'data': tercero})
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        log_security(f"ERROR búsqueda tercero | error={str(e)}")
        return jsonify({'error': 'Error interno'}), 500

# 3. Update seguro con validación
@app.route('/api/actualizar-usuario', methods=['POST'])
def actualizar_usuario_seguro():
    COLUMNAS_PERMITIDAS = ['nombre', 'email', 'activo']
    
    user_id = request.json.get('id')
    datos = request.json.get('datos', {})
    
    # Construir UPDATE seguro
    updates = []
    params = {'id': user_id}
    
    for key, value in datos.items():
        if key in COLUMNAS_PERMITIDAS:
            updates.append(f"{key} = :{key}")
            params[key] = value
    
    if not updates:
        return jsonify({'error': 'No hay campos válidos para actualizar'}), 400
    
    query = text(f"UPDATE usuarios SET {', '.join(updates)} WHERE id = :id")
    db.session.execute(query, params)
    db.session.commit()
    
    return jsonify({'success': True})
```

---

## 📋 CHECKLIST DE SEGURIDAD

- [ ] ✅ Todos los inputs validados con regex/whitelist
- [ ] ✅ Uso de parámetros nombrados (`:parametro`) en vez de f-strings
- [ ] ✅ ORM preferido sobre SQL crudo
- [ ] ✅ Nombres de tabla validados con whitelist
- [ ] ✅ Logs de seguridad para intentos sospechosos
- [ ] ✅ Rate limiting en endpoints sensibles
- [ ] ✅ Autenticación verificada en todos los endpoints
- [ ] ✅ Prepared statements en TODAS las queries

---

## 🚨 ACCIÓN INMEDIATA RECOMENDADA

### 1. **Crear función de sanitización global**

```python
# utils_seguridad.py
import re

def sanitizar_nit(nit):
    """Solo números y guiones, máximo 15 caracteres"""
    nit = re.sub(r'[^\d\-]', '', nit)
    return nit[:15]

def sanitizar_nombre(nombre):
    """Solo letras, espacios y tildes"""
    return re.sub(r'[^a-záéíóúñA-ZÁÉÍÓÚÑ\s]', '', nombre)

def sanitizar_email(email):
    """Validación básica de email"""
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise ValueError("Email inválido")
    return email.lower()
```

### 2. **Aplicar en TODOS los endpoints**

```python
from utils_seguridad import sanitizar_nit, sanitizar_email

@app.route('/api/registro')
def registro():
    nit = sanitizar_nit(request.json.get('nit'))
    email = sanitizar_email(request.json.get('email'))
    # ... resto del código
```

---

## 📚 REFERENCIAS

- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/core/tutorial.html#using-textual-sql)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/sql-prepare.html)

---

**⚠️ IMPORTANTE:** Este es un sistema financiero crítico. La seguridad debe ser **PRIORIDAD #1**.

**Recomendación:** Realizar auditoría de seguridad completa antes de producción.
