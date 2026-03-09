# 🚨 PROBLEMA IDENTIFICADO - RUTAS SIN PROTECCIÓN

## Situación Actual

### ✅ Migración Completada
- Tabla `permisos_usuario` (singular) renombrada a `permisos_usuario_backup_20251127`
- 25 registros únicos migrados exitosamente
- Tabla activa: `permisos_usuarios` (plural) con 612 registros
- Decoradores actualizados para usar tabla correcta

### ❌ PROBLEMA CRÍTICO: RUTAS SIN DECORADORES

El análisis reveló que **0 de 167 rutas** tienen decoradores de permisos correctamente aplicados.

#### Módulos CON Decoradores (Protegidos):
- ✅ `modules/relaciones/routes.py` - 10+ decoradores
- ✅ `modules/admin/usuarios_permisos/routes.py` - 12+ decoradores
- ✅ `modules/admin/monitoreo/routes.py` - 8+ decoradores
- ✅ `modules/causaciones/routes.py` - 1 decorador (solo acceder_modulo)

#### Módulos SIN Decoradores (Vulnerables):
- ❌ `app.py` - `/dashboard` accesible sin permisos
- ❌ `modules/facturas_digitales/routes.py` - TODO sin proteger
- ❌ `modules/recibir_facturas/routes.py` - Algunos endpoints sin decorador
- ❌ `modules/configuracion/routes.py` - TODO sin proteger
- ❌ `modules/notas_contables/routes.py` - TODO sin proteger

### Por Qué Usuario 14652319 Puede Acceder a Todo

**Usuario 14652319 tiene:**
- ✅ 1 permiso activo: `causaciones.acceder_modulo = TRUE`
- ❌ 141 permisos inactivos (FALSE)

**PERO puede acceder a:**
- `/dashboard` - NO tiene decorador ❌
- `/archivo_digital/cargar` - NO tiene decorador ❌
- `/facturas-digitales/` - NO tiene decorador ❌
- `/causaciones/` - ✅ Tiene decorador (funcionaría correctamente)

**Módulos que SÍ lo bloquean correctamente:**
- `/recibir_facturas/nueva_factura` - ✅ Tiene decorador → Redirige a /dashboard
- `/relaciones/generar_relacion` - ✅ Tiene decorador → Redirige a /dashboard
- `/admin/usuarios-permisos/` - ✅ Tiene decorador → Redirige a /dashboard
- `/admin/monitoreo/` - ✅ Tiene decorador → Redirige a /dashboard

---

## Solución Requerida

### 1. Agregar Decoradores a Rutas Principales

#### app.py - Dashboard
```python
from decoradores_permisos import requiere_permiso_html

@app.route("/dashboard")
@requiere_permiso_html('admin', 'ver_dashboard')  # O crear permiso 'dashboard.acceder'
def dashboard():
    ...
```

#### modules/facturas_digitales/routes.py
```python
from decoradores_permisos import requiere_permiso_html, requiere_permiso

@facturas_digitales_bp.route('/')
@facturas_digitales_bp.route('/dashboard')
@requiere_permiso_html('facturas_digitales', 'acceder_modulo')
def dashboard_facturas():
    ...

@facturas_digitales_bp.route('/cargar')
@requiere_permiso_html('facturas_digitales', 'cargar_factura')
def cargar():
    ...
```

#### modules/notas_contables/routes.py
```python
from decoradores_permisos import requiere_permiso, requiere_permiso_html

# Agregar @requiere_permiso_html o @requiere_permiso a TODAS las rutas
```

### 2. Estrategia de Implementación

**Opción A: Permiso General por Módulo** (Recomendado para inicio rápido)
- Agregar solo `@requiere_permiso_html('modulo', 'acceder_modulo')` en la ruta principal
- Ejemplo: Si entra a `/facturas-digitales/`, necesita `facturas_digitales.acceder_modulo`

**Opción B: Permisos Granulares** (Mayor seguridad)
- Cada acción requiere permiso específico
- Ejemplo: 
  - `/facturas-digitales/` → `facturas_digitales.acceder_modulo`
  - `/facturas-digitales/cargar` → `facturas_digitales.cargar_factura`
  - `/facturas-digitales/editar/<id>` → `facturas_digitales.editar_factura`

### 3. Prioridad de Implementación

**Prioridad ALTA:**
1. `/dashboard` en app.py
2. `/facturas-digitales/*` en facturas_digitales/routes.py
3. `/archivo_digital/*` en notas_contables/routes.py
4. `/configuracion/*` en configuracion/routes.py

**Prioridad MEDIA:**
5. Revisar `causaciones/routes.py` (tiene 1 decorador, completar el resto)
6. Revisar `recibir_facturas/routes.py` (algunos tienen, otros no)

**Prioridad BAJA:**
7. Endpoints de API internos que ya validan sesión manualmente

---

## ¿Cómo Agregar Decoradores?

### Paso 1: Importar el decorador
```python
from decoradores_permisos import requiere_permiso_html, requiere_permiso
```

### Paso 2: Aplicar en la ruta
```python
# Para vistas HTML (retorna redirect si falla)
@bp.route('/ruta')
@requiere_permiso_html('modulo', 'accion')
def mi_vista():
    # Ya no necesitas validar sesión aquí
    ...

# Para APIs JSON (retorna 403 si falla)
@bp.route('/api/ruta')
@requiere_permiso('modulo', 'accion')
def mi_api():
    # Ya no necesitas validar sesión aquí
    ...
```

### Paso 3: Eliminar validaciones manuales redundantes
```python
# ❌ ANTES (redundante si usas decorador)
if 'usuario_id' not in session:
    return redirect('/login')

# ✅ DESPUÉS (el decorador ya lo hace)
@requiere_permiso_html('modulo', 'accion')
def mi_vista():
    # El decorador ya validó sesión y permisos
    ...
```

---

## Resumen Ejecutivo

**Estado Actual:**
- ✅ Sistema de permisos funcional (tabla migrada)
- ✅ Decoradores implementados correctamente
- ❌ Decoradores NO aplicados en rutas (0 de 167 protegidas)

**Impacto:**
- Usuario con 1 solo permiso puede acceder a TODO
- Configuración de permisos en UI no tiene efecto real

**Acción Inmediata:**
1. Agregar `@requiere_permiso_html` a `/dashboard` en app.py
2. Agregar `@requiere_permiso_html` a rutas principales de módulos sin protección
3. Probar con usuario 14652319 que ahora SÍ sea bloqueado

**Tiempo Estimado:** 2-3 horas para proteger los 4 módulos principales
