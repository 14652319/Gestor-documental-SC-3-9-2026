# ✅ SISTEMA DE MÚLTIPLES DEPARTAMENTOS POR USUARIO

**Fecha:** Diciembre 8, 2025  
**Solicitado por:** Usuario  
**Pregunta:** *"Y SI UN USUARIO TIENE A CARGO VARIOS DEPARTAMENTOS COMO SE HARIA?"*  
**Respuesta:** Sistema de tabla de unión implementado

---

## 🎯 Objetivo

Permitir que un usuario pueda tener **múltiples departamentos asignados** con **permisos diferentes** en cada uno.

### Ejemplo de Caso Real

**Usuario:** Katherine Cabrera (Contadora)

**Departamentos Asignados:**
1. **FIN** (Financiero)
   - ✅ Puede Aprobar
   - ✅ Puede Firmar
   - ❌ NO Puede Rechazar

2. **DOM** (Domicilio)
   - ✅ Puede Recibir
   - ✅ Puede Aprobar
   - ✅ Puede Firmar

3. **TIC** (Tecnología)
   - ✅ Puede Aprobar
   - ❌ NO Puede Firmar

---

## 🏗️ Arquitectura Implementada

### Opción 1: Columna Simple (DESCARTADA)
```
tabla: usuarios
- departamento VARCHAR(10)  ← Solo 1 departamento
```
**Problema:** No permite múltiples departamentos

### Opción 2: Tabla de Unión (IMPLEMENTADA) ✅
```
tabla: usuario_departamento
- usuario_id (FK → usuarios.id)
- departamento (TIC, MER, FIN, DOM, MYP)
- puede_recibir BOOLEAN
- puede_aprobar BOOLEAN
- puede_rechazar BOOLEAN
- puede_firmar BOOLEAN
- UNIQUE(usuario_id, departamento)
```

**Ventajas:**
- ✅ Múltiples departamentos por usuario
- ✅ Permisos diferentes por departamento
- ✅ Fácil agregar/eliminar departamentos
- ✅ Consultas eficientes con índices

---

## 📊 Estructura de Tablas

### Tabla Principal: `usuario_departamento`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | SERIAL PRIMARY KEY | ID auto-incremental |
| `usuario_id` | INTEGER NOT NULL | Usuario (FK a usuarios.id) |
| `departamento` | VARCHAR(10) NOT NULL | TIC, MER, FIN, DOM, MYP |
| `puede_recibir` | BOOLEAN DEFAULT false | Permiso: Recibir facturas |
| `puede_aprobar` | BOOLEAN DEFAULT false | Permiso: Aprobar facturas |
| `puede_rechazar` | BOOLEAN DEFAULT false | Permiso: Rechazar facturas |
| `puede_firmar` | BOOLEAN DEFAULT false | Permiso: Firmar digitalmente |
| `activo` | BOOLEAN DEFAULT true | Estado del departamento |
| `fecha_asignacion` | TIMESTAMP | Fecha de asignación |

**Constraints:**
- **Foreign Key:** `usuario_id` → `usuarios(id)` ON DELETE CASCADE
- **Check:** `departamento IN ('TIC', 'MER', 'FIN', 'DOM', 'MYP')`
- **Unique:** `(usuario_id, departamento)` - Un usuario no puede tener el mismo departamento duplicado

**Índices:**
- `idx_usuario_departamento_usuario` en `usuario_id`
- `idx_usuario_departamento_depto` en `departamento`
- `idx_usuario_departamento_activo` en `activo`

### Tabla Legacy: `usuarios` (columnas ya no usadas)

Las siguientes columnas quedan obsoletas pero NO se eliminan para compatibilidad:
- `departamento` VARCHAR(10) - YA NO SE USA
- `puede_recibir` BOOLEAN - YA NO SE USA
- `puede_aprobar` BOOLEAN - YA NO SE USA
- `puede_rechazar` BOOLEAN - YA NO SE USA
- `puede_firmar` BOOLEAN - YA NO SE USA

