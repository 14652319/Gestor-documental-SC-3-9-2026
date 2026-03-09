# 📄 Módulo de Facturas Digitales - Guía de Implementación

## 📦 Descripción
Sistema completo para la recepción, gestión y aprobación de facturas digitales con las siguientes características:

### ✨ Funcionalidades
- 📤 **Carga de facturas**: Drag & drop, validación de archivos, detección de duplicados por hash SHA256
- 📊 **Dashboard**: Métricas en tiempo real (pendientes, aprobadas, rechazadas, valor total)
- 📋 **Listado avanzado**: Filtros por estado, NIT, número, fechas con paginación
- 🔍 **Detalle de factura**: Visor PDF inline, historial de cambios, acciones de aprobación/rechazo
- ⚙️ **Configuración**: Rutas de almacenamiento configurables, mantenimiento del sistema
- 🔔 **Notificaciones**: Alertas automáticas en cambios de estado
- 🔐 **Control de acceso**: Permisos diferenciados (externos: solo cargar, internos: aprobar/rechazar)

### 🎨 Características de UI/UX
- ✅ Diseño responsive (mobile, tablet, desktop)
- 🌓 Modo claro/oscuro con persistencia
- 🎨 Colores institucionales (#16A085 verde)
- 💅 Tailwind CSS + SweetAlert2
- ⚡ Carga asíncrona con indicadores de progreso

---

## 📂 Estructura de Archivos Creados

```
modules/facturas_digitales/
├── __init__.py                 # Blueprint definition
├── models.py                   # SQLAlchemy models (6 tables)
└── routes.py                   # Backend routes (10 endpoints)

templates/facturas_digitales/
├── dashboard.html              # Dashboard principal
├── cargar.html                 # Formulario de carga con drag-drop
├── listado.html                # Tabla de facturas con filtros
├── detalle.html                # Vista detallada con PDF viewer
└── configuracion.html          # Panel de administración

sql/
└── facturas_digitales_schema.sql  # Schema completo de BD

crear_tablas_facturas.py        # Script de instalación
```

---

## 🛠️ Instalación en el Proyecto Actual

### 1️⃣ Verificar Archivos Creados
✅ Todos los archivos ya están en su lugar en este proyecto.

### 2️⃣ Verificar Blueprint Registrado
El blueprint ya está registrado en `app.py` (línea ~2550):
```python
from modules.facturas_digitales import facturas_digitales_bp
app.register_blueprint(facturas_digitales_bp)
```

### 3️⃣ Verificar Tablas de Base de Datos
✅ Las tablas ya fueron creadas con `crear_tablas_facturas.py`

Tablas creadas:
- `config_rutas_facturas` - Rutas de almacenamiento
- `facturas_digitales` - Facturas principales
- `facturas_digitales_historial` - Auditoría de cambios
- `facturas_digitales_adjuntos` - Archivos adicionales
- `facturas_digitales_notificaciones` - Alertas a usuarios
- `facturas_digitales_metricas` - Estadísticas diarias

### 4️⃣ Acceder al Módulo
🌐 URL: **http://127.0.0.1:8099/facturas-digitales/**

### 5️⃣ Crear Carpeta de Almacenamiento
Asegúrate de crear la carpeta configurada (por defecto):
```powershell
mkdir D:\facturas_digitales
```

O configúrala desde el panel de administración en:
**http://127.0.0.1:8099/facturas-digitales/configuracion**

---

## 🚀 Instalación en el Proyecto de Destino

### Proyecto destino:
`D:\PERFIL\Escritorio\Escritorio\100. Proyecto\1a. Gestor Documental`

### Pasos:

#### 1️⃣ Copiar Archivos del Módulo
```powershell
# Copiar módulo Python
Copy-Item -Recurse "modules\facturas_digitales" -Destination "D:\PERFIL\Escritorio\Escritorio\100. Proyecto\1a. Gestor Documental\modules\"

# Copiar templates
Copy-Item -Recurse "templates\facturas_digitales" -Destination "D:\PERFIL\Escritorio\Escritorio\100. Proyecto\1a. Gestor Documental\templates\"

# Copiar script SQL
Copy-Item "sql\facturas_digitales_schema.sql" -Destination "D:\PERFIL\Escritorio\Escritorio\100. Proyecto\1a. Gestor Documental\sql\"

# Copiar script de instalación
Copy-Item "crear_tablas_facturas.py" -Destination "D:\PERFIL\Escritorio\Escritorio\100. Proyecto\1a. Gestor Documental\"
```

#### 2️⃣ Registrar Blueprint en app.py
Agregar estas líneas en el archivo `app.py` del proyecto destino (cerca de donde registras otros blueprints):

```python
# Importar blueprint de Facturas Digitales
from modules.facturas_digitales import facturas_digitales_bp
app.register_blueprint(facturas_digitales_bp)  # /facturas-digitales/*
```

#### 3️⃣ Crear Tablas en Base de Datos
```powershell
cd "D:\PERFIL\Escritorio\Escritorio\100. Proyecto\1a. Gestor Documental"
python crear_tablas_facturas.py
```

#### 4️⃣ Crear Carpeta de Almacenamiento
```powershell
mkdir D:\facturas_digitales
# O la ruta que prefieras configurar
```

#### 5️⃣ Reiniciar Servidor Flask
```powershell
# Detener el servidor actual (Ctrl+C)
# Iniciar nuevamente
python app.py
```

#### 6️⃣ Verificar Instalación
1. Abre el navegador en: `http://127.0.0.1:8099/facturas-digitales/`
2. Deberías ver el dashboard de Facturas Digitales
3. Verifica que puedes acceder a todas las secciones

---

## 🔑 Control de Acceso

El módulo usa el sistema de autenticación existente y valida permisos según `tipo_usuario`:

### 👥 Usuarios Externos (Proveedores)
- ✅ Cargar facturas
- ✅ Ver solo sus propias facturas (filtradas por NIT)
- ✅ Descargar sus archivos
- ❌ NO pueden aprobar/rechazar

### 👨‍💼 Usuarios Internos (Empleados)
- ✅ Ver todas las facturas
- ✅ Aprobar facturas
- ✅ Rechazar facturas (requiere motivo)
- ✅ Cambiar estado a "En Revisión"
- ✅ Acceder a todas las funciones

### 🔐 Administradores
- ✅ Todo lo de usuarios internos
- ✅ Acceder a configuración
- ✅ Cambiar rutas de almacenamiento
- ✅ Funciones de mantenimiento

---

## 📡 Endpoints API

### Dashboard
- **GET** `/facturas-digitales/` - Dashboard principal con métricas

### Carga de Facturas
- **GET** `/facturas-digitales/cargar` - Formulario de carga
- **POST** `/facturas-digitales/api/cargar-factura` - API para subir archivo

**Body (FormData):**
```json
{
  "archivo": <File>,
  "numero_factura": "FAC-2025-001",
  "nit_proveedor": "900123456",
  "razon_social_proveedor": "Empresa XYZ SAS",
  "fecha_emision": "2025-01-15",
  "fecha_vencimiento": "2025-02-15",
  "valor_total": 1500000.00,
  "valor_iva": 285000.00,
  "observaciones": "Opcional"
}
```

### Listado
- **GET** `/facturas-digitales/listado` - Vista de tabla
- **GET** `/facturas-digitales/api/facturas` - API con filtros

**Query Params:**
- `page`: Número de página (default: 1)
- `per_page`: Registros por página (default: 20)
- `estado`: pendiente | en_revision | aprobado | rechazado
- `nit`: Filtrar por NIT
- `numero`: Filtrar por número de factura
- `fecha_desde`: Filtrar desde fecha (YYYY-MM-DD)

### Detalle y Acciones
- **GET** `/facturas-digitales/detalle/<id>` - Vista de detalle
- **GET** `/facturas-digitales/descargar/<id>` - Descargar archivo
- **POST** `/facturas-digitales/api/cambiar-estado/<id>` - Cambiar estado (interno only)

**Body:**
```json
{
  "nuevo_estado": "aprobado",
  "observaciones": "Opcional (requerido para rechazos)"
}
```

### Configuración (Admin only)
- **GET** `/facturas-digitales/configuracion` - Panel de config
- **POST** `/facturas-digitales/api/actualizar-ruta` - Actualizar ruta de almacenamiento

**Body:**
```json
{
  "ruta_local": "D:/nueva_ruta",
  "activo": true
}
```

---

## 🗄️ Modelos de Base de Datos

### ConfigRutasFacturas
```python
{
    "id": 1,
    "nombre": "default",
    "ruta_local": "D:/facturas_digitales",
    "ruta_red": null,
    "activa": true,
    "fecha_creacion": "2025-01-14T10:30:00",
    "usuario_creacion": "admin",
    "observaciones": "Ruta predeterminada"
}
```

### FacturaDigital
```python
{
    "id": 1,
    "numero_factura": "FAC-2025-001",
    "nit_proveedor": "900123456",
    "razon_social_proveedor": "Empresa XYZ SAS",
    "fecha_emision": "2025-01-15",
    "fecha_vencimiento": "2025-02-15",
    "valor_total": 1500000.00,
    "valor_iva": 285000.00,
    "estado": "pendiente",
    "fecha_carga": "2025-01-14T11:00:00",
    "usuario_carga": "proveedor1",
    "ruta_archivo": "D:/facturas_digitales/900123456_FAC-2025-001_20250114110000.pdf",
    "nombre_archivo_original": "factura_enero.pdf",
    "hash_archivo": "a1b2c3d4...",
    "tamanio_archivo_kb": 245
}
```

---

## 🎨 Personalización de Colores

Para cambiar los colores institucionales, edita las variables CSS en los templates:

```css
:root {
    --brand-primary: #16A085;     /* Verde principal */
    --brand-secondary: #128C7E;   /* Verde secundario */
    --brand-dark: #0E6F63;        /* Verde oscuro */
}
```

Para cambiar el tema completo:
1. Edita los archivos en `templates/facturas_digitales/`
2. Modifica las clases de Tailwind CSS
3. Ajusta los estilos inline en los `<style>` blocks

---

## 🔧 Troubleshooting

### Error: "No module named 'modules.facturas_digitales'"
**Solución:** Verifica que hayas copiado la carpeta completa y que el blueprint esté registrado en app.py

### Error: "relation 'facturas_digitales' does not exist"
**Solución:** Ejecuta `python crear_tablas_facturas.py` para crear las tablas

### Error al cargar archivos
**Solución:** 
1. Verifica que la carpeta de destino exista: `D:\facturas_digitales`
2. Verifica permisos de escritura en la carpeta
3. Revisa los logs en `logs/` para errores específicos

### Archivos no se ven en el listado
**Solución:**
1. Verifica que el usuario externo esté filtrando por su NIT
2. Usuarios externos solo ven sus propias facturas
3. Usuarios internos ven todas

### Error en dark mode
**Solución:** Limpia el localStorage del navegador:
```javascript
localStorage.removeItem('darkMode');
```

---

## 📊 Métricas y Estadísticas

El dashboard muestra:
- **Total de facturas** cargadas en el sistema
- **Facturas pendientes** de revisión
- **Facturas aprobadas** (listas para pago)
- **Facturas rechazadas** (requieren corrección)
- **Valor total** de todas las facturas

Las métricas se calculan en tiempo real según el estado de cada factura.

---

## 🔄 Flujo de Estados

```
pendiente → en_revision → aprobado
                      ↘ rechazado
```

1. **Pendiente**: Estado inicial al cargar la factura
2. **En Revisión**: Usuario interno marca que está revisando
3. **Aprobado**: Factura aprobada, lista para pago
4. **Rechazado**: Factura con errores, requiere corrección (debe incluir motivo)

Todos los cambios de estado quedan registrados en `facturas_digitales_historial` con:
- Usuario que realizó el cambio
- Fecha y hora
- Estado anterior y nuevo
- Observaciones

---

## 📞 Soporte

Para reportar problemas o solicitar nuevas funcionalidades, contacta al equipo de desarrollo.

**Desarrollado con ❤️ usando:**
- Flask 3.0
- SQLAlchemy
- Tailwind CSS
- SweetAlert2
- PostgreSQL

---

## 📝 Notas Adicionales

### Seguridad
- Los archivos se guardan con nombres únicos: `{NIT}_{numero}_{timestamp}.{ext}`
- Se calcula hash SHA256 para detectar duplicados
- Solo se permiten extensiones: PDF, XML, ZIP, PNG, JPG, JPEG
- Tamaño máximo: 50MB

### Rendimiento
- Paginación: 20 registros por página (configurable)
- Carga asíncrona de PDFs
- Índices en: `nit_proveedor`, `estado`, `fecha_carga`, `hash_archivo`

### Backup
Se recomienda hacer backup periódico de:
1. Base de datos (tablas `facturas_digitales*`)
2. Carpeta de archivos (`D:/facturas_digitales`)

### Próximas Mejoras
- 📧 Notificaciones por email en cambios de estado
- 🤖 OCR para extracción automática de datos
- 📊 Reportes avanzados con gráficos
- 📱 App móvil nativa
- 🔗 Integración con Telegram/WhatsApp
- 🧾 Soporte para XML de facturas electrónicas DIAN

---

**¡El módulo está listo para usar!** 🎉

Accede a: http://127.0.0.1:8099/facturas-digitales/
