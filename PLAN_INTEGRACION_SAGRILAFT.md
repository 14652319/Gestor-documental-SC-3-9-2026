# 🔧 PLAN DE INTEGRACIÓN SAGRILAFT
## Renombramientos para Evitar Conflictos

**Fecha:** 28 de enero de 2026  
**Objetivo:** Integrar módulo SAGRILAFT como `modules/sagrilaft` sin conflictos con `modules/terceros`

---

## 📊 ANÁLISIS DE CONFLICTOS

### ❌ CONFLICTOS DETECTADOS

#### 1. **TABLAS EN BASE DE DATOS**

**SAGRILAFT (Módulo Independiente):**
- `terceros` - ⚠️ **CONFLICTO** (ya existe en proyecto principal)
- `solicitudes_registro` - ✅ OK (ya existe, se reutiliza)
- `documentos_tercero` - ⚠️ **POSIBLE CONFLICTO** (nombre similar)

**PROYECTO PRINCIPAL - modules/terceros:**
- `terceros` - ⚠️ **CONFLICTO** (tabla core)
- `documentos_tercero` - ⚠️ **USADO** (tabla core)
- `estados_documentacion` - ✅ OK
- `historial_notificaciones` - ✅ OK
- `aprobaciones_documentos` - ✅ OK
- `configuracion_notificaciones` - ✅ OK

**RESULTADO:** 
- ❌ SAGRILAFT usa `terceros` (tabla core compartida)
- ✅ SAGRILAFT NO crea tablas propias, solo LEE de tablas existentes
- ✅ NO HAY CONFLICTO: SAGRILAFT es un VISOR/GESTOR de datos existentes

---

## ✅ ESTRATEGIA DE INTEGRACIÓN

### OPCIÓN ELEGIDA: **INTEGRACIÓN DIRECTA COMO `modules/sagrilaft`**

**RAZÓN:** SAGRILAFT NO tiene modelos propios conflictivos:
- Solo usa `Tercero`, `SolicitudRegistro`, `DocumentoTercero` (que YA existen)
- Es un módulo de **GESTIÓN/VISOR**, no de **CREACIÓN** de datos

### 🎯 RENOMBRAMIENTOS NECESARIOS

#### 1. **NOMBRE DEL MÓDULO**
```
✏️Gestionar Terceros/ → modules/sagrilaft/
```

**ARCHIVOS A RENOMBRAR:**
- Carpeta completa → `modules/sagrilaft/`
- Blueprint → `sagrilaft_bp` (en lugar de terceros_bp)
- URL prefix → `/sagrilaft` (en lugar de /terceros)

#### 2. **CÓDIGO PYTHON - Blueprint**

**SAGRILAFT app.py (futuro routes.py):**
```python
# ANTES:
# app = Flask(__name__)

# DESPUÉS:
from flask import Blueprint
sagrilaft_bp = Blueprint('sagrilaft', __name__, 
                         template_folder='templates',
                         static_folder='static',
                         url_prefix='/sagrilaft')
```

#### 3. **RUTAS/ENDPOINTS**

**ANTES (puerto 5001):**
```
http://localhost:5001/
http://localhost:5001/api/radicados/pendientes
http://localhost:5001/api/radicados/<radicado>/documentos
```

**DESPUÉS (integrado en puerto 8099):**
```
http://localhost:8099/sagrilaft/
http://localhost:8099/sagrilaft/api/radicados/pendientes
http://localhost:8099/sagrilaft/api/radicados/<radicado>/documentos
```

#### 4. **TEMPLATES**

**ACTUALIZAR referencias en HTML:**
```html
<!-- ANTES: -->
👥 Terceros <span>›</span> 📋 Radicados Pendientes

<!-- DESPUÉS: -->
📋 SAGRILAFT <span>›</span> 📋 Radicados Pendientes
```

**RUTAS en JavaScript:**
```javascript
// ANTES:
window.location.href = '/terceros/crear?radicado=' + radicado;

// DESPUÉS:
window.location.href = '/terceros/crear?radicado=' + radicado; 
// ✅ MANTENER: Redirige al módulo TERCEROS (correcto)
```

#### 5. **MODELOS - Importaciones**

**SAGRILAFT NO crea modelos propios, importa de app.py:**
```python
# SAGRILAFT routes.py
from extensions import db

# Importar modelos desde app.py (core)
def get_tercero_model():
    from app import Tercero
    return Tercero

def get_solicitud_model():
    from app import SolicitudRegistro
    return SolicitudRegistro

def get_documento_model():
    from app import DocumentoTercero
    return DocumentoTercero
```