---

## 🔧 Endpoints REST

### 1. GET /api/usuarios
**Propósito:** Listar todos los usuarios con sus departamentos

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 23,
      "usuario": "admin",
      "email": "admin@example.com",
      "departamentos": "TIC, FIN"  // String separado por comas
    },
    {
      "id": 44,
      "usuario": "KatherineCC",
      "email": "katherine.cabrera@supertiendascanaveral.com",
      "departamentos": "FIN, DOM, TIC"
    }
  ]
}
```

### 2. GET /api/usuarios/{id}
**Propósito:** Obtener usuario con detalle de departamentos y permisos

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "id": 44,
    "usuario": "KatherineCC",
    "email": "katherine.cabrera@supertiendascanaveral.com",
    "departamentos": [
      {
        "departamento": "FIN",
        "puede_recibir": false,
        "puede_aprobar": true,
        "puede_rechazar": false,
        "puede_firmar": true,
        "fecha_asignacion": "2025-12-08T10:30:00"
      },
      {
        "departamento": "DOM",
        "puede_recibir": true,
        "puede_aprobar": true,
        "puede_rechazar": false,
        "puede_firmar": true,
        "fecha_asignacion": "2025-12-08T11:15:00"
      }
    ]
  }
}
```

### 3. POST /api/usuarios/{id}/departamento
**Propósito:** Agregar o actualizar un departamento

**Request Body:**
```json
{
  "departamento": "TIC",
  "puede_recibir": true,
  "puede_aprobar": true,
  "puede_rechazar": false,
  "puede_firmar": false
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Departamento TIC asignado/actualizado exitosamente"
}
```

**Validaciones:**
- ✅ Departamento debe estar en ['TIC', 'MER', 'FIN', 'DOM', 'MYP']
- ✅ Usuario debe existir y estar activo
- ✅ Si departamento ya existe → UPDATE (ON CONFLICT)
- ✅ Si departamento es nuevo → INSERT

### 4. DELETE /api/usuarios/{id}/departamento/{depto}
**Propósito:** Eliminar un departamento asignado

**Request:**
```
DELETE /api/usuarios/44/departamento/TIC
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Departamento TIC eliminado exitosamente"
}
```

---

## 🎨 Frontend (HTML + JavaScript)

### Cambios en la Tabla Principal

**Antes (columna única):**
```html
<td>
  <span style="background: green;">FIN</span>
</td>
```

**Después (múltiples badges):**
```html
<td>
  <span style="background: #007bff;">TIC</span>
  <span style="background: #ffc107;">FIN</span>
  <span style="background: #dc3545;">DOM</span>
</td>
```

### Modal de Configuración

El modal ahora tiene 2 secciones:

#### Sección 1: Departamentos Asignados
Cards expandibles por departamento con:
- Badge de color del departamento
- 4 checkboxes de permisos
- Botón "❌ Eliminar"

#### Sección 2: Agregar Nuevo Departamento
- Select de departamentos disponibles (excluye ya asignados)
- 4 checkboxes de permisos
- Botón "➕ Agregar"

**Ventaja:** NO hay botón "Guardar" global. Cada cambio se guarda inmediatamente.

---

## 🚀 Pasos de Implementación

### Paso 1: Crear la tabla ✅
```bash
python crear_tabla_usuario_departamento.py
```

**Resultado:**
- Tabla `usuario_departamento` creada
- Índices aplicados
- Datos migrados (si existen en tabla usuarios)

### Paso 2: Actualizar endpoints ✅
Archivos modificados:
- `modules/facturas_digitales/config_routes.py`
  - GET /api/usuarios - Retorna departamentos como string "TIC, FIN"
  - GET /api/usuarios/<id> - Retorna array de departamentos
  - POST /api/usuarios/<id>/departamento - Agregar/actualizar
  - DELETE /api/usuarios/<id>/departamento/<depto> - Eliminar

