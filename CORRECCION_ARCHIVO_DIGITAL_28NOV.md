# 🔒 CORRECCIÓN APLICADA - ARCHIVO DIGITAL BLOQUEADO

## Fecha: 28 de Noviembre 2025, 00:20

## ❌ Problema Identificado:

El usuario 14652319 podía acceder a:
- `/archivo_digital/cargar` ✅ 200 (acceso permitido - NO DEBERÍA)
- `/archivo_digital/visor` ✅ 200 (acceso permitido - NO DEBERÍA)

**Causa raíz:** El módulo `archivo_digital` NO tenía decoradores `@requiere_permiso_html`.

## ✅ Corrección Aplicada:

**Archivo modificado:** `modules/notas_contables/pages.py`

### 1. Importación agregada:
```python
from decoradores_permisos import requiere_permiso_html
```

### 2. Decoradores agregados a 3 rutas:

#### Ruta /cargar (línea 27):
```python
@archivo_digital_pages_bp.route('/cargar')
@requiere_permiso_html('archivo_digital', 'acceder_modulo')  ← NUEVO
def cargar_documento():
```

#### Ruta /visor (línea 36):
```python
@archivo_digital_pages_bp.route('/visor')
@requiere_permiso_html('archivo_digital', 'acceder_modulo')  ← NUEVO
def visor_documentos():
```

#### Ruta /editar (línea 92):
```python
@archivo_digital_pages_bp.route('/editar/<int:documento_id>')
@requiere_permiso_html('archivo_digital', 'acceder_modulo')  ← NUEVO
def editar_documento(documento_id):
```

## 🔍 Validación de Permisos en BD:

Usuario 14652319 (ID: 22):
- `archivo_digital.acceder_modulo`: **FALSE** ❌
- `archivo_digital.cargar_documento`: **FALSE** ❌
- `archivo_digital.ver_documento`: **FALSE** ❌

## 📋 Resultado Esperado:

Después de que Flask recargue automáticamente (modo debug):

| URL | Antes | Después |
|-----|-------|---------|
| `/archivo_digital/cargar` | 200 OK ✅ | 302 Redirect ❌ + Flash message |
| `/archivo_digital/visor` | 200 OK ✅ | 302 Redirect ❌ + Flash message |
| `/causaciones/` | 200 OK ✅ | 200 OK ✅ (único permitido) |
| `/recibir_facturas/` | 302 ❌ | 302 ❌ |
| `/facturas_digitales/` | 302 ❌ | 302 ❌ |

## 🧪 Prueba Ahora:

1. **Refrescar el navegador** (F5) en cualquier página que tengas abierta
2. **Intentar acceder:**
   - `/archivo_digital/cargar` → Debe bloquear ❌
   - `/archivo_digital/visor` → Debe bloquear ❌
   - `/causaciones/` → Debe funcionar ✅

## ⚙️ Auto-reload de Flask:

El servidor detectará el cambio automáticamente:
```
INFO:werkzeug: * Detected change in 'modules/notas_contables/pages.py', reloading
INFO:werkzeug: * Restarting with stat
```

---

**Estado:** ✅ Corrección aplicada, esperando validación del usuario
