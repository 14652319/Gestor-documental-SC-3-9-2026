# MEJORAS AL FORMULARIO DE CREACIÓN DE TERCEROS

**Fecha**: 30 de enero de 2026  
**Módulo**: Terceros (integrado con SAGRILAFT)  
**Archivo**: `templates/tercero_crear.html`

---

## 📋 PROBLEMAS IDENTIFICADOS Y RESUELTOS

### ❌ PROBLEMA 1: Formulario Muy Pequeño
**Antes:**
- Formulario con márgenes grandes
- Mucho espacio desperdiciado
- Difícil de usar en pantallas grandes

**✅ SOLUCIÓN:**
```css
.contenedor {
    max-width: 95%;      /* Antes: 1200px fijo */
    padding: 1.5rem;     /* Antes: 2rem */
}
```
- Formulario ocupa 95% del ancho de pantalla
- Márgenes reducidos para aprovechar espacio
- Mejor experiencia visual

---

### ❌ PROBLEMA 2: Falta Usuario Logueado
**Antes:**
- No aparecía qué usuario estaba usando el sistema
- Falta de contexto

**✅ SOLUCIÓN:**
```html
<div class="header-usuario">
    <div class="header-titulo">📋 Crear Nuevo Tercero</div>
    <div class="header-info">
        <div class="usuario-badge">
            👤 {{ usuario }}
        </div>
        <a href="/sagrilaft" class="btn-volver">← Volver</a>
    </div>
</div>
```
- Header fijo superior con nombre del usuario
- Badge con icono de usuario
- Botón de volver siempre visible

---

### ❌ PROBLEMA 3: Datos No Vienen Prellenados
**Antes:**
- Formulario completamente vacío
- Usuario tenía que escribir TODO manualmente
- Datos ya existían en BD del registro de SAGRILAFT

**✅ SOLUCIÓN:**

**Backend - Nuevo Endpoint:**
```python
# modules/terceros/routes.py

@terceros_bp.route('/api/obtener_datos_radicado/<radicado>')
def obtener_datos_radicado(radicado):
    """Obtiene datos del tercero asociado a un radicado"""
    solicitud = SolicitudRegistro.query.filter_by(radicado=radicado).first()
    tercero = Tercero.query.get(solicitud.tercero_id)
    
    return jsonify({
        'success': True,
        'tercero': {
            'nit': tercero.nit,
            'tipo_persona': tercero.tipo_persona,
            'razon_social': tercero.razon_social,
            'primer_nombre': tercero.primer_nombre,
            'segundo_nombre': tercero.segundo_nombre,
            'primer_apellido': tercero.primer_apellido,
            'segundo_apellido': tercero.segundo_apellido,
            'correo': tercero.correo,
            'telefono': tercero.telefono,
            'direccion': tercero.direccion,
            'ciudad': tercero.ciudad,
            'departamento': tercero.departamento
        }
    })
```

**Frontend - Carga Automática:**
```javascript
async function cargarDatosRadicado() {
    const response = await fetch(`/terceros/api/obtener_datos_radicado/${radicadoActual}`);
    const data = await response.json();
    
    // Llenar todos los campos del formulario
    document.getElementById('nit').value = data.tercero.nit;
    document.getElementById('tipo_persona').value = data.tercero.tipo_persona;
    document.getElementById('correo').value = data.tercero.correo;
    // ... etc
    
    mostrarCamposSegunTipo(data.tercero.tipo_persona);
}
```

---

### ❌ PROBLEMA 4: Falta Campo Tipo Persona
**Antes:**
- No preguntaba si era persona natural o jurídica
- Campos mezclados sin lógica

**✅ SOLUCIÓN:**
```html
<select id="tipo_persona" required>
    <option value="">Seleccione...</option>
    <option value="juridica">Persona Jurídica</option>
    <option value="natural">Persona Natural</option>
</select>
```

**Lógica Dinámica:**
```javascript
function mostrarCamposSegunTipo(tipo) {
    if (tipo === 'natural') {
        // Mostrar: primer_nombre, segundo_nombre, primer_apellido, segundo_apellido
        // Ocultar: razon_social
    } else {
        // Mostrar: razon_social
        // Ocultar: nombres y apellidos
    }
}
```

**Persona Jurídica:**
- ✅ Razón Social (requerido)
- ❌ Nombres y apellidos ocultos

**Persona Natural:**
- ✅ Primer Nombre (requerido)
- ✅ Segundo Nombre (opcional)
- ✅ Primer Apellido (requerido)
- ✅ Segundo Apellido (opcional)
- ❌ Razón social oculta

---

### ❌ PROBLEMA 5: Faltan Campos Importantes
**Antes:**
- Solo: NIT, Razón Social, Correo, Teléfono
- Faltaba: Dirección, Ciudad, Departamento

**✅ SOLUCIÓN:**
```html
<!-- INFORMACIÓN DE CONTACTO -->
<div class="campo-grupo campo-full">
    <label class="campo-label requerido">Dirección</label>
    <input type="text" id="direccion" required>
</div>

<div class="campo-grupo">
    <label class="campo-label requerido">Ciudad</label>
    <input type="text" id="ciudad" required>
</div>

<div class="campo-grupo">
    <label class="campo-label">Departamento</label>
    <input type="text" id="departamento">
</div>

<div class="campo-grupo">
    <label class="campo-label requerido">Estado Inicial</label>
    <select id="estado_inicial" required>
        <option value="inactivo">Inactivo (Por defecto)</option>
        <option value="activo">Activo</option>
    </select>
</div>
```

---

## 🎨 MEJORAS VISUALES

### Grid de 2 Columnas
**Antes**: 1 columna (desperdicio de espacio)  
**Ahora**: 2 columnas con campos completos cuando es necesario

