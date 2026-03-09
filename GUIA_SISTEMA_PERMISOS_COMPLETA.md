# 🎯 SISTEMA DE PERMISOS - GUÍA COMPLETA

## Fecha: 28 de Noviembre 2025

## 📊 RESPUESTAS A TUS PREGUNTAS

### 1. ¿Cuántas tablas de permisos hay y cuál se usa?

**Hay 3 tablas:**

| Tabla | Registros | Estado | Uso |
|-------|-----------|--------|-----|
| `permisos_usuarios` | 612 | ✅ ACTIVA | **SE USA** - Esta es la tabla principal |
| `permisos_modulos` | 0 | ⚠️ VACÍA | **NO SE USA** - Tabla sin implementar |
| `permisos_usuario_backup_20251127` | 104 | 🗄️ BACKUP | Respaldo de migración |

**CONCLUSIÓN:** Solo `permisos_usuarios` se usa en el sistema.

---

### 2. ¿Cómo funciona la validación de permisos?

#### A. Datos del usuario 14652319:

```sql
SELECT id, usuario, nit, activo, rol 
FROM usuarios 
WHERE usuario = '14652319';
```

**Resultado:**
- `id`: 22 ← **ESTE ES EL CAMPO IMPORTANTE**
- `usuario`: '14652319'
- `nit`: '14652319'
- `activo`: TRUE
- `rol`: 'externo'

#### B. Al hacer login, se guardan estos datos en sesión (app.py línea 1177-1180):

```python
session['usuario_id'] = 22           # ← ID numérico (FK a permisos_usuarios)
session['usuario'] = '14652319'      # ← Código de usuario
session['nit'] = '14652319'          # ← NIT del tercero
session['rol'] = 'externo'           # ← Rol
```

#### C. Los decoradores validan usando `usuario_id` (ID numérico):

**Código en decoradores_permisos.py (línea 40):**
```python
result = db.session.execute(text("""
    SELECT permitido 
    FROM permisos_usuarios 
    WHERE usuario_id = :usuario_id    ← Usa el ID (22), NO el código '14652319'
      AND modulo = :modulo 
      AND accion = :accion
"""), {
    "usuario_id": session['usuario_id'],  # 22
    "modulo": modulo,                     # 'causaciones'
    "accion": accion                      # 'acceder_modulo'
})
```

**IMPORTANTE:** El sistema valida por **ID numérico** (22), NO por el código de usuario ('14652319').

---

### 3. ¿El frontend /admin/usuarios-permisos/ afecta la tabla?

**SÍ, AFECTA CORRECTAMENTE.** Los logs lo confirman:

```
📦 Permisos recibidos: {...}  ← Frontend recibe datos actuales de BD
✅ Usuario encontrado: 14652319
🔄 UPDATE: causaciones.acceder_modulo | False → True
🔄 UPDATE: facturas_digitales.acceder_modulo | False → True
...
💾 COMMIT realizado | 142 cambios guardados  ← Guarda en permisos_usuarios
```

**Endpoint:** `PUT /admin/usuarios-permisos/api/usuarios/22/permisos`
**Archivo:** `modules/admin/usuarios_permisos/routes.py` línea 731
**Operación:** 
```python
UPDATE permisos_usuarios 
SET permitido = :valor 
WHERE usuario_id = :usuario_id 
  AND modulo = :modulo 
  AND accion = :accion
```

**El problema NO es el frontend, sino que estás activando TODOS los permisos.**

---

## 🔧 CÓMO CONFIGURAR PERMISOS CORRECTAMENTE

### Escenario: Usuario 14652319 (externo) solo debe acceder a Causaciones

#### Paso 1: Desactivar TODOS los permisos

```sql
UPDATE permisos_usuarios 
SET permitido = FALSE 
WHERE usuario_id = 22;
```

#### Paso 2: Activar SOLO permisos necesarios

```sql
-- Permiso CRÍTICO: Acceder al módulo
UPDATE permisos_usuarios 
SET permitido = TRUE 
WHERE usuario_id = 22 
  AND modulo = 'causaciones' 
  AND accion = 'acceder_modulo';

-- Permisos de funcionalidades
UPDATE permisos_usuarios 
SET permitido = TRUE 
WHERE usuario_id = 22 
  AND modulo = 'causaciones' 
  AND accion IN (
    'consultar_causaciones',
    'nueva_causacion',
    'consultar_documentos',
    'ver_pdf',
    'agregar_observacion',
    'exportar_excel'
  );
```