**✅ NO HAY CONFLICTO:** SAGRILAFT usa modelos core existentes.

---

## 🔄 CAMBIOS REQUERIDOS

### PASO 1: COPIAR Y RENOMBRAR MÓDULO
```cmd
# 1. Copiar módulo SAGRILAFT al proyecto principal
robocopy "C:\...\✏️Gestionar Terceros" "C:\...\GESTOR_DOCUMENTAL_...\modules\sagrilaft" /E /XD __pycache__ .pytest_cache

# 2. Eliminar archivos innecesarios
del modules\sagrilaft\app.py.old
del modules\sagrilaft\*.md
```

### PASO 2: REFACTORIZAR CÓDIGO

#### A) `modules/sagrilaft/__init__.py` (NUEVO)
```python
"""
Módulo SAGRILAFT - Sistema de Gestión de Radicados
Supertiendas Cañaveral
"""
from flask import Blueprint

sagrilaft_bp = Blueprint('sagrilaft', __name__, 
                         template_folder='templates',
                         static_folder='static',
                         url_prefix='/sagrilaft')

from . import routes
```

#### B) `modules/sagrilaft/routes.py` (RENOMBRAR desde app.py)
```python
"""
Rutas del Módulo SAGRILAFT
"""
from flask import render_template, jsonify, request, send_file, session
from . import sagrilaft_bp
from extensions import db
from decoradores_permisos import requiere_permiso, requiere_permiso_html
import os

# Importar modelos desde app.py
def get_models():
    from app import Tercero, SolicitudRegistro, DocumentoTercero
    return Tercero, SolicitudRegistro, DocumentoTercero

# Ruta a documentos (usar configuración de app.py)
RUTA_DOCUMENTOS = os.path.join(os.getcwd(), 'documentos_terceros')

# ==================== ENDPOINTS ====================

@sagrilaft_bp.route('/')
@requiere_permiso_html('sagrilaft', 'acceder_modulo')
def index():
    """Lista de radicados pendientes"""
    return render_template('sagrilaft/lista_radicados.html')

@sagrilaft_bp.route('/api/radicados/pendientes')
@requiere_permiso('sagrilaft', 'consultar')
def listar_radicados_pendientes():
    """API para listar radicados pendientes"""
    try:
        Tercero, SolicitudRegistro, DocumentoTercero = get_models()
        
        # Query existente...
        radicados = SolicitudRegistro.query.filter(
            SolicitudRegistro.estado.in_(['pendiente', 'en_revision'])
        ).all()
        
        # Resto del código igual...
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### PASO 3: ACTUALIZAR app.py PRINCIPAL

#### Agregar registro del blueprint:
```python
# app.py (líneas ~2710)
from modules.sagrilaft import sagrilaft_bp
app.register_blueprint(sagrilaft_bp)  # /sagrilaft/*
```

### PASO 4: ACTUALIZAR TEMPLATES

#### `modules/sagrilaft/templates/lista_radicados.html`:
```html
<!-- Cambiar breadcrumb -->
<div class="breadcrumb">
    🏠 <a href="/">Inicio</a> <span>›</span> 
    📋 <a href="/sagrilaft">SAGRILAFT</a> <span>›</span> 
    📋 Radicados Pendientes
</div>

<!-- Actualizar URLs de APIs -->
<script>
    // ANTES: /api/radicados/pendientes
    // DESPUÉS: /sagrilaft/api/radicados/pendientes
    fetch('/sagrilaft/api/radicados/pendientes')
</script>
```

#### `modules/sagrilaft/templates/revisar_documentos.html`:
```html
<!-- Cambiar breadcrumb -->
<div class="breadcrumb">
    🏠 <a href="/">Inicio</a> <span>›</span> 
    📋 <a href="/sagrilaft">SAGRILAFT</a> <span>›</span> 
    📄 Revisar Documentos
</div>

<!-- IMPORTANTE: Redireccionamiento a módulo terceros (CORRECTO) -->
<script>
    function irACrearTercero() {
        // ✅ MANTENER: Redirige al módulo TERCEROS (no cambiar)
        window.location.href = `http://127.0.0.1:8099/terceros/crear?radicado=${radicado}`;
    }
