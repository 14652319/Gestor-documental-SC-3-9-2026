# NUEVO DISEÑO DEL MODAL DE USUARIOS
## Soporta Múltiples Departamentos

El usuario tendrá una interfaz con:

1. **Información del usuario** (solo lectura)
   - Usuario
   - Email

2. **Lista de departamentos asignados** (cards)
   - Cada departamento es una card con:
     - Nombre del departamento (badge de color)
     - 4 checkboxes de permisos
     - Botón "Eliminar"

3. **Agregar nuevo departamento**
   - Select de departamentos disponibles
   - 4 checkboxes de permisos
   - Botón "Agregar"

4. **Botones de acción**
   - Cerrar

## Flujo de Uso

### Caso: Usuario con 0 departamentos
```
┌─────────────────────────────────────────┐
│ ⚙️ Configurar Usuario: jperez           │
├─────────────────────────────────────────┤
│ 👤 Usuario: jperez                      │
│ 📧 Email: jperez@example.com            │
├─────────────────────────────────────────┤
│ 📋 Departamentos Asignados              │
│                                         │
│ No tiene departamentos asignados        │
├─────────────────────────────────────────┤
│ ➕ Agregar Departamento                 │
│ [Select: Seleccione...]                 │
│ ☐ Recibir  ☐ Aprobar                    │
│ ☐ Rechazar ☐ Firmar                     │
│ [Botón: Agregar]                        │
└─────────────────────────────────────────┘
```

### Caso: Usuario con 2 departamentos
```
┌─────────────────────────────────────────┐
│ ⚙️ Configurar Usuario: jperez           │
├─────────────────────────────────────────┤
│ 👤 Usuario: jperez                      │
│ 📧 Email: jperez@example.com            │
├─────────────────────────────────────────┤
│ 📋 Departamentos Asignados (2)          │
│                                         │
│ ┌───────────────────────────────────┐  │
│ │ 🏢 TIC                       [❌]  │  │
│ │ ☑️ Recibir  ☑️ Aprobar            │  │
│ │ ☐ Rechazar ☑️ Firmar             │  │
│ └───────────────────────────────────┘  │
│                                         │
│ ┌───────────────────────────────────┐  │
│ │ 🏢 FIN                       [❌]  │  │
│ │ ☐ Recibir  ☑️ Aprobar             │  │
│ │ ☑️ Rechazar ☑️ Firmar            │  │
│ └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│ ➕ Agregar Departamento                 │
│ [Select: MER, DOM, MYP]                 │
│ ☐ Recibir  ☐ Aprobar                    │
│ ☐ Rechazar ☐ Firmar                     │
│ [Botón: Agregar]                        │
└─────────────────────────────────────────┘
```

## Endpoints Usados

1. **GET /api/usuarios/{id}**
   - Retorna: `{ departamentos: [{ departamento, puede_recibir, ... }] }`

2. **POST /api/usuarios/{id}/departamento**
   - Body: `{ departamento, puede_recibir, puede_aprobar, puede_rechazar, puede_firmar }`
   - Acción: Agregar o actualizar

3. **DELETE /api/usuarios/{id}/departamento/{depto}**
   - Acción: Eliminar departamento

## Funciones JavaScript

### `renderizarDepartamentos(usuario)`
Renderiza las cards de departamentos asignados con sus permisos.

### `agregarDepartamento(usuarioId)`
Agrega un nuevo departamento con los permisos seleccionados.

### `actualizarPermisoDepartamento(usuarioId, departamento, permiso, valor)`
Actualiza un permiso específico de un departamento.

### `eliminarDepartamento(usuarioId, departamento)`
Elimina un departamento asignado (con confirmación).

## Ventajas del Diseño

✅ Interfaz intuitiva y visual
✅ Cada departamento es independiente
✅ Permisos diferentes por departamento
✅ Agregar/eliminar dinámicamente
✅ Sin necesidad de "Guardar" global (cada acción se guarda inmediatamente)
✅ Validaciones en tiempo real

## Colores de Departamentos

- TIC: Azul (#007bff)
- MER: Verde (#28a745)
- FIN: Amarillo (#ffc107)
- DOM: Rojo (#dc3545)
- MYP: Púrpura (#6f42c1)