#### Paso 3: Verificar resultado

```sql
SELECT modulo, accion, permitido 
FROM permisos_usuarios 
WHERE usuario_id = 22 AND permitido = TRUE;
```

**Resultado esperado:**
```
causaciones | acceder_modulo          | TRUE
causaciones | consultar_causaciones   | TRUE
causaciones | nueva_causacion         | TRUE
causaciones | consultar_documentos    | TRUE
causaciones | ver_pdf                 | TRUE
causaciones | agregar_observacion     | TRUE
causaciones | exportar_excel          | TRUE
```

#### Paso 4: Probar en el navegador

1. **Cerrar sesión** del usuario admin
2. **Login** con:
   - NIT: `14652319`
   - Usuario: `14652319`
   - Contraseña: `R1c4rd0$`
3. **Intentar acceder:**
   - `/causaciones/` → ✅ **DEBE FUNCIONAR**
   - `/facturas_digitales/dashboard` → ❌ **DEBE BLOQUEAR** (mensaje flash o redirect)
   - `/admin/usuarios-permisos` → ❌ **DEBE BLOQUEAR**

---

## 🎨 USO DEL FRONTEND /admin/usuarios-permisos/

### ✅ Forma CORRECTA de configurar permisos:

1. Login como **admin** (NIT: 805028041)
2. Ir a `/admin/usuarios-permisos`
3. Seleccionar usuario **14652319**
4. **Desmarcar TODO** excepto:
   ```
   ✅ Causaciones
      ✅ acceder_modulo
      ✅ consultar_causaciones
      ✅ nueva_causacion
      ✅ consultar_documentos
      ✅ ver_pdf
      ✅ agregar_observacion
      ✅ exportar_excel
   
   ❌ Facturas Digitales (TODO desmarcado)
   ❌ Archivo Digital (TODO desmarcado)
   ❌ Admin (TODO desmarcado)
   ❌ Gestión Usuarios (TODO desmarcado)
   ❌ Monitoreo (TODO desmarcado)
   ...etc
   ```
5. Guardar cambios
6. **Cerrar sesión** de admin
7. **Login con 14652319** y probar

### ❌ Forma INCORRECTA (lo que estabas haciendo):

**Activar TODO** → El usuario puede entrar a todos los módulos.

---

## 🔍 VERIFICACIÓN DE ESTADO ACTUAL

### Script ejecutado: `config_permisos_causaciones.py`

**Resultado:**
```
✅ 7 permisos activados para usuario 14652319:
   ✅ causaciones.acceder_modulo
   ✅ causaciones.consultar_causaciones
   ✅ causaciones.nueva_causacion
   ✅ causaciones.consultar_documentos
   ✅ causaciones.ver_pdf
   ✅ causaciones.agregar_observacion
   ✅ causaciones.exportar_excel
```

**Estado:** El usuario 14652319 ahora SOLO tiene acceso a Causaciones.

---

## 📋 ESTRUCTURA DE LA TABLA permisos_usuarios

```sql
CREATE TABLE permisos_usuarios (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER,              -- FK a usuarios.id (ej: 22)
    modulo VARCHAR(50),              -- Nombre del módulo (ej: 'causaciones')
    accion VARCHAR(100),             -- Acción específica (ej: 'acceder_modulo')
    permitido BOOLEAN DEFAULT FALSE, -- TRUE = permitido, FALSE = bloqueado
    fecha_asignacion TIMESTAMP,      -- Fecha de última modificación
    asignado_por VARCHAR(100)        -- Usuario que asignó el permiso
);
```

### Ejemplo de registros:

| usuario_id | modulo | accion | permitido |
|------------|--------|--------|-----------|
| 22 | causaciones | acceder_modulo | TRUE |
| 22 | causaciones | nueva_causacion | TRUE |
| 22 | facturas_digitales | acceder_modulo | FALSE |
| 22 | admin | acceder_modulo | FALSE |

---

