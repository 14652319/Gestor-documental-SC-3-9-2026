# 📚 DOCUMENTACIÓN COMPLETA DEL SISTEMA - GESTOR DOCUMENTAL
## Supertiendas Cañaveral S.A.S

**Versión del Sistema**: 2.8.5  
**Última Actualización**: 01 de Diciembre de 2025  
**Arquitectura**: Flask + PostgreSQL + Multi-Módulo

---

## 📋 TABLA DE CONTENIDOS

1. [Visión General del Sistema](#visión-general)
2. [Arquitectura y Tecnologías](#arquitectura)
3. [Módulos del Sistema](#módulos)
4. [Base de Datos](#base-de-datos)
5. [Sistema de Permisos](#permisos)
6. [Seguridad y Sesiones](#seguridad)
7. [Sistema de Backup](#backup)
8. [Configuración y Despliegue](#configuración)
9. [Guía de Usuario](#guía-usuario)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 VISIÓN GENERAL DEL SISTEMA {#visión-general}

### Propósito
Sistema integral de gestión documental para administrar facturas, notas contables, relaciones comerciales y procesos contables de Supertiendas Cañaveral y sus filiales.

### Alcance
- **Usuarios**: 150+ usuarios internos y externos
- **Empresas**: Supertiendas Cañaveral (SC), La Galería (LG)
- **Módulos Activos**: 9 módulos principales + 5 auxiliares
- **Documentos**: 50,000+ documentos gestionados
- **Transacciones**: 1,000+ operaciones diarias

### Objetivos Clave
✅ Digitalización completa de procesos contables  
✅ Trazabilidad total de documentos  
✅ Reducción de tiempos de procesamiento en 70%  
✅ Auditoría completa de operaciones  
✅ Integración con sistemas externos (DIAN, ERP)

---

## 🏗️ ARQUITECTURA Y TECNOLOGÍAS {#arquitectura}

### Stack Tecnológico

#### Backend
- **Framework**: Flask 3.0.0 (Python 3.11)
- **ORM**: SQLAlchemy 2.0
- **Base de Datos**: PostgreSQL 18
- **Servidor**: Gunicorn (producción) / Werkzeug (desarrollo)

#### Frontend
- **HTML5 + CSS3** (responsive design)
- **JavaScript Vanilla** (sin frameworks pesados)
- **SweetAlert2** para notificaciones
- **Chart.js** para gráficas

#### Seguridad
- **Autenticación**: Flask-Login + bcrypt
- **Sesiones**: Flask-Session (25 min timeout)
- **CORS**: Flask-CORS (configurado por dominio)
- **CSRF**: Protección habilitada

### Arquitectura de Aplicaciones

```
┌─────────────────────────────────────────────────────────────┐
│                    NGINX (Reverse Proxy)                     │
│                    Puerto 80/443 (HTTPS)                     │
└────────────┬────────────────────────────────┬────────────────┘
             │                                │
             ↓                                ↓
┌────────────────────────────┐  ┌────────────────────────────┐
│   GESTOR DOCUMENTAL        │  │   DIAN vs ERP              │
│   Puerto: 8099             │  │   Puerto: 8097             │
│   Flask App Principal      │  │   Flask App Independiente  │
│   9 Módulos                │  │   Validaciones DIAN        │
└────────────┬───────────────┘  └────────────┬───────────────┘
             │                                │
             └────────────┬───────────────────┘
                          ↓
             ┌────────────────────────────┐
             │   PostgreSQL 18            │
             │   Base: gestor_documental  │
             │   70+ tablas               │
             └────────────────────────────┘
```

### Estructura de Directorios

```
GESTOR_DOCUMENTAL/
├── app.py                          # Aplicación Flask principal (8000+ líneas)
├── extensions.py                   # Instancia compartida de SQLAlchemy
├── decoradores_permisos.py         # Decoradores de seguridad
├── utils_fecha.py                  # Utilidades de fecha/hora Colombia
├── backup_manager.py               # Sistema de backups automatizado
│
├── modules/                        # MÓDULOS DEL SISTEMA
│   ├── admin/                      # Administración
│   ├── causaciones/                # Causaciones contables
│   ├── configuracion/              # Configuración del sistema
│   ├── dian_vs_erp/               # Validación DIAN
│   ├── facturas_digitales/        # Facturas digitales
│   ├── notas_contables/           # Notas contables
│   ├── recibir_facturas/          # Recepción de facturas
│   ├── relaciones/                # Relaciones comerciales
│   └── terceros/                  # Gestión de terceros
│
├── templates/                      # PLANTILLAS HTML (70+ archivos)
│   ├── facturas_digitales/
│   ├── dian_vs_erp/
│   └── ... (otros módulos)
│
├── static/                         # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── img/
│
├── logs/                          # LOGS DEL SISTEMA
│   ├── app.log                    # Log general
│   ├── security.log               # Log de seguridad
│   ├── errors.log                 # Errores críticos
│   ├── facturas_digitales.log     # Log módulo facturas
│   ├── relaciones.log             # Log módulo relaciones
│   └── backup.log                 # Log de backups
│
├── documentos_terceros/           # ALMACENAMIENTO DE DOCUMENTOS
│   ├── {NIT}-{RADICADO}-{FECHA}/ # Carpetas por tercero
│   └── ...
│
├── documentos_contables/          # Documentos contables
├── facturas_digitales/            # Facturas digitales
│
├── sql/                           # SCRIPTS SQL
│   ├── schema_core.sql            # Schema principal
│   ├── schema_backup.sql          # Schema de backup
│   └── ... (otros schemas)
│
└── docs/                          # DOCUMENTACIÓN
    ├── GUIA_INSTALACION_COMPLETA.md
    ├── ARQUITECTURA_SISTEMA_BACKUP.md
    └── ... (otras guías)
```

---

## 📦 MÓDULOS DEL SISTEMA {#módulos}

### 1. 🔹 ADMIN - Administración
**Estado**: ✅ Operativo  
**Ruta**: `/admin`  
**Permisos**: 9 permisos (3 críticos)

**Funcionalidades**:
- Gestión de usuarios y permisos
- Activación/desactivación de cuentas
- Auditoría de accesos
- Dashboard de administración

**Permisos Críticos**:
- `gestionar_usuarios` - Crear, editar, eliminar usuarios
- `gestionar_permisos` - Asignar permisos a usuarios
- `ver_dashboard` - Acceso al panel administrativo

**Endpoints Principales**:
- `GET /admin/usuarios` - Listar usuarios
- `POST /admin/usuarios/crear` - Crear usuario
- `PUT /admin/usuarios/{id}` - Editar usuario
- `POST /admin/usuarios/{id}/activar` - Activar/desactivar

---

### 2. 🔹 RECIBIR FACTURAS - Recepción de Facturas
**Estado**: ✅ Operativo (Productivo desde Nov 2025)  
**Ruta**: `/recibir_facturas`  
**Permisos**: 15 permisos (3 críticos)

**Funcionalidades**:
- Recepción de facturas de proveedores
- Validación de NIT en tiempo real
- Sistema de facturas temporales (editable)
- Migración a facturas recibidas (persistente)
- Exportación a Excel (19 columnas)
- Sistema de observaciones con auditoría

**Flujo de Trabajo**:
```
1. Usuario ingresa factura → Valida NIT
2. Valida clave única → Adiciona factura temporal
3. Facturas en tabla temporal → Edición permitida
4. Click "Guardar Facturas" → Migra a facturas_recibidas
5. Facturas recibidas → NO editables, solo consulta
```

**Permisos Críticos**:
- `eliminar_factura` - Borrar facturas temporales
- `guardar_facturas` - Confirmar y persistir facturas en BD
- `limpiar_todo` - Borrar todas las facturas temporales

**Modelos**:
- `FacturaTemporal` - Facturas en edición
- `FacturaRecibida` - Facturas guardadas permanentemente
- `ObservacionFacturaTemporal` - Observaciones editables
- `ObservacionFactura` - Observaciones persistentes
- `CentroOperacion` - Catálogo de tiendas/bodegas

**Template Principal**: `templates/nueva_factura_REFACTORED.html` (3000+ líneas)

---

### 3. 🔹 RELACIONES - Relaciones de Facturas
**Estado**: ✅ Operativo (Productivo desde Oct 2025)  
**Ruta**: `/relaciones`  
**Permisos**: 14 permisos (3 críticos)

**Funcionalidades**:
- Generación de relaciones digitales (sin impresión)
- Recepción digital con firma SHA256
- Validación individual de facturas físicas
- Sistema de tokens de firma digital (validez 24h)
- Paginación de resultados (10/25/50/100 por página)
- Reimprimir relaciones existentes
- Auditoría completa de recepciones

**Flujo de Generación**:
```
1. Usuario filtra facturas por fecha (default: HOY)
2. Sistema resalta facturas ya relacionadas (amarillo)
3. Usuario selecciona facturas (validación anti-duplicados)
4. Elige: "📱 Digital" o "🖨️ Física"
5. Sistema genera consecutivo REL-XXX
6. Registra facturas en BD
7. Si digital: Redirige a recepción_digital
   Si física: Descarga Excel
```

**Permisos Críticos**:
- `confirmar_recepcion` - Firmar digitalmente recepciones
- `generar_token_firma` - Crear tokens de firma digital
- `verificar_token` - Validar tokens de firma digital

**Modelos**:
- `RelacionFactura` - Relaciones generadas
- `RecepcionDigital` - Recepciones digitales firmadas
- `FacturaRecibidaDigital` - Facturas de cada relación
- `TokenFirmaDigital` - Tokens de firma (6 dígitos, 24h validez)
- `Consecutivo` - Autoincremental para REL-XXX

**Firma Digital SHA256**:
```python
hash_input = f"{numero_relacion}|{usuario}|{fecha_iso}|{facturas_recibidas}"
firma_digital = hashlib.sha256(hash_input.encode()).hexdigest()
```

**Templates**:
- `templates/generar_relacion_REFACTORED.html` (1700+ líneas)
- `templates/recepcion_digital.html` (800+ líneas)

---

### 4. 🔹 FACTURAS DIGITALES - Radicación Digital
**Estado**: ✅ Operativo (Actualizado Dic 2025)  
**Ruta**: `/facturas-digitales`  
**Permisos**: 15 permisos (5 críticos)

**Funcionalidades**:
- **Radicación de facturas digitales** (OPTIMIZADO - 3 líneas)
- Carga de archivos PDF + anexos (ZIP, XML, PSD)
- Validación de duplicados en tiempo real
- Integración con catálogo de empresas
- Sistema de observaciones (5000 caracteres)
- Exportación a Excel

**Formulario Optimizado** (cargar_nueva.html):
- **Línea 1**: NIT Emisor, Razón Social, Prefijo, Folio, Empresa, Fecha Exp (6 campos)
- **Línea 2**: F.Radicación, Tipo Doc, F.Pago, Clasificación, Dpto, V.Bruto, IVA, Total (8 campos)
- **Línea 3**: Observaciones, Archivo Principal, Anexos, Seg.Social (4 campos)
- Cálculo automático de valor total (Bruto + IVA)

**Permisos Críticos**:
- `cambiar_estado` - Actualizar estado de factura
- `cargar_firmado` - Subir documento firmado digitalmente
- `configurar_rutas` - Administrar rutas de almacenamiento
- `editar_factura` - Modificar datos de factura digital
- `enviar_a_firmar` - Enviar factura para firma digital (Adobe Sign)

**Modelos**:
- `FacturaDigital` - Facturas radicadas
- `AnexoFactura` - Archivos adjuntos
- `EstadoFactura` - Estados (pendiente, enviada, firmada, contabilizada)

**Templates**:
- `templates/facturas_digitales/cargar_nueva.html` (1500+ líneas) ⭐ **OPTIMIZADO**
- `templates/facturas_digitales/dashboard.html` (800+ líneas)
- `templates/facturas_digitales/listado.html` (500+ líneas)
- `templates/facturas_digitales/detalle.html` (400+ líneas)

---

### 5. 🔹 CAUSACIONES - Causaciones Contables
**Estado**: ✅ Operativo  
**Ruta**: `/causaciones`  
**Permisos**: 16 permisos (1 crítico)

**Funcionalidades**:
- Causación de documentos contables
- Renombrado automático de archivos
- Validación de información contable
- Exportación de causaciones

**Permiso Crítico**:
- `renombrar_archivo` - Cambiar nombre de archivos de causaciones

---

### 6. 🔹 NOTAS CONTABLES - Archivo Digital
**Estado**: ✅ Operativo  
**Ruta**: `/notas-contables`  
**Permisos**: 19 permisos (4 críticos)

**Funcionalidades**:
- Gestión de notas contables
- Sistema de correcciones con validación por correo
- Búsqueda avanzada de documentos
- Exportación de notas

**Permisos Críticos**:
- `aprobar_correccion_critica` - Autorizar correcciones críticas
- `eliminar_documento` - Borrar documentos del archivo
- `solicitar_correccion_documento` - Iniciar proceso de corrección
- `validar_correccion_documento` - Ingresar código de validación

---

### 7. 🔹 DIAN vs ERP - Validación Tributaria
**Estado**: ✅ Operativo (Puerto 8097)  
**Ruta**: Aplicación independiente  
**Permisos**: 13 permisos (3 críticos)

**Funcionalidades**:
- Comparación de facturas DIAN vs ERP
- Detección de diferencias
- Asignación de responsables
- Reportes de validación
- Configuración SMTP

**Permisos Críticos**:
- `asignar_usuario_factura` - Asignar responsable a factura
- `cambiar_estado_factura` - Actualizar estado de validación
- `configurar_smtp` - Administrar configuración de correo

**Aplicación Independiente**:
- Puerto: 8097
- Base de datos: Compartida con Gestor Documental
- Módulo autónomo para auditoría tributaria

---

### 8. 🔹 TERCEROS - Gestión de Terceros
**Estado**: ✅ Operativo  
**Ruta**: `/terceros`  
**Permisos**: 16 permisos (7 críticos)

**Funcionalidades**:
- Creación y edición de terceros (proveedores, clientes)
- Validación de NIT con BD externa
- Gestión de documentos por tercero
- Activación/desactivación de terceros
- Importación masiva desde Excel

**Permisos Críticos** (7):
- `activar_tercero` - Cambiar estado activo
- `aprobar_registro` - Aprobar solicitudes de registro
- `crear_tercero` - Dar de alta nuevos terceros
- `editar_tercero` - Modificar datos existentes
- `eliminar_tercero` - Borrar terceros del sistema
- `importar_terceros` - Importar masivamente desde Excel
- `rechazar_registro` - Rechazar solicitudes de registro

---

### 9. 🔹 CONFIGURACIÓN - Configuración del Sistema
**Estado**: ✅ Operativo  
**Ruta**: `/configuracion`  
**Permisos**: 5 permisos (1 crítico)

**Funcionalidades**:
- Gestión de catálogos (empresas, departamentos, formas de pago)
- Configuración de parámetros del sistema
- Gestión de backups
- Monitoreo del sistema

**Permiso Crítico**:
- `parametros_sistema` - Configuración general del sistema

**Catálogos Disponibles**:
- Empresas (SC, LG)
- Departamentos (FINANCIERO, TECNOLOGÍA, COMPRAS, etc.)
- Formas de Pago (ESTÁNDAR, TARJETA_CREDITO)
- Tipos de Servicio (SERVICIO, COMPRA, AMBOS)
- Tipos de Documento (FACTURA, NOTA_CREDITO)

---

### 📊 Módulos Auxiliares (Sin carpeta física)

#### ARCHIVO DIGITAL
**Permisos**: 6 | **Asignados**: 27
- Gestión de archivo digital de documentos

#### GESTIÓN USUARIOS
**Permisos**: 22 | **Asignados**: 66
- Gestión avanzada de usuarios internos
- Asignación de permisos masiva

#### MONITOREO
**Permisos**: 13 | **Asignados**: 38
- Monitoreo de servidores
- Alertas de disco
- Logs del sistema
- Dashboard de backups

#### REPORTES
**Permisos**: 4 | **Asignados**: 16
- Generación de reportes
- Exportaciones personalizadas

#### USUARIOS INTERNOS
**Permisos**: 4 | **Asignados**: 12
- Gestión específica de usuarios internos

---

## 🗄️ BASE DE DATOS {#base-de-datos}

### Información General
- **Motor**: PostgreSQL 18
- **Base de Datos**: `gestor_documental`
- **Usuario**: `gestor_user`
- **Puerto**: 5432
- **Tablas**: 70+ tablas
- **Registros**: 500,000+ registros totales

### Tablas Principales

#### Usuarios y Autenticación
```sql
-- Usuarios del sistema
usuarios (
    id SERIAL PRIMARY KEY,
    tercero_id INTEGER REFERENCES terceros(id),
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro TIMESTAMP DEFAULT NOW()
)

-- Terceros (proveedores, clientes)
terceros (
    id SERIAL PRIMARY KEY,
    nit VARCHAR(20) UNIQUE NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    tipo_persona VARCHAR(20),  -- JURIDICA, NATURAL
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT NOW()
)

-- Sesiones y accesos
accesos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    ip VARCHAR(50),
    user_agent TEXT,
    exito BOOLEAN,
    motivo VARCHAR(255),
    fecha TIMESTAMP DEFAULT NOW()
)
```

#### Sistema de Permisos (171 permisos disponibles)
```sql
-- Catálogo de permisos disponibles
catalogo_permisos (
    id SERIAL PRIMARY KEY,
    modulo VARCHAR(50) NOT NULL,              -- admin, recibir_facturas, etc.
    modulo_nombre VARCHAR(100) NOT NULL,
    modulo_descripcion TEXT,
    accion VARCHAR(100) NOT NULL,             -- crear, editar, eliminar, etc.
    accion_descripcion TEXT,
    tipo_accion VARCHAR(50),
    es_critico BOOLEAN DEFAULT FALSE,         -- 42 permisos críticos
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    UNIQUE(modulo, accion)
)

-- Permisos asignados a usuarios (716 asignaciones)
permisos_usuarios (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    modulo VARCHAR(50) NOT NULL,
    accion VARCHAR(100) NOT NULL,
    permitido BOOLEAN DEFAULT TRUE,
    fecha_asignacion TIMESTAMP DEFAULT NOW(),
    asignado_por VARCHAR(50)
)

-- Auditoría de cambios de permisos
auditoria_permisos (
    id SERIAL PRIMARY KEY,
    usuario_afectado_id INTEGER,
    tipo_cambio VARCHAR(50),  -- ASIGNACION, REVOCACION
    modulo VARCHAR(50),
    accion VARCHAR(100),
    usuario_que_cambio VARCHAR(50),
    fecha_cambio TIMESTAMP DEFAULT NOW()
)
```

#### Recibir Facturas
```sql
-- Facturas temporales (editables)
facturas_temporales (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    empresa VARCHAR(10),
    nit_proveedor VARCHAR(20),
    razon_social VARCHAR(255),
    prefijo VARCHAR(20),
    folio VARCHAR(50),
    fecha_emision DATE,
    valor_total NUMERIC(15,2),
    valor_iva NUMERIC(15,2),
    fecha_creacion TIMESTAMP DEFAULT NOW()
)

-- Facturas recibidas (persistentes, NO editables)
facturas_recibidas (
    id SERIAL PRIMARY KEY,
    empresa VARCHAR(10),
    nit_proveedor VARCHAR(20),
    razon_social VARCHAR(255),
    prefijo VARCHAR(20),
    folio VARCHAR(50),
    fecha_emision DATE,
    valor_total NUMERIC(15,2),
    valor_iva NUMERIC(15,2),
    usuario_registro VARCHAR(50),
    fecha_registro TIMESTAMP DEFAULT NOW()
)

-- Observaciones (auditables)
observaciones_factura (
    id SERIAL PRIMARY KEY,
    factura_recibida_id INTEGER REFERENCES facturas_recibidas(id),
    observacion TEXT,
    usuario_registro VARCHAR(50),
    fecha_registro TIMESTAMP DEFAULT NOW()
)
```

#### Relaciones de Facturas
```sql
-- Relaciones generadas
relaciones_facturas (
    id SERIAL PRIMARY KEY,
    numero_relacion VARCHAR(20) UNIQUE,  -- REL-001, REL-002, etc.
    tercero_nit VARCHAR(20),
    razon_social VARCHAR(255),
    cantidad_facturas INTEGER,
    valor_total NUMERIC(15,2),
    tipo_generacion VARCHAR(20),  -- digital, fisica
    usuario_generador VARCHAR(100),
    fecha_generacion TIMESTAMP DEFAULT NOW()
)

-- Recepciones digitales con firma
recepciones_digitales (
    id SERIAL PRIMARY KEY,
    numero_relacion VARCHAR(20) REFERENCES relaciones_facturas(numero_relacion),
    usuario_receptor VARCHAR(100),
    nombre_receptor VARCHAR(255),
    facturas_recibidas INTEGER,
    facturas_totales INTEGER,
    completa BOOLEAN,
    firma_digital VARCHAR(255),  -- SHA256 hash
    ip_recepcion VARCHAR(50),
    user_agent TEXT,
    fecha_recepcion TIMESTAMP DEFAULT NOW()
)

-- Tokens de firma digital
tokens_firma_digital (
    id SERIAL PRIMARY KEY,
    numero_relacion VARCHAR(20),
    token VARCHAR(6),  -- PIN 6 dígitos
    usuario_receptor VARCHAR(100),
    intentos_validacion INTEGER DEFAULT 0,
    usado BOOLEAN DEFAULT FALSE,
    fecha_expiracion TIMESTAMP,  -- Validez 24 horas
    fecha_creacion TIMESTAMP DEFAULT NOW()
)
```

#### Facturas Digitales
```sql
-- Facturas digitales radicadas
facturas_digitales (
    id SERIAL PRIMARY KEY,
    numero_radicado VARCHAR(50) UNIQUE,
    empresa VARCHAR(10),
    nit_emisor VARCHAR(20),
    razon_social VARCHAR(255),
    prefijo VARCHAR(20),
    folio VARCHAR(50),
    fecha_emision DATE,
    fecha_radicacion TIMESTAMP,
    tipo_documento VARCHAR(20),  -- factura, nota_credito
    forma_pago VARCHAR(50),
    tipo_servicio VARCHAR(50),
    departamento VARCHAR(100),
    valor_bruto NUMERIC(15,2),
    valor_iva NUMERIC(15,2),
    valor_total NUMERIC(15,2),
    observaciones TEXT,
    estado VARCHAR(50) DEFAULT 'pendiente',
    usuario_radicador VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT NOW()
)

-- Archivos adjuntos
anexos_facturas (
    id SERIAL PRIMARY KEY,
    factura_digital_id INTEGER REFERENCES facturas_digitales(id),
    tipo_archivo VARCHAR(50),  -- pdf, zip, seguridad_social, soporte
    nombre_archivo VARCHAR(255),
    ruta_archivo TEXT,
    tamaño_bytes BIGINT,
    fecha_carga TIMESTAMP DEFAULT NOW()
)
```

#### Sistema de Backup
```sql
-- Configuración de backups
configuracion_backup (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) UNIQUE,  -- base_datos, archivos, codigo
    activo BOOLEAN DEFAULT TRUE,
    ruta_destino TEXT,
    frecuencia_horas INTEGER,
    retener_dias INTEGER,
    ultimo_backup TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
)

-- Historial de backups
historial_backup (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50),
    fecha_inicio TIMESTAMP,
    fecha_fin TIMESTAMP,
    estado VARCHAR(50),  -- exitoso, fallido, en_progreso
    tamaño_mb NUMERIC(10,2),
    ruta_archivo TEXT,
    mensaje TEXT,
    usuario VARCHAR(50)
)
```

### Índices Importantes
```sql
-- Índices de rendimiento
CREATE INDEX idx_usuarios_tercero ON usuarios(tercero_id);
CREATE INDEX idx_permisos_usuario ON permisos_usuarios(usuario_id);
CREATE INDEX idx_facturas_temporales_usuario ON facturas_temporales(usuario_id);
CREATE INDEX idx_facturas_recibidas_nit ON facturas_recibidas(nit_proveedor);
CREATE INDEX idx_relaciones_numero ON relaciones_facturas(numero_relacion);
CREATE INDEX idx_facturas_digitales_radicado ON facturas_digitales(numero_radicado);
CREATE INDEX idx_facturas_digitales_estado ON facturas_digitales(estado);
```

---

## 🔐 SISTEMA DE PERMISOS {#permisos}

### Arquitectura de Permisos

El sistema usa un modelo de **permisos granulares por acción y módulo**:

```
Usuario → permisos_usuarios → catalogo_permisos → Módulo.Acción
```

### Estadísticas del Sistema
- **📚 Catálogo maestro**: 171 permisos disponibles
- **📦 Módulos**: 14 módulos diferentes (9 físicos + 5 virtuales)
- **🔴 Permisos críticos**: 42 permisos
- **👤 Permisos asignados**: 716 asignaciones
- **👥 Usuarios con permisos**: 6 usuarios
- **✅ Cobertura**: 100% de módulos físicos

### Permisos por Módulo

#### Admin (9 permisos, 3 críticos)
```
✅ acceder_modulo
🔴 configuracion_avanzada
🔴 gestionar_permisos
🔴 gestionar_usuarios
✅ ver_dashboard
✅ ver_logs_auditoria
✅ ver_logs_sistema
✅ ver_reportes
✅ ver_usuarios
```

#### Recibir Facturas (15 permisos, 3 críticos)
```
✅ acceder_modulo
✅ adicionar_factura
✅ consultar_factura
🔴 eliminar_factura
✅ exportar_temporales
🔴 guardar_facturas
🔴 limpiar_todo
✅ listar_facturas
✅ validar_nit
```

#### Relaciones (14 permisos, 3 críticos)
```
✅ acceder_modulo
🔴 confirmar_recepcion
✅ consultar_recepcion
✅ eliminar_relacion
✅ exportar_relacion
✅ generar_relacion
🔴 generar_token_firma
✅ historial_recepciones
✅ listar_facturas_relacion
✅ listar_recepciones
✅ reimprimir_relacion
🔴 verificar_token
```

#### Facturas Digitales (15 permisos, 5 críticos)
```
✅ acceder_modulo
✅ cargar_factura
🔴 cambiar_estado
🔴 cargar_firmado
🔴 configurar_rutas
✅ consultar_factura
🔴 editar_factura
✅ eliminar_factura
🔴 enviar_a_firmar
✅ exportar_facturas
✅ listar_facturas
✅ validar_duplicada
```

### Decoradores de Permisos

**Archivo**: `decoradores_permisos.py`

```python
# Para endpoints JSON
@requiere_permiso('recibir_facturas', 'guardar_facturas')
def api_guardar():
    pass

# Para páginas HTML
@requiere_permiso_html('relaciones', 'acceder_modulo')
def vista_relaciones():
    pass

# Por rol
@requiere_rol('admin', 'interno')
def solo_internos():
    pass
```

### Usuarios con Más Permisos

| Usuario | Empresa | Total Permisos |
|---------|---------|---------------|
| admin | Supertiendas Cañaveral | 181 |
| eliza | Supertiendas Cañaveral | 142 |
| master | N/A | 97 |
| externa | Empresa Prueba Externa | 51 |
| KatherineCC | Supertiendas Cañaveral | 16 |

---

## 🔒 SEGURIDAD Y SESIONES {#seguridad}

### Autenticación

#### Hash de Contraseñas
- **Algoritmo**: bcrypt (10 rounds)
- **Validación**: Fuerza mínima (8+ chars, mayúscula, minúscula, número, especial)
- **Historial**: Previene reutilización de últimas 5 contraseñas

#### Sesiones
- **Duración**: 25 minutos de inactividad
- **Almacenamiento**: Flask-Session (server-side)
- **Timeout Frontend**: JavaScript con auto-logout
- **Keys de Sesión**:
  ```python
  session['usuario_id']  # ID de usuario
  session['usuario']     # Nombre de usuario
  session['nit']         # NIT activo
  session['rol']         # Rol del usuario
  session['tipo_usuario']  # interno/externo
  ```

### Timeout Automático (25 Minutos)

**Implementado en**: 66 de 70 templates (94.3%)

**Código JavaScript**:
```javascript
const SESSION_TIMEOUT = 25 * 60 * 1000; // 25 minutos

function cerrarSesionPorInactividad() {
    alert('⏰ Tu sesión ha expirado por inactividad (25 minutos).');
    fetch('/api/auth/logout', { method: 'POST' })
        .finally(() => window.location.href = '/');
}

// Reinicia contador con actividad del usuario
document.addEventListener('mousemove', reiniciarContadorSesion);
document.addEventListener('keypress', reiniciarContadorSesion);
document.addEventListener('click', reiniciarContadorSesion);
```

**Templates con Timeout**:
- ✅ Todos los módulos principales
- ✅ Todas las vistas de datos
- ✅ Todas las configuraciones
- ❌ Excluidos: login.html, error.html, templates de correo

### Protección de IP

#### Listas de Control
- **Lista Blanca**: IPs permitidas sin restricciones
- **Lista Negra**: IPs bloqueadas permanentemente
- **Lista Sospechosas**: IPs con intentos fallidos (3+ intentos → bloqueo)

#### Registro de Accesos
Todos los intentos de login se registran en `logs/security.log`:

```
2025-12-01 10:30:45 | LOGIN EXITOSO | usuario=admin | ip=192.168.1.100 | nit=805028041
2025-12-01 10:35:12 | LOGIN FALLIDO | usuario=test | ip=10.0.0.50 | motivo=Contraseña incorrecta
2025-12-01 10:40:33 | IP BLOQUEADA | ip=10.0.0.50 | motivo=3 intentos fallidos
```

### CORS (Cross-Origin Resource Sharing)
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8099", "http://localhost:8097"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})
```

### Protección CSRF
- Habilitada para todos los formularios
- Token de sesión único por usuario
- Validación automática en Flask

---

## 💾 SISTEMA DE BACKUP {#backup}

### Información General
**Archivo**: `backup_manager.py` (540 líneas)  
**Configuración**: Tabla `configuracion_backup`  
**Historial**: Tabla `historial_backup`  
**Logs**: `logs/backup.log`

### Tipos de Backup

#### 1. Backup de Base de Datos
- **Comando**: `pg_dump`
- **Formato**: `.backup` (formato custom PostgreSQL)
- **Retención**: 30 días
- **Frecuencia**: Diaria (configurable)
- **Ruta**: `C:\Backups_GestorDocumental\backup_bd_YYYYMMDD_HHMMSS.backup`

#### 2. Backup de Archivos
- **Carpetas**:
  - `documentos_terceros/` (50,000+ archivos)
  - `documentos_contables/`
  - `facturas_digitales/`
- **Formato**: `.zip` comprimido
- **Retención**: 15 días
- **Frecuencia**: Semanal
- **Ruta**: `C:\Backups_GestorDocumental\backup_archivos_YYYYMMDD_HHMMSS.zip`

#### 3. Backup de Código
- **Incluye**:
  - `app.py`, `extensions.py`
  - `modules/` (todos los módulos)
  - `templates/`
  - `sql/` (schemas)
  - `requirements.txt`
- **Excluye**: `.venv`, `__pycache__`, `logs/`
- **Formato**: `.zip`
- **Retención**: 60 días
- **Frecuencia**: Mensual
- **Ruta**: `C:\Backups_GestorDocumental\backup_codigo_YYYYMMDD_HHMMSS.zip`

### Ejecutar Backups

#### Backup Individual
```powershell
cd "C:\...\GESTOR_DOCUMENTAL"
python backup_manager.py bd          # Solo base de datos
python backup_manager.py archivos    # Solo archivos
python backup_manager.py codigo      # Solo código
```

#### Backup Completo
```powershell
python backup_manager.py todos       # Todos los backups
```

#### Restauración
```powershell
# Restaurar BD
pg_restore -U gestor_user -d gestor_documental backup_bd_20251201_103045.backup

# Restaurar archivos
unzip backup_archivos_20251201_103045.zip -d .

# Restaurar código
unzip backup_codigo_20251201_103045.zip -d .
```

### API de Backups

#### Endpoints
```python
POST /api/backup/ejecutar
    Body: {"tipo": "bd|archivos|codigo|todos"}
    Response: {"success": true, "archivo": "...", "tamaño_mb": 150.5}

GET /api/backup/historial
    Response: [{"id": 1, "tipo": "bd", "fecha": "...", "estado": "exitoso"}]

GET /api/backup/configuracion
    Response: {"bd": {...}, "archivos": {...}, "codigo": {...}}

PUT /api/backup/configuracion
    Body: {"tipo": "bd", "activo": true, "frecuencia_horas": 24}
```

### Monitoreo de Backups

**Dashboard**: Accesible desde módulo de Monitoreo

**Métricas**:
- Último backup exitoso por tipo
- Tamaño promedio de backups
- Fallos recientes
- Espacio en disco disponible

**Alertas**:
- Email si backup falla
- Telegram si espacio < 10GB
- Log en `logs/backup.log`

---

## ⚙️ CONFIGURACIÓN Y DESPLIEGUE {#configuración}

### Variables de Entorno (.env)

```env
# Base de Datos
DATABASE_URL=postgresql://gestor_user:password@localhost:5432/gestor_documental

# Flask
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura
FLASK_ENV=production
FLASK_DEBUG=False

# Puertos
PORT=8099
DIAN_VS_ERP_PORT=8097

# Rutas de Almacenamiento
DOCUMENTOS_TERCEROS=C:\GestorDocumental\documentos_terceros
DOCUMENTOS_CONTABLES=C:\GestorDocumental\documentos_contables
FACTURAS_DIGITALES=C:\GestorDocumental\facturas_digitales

# Rutas de Backup
BACKUP_DIR=C:\Backups_GestorDocumental

# Correo Electrónico
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=gestordocumentalsc01@gmail.com
MAIL_PASSWORD=tu_app_password
MAIL_DEFAULT_SENDER=gestordocumentalsc01@gmail.com

# Telegram (Opcional)
TELEGRAM_BOT_TOKEN=tu_token_bot
TELEGRAM_CHAT_ID=tu_chat_id

# Adobe Sign (Firma Digital)
ADOBE_CLIENT_ID=tu_client_id
ADOBE_CLIENT_SECRET=tu_client_secret
ADOBE_API_BASE_URL=https://api.na4.adobesign.com/api/rest/v6
```

### Instalación en Producción

#### 1. Requisitos Previos
```powershell
# Python 3.11+
python --version

# PostgreSQL 18
psql --version

# Git (opcional)
git --version
```

#### 2. Clonar/Copiar Proyecto
```powershell
cd C:\
mkdir GestorDocumental
cd GestorDocumental
# Copiar archivos del transportable
```

#### 3. Crear Entorno Virtual
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

#### 4. Instalar Dependencias
```powershell
pip install -r requirements.txt
```

#### 5. Configurar Base de Datos
```powershell
# Crear usuario y BD
psql -U postgres -f sql\init_postgres.sql

# Crear esquema
psql -U gestor_user -d gestor_documental -f sql\schema_core.sql
```

#### 6. Configurar .env
```powershell
copy .env.example .env
notepad .env  # Editar con tus datos
```

#### 7. Iniciar Servidor
```powershell
# Desarrollo
python app.py

# Producción (Gunicorn)
gunicorn -w 4 -b 0.0.0.0:8099 app:app
```

### Configuración de NGINX (Reverse Proxy)

```nginx
# /etc/nginx/sites-available/gestor-documental

upstream gestor_documental {
    server 127.0.0.1:8099;
}

upstream dian_vs_erp {
    server 127.0.0.1:8097;
}

server {
    listen 80;
    server_name gestor.supertiendascanaveral.com;

    # Redirigir a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name gestor.supertiendascanaveral.com;

    ssl_certificate /etc/ssl/certs/gestor.crt;
    ssl_certificate_key /etc/ssl/private/gestor.key;

    # Gestor Documental Principal
    location / {
        proxy_pass http://gestor_documental;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout para archivos grandes
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }

    # DIAN vs ERP
    location /dian-vs-erp/ {
        proxy_pass http://dian_vs_erp/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Archivos estáticos
    location /static/ {
        alias /var/www/gestor-documental/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Límites de carga
    client_max_body_size 100M;
}
```

### Servicio Systemd (Linux)

```ini
# /etc/systemd/system/gestor-documental.service

[Unit]
Description=Gestor Documental - Supertiendas Cañaveral
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/gestor-documental
Environment="PATH=/var/www/gestor-documental/.venv/bin"
ExecStart=/var/www/gestor-documental/.venv/bin/gunicorn -w 4 -b 127.0.0.1:8099 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Comandos**:
```bash
sudo systemctl enable gestor-documental
sudo systemctl start gestor-documental
sudo systemctl status gestor-documental
sudo systemctl restart gestor-documental
```

### Tarea Programada de Backups (Windows)

```powershell
# Crear tarea programada para backup diario
$action = New-ScheduledTaskAction -Execute "C:\GestorDocumental\.venv\Scripts\python.exe" -Argument "C:\GestorDocumental\backup_manager.py todos" -WorkingDirectory "C:\GestorDocumental"

$trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM

Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "GestorDocumental_Backup" -Description "Backup diario automático del Gestor Documental"
```

---

## 📖 GUÍA DE USUARIO {#guía-usuario}

### Primer Acceso

#### 1. Login
- **URL**: `http://localhost:8099` o `https://gestor.supertiendascanaveral.com`
- **Credenciales**: Proporcionadas por el administrador
- **Sesión**: Expira después de 25 minutos de inactividad

#### 2. Establecer Contraseña (Primer Login)
1. Ingresar con credenciales temporales
2. Sistema redirige a establecer contraseña nueva
3. Contraseña debe cumplir requisitos:
   - 8+ caracteres
   - Al menos 1 mayúscula
   - Al menos 1 minúscula
   - Al menos 1 número
   - Al menos 1 carácter especial

#### 3. Dashboard Principal
- Vista de módulos según permisos
- Acceso rápido a funciones frecuentes
- Notificaciones pendientes

### Módulos Principales

#### 📄 Recibir Facturas

**Flujo de Trabajo**:
1. Click en "Recibir Facturas" en menú
2. Click en "Nueva Factura"
3. Completar formulario (3 líneas optimizadas):
   - **Línea 1**: NIT, Razón Social (se autocompleta), Prefijo, Folio, Empresa, Fecha
   - **Línea 2**: Tipo, Forma Pago, Clasificación, Departamento, Valores
   - **Línea 3**: Observaciones, Archivos
4. Click "Adicionar a Lista" (se puede editar)
5. Seleccionar facturas a guardar
6. Click "Guardar Facturas" (se persiste en BD, NO editable)
7. Exportar a Excel si necesario

**Tips**:
- El NIT valida automáticamente con la BD
- Puedes editar facturas temporales antes de guardar
- Usa "Limpiar Todo" para empezar de nuevo
- El valor total se calcula automáticamente (Bruto + IVA)

#### 🔗 Generar Relación

**Flujo de Trabajo**:
1. Click en "Relaciones" → "Generar Relación"
2. Filtrar facturas por fecha (default: HOY)
3. Sistema resalta facturas ya relacionadas (amarillo)
4. Seleccionar facturas (validación anti-duplicados)
5. Elegir tipo:
   - **📱 Digital (Sin Impresión)**: Genera relación + token firma
   - **🖨️ Física (Con Excel)**: Descarga Excel
6. Sistema genera consecutivo REL-XXX
7. Si digital: Redirige a recepción digital

#### ✅ Recepción Digital

**Flujo de Trabajo**:
1. Click en "Relaciones" → "Recepción Digital"
2. Buscar por número de relación (ej: REL-001)
3. Sistema muestra facturas de la relación
4. Marcar checkboxes de facturas recibidas físicamente
5. Contador en tiempo real: "8 de 15 facturas (53%)"
6. Click "Confirmar Recepción Digital"
7. Ingresar token de firma (6 dígitos, validez 24h)
8. Sistema crea firma SHA256 y registra auditoría

#### 📱 Facturas Digitales - Radicación

**Flujo de Trabajo (Optimizado Dic 2025)**:
1. Click en "Facturas Digitales" → "Cargar Nueva"
2. Formulario optimizado en 3 líneas:
   - **Línea 1**: Datos del emisor y documento básico
   - **Línea 2**: Información contable completa
   - **Línea 3**: Observaciones y archivos adjuntos
3. Cargar archivos:
   - **PDF Principal** (requerido)
   - Anexos opcionales: ZIP (XML/PSD), Seguridad Social
4. Sistema valida duplicados en tiempo real
5. Click "Adicionar a Lista"
6. Seleccionar facturas y "Radicar"
7. Sistema genera número de radicado automático

**Mejoras Recientes**:
- ✅ Formulario compacto (3 líneas vs 10+ anteriores)
- ✅ Cálculo automático de valor total
- ✅ Validación de duplicados instantánea
- ✅ Sincronización automática de campos

---

## 🔧 TROUBLESHOOTING {#troubleshooting}

### Problemas Comunes

#### ❌ Error: "Sesión expirada"
**Causa**: Inactividad de 25 minutos  
**Solución**: Volver a hacer login  
**Prevención**: Mover el mouse cada 20 minutos

#### ❌ Error: "Usuario inactivo"
**Causa**: Cuenta desactivada por administrador  
**Solución**: Contactar al administrador para activación  
**Admin**: Usar endpoint `/api/admin/activar_usuario`

#### ❌ Error: "Permiso denegado"
**Causa**: Usuario no tiene el permiso necesario  
**Solución**: Solicitar permiso al administrador  
**Admin**: Asignar permiso en módulo de Gestión de Usuarios

#### ❌ Error: "Factura duplicada"
**Causa**: Prefijo + Folio ya existe en BD  
**Solución**: Verificar datos o usar prefijo/folio diferente  
**Nota**: El sistema detecta duplicados en `facturas_recibidas` y `facturas_digitales`

#### ❌ Error: "NIT no encontrado"
**Causa**: NIT no existe en tabla `terceros`  
**Solución**: Crear tercero primero en módulo de Terceros  
**Admin**: Importar terceros masivamente desde Excel

#### ❌ Error: "Token de firma inválido"
**Causa**: Token expirado (>24h) o 3+ intentos fallidos  
**Solución**: Generar nuevo token  
**Nota**: Tokens son de un solo uso

#### ❌ Error: "Base de datos no disponible"
**Causa**: PostgreSQL no está corriendo  
**Solución**:
```powershell
# Windows
net start postgresql-x64-18

# Linux
sudo systemctl start postgresql
```

#### ❌ Error: "Puerto 8099 ya en uso"
**Causa**: Otra instancia de Flask corriendo  
**Solución**:
```powershell
# Windows
netstat -ano | findstr :8099
taskkill /PID <PID> /F

# Linux
sudo lsof -ti:8099 | xargs kill -9
```

### Logs del Sistema

#### Ubicación
```
logs/
├── app.log                    # Log general de aplicación
├── security.log               # Logs de autenticación y permisos
├── errors.log                 # Errores críticos
├── facturas_digitales.log     # Módulo facturas digitales
├── relaciones.log             # Módulo relaciones
└── backup.log                 # Sistema de backups
```

#### Ver Logs en Tiempo Real
```powershell
# Windows
Get-Content logs\app.log -Wait -Tail 50

# Linux
tail -f logs/app.log
```

#### Buscar Errores
```powershell
# Windows
Select-String -Path logs\errors.log -Pattern "ERROR" | Select-Object -Last 20

# Linux
grep "ERROR" logs/errors.log | tail -20
```

### Mantenimiento

#### Limpieza de Logs (Mensual)
```powershell
# Rotar logs antiguos
python -c "from backup_manager import rotar_logs; rotar_logs()"
```

#### Limpieza de Archivos Temporales
```powershell
# Eliminar carpetas TEMP de más de 30 días
$temp_dirs = Get-ChildItem "documentos_terceros" -Filter "*-TEMP-*" | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)}
$temp_dirs | Remove-Item -Recurse -Force
```

#### Optimización de Base de Datos
```sql
-- Ejecutar mensualmente
VACUUM ANALYZE;
REINDEX DATABASE gestor_documental;
```

#### Verificar Integridad de Backups
```powershell
# Listar backups recientes
python backup_manager.py listar

# Verificar último backup de BD
pg_restore --list backup_bd_20251201_103045.backup
```

---

## 📞 CONTACTO Y SOPORTE

### Equipo de Desarrollo
- **Desarrollador Principal**: Ricardo Riascos
- **Email**: ricardo.riascos@supertiendascanaveral.com
- **Telegram**: @ricardo_riascos

### Administradores del Sistema
- **Admin Principal**: admin@supertiendascanaveral.com
- **Soporte TI**: soporte.ti@supertiendascanaveral.com

### Horario de Soporte
- **Lunes a Viernes**: 8:00 AM - 6:00 PM
- **Sábados**: 8:00 AM - 12:00 PM
- **Emergencias**: 24/7 (solo incidentes críticos)

---

## 📜 HISTORIAL DE VERSIONES

### v2.8.5 (01 Diciembre 2025)
- ✅ Optimización formulario facturas digitales (3 líneas)
- ✅ Validación completa de permisos (171 permisos, 100% cobertura)
- ✅ Timeout de sesión en 66 templates (94.3%)
- ✅ Documentación completa del sistema
- ✅ Scripts de validación de permisos

### v2.8.0 (27 Noviembre 2025)
- ✅ Sistema completo de backups automatizados
- ✅ Módulo de monitoreo con alertas
- ✅ 6 archivos de logs independientes
- ✅ API REST para gestión de backups

### v2.7.0 (20 Octubre 2025)
- ✅ Módulo Relaciones completamente operativo
- ✅ Recepción digital con firma SHA256
- ✅ Sistema de tokens de firma (24h validez)
- ✅ Paginación de resultados
- ✅ Validación de facturas duplicadas

### v2.6.0 (19 Octubre 2025)
- ✅ Módulo Recibir Facturas operativo
- ✅ Sistema de facturas temporales/recibidas
- ✅ Exportación a Excel (19 columnas)
- ✅ Sistema de observaciones auditables

### v2.5.0 (17 Octubre 2025)
- ✅ Integración con Adobe Sign
- ✅ Firma masiva de documentos
- ✅ 115+ páginas de documentación Adobe

---

## 📄 LICENCIA Y TÉRMINOS

**Propietario**: Supertiendas Cañaveral S.A.S  
**Uso**: Exclusivo interno - Prohibida distribución  
**Confidencialidad**: Sistema contiene información sensible

---

**FIN DE LA DOCUMENTACIÓN**

*Documento generado automáticamente*  
*Última actualización: 01 de Diciembre de 2025, 11:00 AM*