```css
.grid-campos {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
}

.campo-full {
    grid-column: 1 / -1;  /* Ocupa ambas columnas */
}
```

### Alertas de Estado
```html
<div class="alerta alerta-info">
    Cargando datos del radicado...
</div>

<div class="alerta alerta-success">
    ✅ Tercero creado exitosamente
</div>

<div class="alerta alerta-error">
    Error al procesar la solicitud
</div>
```

---

## 📊 FLUJO COMPLETO

### 1. Usuario en SAGRILAFT
```
http://127.0.0.1:8099/sagrilaft
   ↓
Click en RAD-031854 (estado APROBADO)
   ↓
Click en botón "Crear Tercero"
```

### 2. Redirección con Radicado
```
http://127.0.0.1:8099/terceros/crear?radicado=RAD-031854
```

### 3. Carga Automática de Datos
```javascript
// Al cargar la página
if (radicadoActual) {
    cargarDatosRadicado();  // ← Carga automática
}
```

### 4. Endpoint Consulta Datos
```
GET /terceros/api/obtener_datos_radicado/RAD-031854
   ↓
Busca solicitud en BD
   ↓
Obtiene tercero asociado
   ↓
Retorna JSON con TODOS los datos
```

### 5. Formulario Prellenado
```
✅ NIT: 1465318
✅ Tipo Persona: natural/juridica
✅ Nombres o Razón Social (según tipo)
✅ Correo
✅ Teléfono
✅ Dirección
✅ Ciudad
✅ Departamento
```

### 6. Usuario Puede Modificar
- Todos los campos son editables (excepto NIT)
- Puede cambiar tipo de persona
- Campos se adaptan dinámicamente

### 7. Guardar Tercero
```
POST /terceros/api/crear
   ↓
Valida datos
   ↓
Crea registro en tabla terceros
   ↓
Retorna success
   ↓
Redirige a /sagrilaft
```

---

## 🔄 CAMBIOS EN ARCHIVOS

### 1. `modules/terceros/routes.py`
**Línea agregada**: ~236-310

```python
@terceros_bp.route('/api/obtener_datos_radicado/<radicado>')
def obtener_datos_radicado(radicado):
    # Consulta BD y retorna datos del tercero
```

### 2. `templates/tercero_crear.html`
**Archivo COMPLETAMENTE REESCRITO**

**Backup creado**: `tercero_crear_BACKUP_20260130_XXXXXX.html`

**Cambios principales**:
- Header con usuario
- CSS responsivo mejorado
- Grid de 2 columnas
- Campos dinámicos según tipo persona
- Carga automática de datos
- Validaciones mejoradas
- Alertas de estado

---

## 📝 VALIDACIONES

### Formulario
- ✅ NIT requerido (readonly cuando viene de radicado)
- ✅ Tipo Persona requerido
- ✅ Nombres/Razón Social según tipo
- ✅ Correo con formato email
- ✅ Teléfono requerido
- ✅ Dirección requerida
- ✅ Ciudad requerida

### JavaScript
```javascript
if (tipoPersona === 'natural') {
    if (!primer_nombre || !primer_apellido) {
        mostrarAlerta('error', 'Nombres y apellido requeridos');
        return;
    }
} else {
    if (!razon_social) {
        mostrarAlerta('error', 'Razón social requerida');
        return;
    }
}
```

---

## 🎯 PRUEBAS

### Caso 1: Persona Jurídica
1. Ir a `/terceros/crear?radicado=RAD-031854`
2. Seleccionar "Persona Jurídica"
3. Ver campo "Razón Social" visible
4. Nombres y apellidos ocultos
5. Llenar datos y guardar

### Caso 2: Persona Natural
1. Ir a `/terceros/crear?radicado=RAD-031857`
2. Seleccionar "Persona Natural"
3. Ver campos de nombres y apellidos visibles
4. Razón social oculta
5. Llenar datos y guardar

### Caso 3: Sin Radicado
1. Ir a `/terceros/crear` (sin parámetro)
2. Formulario vacío
3. Usuario debe llenar todo manualmente
4. Funciona normalmente

---

## ✅ CHECKLIST DE CORRECCIONES

- [x] Formulario más grande (95% ancho)
- [x] Márgenes reducidos (1.5rem)
- [x] Header con usuario logueado
- [x] Carga automática de datos desde radicado
- [x] Campo tipo_persona (natural/jurídica)
- [x] Campos dinámicos según tipo
- [x] Primer Nombre (para natural)
- [x] Segundo Nombre (para natural)
- [x] Primer Apellido (para natural)
- [x] Segundo Apellido (para natural)
- [x] Razón Social (para jurídica)
- [x] Campo Dirección
- [x] Campo Ciudad
- [x] Campo Departamento
- [x] Campo Estado Inicial
- [x] Grid de 2 columnas
- [x] Validaciones mejoradas
- [x] Alertas de éxito/error
- [x] Botón volver a SAGRILAFT

---

## 🚀 PRÓXIMOS PASOS

1. **Reiniciar servidor**:
   ```cmd
   python app.py
   ```

2. **Probar formulario**:
   - Ir a SAGRILAFT
   - Seleccionar RAD con estado APROBADO
   - Click en "Crear Tercero"
   - Verificar carga automática de datos

3. **Validar guardado**:
   - Modificar datos si es necesario
   - Click en "Guardar Tercero"
   - Verificar creación en BD

---

## 📞 SOPORTE

Si encuentras algún problema:
1. Verifica que el servidor esté corriendo
2. Revisa logs en consola
3. Verifica que el radicado exista en BD
4. Consulta backup si necesitas versión anterior

**Backup disponible**: `templates/tercero_crear_BACKUP_*.html`

---

**FIN DEL DOCUMENTO**
