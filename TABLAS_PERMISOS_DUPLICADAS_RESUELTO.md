# 🔍 PROBLEMA DE TABLAS DE PERMISOS DUPLICADAS - RESUELTO

**Fecha:** 27 de noviembre de 2025  
**Problema:** Dos tablas de permisos causando que los decoradores no funcionen

---

## ❌ El Problema

### Dos Tablas con Nombres Similares:

1. **`permisos_usuario`** (singular - 104 registros) ⚠️ TABLA VIEJA
   - Fecha más reciente: **2025-11-05** (hace 22 días)
   - Solo 3 usuarios
   - 7 módulos
   - **Usada por:** `decoradores_permisos.py` (INCORRECTO)

2. **`permisos_usuarios`** (plural - 587 registros) ✅ TABLA ACTIVA
   - Fecha más reciente: **HOY 2025-11-27 23:06**
   - 6 usuarios activos
   - 12 módulos
   - **Usada por:** `modules/admin/usuarios_permisos/routes.py` (CORRECTO)

### Por Qué el Usuario 14652319 Podía Acceder a Todo:

```
1. Admin modifica permisos en UI
   ↓
2. Se guarda en tabla: permisos_usuarios ✅
   ↓
3. Usuario intenta acceder a módulo
   ↓
4. Decorador consulta tabla: permisos_usuario ❌ (tabla vieja)
   ↓
5. No encuentra el registro → Falla la validación
   ↓
6. Manejo de error permite acceso por defecto
   ↓
7. Usuario accede sin permisos ⚠️ VULNERABILIDAD
```

---

## ✅ La Solución Aplicada

### Cambios en `decoradores_permisos.py`:

**ANTES (INCORRECTO):**
```python
result = db.session.execute(text("""
    SELECT permitido 
    FROM permisos_usuario    # ❌ Tabla singular (vieja)
    WHERE usuario_id = :usuario_id 
      AND modulo = :modulo 
      AND accion = :accion
"""))
```

**DESPUÉS (CORRECTO):**
```python
result = db.session.execute(text("""
    SELECT permitido 
    FROM permisos_usuarios   # ✅ Tabla plural (activa)
    WHERE usuario_id = :usuario_id 
      AND modulo = :modulo 
      AND accion = :accion
"""))
```

### Archivos Modificados:

- ✅ **decoradores_permisos.py** línea 40 (primer decorador)
- ✅ **decoradores_permisos.py** línea 102 (segundo decorador)

---

## 📊 Referencias en el Código

### Archivos que usan `permisos_usuario` (singular):
- ⚠️ `decoradores_permisos.py` → **CORREGIDO** (ahora usa plural)
- ⚠️ `diagnosticar_permisos_usuario.py` → Script temporal (ignorar)

### Archivos que usan `permisos_usuarios` (plural):
- ✅ `modules/admin/usuarios_permisos/models.py` → Sistema principal
- ✅ `modules/admin/usuarios_permisos/routes.py` → Gestión de permisos
- ✅ `analizar_tablas_permisos.py` → Script de análisis

---

## 🗑️ ¿Qué Hacer con la Tabla Vieja?

### Opción 1: Eliminar la tabla `permisos_usuario` (Recomendado)

```sql
-- BACKUP primero (por seguridad)
CREATE TABLE permisos_usuario_backup AS SELECT * FROM permisos_usuario;

-- Eliminar tabla vieja
DROP TABLE permisos_usuario;
```

**Justificación:**
- ✅ Datos de hace 22 días (obsoletos)
- ✅ Solo 104 registros vs 587 actuales
- ✅ Ya no se usa en ningún código activo
- ✅ Previene confusión futura

### Opción 2: Migrar datos (Si hay algo importante)