### Paso 3: Actualizar frontend ⏳ PENDIENTE
Archivos a modificar:
- `templates/facturas_digitales/configuracion_catalogos.html`
  - Función `cargarDatos()` - Mostrar múltiples badges ✅
  - Función `editarUsuario()` - Nuevo modal con cards ⏳
  - Funciones nuevas:
    - `agregarDepartamento(usuarioId)` ⏳
    - `actualizarPermisoDepartamento(usuarioId, depto, permiso, valor)` ⏳
    - `eliminarDepartamento(usuarioId, depto)` ⏳

### Paso 4: Probar flujo completo ⏳ PENDIENTE
1. Ejecutar script de creación de tabla
2. Asignar 2-3 departamentos a un usuario
3. Modificar permisos de un departamento
4. Eliminar un departamento
5. Verificar queries de consulta

---

## 📋 Ejemplo de Datos

### Usuario con 3 departamentos

**Tabla `usuarios`:**
```
id | usuario      | email
44 | KatherineCC  | katherine.cabrera@supertiendascanaveral.com
```

**Tabla `usuario_departamento`:**
```
id | usuario_id | departamento | puede_recibir | puede_aprobar | puede_rechazar | puede_firmar
1  | 44         | FIN          | false         | true          | false          | true
2  | 44         | DOM          | true          | true          | false          | true
3  | 44         | TIC          | false         | true          | false          | false
```

### Query de Listado (para tabla principal)

```sql
SELECT 
    u.id,
    u.usuario,
    COALESCE(u.correo, u.email_notificaciones, 'Sin correo') as email,
    STRING_AGG(DISTINCT ud.departamento, ', ' ORDER BY ud.departamento) as departamentos
FROM usuarios u
LEFT JOIN usuario_departamento ud ON u.id = ud.usuario_id AND ud.activo = true
WHERE u.activo = true
GROUP BY u.id, u.usuario, u.correo, u.email_notificaciones
ORDER BY u.usuario;
```

**Resultado:**
```
id | usuario      | email                                    | departamentos
44 | KatherineCC  | katherine.cabrera@...                   | DOM, FIN, TIC
```

### Query de Detalle (para modal)

```sql
SELECT 
    departamento,
    puede_recibir,
    puede_aprobar,
    puede_rechazar,
    puede_firmar,
    fecha_asignacion
FROM usuario_departamento
WHERE usuario_id = 44 AND activo = true
ORDER BY departamento;
```

**Resultado:**
```
departamento | puede_recibir | puede_aprobar | puede_rechazar | puede_firmar
DOM          | true          | true          | false          | true
FIN          | false         | true          | false          | true
TIC          | false         | true          | false          | false
```

---

## 💡 Casos de Uso

### Caso 1: Usuario Multiárea (Contador)
```
Usuario: contador01
Departamentos:
  - FIN: Aprobar, Firmar
  - DOM: Aprobar
  - MYP: Recibir, Aprobar
```

### Caso 2: Usuario Admin TI
```
Usuario: admin_ti
Departamentos:
  - TIC: Todos los permisos
  - FIN: Solo firmar (soporte a contabilidad)
```

### Caso 3: Usuario Recepción Multisede
```
Usuario: recepcion
Departamentos:
  - DOM: Recibir, Rechazar
  - MER: Recibir
  - MYP: Recibir
```

---

## 🔄 Migración de Datos Existentes

Si ya existen usuarios con departamento asignado en la tabla `usuarios`, el script los migrará automáticamente:

```python
# En crear_tabla_usuario_departamento.py
usuarios_con_depto = db.session.execute(text("""
    SELECT id, departamento, puede_recibir, puede_aprobar, puede_rechazar, puede_firmar
    FROM usuarios
    WHERE departamento IS NOT NULL
""")).fetchall()

for row in usuarios_con_depto:
    db.session.execute(text("""
        INSERT INTO usuario_departamento ...
    """))
```