</script>
```

### PASO 5: PERMISOS

#### Agregar permisos del módulo SAGRILAFT:
```sql
-- Insertar en catalogo_permisos
INSERT INTO catalogo_permisos (modulo, accion, descripcion, nivel_requerido) VALUES
('sagrilaft', 'acceder_modulo', 'Acceder al módulo SAGRILAFT', 'interno'),
('sagrilaft', 'consultar', 'Consultar radicados pendientes', 'interno'),
('sagrilaft', 'revisar_documentos', 'Revisar documentos de radicados', 'interno'),
('sagrilaft', 'cambiar_estado', 'Cambiar estado de radicados', 'admin'),
('sagrilaft', 'aprobar', 'Aprobar radicados', 'admin'),
('sagrilaft', 'rechazar', 'Rechazar radicados', 'admin'),
('sagrilaft', 'exportar', 'Exportar radicados a Excel', 'interno'),
('sagrilaft', 'descargar_documentos', 'Descargar documentos ZIP', 'interno');
```

---

## 🗂️ ESTRUCTURA FINAL

```
GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059/
├── app.py                                ⭐ (registra sagrilaft_bp)
├── modules/
│   ├── terceros/                         ✅ MANTENER (Nov 28, 2025)
│   │   ├── __init__.py                  # terceros_bp
│   │   ├── routes.py                    # /terceros/*
│   │   ├── models.py                    # TerceroStats, TerceroHelper
│   │   └── templates/
│   │       ├── terceros_dashboard.html
│   │       ├── terceros_consulta.html
│   │       └── tercero_crear.html       ⭐ DESTINO de SAGRILAFT
│   │
│   └── sagrilaft/                        ⭐ NUEVO (Ene 28, 2026)
│       ├── __init__.py                  # sagrilaft_bp
│       ├── routes.py                    # /sagrilaft/*
│       ├── templates/
│       │   ├── lista_radicados.html
│       │   └── revisar_documentos.html
│       └── static/
│           └── css/
│               └── styles.css
└── documentos_terceros/                  ✅ COMPARTIDO (ambos módulos)
```

---

## 🎯 RESUMEN DE RENOMBRAMIENTOS

| Componente | ANTES (SAGRILAFT Independiente) | DESPUÉS (Integrado) |
|------------|--------------------------------|---------------------|
| **Carpeta** | `✏️Gestionar Terceros/` | `modules/sagrilaft/` |
| **Blueprint** | `app = Flask()` | `sagrilaft_bp = Blueprint()` |
| **URL Prefix** | `http://localhost:5001/` | `http://localhost:8099/sagrilaft/` |
| **Endpoints** | `/api/radicados/pendientes` | `/sagrilaft/api/radicados/pendientes` |
| **Templates** | `Terceros › Radicados` | `SAGRILAFT › Radicados` |
| **Modelos** | `class Tercero(db.Model)` | Importa desde `app.py` |
| **Permisos** | N/A | `('sagrilaft', 'acceder_modulo')` |
| **Puerto** | `5001` (independiente) | `8099` (integrado) |

---

## ✅ VENTAJAS DE ESTA ESTRATEGIA

1. ✅ **Sin conflictos de nombres** - `sagrilaft` vs `terceros` son diferentes
2. ✅ **Sin duplicación de datos** - Ambos usan las MISMAS tablas core
3. ✅ **Separación clara** - SAGRILAFT = Gestión de RADs, Terceros = CRUD
4. ✅ **Integración fluida** - SAGRILAFT redirige a Terceros para crear
5. ✅ **Mantenimiento simple** - Cada módulo tiene su propósito específico
6. ✅ **Escalabilidad** - Se pueden agregar más módulos sin conflictos

---

## 🚀 PRÓXIMOS PASOS

1. **Copiar módulo** SAGRILAFT a `modules/sagrilaft/`
2. **Refactorizar** app.py → routes.py con Blueprint
3. **Actualizar** rutas en templates (prefijo `/sagrilaft`)
4. **Registrar** blueprint en app.py principal
5. **Agregar** permisos en BD
6. **Probar** integración

---

## ⚠️ ARCHIVOS A MODIFICAR

### Archivos SAGRILAFT (antes de mover):
- [ ] `app.py` → Convertir a `routes.py` con Blueprint
- [ ] `templates/*.html` → Actualizar breadcrumbs y URLs
- [ ] Crear `__init__.py` con blueprint

### Archivos Proyecto Principal:
- [ ] `app.py` → Agregar registro de `sagrilaft_bp`
- [ ] SQL → Agregar permisos del módulo SAGRILAFT
- [ ] `.github/copilot-instructions.md` → Documentar nuevo módulo

---

**COMPLEJIDAD:** ⭐⭐⭐ MEDIA  
**TIEMPO ESTIMADO:** 1-2 horas  
**RIESGO:** BAJO (solo renombramientos, sin cambios de lógica)

---

**NOTA IMPORTANTE:** 
SAGRILAFT NO crea modelos propios, solo IMPORTA modelos de app.py.
Por lo tanto, NO hay conflictos de tablas, solo de nombres de módulo/blueprint.