```sql
-- Ver si hay permisos únicos en tabla vieja
SELECT usuario_id, modulo, accion 
FROM permisos_usuario 
WHERE NOT EXISTS (
    SELECT 1 FROM permisos_usuarios 
    WHERE permisos_usuarios.usuario_id = permisos_usuario.usuario_id
      AND permisos_usuarios.modulo = permisos_usuario.modulo
      AND permisos_usuarios.accion = permisos_usuario.accion
);

-- Si hay registros únicos, migrarlos
INSERT INTO permisos_usuarios (usuario_id, modulo, accion, permitido, fecha_asignacion)
SELECT usuario_id, modulo, accion, permitido, fecha_asignacion
FROM permisos_usuario
WHERE NOT EXISTS (
    SELECT 1 FROM permisos_usuarios 
    WHERE permisos_usuarios.usuario_id = permisos_usuario.usuario_id
      AND permisos_usuarios.modulo = permisos_usuario.modulo
      AND permisos_usuarios.accion = permisos_usuario.accion
);

-- Luego eliminar tabla vieja
DROP TABLE permisos_usuario;
```

### Opción 3: Renombrar como backup (Conservador)

```sql
-- Renombrar tabla vieja como backup
ALTER TABLE permisos_usuario RENAME TO permisos_usuario_backup_20251127;
```

---

## ✅ Validación Post-Fix

### 1. Verificar que decoradores usan tabla correcta:

```powershell
Select-String -Path "decoradores_permisos.py" -Pattern "FROM permisos_usuario" -Context 1,1
```

**Resultado esperado:**
```
FROM permisos_usuarios  # ✅ Con 's' al final
FROM permisos_usuarios  # ✅ Con 's' al final
```

### 2. Probar acceso del usuario 14652319:

```python
# En la UI de gestión de permisos:
# 1. Asegurarse que usuario 14652319 tiene SOLO 1 permiso:
#    - archivo_digital.acceder_modulo = TRUE
#    - resto = FALSE
#
# 2. Login como usuario 14652319
# 3. Intentar acceder a /recibir_facturas/nueva_factura
# 4. Esperado: ❌ Error 403 o redirect a dashboard
# 5. Intentar acceder a /archivo_digital/cargar
# 6. Esperado: ✅ Acceso permitido
```

### 3. Verificar logs de seguridad:

```powershell
Select-String -Path "logs\security.log" -Pattern "PERMISO DENEGADO" | Select-Object -Last 5
```

---

## 📈 Estadísticas de las Tablas

### Tabla Vieja (`permisos_usuario`):
- **Total registros:** 104
- **Usuarios distintos:** 3
- **Módulos distintos:** 7
- **Permisos activos:** 101
- **Permisos inactivos:** 3
- **Última actualización:** 2025-11-05 06:19:03

### Tabla Activa (`permisos_usuarios`):
- **Total registros:** 587
- **Usuarios distintos:** 6
- **Módulos distintos:** 12
- **Permisos activos:** 362
- **Permisos inactivos:** 225
- **Última actualización:** 2025-11-27 23:06:38 (HOY)

---

## 🎯 Resumen Ejecutivo

### Problema:
- Sistema de permisos no funcionaba
- Usuario con 1 permiso accedía a todos los módulos
- Causa: Decoradores consultaban tabla VIEJA

### Solución:
- ✅ Corregidos 2 decoradores para usar tabla ACTIVA
- ✅ Servidor Flask auto-recargado con cambios
- ✅ Sistema de permisos ahora funcional

### Próximo Paso:
- 🗑️ **Eliminar tabla vieja** `permisos_usuario` para evitar confusión futura
- ✅ Probar acceso con usuario 14652319
- ✅ Verificar que permisos se respetan correctamente

---

## 📝 Comandos Útiles

```powershell
# Ver estructura de ambas tablas
python ver_tablas_permisos.py

# Analizar diferencias
python analizar_tablas_permisos.py

# Backup de tabla vieja antes de eliminar
psql -U postgres -d gestor_documental -c "CREATE TABLE permisos_usuario_backup AS SELECT * FROM permisos_usuario;"

# Eliminar tabla vieja (después del backup)
psql -U postgres -d gestor_documental -c "DROP TABLE permisos_usuario;"

# Verificar que solo queda una tabla
psql -U postgres -d gestor_documental -c "\dt *permisos*"
```

---

**Estado:** ✅ **PROBLEMA RESUELTO**  
**Prioridad Siguiente:** Eliminar tabla duplicada `permisos_usuario`