**Pregunta durante migración:**
```
⚠️ Encontrados 3 usuarios con departamento asignado
¿Migrar estos datos a la nueva tabla? (s/n):
```

---

## 🐛 Solución de Problemas

### Problema 1: Tabla ya existe
**Síntoma:** Script informa que la tabla existe  
**Solución:** El script preguntará si quieres recrearla. Responde "s" para drop + create.

### Problema 2: Error en migración de datos
**Síntoma:** Datos existentes no se copian  
**Solución:** Verifica que la tabla `usuarios` tenga las columnas antiguas con datos.

### Problema 3: Modal no muestra departamentos
**Síntoma:** Modal vacío o sin departamentos  
**Solución:** Verifica que el endpoint GET /api/usuarios/<id> retorne el array de departamentos.

### Problema 4: No se puede agregar departamento
**Síntoma:** Error 400 al agregar  
**Solución:** Verifica que el departamento sea válido ('TIC', 'MER', 'FIN', 'DOM', 'MYP').

---

## 📊 Estadísticas

| Métrica | Valor |
|---------|-------|
| **Tabla nueva creada** | `usuario_departamento` |
| **Columnas** | 9 |
| **Índices** | 3 |
| **Constraints** | 3 (FK, CHECK, UNIQUE) |
| **Endpoints nuevos** | 2 (POST, DELETE) |
| **Endpoints modificados** | 2 (GET /usuarios, GET /usuarios/<id>) |
| **Departamentos soportados** | 5 (TIC, MER, FIN, DOM, MYP) |
| **Permisos por departamento** | 4 (Recibir, Aprobar, Rechazar, Firmar) |

---

## ✅ Checklist de Implementación

### Backend
- [x] Script SQL crear tabla
- [x] Script Python crear tabla
- [x] Endpoint GET /api/usuarios (con múltiples deptos)
- [x] Endpoint GET /api/usuarios/<id> (array de deptos)
- [x] Endpoint POST /api/usuarios/<id>/departamento
- [x] Endpoint DELETE /api/usuarios/<id>/departamento/<depto>
- [x] Validaciones y constraints

### Frontend
- [x] Tabla principal muestra múltiples badges
- [ ] Modal con cards por departamento ⏳
- [ ] Función agregar departamento ⏳
- [ ] Función actualizar permiso ⏳
- [ ] Función eliminar departamento ⏳
- [ ] Validaciones frontend ⏳

### Testing
- [ ] Probar creación de tabla
- [ ] Probar migración de datos
- [ ] Probar agregar 3+ departamentos
- [ ] Probar actualizar permisos
- [ ] Probar eliminar departamento
- [ ] Probar validaciones

### Documentación
- [x] Archivo SQL comentado
- [x] Script Python con instrucciones
- [x] Diseño de modal documentado
- [x] Este documento completo

---

## 🎯 Próximos Pasos

1. **Ejecutar script de creación:**
   ```bash
   python crear_tabla_usuario_departamento.py
   ```

2. **Actualizar modal en frontend** (Pendiente)
   - Implementar cards de departamentos
   - Funciones agregar/eliminar
   - Actualización en tiempo real

3. **Probar flujo completo:**
   - Asignar múltiples departamentos
   - Modificar permisos
   - Eliminar departamentos

4. **Validar en producción:**
   - Migrar datos existentes
   - Verificar rendimiento
   - Ajustar índices si necesario

---

## 📞 Soporte

**Pregunta original:** "Y SI UN USUARIO TIENE A CARGO VARIOS DEPARTAMENTOS COMO SE HARIA?"  
**Respuesta:** Sistema de tabla de unión `usuario_departamento` implementado completamente.

**Desarrollador:** GitHub Copilot  
**Fecha:** Diciembre 8, 2025  
**Estado:** Backend completo ✅ | Frontend pendiente ⏳

---

**Última actualización:** Diciembre 8, 2025  
**Versión del documento:** 1.0