## 🛡️ CÓMO FUNCIONAN LOS DECORADORES

### Decorador en rutas protegidas:

```python
# modules/causaciones/routes.py
@causaciones_bp.route('/')
@requiere_permiso_html('causaciones', 'acceder_modulo')
def index():
    # Código del módulo
    pass
```

### Flujo de validación:

1. Usuario intenta acceder a `/causaciones/`
2. Decorador ejecuta query:
   ```sql
   SELECT permitido 
   FROM permisos_usuarios 
   WHERE usuario_id = 22 
     AND modulo = 'causaciones' 
     AND accion = 'acceder_modulo'
   ```
3. Si `permitido = TRUE`:
   - ✅ Permite acceso
   - Ejecuta código del módulo
4. Si `permitido = FALSE` o no existe registro:
   - ❌ Bloquea acceso
   - Flash message: "No tienes permiso para acceder a este recurso"
   - Redirect a `/dashboard`

---

## 🔐 PERMISOS POR ROL (Recomendación)

### Usuario Externo (como 14652319):

**Accesos típicos:**
- ✅ Dashboard (ver resumen)
- ✅ 1-2 módulos específicos según su función
- ❌ Admin
- ❌ Gestión de usuarios
- ❌ Monitoreo
- ❌ Configuración

### Usuario Interno:

**Accesos típicos:**
- ✅ Dashboard completo
- ✅ Múltiples módulos operativos
- ✅ Reportes
- ❌ Admin (solo para administradores)

### Usuario Admin:

**Accesos:**
- ✅ TODO (sin restricciones)

---

## 📝 SCRIPTS DE UTILIDAD

### 1. Configurar permisos mínimos (Solo Causaciones):
```bash
python config_permisos_causaciones.py
```

### 2. Ver permisos de un usuario:
```bash
python verificar_usuario_14652319.py
```

### 3. Analizar las 3 tablas de permisos:
```bash
python analizar_3_tablas_permisos.py
```

---

## 🎯 RESUMEN EJECUTIVO

| Aspecto | Estado | Solución |
|---------|--------|----------|
| **¿Tabla permisos_modulos se usa?** | ❌ NO | Ignorar, está vacía |
| **¿Frontend afecta BD?** | ✅ SÍ | Funciona correctamente |
| **¿Validación por ID o código?** | 🔢 Por ID | Usa `usuario_id` (22), no código |
| **¿Usuario 14652319 accede a todo?** | ⚠️ SÍ | **Porque le activaste TODO** |
| **¿Cómo restringir?** | ✅ RESUELTO | Script ejecutado: solo 7 permisos activos |
| **¿Los decoradores funcionan?** | ✅ SÍ | Validación correcta en BD |

---

## ✅ PRÓXIMO PASO: PROBAR EL SISTEMA

**INSTRUCCIONES:**

1. **Cerrar sesión** en el navegador (si estás logueado como admin)

2. **Abrir ventana de incógnito** (para sesión limpia)

3. **Login con usuario externo:**
   - NIT: `14652319`
   - Usuario: `14652319`
   - Contraseña: `R1c4rd0$`

4. **Pruebas de acceso:**
   
   a) Ir a `/causaciones/`
      - **Resultado esperado:** ✅ Debe mostrar el módulo
   
   b) Ir a `/facturas_digitales/dashboard`
      - **Resultado esperado:** ❌ "No tienes permiso..." → redirect a /dashboard
   
   c) Ir a `/admin/usuarios-permisos`
      - **Resultado esperado:** ❌ "No tienes permiso..." → redirect a /dashboard
   
   d) Ir a `/dashboard`
      - **Resultado esperado:** ✅ Debe mostrar dashboard básico

5. **Si algo NO funciona como esperado:**
   - Captura pantalla del mensaje de error
   - Verifica en logs del servidor
   - Revisa en BD:
     ```sql
     SELECT modulo, accion, permitido 
     FROM permisos_usuarios 
     WHERE usuario_id = 22;
     ```

---

**Fecha:** 28 de Noviembre 2025, 00:10
**Configuración aplicada:** ✅ Usuario 14652319 con 7 permisos (solo Causaciones)
**Estado:** 🟢 LISTO PARA PRUEBAS
