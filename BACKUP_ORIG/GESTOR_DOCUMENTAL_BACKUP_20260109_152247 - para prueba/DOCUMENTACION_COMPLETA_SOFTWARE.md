# 📚 DOCUMENTACIÓN COMPLETA - SISTEMA DE GESTIÓN DOCUMENTAL

**Proyecto:** Sistema de Gestión Documental  
**Cliente:** Supertiendas Cañaveral S.A.S.  
**Versión:** 1.0  
**Fecha:** 29 de Diciembre de 2025  

---

## 📑 ÍNDICE GENERAL

### PARTE 1: VISIÓN GENERAL
1. [Descripción del Sistema](#1-descripción-del-sistema)
2. [Arquitectura General](#2-arquitectura-general)
3. [Tecnologías Utilizadas](#3-tecnologías-utilizadas)
4. [Estructura de Directorios](#4-estructura-de-directorios)

### PARTE 2: MÓDULOS DEL SISTEMA
5. [Módulo de Autenticación](#5-módulo-de-autenticación)
6. [Módulo Recibir Facturas](#6-módulo-recibir-facturas)
7. [Módulo Relaciones](#7-módulo-relaciones)
8. [Módulo DIAN vs ERP](#8-módulo-dian-vs-erp)
9. [Módulo Causaciones](#9-módulo-causaciones)
10. [Módulo Configuración](#10-módulo-configuración)
11. [Módulo Administración](#11-módulo-administración)

### PARTE 3: COMPONENTES TRANSVERSALES
12. [Base de Datos](#12-base-de-datos)
13. [Sistema de Permisos](#13-sistema-de-permisos)
14. [Sistema de Auditoría](#14-sistema-de-auditoría)
15. [Sistema de Correos](#15-sistema-de-correos)

### PARTE 4: DESPLIEGUE Y OPERACIÓN
16. [Instalación](#16-instalación)
17. [Configuración](#17-configuración)
18. [Mantenimiento](#18-mantenimiento)
19. [Troubleshooting](#19-troubleshooting)

---

# PARTE 1: VISIÓN GENERAL

## 1. DESCRIPCIÓN DEL SISTEMA

### 1.1 Propósito

El **Sistema de Gestión Documental** es una plataforma web diseñada para **Supertiendas Cañaveral S.A.S.** que automatiza y centraliza la gestión de documentos electrónicos provenientes de la DIAN, incluyendo:

- 📄 Facturas electrónicas
- 📝 Notas crédito y débito
- 📊 Documentos de soporte
- 🔐 Firma digital de documentos
- 📧 Notificaciones automáticas

### 1.2 Objetivos Principales

✅ **Centralización:** Un solo punto de acceso a todos los documentos electrónicos  
✅ **Trazabilidad:** Registro completo de todas las acciones realizadas  
✅ **Automatización:** Reducir tareas manuales mediante procesos automáticos  
✅ **Control:** Sistema robusto de permisos y roles de usuario  
✅ **Integración:** Conexión con sistemas externos (DIAN, ERP, Adobe Sign)  

### 1.3 Usuarios del Sistema

| Rol | Descripción | Acceso |
|-----|-------------|--------|
| **Admin** | Administrador del sistema | Total |
| **Interno** | Empleado de Supertiendas Cañaveral | Módulos según permisos |
| **Externo** | Proveedor o tercero | Solo sus documentos |

---

## 2. ARQUITECTURA GENERAL

### 2.1 Arquitectura de Alto Nivel

```
┌──────────────────────────────────────────────────────────────┐
│                     CAPA DE PRESENTACIÓN                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   HTML5      │  │   CSS3       │  │  JavaScript  │       │
│  │   Jinja2     │  │   Bootstrap  │  │  Tabulator   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────┴───────────────────────────────────────┐
│                     CAPA DE APLICACIÓN                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Flask Application (app.py)               │   │
│  │                  - Blueprints                         │   │
│  │                  - Middleware                         │   │
│  │                  - Session Management                 │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐ │
│  │  Recibir   │ │ Relaciones │ │  DIAN vs  │ │  Admin   │ │
│  │  Facturas  │ │            │ │    ERP    │ │          │ │
│  └────────────┘ └────────────┘ └────────────┘ └──────────┘ │
└──────────────────────┬───────────────────────────────────────┘
                       │ SQLAlchemy ORM
┌──────────────────────┴───────────────────────────────────────┐
│                     CAPA DE DATOS                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            PostgreSQL 18 (gestor_documental)          │   │
│  │  - 30+ tablas                                         │   │
│  │  - 785K+ registros en maestro                        │   │
│  │  - Relaciones con integridad referencial             │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                 SISTEMAS EXTERNOS                             │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐               │
│  │   DIAN    │  │ Adobe Sign│  │   SMTP    │               │
│  │   APIs    │  │  REST API │  │  Gmail    │               │
│  └───────────┘  └───────────┘  └───────────┘               │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Flujo de Peticiones

```
1. Usuario accede al navegador
         ↓
2. Login → Validación de credenciales
         ↓
3. Sistema verifica permisos
         ↓
4. Carga dashboard según rol
         ↓
5. Usuario navega a módulo (ej: Recibir Facturas)
         ↓
6. Blueprint procesa petición
         ↓
7. Consulta a PostgreSQL
         ↓
8. Respuesta JSON al frontend
         ↓
9. Renderizado con JavaScript
```

### 2.3 Patrón de Arquitectura

El sistema utiliza **arquitectura modular basada en Flask Blueprints**:

```python
# Patrón estándar de módulo
modules/
└── nombre_modulo/
    ├── __init__.py          # Definición del Blueprint
    ├── routes.py            # Endpoints HTTP
    ├── models.py            # Modelos SQLAlchemy
    └── services.py          # Lógica de negocio
```

**Ventajas:**
- ✅ Separación de responsabilidades
- ✅ Código modular y mantenible
- ✅ Fácil escalabilidad
- ✅ Testing independiente por módulo

---

## 3. TECNOLOGÍAS UTILIZADAS

### 3.1 Backend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.11+ | Lenguaje principal |
| **Flask** | 3.0+ | Framework web |
| **SQLAlchemy** | 2.0+ | ORM para base de datos |
| **Flask-Bcrypt** | 1.0+ | Hash de contraseñas |
| **Flask-Mail** | 0.9+ | Envío de correos |
| **APScheduler** | 3.10+ | Tareas programadas |
| **openpyxl** | 3.1+ | Exportación a Excel |
| **python-dotenv** | 1.0+ | Variables de entorno |

### 3.2 Frontend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **HTML5** | - | Estructura de páginas |
| **CSS3** | - | Estilos y diseño |
| **JavaScript ES6** | - | Interactividad |
| **Bootstrap** | 5.3+ | Framework CSS |
| **Jinja2** | 3.1+ | Motor de templates |
| **Tabulator.js** | 5.5+ | Tablas interactivas |

### 3.3 Base de Datos

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **PostgreSQL** | 18 | Base de datos principal |
| **psycopg2** | 2.9+ | Driver de conexión |

### 3.4 Integraciones Externas

| Servicio | Propósito |
|----------|-----------|
| **Adobe Sign REST API v6** | Firma digital masiva de documentos |
| **Gmail SMTP** | Envío de correos (desarrollo) |
| **Zimbra SMTP** | Envío de correos (producción) |
| **Telegram Bot API** | Notificaciones alternativas |

---

## 4. ESTRUCTURA DE DIRECTORIOS

### 4.1 Árbol Completo del Proyecto

```
gestor_documental/
├── app.py                              # ⭐ Aplicación Flask principal (2,343 líneas)
├── extensions.py                       # ⭐ Instancia compartida de SQLAlchemy
├── decoradores_permisos.py            # Sistema de decoradores de permisos
├── utils_fecha.py                     # Utilidades de zona horaria Colombia
├── backup_manager.py                  # Sistema de backups automáticos
├── config_carpetas.py                 # Configuración de rutas de archivos
│
├── .env                               # ⭐ Variables de entorno (NO en Git)
├── .env.example                       # Plantilla de configuración
├── requirements.txt                   # ⭐ Dependencias Python
│
├── modules/                           # ⭐ MÓDULOS PRINCIPALES
│   ├── recibir_facturas/             # Recepción de facturas de proveedores
│   │   ├── __init__.py
│   │   ├── routes.py                 # 1,067 líneas - 10+ endpoints
│   │   ├── models.py                 # 640 líneas - 4 modelos
│   │   └── endpoints_nuevos.py       # Desarrollo futuro
│   │
│   ├── relaciones/                   # Generación de relaciones digitales
│   │   ├── __init__.py
│   │   ├── routes.py                 # 1,595 líneas - 15+ endpoints
│   │   ├── models.py                 # 285 líneas - 5 modelos
│   │   └── backend_relaciones.py     # Backend separado puerto 5002
│   │
│   ├── dian_vs_erp/                  # Visor maestro y sincronización
│   │   ├── __init__.py
│   │   ├── routes.py                 # 3,231 líneas - Visor principal
│   │   ├── models.py                 # 458 líneas - Maestro DIAN
│   │   ├── sync_service.py           # 457 líneas - Sincronización
│   │   └── scheduler_envios.py       # 1,056 líneas - Envíos programados
│   │
│   ├── causaciones/                  # ⚠️ EN CONSTRUCCIÓN
│   │   ├── models.py
│   │   └── routes.py
│   │
│   ├── configuracion/                # Configuración del sistema
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── models.py
│   │
│   └── admin/                        # Administración de usuarios
│       ├── __init__.py
│       └── routes.py
│
├── templates/                         # ⭐ PLANTILLAS HTML
│   ├── login.html                    # 2,480 líneas - SPA de autenticación
│   ├── nueva_factura_REFACTORED.html # 3,000+ líneas - Recepción de facturas
│   ├── generar_relacion_REFACTORED.html # 1,700+ líneas - Generación de relaciones
│   ├── recepcion_digital.html        # 800+ líneas - Recepción digital
│   ├── visor_moderno.html            # 1,500+ líneas - Visor DIAN vs ERP
│   └── ...
│
├── sql/                               # ⭐ ESQUEMAS DE BASE DE DATOS
│   ├── schema_core.sql               # 140 líneas - Tablas principales
│   ├── recibir_facturas_schema.sql   # Esquema módulo facturas
│   ├── causaciones_schema.sql        # Esquema módulo causaciones
│   └── schema_relaciones.sql         # Esquema módulo relaciones
│
├── logs/                              # ⭐ LOGS DEL SISTEMA
│   └── security.log                  # Registro de eventos de seguridad
│
├── documentos_terceros/               # ⭐ ALMACENAMIENTO DE DOCUMENTOS
│   ├── {NIT}-{RADICADO}-{FECHA}/    # Carpetas por tercero
│   └── ...
│
├── docs/                              # 📄 DOCUMENTACIÓN
│   ├── GUIA_INSTALACION_COMPLETA.md
│   ├── CONFIGURACION_CORREO.md
│   ├── SISTEMA_TELEGRAM.md
│   ├── GUIA_ADOBE_PARA_IMPRIMIR.md
│   └── ...
│
├── .github/
│   └── copilot-instructions.md       # ⭐ Instrucciones para AI (este archivo)
│
└── scripts/                           # Scripts de utilidad
    ├── check_user_status.py
    ├── crear_usuario_prueba.py
    ├── ver_radicados.py
    └── ...
```

### 4.2 Archivos Críticos (NO ELIMINAR)

| Archivo | Líneas | Propósito |
|---------|--------|-----------|
| `app.py` | 2,343 | Aplicación principal Flask |
| `extensions.py` | ~10 | Instancia compartida de db (evita circular imports) |
| `decoradores_permisos.py` | 103 | Sistema de permisos |
| `requirements.txt` | 80 | Dependencias del proyecto |
| `.env` | Variable | Configuración secreta |
| `sql/schema_core.sql` | 140 | Esquema de base de datos |

---

# PARTE 2: MÓDULOS DEL SISTEMA

## 5. MÓDULO DE AUTENTICACIÓN

### 5.1 Descripción

Sistema completo de autenticación y gestión de sesiones con:
- Login con NIT + Usuario + Contraseña
- Registro de terceros (proveedores)
- Recuperación de contraseña con tokens de 6 dígitos
- Gestión de sesiones con timeout de 25 minutos

### 5.2 Ubicación

- **Archivo principal:** `app.py` (líneas 1177-1500)
- **Template:** `templates/login.html` (2,480 líneas - SPA)
- **Modelos:** `Usuario`, `Tercero`, `TokenRecuperacion`, `PasswordUsada`

### 5.3 Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Página de login |
| `/api/auth/login` | POST | Autenticación de usuario |
| `/api/auth/forgot_request` | POST | Solicitar token de recuperación |
| `/api/auth/forgot_verify` | POST | Verificar token de 6 dígitos |
| `/api/auth/change_password` | POST | Cambiar contraseña |
| `/api/registro/proveedor` | POST | Validar datos de registro |
| `/api/registro/cargar_documentos` | POST | Subir documentos temporales |
| `/api/registro/finalizar` | POST | Completar registro y generar radicado |

### 5.4 Flujo de Login

```
Usuario ingresa NIT + Usuario + Contraseña
         ↓
Sistema valida en tabla usuarios
         ↓
Verifica campo activo=True
         ↓
Valida hash bcrypt de contraseña
         ↓
Crea sesión con Flask session
         ↓
session['usuario_id'] = user.id
session['usuario'] = user.usuario
session['nit'] = user.nit_tercero
session['rol'] = user.rol
         ↓
Redirige a dashboard según rol
```

### 5.5 Seguridad

- **Contraseñas:** Hash bcrypt con salt
- **Sesiones:** Flask session con SECRET_KEY
- **Timeout:** 25 minutos de inactividad
- **IPs:** Sistema de listas blanca/negra/sospechosas
- **Auditoría:** Todos los intentos registrados en `logs/security.log`

### 5.6 Registro de Terceros (3 Fases)

```
FASE 1: VALIDACIÓN DE DATOS
- Usuario llena formulario (NIT, razón social, etc.)
- Sistema valida NIT único
- NO persiste en BD aún

FASE 2: CARGA DE DOCUMENTOS
- Usuario sube 7 PDFs obligatorios
- Se guardan en carpeta temporal: {NIT}-TEMP-{fecha}/
- Sistema valida formato y tamaño

FASE 3: FINALIZACIÓN
- Persiste Tercero en BD
- Genera radicado: RAD-000027
- Crea usuarios con activo=False
- Renombra carpeta: {NIT}-RAD-000027-{fecha}/
- Envía email de confirmación
```

**Documentos Obligatorios:**
1. RUT
2. Cámara de Comercio
3. Cédula Representante Legal
4. Certificación Bancaria
5. Formulario Conocimiento del Proveedor
6. Declaración Fondos (Jurídica)
7. Declaración Fondos (Natural)

---

## 6. MÓDULO RECIBIR FACTURAS

### 6.1 Descripción

Sistema de recepción y gestión de facturas de proveedores.

### 6.2 Ubicación

```
modules/recibir_facturas/
├── __init__.py
├── routes.py          # 1,067 líneas - 10+ endpoints
└── models.py          # 640 líneas - 4 modelos
```

**Template:** `templates/nueva_factura_REFACTORED.html` (3,000+ líneas)

### 6.3 Modelos de Base de Datos

#### `FacturaTemporal`
Facturas en proceso de edición (una por sesión de usuario).

```python
class FacturaTemporal:
    id: int
    nit: str                    # NIT del proveedor
    prefijo: str                # Prefijo de factura
    folio: str                  # Número de folio
    fecha_expedicion: date
    fecha_radicacion: date
    valor_bruto: Decimal
    valor_neto: Decimal
    centro_operacion_id: int
    usuario_id: int
    fecha_creacion: datetime
```

#### `FacturaRecibida`
Facturas guardadas permanentemente.

```python
class FacturaRecibida:
    id: int
    nit: str
    prefijo: str
    folio: str
    fecha_expedicion: date
    fecha_radicacion: date
    valor_bruto: Decimal
    valor_neto: Decimal
    centro_operacion_id: int
    usuario_id: int
    fecha_creacion: datetime
```

#### `ObservacionFacturaTemporal`
Observaciones editables de facturas temporales.

```python
class ObservacionFacturaTemporal:
    id: int
    factura_temporal_id: int
    descripcion: str
    fecha_creacion: datetime
```

#### `ObservacionFactura`
Observaciones persistentes (auditoría completa).

```python
class ObservacionFactura:
    id: int
    factura_recibida_id: int
    descripcion: str
    fecha_creacion: datetime
```

### 6.4 Endpoints Principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/recibir_facturas/nueva_factura` | GET | Formulario de recepción |
| `/recibir_facturas/verificar_tercero` | GET | Valida NIT existe en BD |
| `/recibir_facturas/adicionar_factura` | POST | Crea factura temporal |
| `/recibir_facturas/cargar_facturas` | GET | Lista facturas temporales |
| `/recibir_facturas/actualizar_factura_temporal/<id>` | PUT | Edita factura |
| `/recibir_facturas/eliminar_factura/<id>` | DELETE | Elimina factura temporal |
| `/recibir_facturas/guardar_facturas` | POST | Migra a facturas recibidas |
| `/recibir_facturas/exportar_temporales` | POST | Exporta a Excel |

### 6.5 Flujo de Trabajo

```
1. Usuario ingresa NIT del proveedor
         ↓
2. Sistema valida en tabla terceros
         ↓
3. Usuario ingresa datos de factura
         ↓
4. Sistema crea FacturaTemporal
         ↓
5. Usuario puede editar/eliminar
         ↓
6. Click en "Guardar Facturas"
         ↓
7. Sistema migra a FacturaRecibida
         ↓
8. Llama sync_service.sincronizar_factura_recibida()
         ↓
9. Actualiza maestro_dian_vs_erp
         ↓
10. Facturas ahora visibles en DIAN vs ERP
```

### 6.6 Estado Actual

✅ **OPERATIVO** (Desde Octubre 19, 2025)
- 10+ endpoints funcionando
- Validación en tiempo real
- Edición y eliminación de facturas temporales
- Exportación a Excel (19 columnas)
- Sincronización con maestro DIAN

---

## 7. MÓDULO RELACIONES

### 7.1 Descripción

Sistema de generación y recepción digital de relaciones de facturas.

### 7.2 Ubicación

```
modules/relaciones/
├── __init__.py
├── routes.py              # 1,595 líneas - 15+ endpoints
├── models.py              # 285 líneas - 5 modelos
└── backend_relaciones.py  # Backend separado puerto 5002
```

**Templates:**
- `templates/generar_relacion_REFACTORED.html` (1,700+ líneas)
- `templates/recepcion_digital.html` (800+ líneas)

### 7.3 Modelos de Base de Datos

#### `RelacionFactura`
Encabezado de la relación.

```python
class RelacionFactura:
    numero_relacion: str      # REL-001, REL-002, etc.
    tercero_nit: str
    razon_social: str
    cantidad_facturas: int
    valor_total: Decimal
    tipo_generacion: str      # "digital" o "fisica"
    usuario_generador: str
    fecha_generacion: datetime
```

#### `RecepcionDigital`
Registro de recepción con firma SHA256.

```python
class RecepcionDigital:
    numero_relacion: str
    usuario_receptor: str
    nombre_receptor: str
    facturas_recibidas: int
    facturas_totales: int
    completa: bool
    firma_digital: str        # SHA256 hash
    ip_recepcion: str
    user_agent: str
    fecha_recepcion: datetime
```

#### `FacturaRecibidaDigital`
Facturas individuales de la relación.

```python
class FacturaRecibidaDigital:
    numero_relacion: str
    prefijo: str
    folio: str
    recibida: bool
    usuario_receptor: str
    fecha_recepcion: datetime
```

#### `TokenFirmaDigital`
Tokens de 6 dígitos para firma digital.

```python
class TokenFirmaDigital:
    numero_relacion: str
    token: str                # 6 dígitos
    usuario_receptor: str
    intentos_validacion: int
    usado: bool
    fecha_expiracion: datetime  # 24 horas
    fecha_creacion: datetime
```

#### `Consecutivo`
Gestión de consecutivos.

```python
class Consecutivo:
    tipo: str                 # "relaciones"
    ultimo_numero: int        # Autoincremental
```

### 7.4 Endpoints Principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/relaciones/generar_relacion` | GET/POST | Genera relación digital o física |
| `/relaciones/filtrar_facturas` | POST | Filtra facturas por fecha |
| `/relaciones/recepcion_digital` | GET | Módulo de recepción digital |
| `/relaciones/buscar_relacion_recepcion` | POST | Busca relación para recibir |
| `/relaciones/confirmar_recepcion_digital` | POST | Confirma con firma SHA256 |
| `/relaciones/generar_token_firma` | POST | Genera token de 6 dígitos |
| `/relaciones/verificar_token_firma` | POST | Valida token |
| `/relaciones/exportar_relacion/<numero>` | GET | Exporta a Excel |

### 7.5 Flujo de Generación de Relación

```
1. Usuario selecciona facturas (filtro por fecha)
         ↓
2. Sistema resalta facturas ya relacionadas (amarillo)
         ↓
3. Usuario elige tipo: Digital o Física
         ↓
4. Sistema genera consecutivo: REL-001
         ↓
5. Inserta en relaciones_facturas
         ↓
6. Llama sync_service.sincronizar_factura_en_tramite()
         ↓
7. Actualiza maestro_dian_vs_erp
         ↓
8. Si digital → Redirige a recepción digital
   Si física → Descarga Excel
```

### 7.6 Flujo de Recepción Digital

```
1. Usuario receptor busca relación: REL-001
         ↓
2. Sistema valida relación existe
         ↓
3. Muestra tabla de facturas
         ↓
4. Usuario marca facturas recibidas físicamente
         ↓
5. Click en "Confirmar Recepción"
         ↓
6. Sistema solicita token de firma
         ↓
7. Usuario ingresa token de 6 dígitos
         ↓
8. Sistema valida token (3 intentos máx)
         ↓
9. Genera firma SHA256:
   hash(numero_relacion + usuario + fecha + cantidad)
         ↓
10. Inserta en recepciones_digitales
         ↓
11. Log de auditoría completo
```

### 7.7 Estado Actual

✅ **OPERATIVO** (Desde Octubre 20, 2025)
- Generación de relaciones digitales
- Recepción digital con firma SHA256
- Sistema de tokens de firma (24h validez)
- Paginación (10/25/50/100 por página)
- Bloqueo de facturas duplicadas
- Auditoría completa

---

## 8. MÓDULO DIAN VS ERP

### 8.1 Descripción

Visor maestro de todos los documentos electrónicos con sincronización entre módulos.

### 8.2 Ubicación

```
modules/dian_vs_erp/
├── __init__.py
├── routes.py           # 3,231 líneas - Visor principal
├── models.py           # 458 líneas - Maestro DIAN
├── sync_service.py     # 457 líneas - Sincronización
└── scheduler_envios.py # 1,056 líneas - Envíos programados
```

**Template:** `templates/visor_moderno.html` (1,500+ líneas)

### 8.3 Tabla Principal: `maestro_dian_vs_erp`

**Registros:** ~785,642 documentos  
**Tamaño:** ~1.2 GB

```sql
CREATE TABLE maestro_dian_vs_erp (
    id SERIAL PRIMARY KEY,
    nit_emisor VARCHAR(20),
    razon_social VARCHAR(255),
    prefijo VARCHAR(10),
    folio VARCHAR(20),
    cufe VARCHAR(255) UNIQUE,
    
    fecha_emision DATE,
    fecha_recibida TIMESTAMP,
    fecha_causacion TIMESTAMP,
    dias_desde_emision INTEGER,
    
    valor NUMERIC(15,2),
    
    estado_contable VARCHAR(50),    -- CRÍTICO
    estado_aprobacion VARCHAR(50),
    tipo_documento VARCHAR(100),
    forma_pago VARCHAR(10),
    tipo_tercero VARCHAR(50),
    
    recibida BOOLEAN,
    causada BOOLEAN,
    rechazada BOOLEAN,
    
    usuario_recibio VARCHAR(100),
    usuario_causacion VARCHAR(100),
    origen_sincronizacion VARCHAR(100),
    
    UNIQUE (nit_emisor, prefijo, folio)
);
```

### 8.4 Estados Contables

| Estado | Origen | Descripción |
|--------|--------|-------------|
| **Recibida** | Módulo Recibir Facturas | Factura recibida |
| **En Trámite** | Módulo Relaciones | En relación generada |
| **Causada** | Módulo Causaciones | Procesada en contabilidad |
| **Rechazada** | Cualquier módulo | Rechazada |
| **No Registrada** | Por defecto | No procesada |

### 8.5 Sistema de Sincronización

**Archivo:** `sync_service.py` (457 líneas)

#### Funciones Principales

```python
sincronizar_factura_recibida(nit, prefijo, folio, fecha, usuario, origen)
  → Marca como "Recibida" en maestro

sincronizar_factura_en_tramite(nit, prefijo, folio, numero_relacion, usuario)
  → Marca como "En Trámite"

sincronizar_factura_causada(nit, prefijo, folio, usuario)
  → Marca como "Causada"

sincronizar_factura_rechazada(nit, prefijo, folio, motivo, usuario, origen)
  → Marca como "Rechazada"
```

### 8.6 Sistema de Envíos Programados

**Archivo:** `scheduler_envios.py` (1,056 líneas)  
**Tecnología:** APScheduler 3.10

#### Tipos de Envíos

1. **Sin Causar >= 5 Días**
   - Frecuencia: Diario 08:00 (Lun-Vie)
   - Destinatario: supervisor@supertiendascanaveral.com
   - Formato: HTML + Excel adjunto

2. **Crédito Sin Acuses Completos**
   - Frecuencia: Diario 14:00
   - Filtro: forma_pago='2'

3. **Débito Sin Acuses Completos**
   - Frecuencia: Diario 08:00

4. **Pendientes >= 3 Días**
   - Frecuencia: Diario 08:00

### 8.7 Estado Actual

✅ **OPERATIVO**
- Visor con 785K+ documentos
- Sincronización entre módulos
- Envíos programados activos
- Fix aplicado (28/12/2025): Prioriza estado_contable real sobre cálculos legacy

**Documentación Completa:** Ver `DOCUMENTACION_MODULO_DIAN_VS_ERP.md`

---

## 9. MÓDULO CAUSACIONES

### 9.1 Estado

⚠️ **EN CONSTRUCCIÓN**

### 9.2 Ubicación

```
modules/causaciones/
├── models.py
└── routes.py
```

### 9.3 Propósito (Planificado)

- Causación de facturas en sistema contable
- Integración con ERP
- Generación de comprobantes
- Actualización de estado en maestro DIAN

---

## 10. MÓDULO CONFIGURACIÓN

### 10.1 Descripción

Configuración general del sistema.

### 10.2 Ubicación

```
modules/configuracion/
├── __init__.py
├── routes.py
└── models.py
```

### 10.3 Funcionalidades

- Configuración de terceros
- Gestión de centros operativos
- Configuración de empresas
- Parámetros del sistema

---

## 11. MÓDULO ADMINISTRACIÓN

### 11.1 Descripción

Gestión de usuarios, permisos y roles.

### 11.2 Ubicación

```
modules/admin/
├── __init__.py
└── routes.py
```

### 11.3 Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/admin/listar_usuarios` | GET | Lista todos los usuarios |
| `/api/admin/activar_usuario` | POST | Activa/desactiva usuario |
| `/api/admin/agregar_usuario_tercero` | POST | Añade usuario a tercero |

---

# PARTE 3: COMPONENTES TRANSVERSALES

## 12. BASE DE DATOS

### 12.1 Información General

- **Motor:** PostgreSQL 18
- **Base de Datos:** `gestor_documental`
- **Puerto:** 5432
- **Usuario:** `gestor_user`
- **Conexión:** SQLAlchemy ORM

### 12.2 Tablas Principales

| Tabla | Registros | Propósito |
|-------|-----------|-----------|
| `maestro_dian_vs_erp` | ~785K | Documentos DIAN |
| `facturas_recibidas` | Variable | Facturas recibidas |
| `relaciones_facturas` | Variable | Relaciones generadas |
| `usuarios` | Variable | Usuarios del sistema |
| `terceros` | Variable | Proveedores y terceros |
| `permisos_usuario` | Variable | Permisos por usuario |

### 12.3 Esquemas SQL

```
sql/
├── schema_core.sql           # Tablas principales
├── recibir_facturas_schema.sql
├── causaciones_schema.sql
└── schema_relaciones.sql
```

### 12.4 Conexión

```python
# extensions.py
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# app.py
from extensions import db
db.init_app(app)
```

### 12.5 Patrón de Importación (Evitar Circular Imports)

```python
# ✅ CORRECTO - En todos los módulos
from extensions import db

# ❌ INCORRECTO - Causa circular import
from app import db
```

---

## 13. SISTEMA DE PERMISOS

### 13.1 Archivo Principal

`decoradores_permisos.py` (103 líneas)

### 13.2 Decoradores Disponibles

```python
@requiere_permiso('modulo', 'accion')
# Para endpoints JSON API

@requiere_permiso_html('modulo', 'accion')
# Para páginas HTML

@requiere_rol('admin', 'interno')
# Basado en rol de usuario
```

### 13.3 Tabla: `permisos_usuario`

```sql
CREATE TABLE permisos_usuario (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER,
    modulo VARCHAR(100),
    accion VARCHAR(100),
    permitido BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
```

### 13.4 Módulos y Acciones

| Módulo | Acciones Disponibles |
|--------|----------------------|
| `recibir_facturas` | `acceder_modulo`, `nueva_factura`, `editar`, `eliminar` |
| `relaciones` | `acceder_modulo`, `generar`, `recibir`, `exportar` |
| `dian_vs_erp` | `acceder_modulo`, `exportar`, `sincronizar` |
| `causaciones` | `acceder_modulo`, `causar`, `rechazar` |
| `configuracion` | `acceder_modulo`, `editar_terceros` |
| `admin` | `acceder_modulo`, `gestionar_usuarios`, `gestionar_permisos` |

### 13.5 Ejemplo de Uso

```python
@recibir_facturas_bp.route('/nueva_factura')
@requiere_permiso_html('recibir_facturas', 'acceder_modulo')
def nueva_factura():
    # Solo usuarios con permiso pueden acceder
    return render_template('nueva_factura_REFACTORED.html')
```

---

## 14. SISTEMA DE AUDITORÍA

### 14.1 Archivo de Logs

`logs/security.log`

### 14.2 Función de Logging

```python
def log_security(mensaje):
    """
    Registra eventos de seguridad con timestamp
    """
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('logs/security.log', 'a', encoding='utf-8') as f:
        f.write(f"[{fecha}] {mensaje}\n")
```

### 14.3 Eventos Registrados

| Tipo | Formato | Ejemplo |
|------|---------|---------|
| Login exitoso | `LOGIN OK \| usuario=X \| ip=Y` | `LOGIN OK \| usuario=admin \| ip=192.168.1.100` |
| Login fallido | `LOGIN BLOQUEADO \| usuario=X \| motivo=Y` | `LOGIN BLOQUEADO \| usuario=test \| motivo=Usuario inactivo` |
| Registro | `REGISTRO COMPLETO \| nit=X \| radicado=Y` | `REGISTRO COMPLETO \| nit=805003786 \| radicado=RAD-000027` |
| Cambio contraseña | `CAMBIO DE CONTRASEÑA \| usuario=X` | `CAMBIO DE CONTRASEÑA \| usuario=admin` |
| Token recuperación | `TOKEN RECUPERACION ENVIADO \| usuario=X` | `TOKEN RECUPERACION ENVIADO \| usuario=14652319` |
| Sincronización | `SINCRONIZACION EXITOSA \| facturas=X` | `SINCRONIZACION EXITOSA \| facturas=785642` |
| Relación generada | `RELACION GENERADA \| consecutivo=X` | `RELACION GENERADA \| consecutivo=REL-001` |
| Recepción digital | `RECEPCION DIGITAL CONFIRMADA \| relacion=X` | `RECEPCION DIGITAL CONFIRMADA \| relacion=REL-001` |

### 14.4 Monitoreo de Logs

```bash
# Ver últimos eventos
tail -n 50 logs/security.log

# Filtrar por tipo
grep "LOGIN" logs/security.log

# Buscar por usuario
grep "usuario=admin" logs/security.log

# Ver errores
grep "ERROR" logs/security.log
```

---

## 15. SISTEMA DE CORREOS

### 15.1 Configuración

**Librería:** Flask-Mail

**Variables de entorno (.env):**

```env
# Gmail (Desarrollo)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=gestordocumentalsc01@gmail.com
MAIL_PASSWORD=app_password_aqui

# Zimbra (Producción - Futuro)
MAIL_SERVER=smtp.supertiendascanaveral.com
MAIL_PORT=587
MAIL_USERNAME=rriascos@supertiendascanaveral.com
MAIL_PASSWORD=password
```

### 15.2 Tipos de Correos

#### Confirmación de Registro

**Disparador:** Al completar registro de tercero  
**Destinatario:** Email del tercero  
**Contenido:**
- Número de radicado generado
- Información del tercero
- Próximos pasos

#### Recuperación de Contraseña

**Disparador:** Solicitud de reset de contraseña  
**Destinatario:** Email del usuario  
**Contenido:**
- Token de 6 dígitos
- Validez de 10 minutos
- Instrucciones

#### Alertas DIAN vs ERP

**Disparador:** APScheduler (horarios configurados)  
**Destinatario:** Supervisor configurado  
**Contenido:**
- HTML con tabla de documentos pendientes (primeros 20)
- Excel adjunto con todos los documentos
- Estadísticas

### 15.3 Funciones de Envío

```python
def enviar_correo_confirmacion_radicado(radicado, tercero_data, destinatario):
    """Envía confirmación de registro con radicado"""
    pass

def enviar_correo_token_recuperacion(token, usuario, destinatario):
    """Envía token de recuperación de contraseña"""
    pass

def enviar_alerta_documentos_pendientes(documentos, destinatario, tipo):
    """Envía alerta programada con documentos pendientes"""
    pass
```

### 15.4 Estado Actual

✅ Gmail configurado y funcionando  
⏳ Migración a Zimbra corporativo pendiente  
📧 Envío de confirmaciones activo  
📧 Recuperación de contraseña activo  
📧 Alertas programadas activas

**Documentación Completa:** Ver `docs/CONFIGURACION_CORREO.md`

---

# PARTE 4: DESPLIEGUE Y OPERACIÓN

## 16. INSTALACIÓN

### 16.1 Requisitos Previos

- **Python:** 3.11+
- **PostgreSQL:** 18
- **Sistema Operativo:** Windows 10/11 o Linux
- **RAM:** Mínimo 4 GB
- **Disco:** Mínimo 10 GB libres

### 16.2 Instalación Paso a Paso

#### Windows

```powershell
# 1. Clonar repositorio o copiar carpeta
cd C:\ruta\del\proyecto

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno virtual
.\.venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Crear base de datos PostgreSQL
psql -U postgres -f init_postgres.sql

# 6. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 7. Iniciar servidor
python app.py
```

#### Linux

```bash
# 1. Navegar al proyecto
cd /ruta/del/proyecto

# 2. Crear entorno virtual
python3 -m venv .venv

# 3. Activar entorno virtual
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Crear base de datos PostgreSQL
sudo -u postgres psql -f init_postgres.sql

# 6. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 7. Iniciar servidor
python app.py
```

### 16.3 Verificación de Instalación

```bash
# Verificar que el servidor inició correctamente
# Debe mostrar:
# * Running on http://127.0.0.1:8099

# Acceder al navegador
http://localhost:8099
```

**Documentación Completa:** Ver `docs/GUIA_INSTALACION_COMPLETA.md`

---

## 17. CONFIGURACIÓN

### 17.1 Archivo .env (Variables de Entorno)

```env
# ===== BASE DE DATOS =====
DATABASE_URL=postgresql://gestor_user:password@localhost:5432/gestor_documental

# ===== FLASK =====
SECRET_KEY=clave_secreta_muy_larga_y_aleatoria
DEBUG=True
PORT=8099

# ===== CORREO ELECTRÓNICO =====
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=correo@example.com
MAIL_PASSWORD=app_password

# ===== TELEGRAM (OPCIONAL) =====
TELEGRAM_BOT_TOKEN=bot_token_aqui
TELEGRAM_CHAT_ID=chat_id_aqui

# ===== ADOBE SIGN (OPCIONAL) =====
ADOBE_CLIENT_ID=client_id
ADOBE_CLIENT_SECRET=client_secret
ADOBE_REDIRECT_URI=https://example.com/oauth
ADOBE_API_BASE_URL=https://api.na4.adobesign.com/api/rest/v6

# ===== ZONA HORARIA =====
TZ=America/Bogota

# ===== CARPETAS =====
DOCUMENTOS_TERCEROS=documentos_terceros
```

### 17.2 Configuración de PostgreSQL

```sql
-- init_postgres.sql

-- Crear usuario
CREATE USER gestor_user WITH PASSWORD 'password';

-- Crear base de datos
CREATE DATABASE gestor_documental
    OWNER gestor_user
    ENCODING 'UTF8'
    LC_COLLATE = 'es_CO.UTF-8'
    LC_CTYPE = 'es_CO.UTF-8';

-- Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE gestor_documental TO gestor_user;
```

### 17.3 Configuración de Firewall (Windows)

```powershell
# Permitir puerto 8099
New-NetFirewallRule -DisplayName "Gestor Documental" -Direction Inbound -LocalPort 8099 -Protocol TCP -Action Allow

# Permitir puerto SMTP 587 (si es necesario)
New-NetFirewallRule -DisplayName "SMTP Outbound" -Direction Outbound -LocalPort 587 -Protocol TCP -Action Allow
```

---

## 18. MANTENIMIENTO

### 18.1 Backups Automáticos

**Script:** `backup_manager.py`

```python
# Configuración de backup
BACKUP_SCHEDULE = {
    'daily': '02:00',    # 2:00 AM
    'weekly': 'sunday',  # Domingos
    'monthly': 1         # Día 1 de cada mes
}

BACKUP_RETENTION = {
    'daily': 7,     # Mantener 7 días
    'weekly': 4,    # Mantener 4 semanas
    'monthly': 12   # Mantener 12 meses
}
```

**Ejecución manual:**

```bash
python backup_manager.py
```

### 18.2 Limpieza de Logs

```bash
# Archivar logs antiguos (>30 días)
python -c "
import os
from datetime import datetime, timedelta
logs_dir = 'logs'
limite = datetime.now() - timedelta(days=30)
for f in os.listdir(logs_dir):
    if f.endswith('.log'):
        ruta = os.path.join(logs_dir, f)
        if datetime.fromtimestamp(os.path.getmtime(ruta)) < limite:
            os.rename(ruta, f'logs/archive/{f}')
"
```

### 18.3 Actualización de Dependencias

```bash
# Actualizar todas las dependencias
pip install --upgrade -r requirements.txt

# Verificar versiones
pip list

# Regenerar requirements.txt
pip freeze > requirements.txt
```

### 18.4 Vacuum de PostgreSQL

```sql
-- Liberar espacio y optimizar índices
VACUUM ANALYZE maestro_dian_vs_erp;
VACUUM ANALYZE facturas_recibidas;
VACUUM ANALYZE relaciones_facturas;

-- Reindexar (mensual)
REINDEX TABLE maestro_dian_vs_erp;
```

### 18.5 Monitoreo de Rendimiento

```python
# Script de monitoreo
python -c "
from app import app, db
with app.app_context():
    # Verificar conexión
    db.engine.execute('SELECT 1')
    print('✅ Base de datos conectada')
    
    # Verificar tablas
    from modules.dian_vs_erp.models import MaestroDianVsErp
    total = MaestroDianVsErp.query.count()
    print(f'📊 Total documentos DIAN: {total}')
"
```

---

## 19. TROUBLESHOOTING

### 19.1 Problemas Comunes

#### Error: "No module named 'flask'"

**Causa:** Entorno virtual no activado o dependencias no instaladas.

**Solución:**

```bash
# Windows
.\.venv\Scripts\activate
pip install -r requirements.txt

# Linux
source .venv/bin/activate
pip install -r requirements.txt
```

#### Error: "FATAL: database 'gestor_documental' does not exist"

**Causa:** Base de datos no creada.

**Solución:**

```bash
psql -U postgres -f init_postgres.sql
```

#### Error: "ImportError: cannot import name 'db' from 'app'"

**Causa:** Circular import.

**Solución:**

```python
# Cambiar todas las importaciones a:
from extensions import db

# En lugar de:
from app import db
```

#### Error: "Port 8099 already in use"

**Causa:** Proceso anterior aún corriendo.

**Solución:**

```powershell
# Windows
taskkill /F /IM python.exe

# Linux
pkill python
```

#### Error: "SMTPAuthenticationError"

**Causa:** Credenciales de correo incorrectas o 2FA no configurado.

**Solución:**

1. Gmail: Generar App Password en https://myaccount.google.com/apppasswords
2. Actualizar `MAIL_PASSWORD` en `.env`

#### Error: Facturas aparecen como "No Registrada" a pesar de estar recibidas

**Causa:** Lógica de API priorizaba cálculos legacy sobre estados sincronizados.

**Solución:** Ya aplicada en `routes.py` líneas 326-341 (28/12/2025).

### 19.2 Comandos de Diagnóstico

```bash
# Verificar estado del servidor
curl http://localhost:8099

# Verificar logs
tail -f logs/security.log

# Verificar base de datos
psql -U gestor_user -d gestor_documental -c "SELECT COUNT(*) FROM maestro_dian_vs_erp;"

# Verificar permisos de usuario
python check_user_status.py

# Verificar radicados
python ver_radicados.py
```

### 19.3 Contacto de Soporte

**Desarrollador:** Sistema de Gestión Documental  
**Empresa:** Supertiendas Cañaveral S.A.S.  
**Email:** soporte@supertiendascanaveral.com  
**Logs:** `logs/security.log`

---

## ANEXOS

### A. Glosario de Términos

| Término | Definición |
|---------|-----------|
| **DIAN** | Dirección de Impuestos y Aduanas Nacionales (Colombia) |
| **CUFE** | Código Único de Facturación Electrónica |
| **Maestro** | Tabla `maestro_dian_vs_erp` con todos los documentos |
| **Sincronización** | Actualizar estado contable desde otros módulos |
| **Radicado** | Número único de identificación de solicitud (RAD-XXXXXX) |
| **Blueprint** | Módulo de Flask para organizar código |
| **ORM** | Object-Relational Mapping (SQLAlchemy) |
| **Hash** | Función criptográfica para contraseñas (bcrypt) |

### B. Referencias Externas

- **Flask Documentation:** https://flask.palletsprojects.com/
- **SQLAlchemy Documentation:** https://www.sqlalchemy.org/
- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **APScheduler Documentation:** https://apscheduler.readthedocs.io/
- **Adobe Sign API:** https://www.adobe.com/sign/developer-form.html

### C. Changelog

| Fecha | Versión | Cambios |
|-------|---------|---------|
| 15/10/2025 | 0.1 | Sistema básico de autenticación y registro |
| 16/10/2025 | 0.2 | Sistema de recuperación de contraseña + email |
| 17/10/2025 | 0.3 | Sistema de firma masiva con Adobe Sign |
| 19/10/2025 | 1.0 | Módulo Recibir Facturas operativo |
| 20/10/2025 | 1.1 | Módulo Relaciones operativo |
| 28/12/2025 | 1.2 | Fix estado_contable en API DIAN vs ERP |
| 29/12/2025 | 1.3 | Documentación completa del sistema |

---

**FIN DE LA DOCUMENTACIÓN COMPLETA DEL SISTEMA**

**Versión:** 1.0  
**Fecha:** 29 de Diciembre de 2025  
**Total de Páginas:** 50+  
**Autor:** Sistema de Gestión Documental - Supertiendas Cañaveral