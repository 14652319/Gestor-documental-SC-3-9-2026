# 📋 DOCUMENTACIÓN COMPLETA - MÓDULO DIAN VS ERP
**Versión:** 2.0  
**Fecha:** 29 de Diciembre de 2025  
**Autor:** Sistema de Gestión Documental - Supertiendas Cañaveral  

---

## 📑 ÍNDICE

1. [Descripción General](#descripción-general)
2. [Arquitectura del Módulo](#arquitectura-del-módulo)
3. [Modelos de Base de Datos](#modelos-de-base-de-datos)
4. [Endpoints y APIs](#endpoints-y-apis)
5. [Sistema de Sincronización](#sistema-de-sincronización)
6. [Sistema de Envíos Programados](#sistema-de-envíos-programados)
7. [Flujos de Trabajo](#flujos-de-trabajo)
8. [Configuración](#configuración)
9. [Troubleshooting](#troubleshooting)
10. [Mantenimiento y Mejoras Futuras](#mantenimiento-y-mejoras-futuras)
11. [Glosario](#glosario)

---

## 1. DESCRIPCIÓN GENERAL

### 1.1 Propósito del Módulo

El módulo **DIAN vs ERP** es el componente central del sistema que:

- 📥 **Recibe** y almacena documentos electrónicos desde la DIAN (facturas, notas crédito, débito)
- 🔄 **Sincroniza** el estado contable entre módulos (Recibir Facturas, Causaciones, etc.)
- 📊 **Visualiza** el estado de todos los documentos en una tabla unificada
- 📧 **Envía alertas** automáticas programadas sobre documentos pendientes
- 🔍 **Permite filtrar** y exportar documentos según múltiples criterios

### 1.2 Ubicación en el Sistema

```
modules/
└── dian_vs_erp/
    ├── __init__.py              # Inicialización del blueprint
    ├── routes.py                # 3,231 líneas - Endpoints principales
    ├── models.py                # 458 líneas - Modelos SQLAlchemy
    ├── sync_service.py          # 457 líneas - Servicio de sincronización
    ├── scheduler_envios.py      # 1,056 líneas - Sistema de envíos programados
    └── README.txt               # Documentación básica
```

### 1.3 Tecnologías Utilizadas

- **Backend:** Flask Blueprint + SQLAlchemy ORM
- **Base de Datos:** PostgreSQL 18
- **Scheduler:** APScheduler 3.10
- **Email:** Flask-Mail + SMTP
- **Frontend:** Tabulator.js 5.5 + HTML5/CSS3/JavaScript
- **Exportación:** openpyxl (Excel), CSV nativo

---

## 2. ARQUITECTURA DEL MÓDULO

### 2.1 Componentes Principales

```
┌─────────────────────────────────────────────────────────┐
│                   FRONTEND (Visor)                       │
│  templates/visor_moderno.html (1,500+ líneas)          │
│  - Tabla Tabulator.js                                    │
│  - Filtros avanzados                                     │
│  - Exportación Excel/CSV                                 │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP REST API
                   ↓
┌─────────────────────────────────────────────────────────┐
│              BACKEND (Flask Blueprint)                   │
│  modules/dian_vs_erp/routes.py                          │
│  - /api/dian (consulta documentos)                      │
│  - /api/sincronizar (sincronización manual)            │
│  - /api/config/envios (configuración scheduler)        │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┴───────────┐
        ↓                      ↓
┌──────────────────┐  ┌──────────────────────┐
│  sync_service.py │  │ scheduler_envios.py  │
│  Sincronización  │  │ Envíos Programados   │
│  entre módulos   │  │ APScheduler          │
└─────────┬────────┘  └──────────┬───────────┘
          │                      │
          ↓                      ↓
┌─────────────────────────────────────────────┐
│         BASE DE DATOS PostgreSQL             │
│  - maestro_dian_vs_erp (785K+ registros)    │
│  - envios_programados_dian_vs_erp           │
│  - facturas_recibidas                        │
│  - facturas_temporales                       │
└─────────────────────────────────────────────┘
```

### 2.2 Flujo de Datos

```
1. CARGA INICIAL
   ┌─────────────┐
   │ Archivo CSV │ → Carga masiva → maestro_dian_vs_erp (785K docs)
   │ desde DIAN  │
   └─────────────┘

2. RECEPCIÓN DE FACTURAS
   Usuario recibe factura → facturas_recibidas
                          ↓
                    sync_service.py
                          ↓
          maestro_dian_vs_erp.estado_contable = "Recibida"

3. CAUSACIÓN
   Usuario causa factura → módulo causaciones
                         ↓
                   sync_service.py
                         ↓
         maestro_dian_vs_erp.estado_contable = "Causada"

4. SINCRONIZACIÓN MANUAL
   Usuario click "Sincronizar" → /api/sincronizar
                                ↓
                    Valida en otras tablas
                                ↓
                    Actualiza días desde emisión
                                ↓
                    Retorna estadísticas

5. ALERTAS AUTOMÁTICAS
   APScheduler (cron) → scheduler_envios.py
                      ↓
                Consulta documentos pendientes
                      ↓
                Genera HTML + Excel
                      ↓
                Envía por email (Flask-Mail)
```

---

## 3. MODELOS DE BASE DE DATOS

### 3.1 Tabla Principal: `maestro_dian_vs_erp`

**Total de registros:** ~785,642 documentos  
**Tamaño estimado:** 1.2 GB

#### Estructura de la Tabla

```sql
CREATE TABLE maestro_dian_vs_erp (
    -- IDENTIFICACIÓN
    id SERIAL PRIMARY KEY,
    nit_emisor VARCHAR(20) NOT NULL,
    razon_social VARCHAR(255),
    prefijo VARCHAR(10),
    folio VARCHAR(20) NOT NULL,
    cufe VARCHAR(255) UNIQUE,
    
    -- FECHAS
    fecha_emision DATE NOT NULL,
    fecha_recibida TIMESTAMP,
    fecha_causacion TIMESTAMP,
    fecha_rechazo TIMESTAMP,
    dias_desde_emision INTEGER,
    
    -- VALORES
    valor NUMERIC(15,2),
    
    -- ESTADOS (CRÍTICOS)
    estado_contable VARCHAR(50),  -- "Recibida", "Causada", "No Registrada", "Rechazada"
    estado_aprobacion VARCHAR(50), -- "Pendiente", "Aprobado", etc.
    tipo_documento VARCHAR(100),
    forma_pago VARCHAR(10),  -- "1" = Contado, "2" = Crédito
    tipo_tercero VARCHAR(50),
    
    -- FLAGS DE SINCRONIZACIÓN
    recibida BOOLEAN DEFAULT FALSE,
    causada BOOLEAN DEFAULT FALSE,
    rechazada BOOLEAN DEFAULT FALSE,
    
    -- AUDITORÍA
    usuario_recibio VARCHAR(100),
    usuario_causacion VARCHAR(100),
    doc_causado_por VARCHAR(100),
    origen_sincronizacion VARCHAR(100),  -- "RECIBIR_FACTURAS", "CAUSACIONES", etc.
    modulo VARCHAR(100),
    motivo_rechazo TEXT,
    
    -- ÍNDICES
    INDEX idx_nit_emisor (nit_emisor),
    INDEX idx_prefijo_folio (prefijo, folio),
    INDEX idx_fecha_emision (fecha_emision),
    INDEX idx_estado_contable (estado_contable),
    INDEX idx_recibida (recibida),
    INDEX idx_causada (causada),
    UNIQUE (nit_emisor, prefijo, folio)
);
```

#### Estados del Campo `estado_contable`

| Estado | Descripción | Origen | Prioridad |
|--------|-------------|--------|-----------|
| **Recibida** | Factura recibida en módulo Recibir Facturas | sync_service.py | Alta |
| **En Trámite** | Factura en relación generada | Módulo Relaciones | Alta |
| **Causada** | Factura causada en contabilidad | Módulo Causaciones | Muy Alta |
| **Rechazada** | Factura rechazada por algún motivo | Cualquier módulo | Muy Alta |
| **No Registrada** | No ha pasado por ningún módulo | Por defecto (legacy) | Baja |

**IMPORTANTE:** El API prioriza estados sincronizados sobre cálculos legacy (ver routes.py líneas 326-341).

### 3.2 Tabla: `envios_programados_dian_vs_erp`

Almacena las configuraciones de envíos automáticos programados.

```sql
CREATE TABLE envios_programados_dian_vs_erp (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50) NOT NULL,  -- "sin_causar_5_dias", "credito_sin_acuses", etc.
    
    -- DESTINATARIOS
    email_supervisor VARCHAR(255) NOT NULL,
    emails_adicionales TEXT,  -- JSON array: ["email1@example.com", "email2@example.com"]
    
    -- HORARIO
    hora_envio TIME NOT NULL,  -- Ej: "08:00:00", "14:00:00"
    dias_semana VARCHAR(50),  -- "1,2,3,4,5" (Lun-Vie), "0,1,2,3,4,5,6" (Todos)
    
    -- FILTROS
    filtro_dias_minimos INTEGER,  -- Ej: 5 para "facturas con más de 5 días"
    filtro_estado_aprobacion VARCHAR(50),  -- Ej: "Pendiente"
    filtro_forma_pago VARCHAR(20),  -- Ej: "Crédito"
    filtro_tipos_documento TEXT,  -- JSON array
    filtro_nit_exclusion TEXT,  -- JSON array de NITs a excluir
    filtro_tipos_tercero TEXT,  -- JSON array: ["Proveedor", "Comercial"]
    
    -- CONFIGURACIÓN
    activo BOOLEAN DEFAULT TRUE,
    ultima_ejecucion TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    
    -- AUDITORÍA
    creado_por VARCHAR(100),
    modificado_por VARCHAR(100)
);
```

#### Tipos de Envíos Configurables

| Tipo | Descripción | Frecuencia Típica |
|------|-------------|-------------------|
| `sin_causar_5_dias` | Facturas pendientes >= 5 días | Diario 08:00 |
| `credito_sin_acuses` | Crédito sin acuses completos | Diario 14:00 |
| `debito_sin_acuses` | Débito sin acuses completos | Diario 08:00 |
| `pendientes_3_dias` | Documentos pendientes >= 3 días | Diario 08:00 |

---

## 4. ENDPOINTS Y APIs

### 4.1 Endpoint Principal: `GET /dian_vs_erp/api/dian`

**Descripción:** Consulta documentos con filtros avanzados.

**Parámetros Query:**

| Parámetro | Tipo | Requerido | Descripción | Ejemplo |
|-----------|------|-----------|-------------|---------|
| `fecha_inicial` | DATE | ✅ Sí | Fecha inicio (YYYY-MM-DD) | `2025-01-01` |
| `fecha_final` | DATE | ✅ Sí | Fecha fin (YYYY-MM-DD) | `2025-12-31` |
| `buscar` | STRING | ❌ No | Búsqueda en NIT, prefijo, folio, razón social | `805003786` |
| `tipo_documento` | STRING | ❌ No | Filtrar por tipo | `Factura electrónica` |
| `estado_contable` | STRING | ❌ No | Filtrar por estado | `Recibida` |
| `page` | INTEGER | ❌ No | Página (default: 1) | `1` |
| `size` | INTEGER | ❌ No | Tamaño página (default: 500, max: 1000) | `500` |

**Respuesta Exitosa (200 OK):**

```json
[
  {
    "nit_emisor": "805003786",
    "nombre_emisor": "LISTO Y FRESCO S.A.S.",
    "fecha_emision": "2025-12-18",
    "tipo_documento": "Factura electrónica",
    "prefijo": "LF",
    "folio": "29065",
    "valor": 193750.00,
    "cufe": "abc123...",
    "estado_aprobacion": "Pendiente",
    "forma_pago_texto": "Crédito",
    "estado_contable": "Recibida",
    "dias_desde_emision": 10,
    "tipo_tercero": "Proveedor",
    "modulo": "",
    "doc_causado_por": "",
    "usuario_solicitante": "",
    "usuario_aprobador": "",
    "observaciones": "",
    "tiene_usuarios_email": false
  }
]
```

#### Lógica de Estado Contable (CRÍTICO - Actualizado 28/12/2025)

**El API prioriza el `estado_contable` sincronizado de la BD sobre cálculos legacy:**

```python
# modules/dian_vs_erp/routes.py (líneas 326-341)

estado_contable_bd = (registro.estado_contable or "").strip()

# Estados válidos sincronizados
estados_validos = ["Recibida", "En Trámite", "Causada", "Rechazada"]

if estado_contable_bd and estado_contable_bd in estados_validos:
    # ✅ PRIORIDAD 1: Usar estado sincronizado de la BD
    estado_contable_validado = estado_contable_bd
else:
    # ❌ FALLBACK: Calcular según módulo (legacy)
    modulo_val = (registro.modulo or "").strip()
    if modulo_val and modulo_val != "No Registrada":
        estado_contable_validado = "Causada"
    else:
        estado_contable_validado = "No Registrada"
```

**Motivo del cambio:** Corregir inconsistencia donde facturas recibidas mostraban "No Registrada" a pesar de tener `estado_contable="Recibida"` en la BD.

---

### 4.2 Endpoint: `POST /dian_vs_erp/api/sincronizar`

**Descripción:** Sincroniza manualmente el estado de documentos entre módulos.

**Request Body:** Ninguno (POST vacío)

**Proceso de Sincronización:**

```python
# 1. ACTUALIZAR DÍAS DESDE EMISIÓN (785K+ docs)
UPDATE maestro_dian_vs_erp
SET dias_desde_emision = (CURRENT_DATE - fecha_emision)::INTEGER
WHERE fecha_emision IS NOT NULL;

# 2. VALIDAR EN OTRAS TABLAS DE FACTURAS
# - facturas_temporales
# - facturas_recibidas
# - facturas_recibidas_digitales

# 3. CALCULAR ESTADÍSTICAS
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN causada = TRUE THEN 1 ELSE 0 END) as causadas,
    SUM(CASE WHEN causada = FALSE OR causada IS NULL THEN 1 ELSE 0 END) as pendientes,
    -- ... más estadísticas
FROM maestro_dian_vs_erp;
```

**Respuesta Exitosa (200 OK):**

```json
{
  "exito": true,
  "mensaje": "Sincronización completada exitosamente",
  "estadisticas": {
    "total": 785642,
    "causados": 933,
    "pendientes": 784709,
    "recibidas": 0,
    "rechazadas": 0,
    "credito": 519243,
    "sin_acuses_completos": 519243,
    "pendientes_5_dias": 784707,
    "pendientes_10_dias": 784707
  },
  "fecha_sincronizacion": "29/12/2025 10:30:45"
}
```

**Tiempo de ejecución:** ~60-90 segundos (785K registros)

---

## 5. SISTEMA DE SINCRONIZACIÓN

### 5.1 Archivo: `sync_service.py`

**Ubicación:** `modules/dian_vs_erp/sync_service.py` (457 líneas)

**Propósito:** Sincronizar en tiempo real el estado de facturas entre módulos y `maestro_dian_vs_erp`.

#### 5.2 Funciones Principales

##### `sincronizar_factura_recibida()`

**Invocado desde:** Módulo Recibir Facturas, Recibir Facturas Digitales

```python
def sincronizar_factura_recibida(nit, prefijo, folio, fecha_recibida, usuario, origen):
    """
    Marca una factura como RECIBIDA en maestro_dian_vs_erp
    """
    # 1. Normalizar clave (NIT, prefijo, folio)
    nit_limpio, prefijo_limpio, folio_8 = normalizar_clave_factura(nit, prefijo, folio)
    
    # 2. Buscar en maestro
    factura = MaestroDianVsErp.query.filter_by(
        nit_emisor=nit_limpio,
        prefijo=prefijo_limpio,
        folio=folio_8
    ).first()
    
    if factura:
        # 3. Actualizar estado
        factura.estado_contable = "Recibida"
        factura.recibida = True
        factura.usuario_recibio = usuario
        factura.fecha_recibida = fecha_recibida
        factura.origen_sincronizacion = origen
        
        # ⚠️ NO sobrescribir: tipo_documento, tipo_tercero, valor (vienen de DIAN)
        
        db.session.commit()
        return True, "Factura marcada como recibida", "ACTUALIZADA"
    else:
        # 4. Si no existe, insertar nueva
        nueva_factura = MaestroDianVsErp(
            nit_emisor=nit_limpio,
            prefijo=prefijo_limpio,
            folio=folio_8,
            estado_contable="Recibida",
            recibida=True,
            # ... resto de campos
        )
        db.session.add(nueva_factura)
        db.session.commit()
        return True, "Factura insertada como recibida", "INSERTADA"
```

---

## 6. SISTEMA DE ENVÍOS PROGRAMADOS

### 6.1 Archivo: `scheduler_envios.py`

**Ubicación:** `modules/dian_vs_erp/scheduler_envios.py` (1,056 líneas)

**Tecnología:** APScheduler 3.10 (BackgroundScheduler)

#### 6.2 Clase Principal: `SchedulerEnviosDianVsErp`

```python
class SchedulerEnviosDianVsErp:
    def __init__(self, app):
        self.app = app
        self.scheduler = BackgroundScheduler(
            timezone='America/Bogota',
            job_defaults={
                'coalesce': True,  # Consolidar ejecuciones perdidas
                'max_instances': 1  # Solo 1 instancia por job
            }
        )
        
    def iniciar(self):
        """Inicia el scheduler y carga configuraciones de BD"""
        configs = EnvioProgramadoDianVsErp.query.filter_by(activo=True).all()
        
        for config in configs:
            self.agregar_job(config)
        
        self.scheduler.start()
```

---

## 7. FLUJOS DE TRABAJO

### 7.1 Flujo Completo: Recepción de Factura

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USUARIO RECIBE FACTURA EN MÓDULO RECIBIR FACTURAS      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. SE GUARDA EN facturas_recibidas                         │
│    - nit: 805003786                                         │
│    - prefijo: LF                                            │
│    - folio: 29065                                           │
│    - fecha_recepcion: 2025-12-28 20:17:56                  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. TRIGGER AUTOMÁTICO (futuro) O SINCRONIZACIÓN MANUAL     │
│    sync_service.sincronizar_factura_recibida()             │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. ACTUALIZA maestro_dian_vs_erp                           │
│    UPDATE maestro_dian_vs_erp SET                          │
│      estado_contable = 'Recibida',                         │
│      recibida = TRUE,                                      │
│      usuario_recibio = 'admin',                            │
│      fecha_recibida = '2025-12-28 00:00:00',              │
│      origen_sincronizacion = 'RECIBIR_FACTURAS'           │
│    WHERE nit_emisor='805003786'                            │
│      AND prefijo='LF' AND folio='00029065';               │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. USUARIO HACE CLIC EN "SINCRONIZAR" (FRONTEND)          │
│    POST /dian_vs_erp/api/sincronizar                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. API RETORNA ESTADO ACTUALIZADO                          │
│    estado_contable: "Recibida" ✅                          │
│    (Ya no muestra "No Registrada")                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. CONFIGURACIÓN

### 8.1 Variables de Entorno (.env)

```env
# Base de Datos
DATABASE_URL=postgresql://gestor_user:password@localhost:5432/gestor_documental

# Email (Flask-Mail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=gestordocumentalsc01@gmail.com
MAIL_PASSWORD=app_password_aqui

# Timezone
TZ=America/Bogota

# Puerto del servidor
PORT=8099
```

---

## 9. TROUBLESHOOTING

### 9.1 Problema: Estado Contable No Se Actualiza

**Síntoma:** Facturas recibidas aparecen como "No Registrada".

**Causa:** La lógica del API priorizaba cálculos legacy sobre estados sincronizados.

**Solución Implementada (28/12/2025):**

```python
# routes.py líneas 326-341
estados_validos = ["Recibida", "En Trámite", "Causada", "Rechazada"]

if estado_contable_bd in estados_validos:
    estado_contable_validado = estado_contable_bd  # ✅ USA EL REAL
else:
    # Fallback legacy
    estado_contable_validado = "No Registrada"
```

---

## 10. MANTENIMIENTO Y MEJORAS FUTURAS

### 10.1 Mejoras Futuras Propuestas

1. **Sincronización Automática:**
   - Trigger en `facturas_recibidas` que llame a `sync_service` automáticamente
   - Eliminar necesidad de click en "Sincronizar"

2. **Dashboard de Estadísticas:**
   - Gráficos en tiempo real de estados
   - Métricas de tiempo promedio de causación

---

## 11. GLOSARIO

| Término | Definición |
|---------|-----------|
| **DIAN** | Dirección de Impuestos y Aduanas Nacionales (Colombia) |
| **CUFE** | Código Único de Facturación Electrónica |
| **Maestro** | Tabla principal `maestro_dian_vs_erp` con todos los documentos |
| **Sincronización** | Proceso de actualizar estado contable desde otros módulos |
| **Estado Contable** | Estado actual del documento (Recibida, Causada, etc.) |

---

**FIN DE LA DOCUMENTACIÓN MÓDULO DIAN VS ERP****Sistema de Envíos Programados Automáticos**  
**Fecha de Documentación:** 26 de Diciembre de 2025  
**Estado:** ✅ FUNCIONAL Y PRODUCTIVO

---

## 📑 ÍNDICE
1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Base de Datos](#base-de-datos)
4. [Sistema de Envíos Programados](#sistema-de-envíos-programados)
5. [Generación de Excel Adjunto](#generación-de-excel-adjunto)
6. [Flujos de Trabajo](#flujos-de-trabajo)
7. [Configuración y Uso](#configuración-y-uso)
8. [Troubleshooting](#troubleshooting)

---

## 📖 DESCRIPCIÓN GENERAL

El **Módulo DIAN vs ERP** es un sistema automatizado que monitorea facturas electrónicas recibidas desde la DIAN y envía alertas por correo electrónico cuando los documentos cumplen ciertos criterios (días pendientes, falta de acuses, etc.).

### Características Principales
- ✅ **Envíos programados automáticos** con APScheduler
- ✅ **Filtros configurables** por días, estados, acuses
- ✅ **Emails consolidados** con HTML profesional
- ✅ **Excel adjunto** cuando hay más de 50 documentos
- ✅ **Hipervínculos a DIAN** en Excel para ver documentos
- ✅ **Ordenamiento inteligente** (más antiguo primero)
- ✅ **Usuarios por NIT** para envíos dirigidos
- ✅ **Logs completos** de auditoría

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### Estructura de Archivos
```
modules/dian_vs_erp/
├── __init__.py                 # Inicialización del blueprint
├── models.py                   # Modelos SQLAlchemy (5 tablas)
├── routes.py                   # Endpoints HTTP (30+ endpoints)
├── scheduler_envios.py         # Sistema de envíos programados ⭐
└── backend_relaciones.py       # Backend secundario (puerto 5002)

templates/dian_vs_erp/
├── visor_dian_v2.html         # Interfaz principal del visor
├── configuracion.html          # Configuración de envíos programados
└── recepcion_digital.html      # Recepción de relaciones

sql/
└── dian_vs_erp_schema.sql     # Schema de base de datos
```

### Tecnologías Utilizadas
- **Backend:** Flask 3.0 + SQLAlchemy 2.0 + PostgreSQL 18
- **Scheduler:** APScheduler 3.x (BackgroundScheduler)
- **Email:** Flask-Mail + SMTP (Gmail/Zimbra)
- **Excel:** openpyxl 3.1.2
- **Frontend:** Tabulator.js 5.5.2 + JavaScript vanilla

---

## 🗄️ BASE DE DATOS

### Tabla: `maestro_dian_vs_erp`
**Descripción:** Maestro de todos los documentos electrónicos recibidos desde la DIAN.

```sql
CREATE TABLE maestro_dian_vs_erp (
    id SERIAL PRIMARY KEY,
    nit_emisor VARCHAR(20),
    razon_social VARCHAR(255),
    prefijo VARCHAR(10),
    folio VARCHAR(20),
    cufe TEXT,  -- CUFE del documento
    fecha_emision TIMESTAMP,
    valor NUMERIC(15,2),
    estado_aprobacion VARCHAR(50),  -- 'Pendiente', 'Causada', 'Recibida', etc.
    dias_desde_emision INTEGER,     -- Calculado automáticamente
    acuses_recibidos INTEGER DEFAULT 0,
    acuses_requeridos INTEGER DEFAULT 3,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP
);

CREATE INDEX idx_dias_emision ON maestro_dian_vs_erp(dias_desde_emision);
CREATE INDEX idx_estado ON maestro_dian_vs_erp(estado_aprobacion);
CREATE INDEX idx_nit_emisor ON maestro_dian_vs_erp(nit_emisor);
```

### Tabla: `envios_programados_dian_vs_erp`
**Descripción:** Configuraciones de envíos automáticos programados.

```sql
CREATE TABLE envios_programados_dian_vs_erp (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,           -- Nombre descriptivo del envío
    tipo_envio VARCHAR(50),                 -- 'PENDIENTES_DIAS' o 'CREDITO_SIN_ACUSES'
    dias_minimos INTEGER,                   -- Mínimo de días para incluir documento
    estados_excluidos TEXT,                 -- JSON: ["Causada", "Recibida"]
    frecuencia VARCHAR(20),                 -- 'DIARIO' o 'SEMANAL'
    hora_envio VARCHAR(5),                  -- Formato: '08:00', '14:00'
    dias_semana TEXT,                       -- JSON: [1,2,3,4,5] (Lun-Vie)
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);
```

**Ejemplos de configuraciones:**
```json
// 1. Documentos pendientes +3 días (diario a las 08:00)
{
  "nombre": "Documentos pendientes +3 días",
  "tipo_envio": "PENDIENTES_DIAS",
  "dias_minimos": 3,
  "estados_excluidos": ["Causada", "Recibida"],
  "frecuencia": "DIARIO",
  "hora_envio": "08:00"
}

// 2. Alerta sin causar 5 días (diario a las 08:00)
{
  "nombre": "Alerta sin causar 5 dias",
  "tipo_envio": "PENDIENTES_DIAS",
  "dias_minimos": 5,
  "estados_excluidos": ["Causada"],
  "frecuencia": "DIARIO",
  "hora_envio": "08:00"
}

// 3. Crédito sin acuses completos (diario a las 14:00)
{
  "nombre": "Crédito sin acuses completos",
  "tipo_envio": "CREDITO_SIN_ACUSES",
  "acuses_minimos": 2,
  "estados_excluidos": null,
  "frecuencia": "DIARIO",
  "hora_envio": "14:00"
}
```

### Tabla: `usuarios_asignados`
**Descripción:** Usuarios que recibirán los correos, asociados por NIT.

```sql
CREATE TABLE usuarios_asignados (
    id SERIAL PRIMARY KEY,
    nit VARCHAR(20) NOT NULL,               -- NIT del tercero
    razon_social VARCHAR(255),
    tipo_usuario VARCHAR(50),               -- 'APROBADOR', 'SOLICITANTE'
    nombres VARCHAR(100),
    apellidos VARCHAR(100),
    correo VARCHAR(255) NOT NULL,           -- Email destino ⭐
    telefono VARCHAR(20),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP
);

CREATE INDEX idx_nit_activo ON usuarios_asignados(nit, activo);
```

**Ejemplo de registro:**
```sql
INSERT INTO usuarios_asignados (nit, razon_social, nombres, apellidos, correo, tipo_usuario)
VALUES ('805013653', 'LA GALERIA Y CIA SAS', 'RICARDO', 'RIASCOS BURGOS', 
        'ricardoriascos07@gmail.com', 'APROBADOR');
```

### Tabla: `historial_envios_dian_vs_erp`
**Descripción:** Auditoría completa de todos los envíos ejecutados.

```sql
CREATE TABLE historial_envios_dian_vs_erp (
    id SERIAL PRIMARY KEY,
    envio_programado_id INTEGER REFERENCES envios_programados_dian_vs_erp(id),
    fecha_ejecucion TIMESTAMP DEFAULT NOW(),
    estado VARCHAR(20),                     -- 'EXITOSO', 'FALLIDO', 'PARCIAL'
    docs_procesados INTEGER,
    docs_enviados INTEGER,
    emails_enviados INTEGER,
    emails_fallidos INTEGER,
    tiempo_ejecucion NUMERIC(10,2),         -- Segundos
    detalles TEXT                           -- JSON con información adicional
);
```

### Tabla: `usuarios_causacion_dian_vs_erp`
**Descripción:** Usuarios específicos para causación de documentos.

```sql
CREATE TABLE usuarios_causacion_dian_vs_erp (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(255) NOT NULL UNIQUE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);
```

---

## 📧 SISTEMA DE ENVÍOS PROGRAMADOS

### Clase Principal: `EnviosProgramadosSchedulerDianVsErp`

**Ubicación:** `modules/dian_vs_erp/scheduler_envios.py` (594 líneas)

#### Inicialización
```python
class EnviosProgramadosSchedulerDianVsErp:
    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler()
        self.app = app
        self.smtp_config = {
            'server': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
            'port': int(os.getenv('MAIL_PORT', 465)),
            'username': os.getenv('MAIL_USERNAME'),
            'password': os.getenv('MAIL_PASSWORD'),
            'use_ssl': os.getenv('MAIL_USE_SSL', 'True') == 'True',
            'use_tls': os.getenv('MAIL_USE_TLS', 'False') == 'True'
        }
```

#### Métodos Principales

##### 1. `iniciar_scheduler()`
**Propósito:** Inicia el scheduler con todas las configuraciones activas.

```python
def iniciar_scheduler(self):
    """
    - Carga configuraciones activas desde base de datos
    - Crea triggers cron basados en frecuencia (DIARIO/SEMANAL)
    - Agrega jobs al scheduler
    - Inicia el scheduler en background
    """
```

**Logs generados:**
```
INFO:modules.dian_vs_erp.scheduler_envios:📋 Cargadas 5 configuraciones activas
INFO:modules.dian_vs_erp.scheduler_envios:✅ Job agregado: Documentos pendientes +3 días (08:00)
INFO:modules.dian_vs_erp.scheduler_envios:✅ Job agregado: Alerta sin causar 5 dias (08:00)
INFO:modules.dian_vs_erp.scheduler_envios:🚀 Scheduler DIAN VS ERP iniciado
```

##### 2. `ejecutar_envio_programado(config_id)`
**Propósito:** Ejecuta un envío específico (manual o programado).

**Flujo:**
1. Consulta configuración por ID
2. Determina tipo de envío (PENDIENTES_DIAS o CREDITO_SIN_ACUSES)
3. Llama al método procesador correspondiente
4. Registra resultado en historial
5. Calcula próxima ejecución

##### 3. `_procesar_pendientes_dias(config)`
**Propósito:** Procesa documentos con días pendientes >= mínimo configurado.

**Lógica:**
```python
def _procesar_pendientes_dias(self, config):
    # 1. Query documentos ORDENADOS por días (más antiguo primero)
    query = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.dias_desde_emision >= config.dias_minimos
    )
    
    # 2. Excluir estados configurados
    if config.estados_excluidos:
        estados = json.loads(config.estados_excluidos)
        query = query.filter(~MaestroDianVsErp.estado_aprobacion.in_(estados))
    
    # 3. ⭐ ORDENAR: Más días arriba (más antiguo), menos días abajo (más reciente)
    query = query.order_by(MaestroDianVsErp.dias_desde_emision.desc())
    
    documentos = query.all()
    
    # 4. Agrupar por NIT
    docs_por_nit = {}
    for doc in documentos:
        nit = doc.nit_emisor
        if nit not in docs_por_nit:
            docs_por_nit[nit] = []
        docs_por_nit[nit].append(doc)
    
    # 5. Buscar usuarios asignados por NIT
    docs_por_usuario = {}
    for nit, docs in docs_por_nit.items():
        query_usuarios = """
            SELECT correo, nombres, apellidos 
            FROM usuarios_asignados 
            WHERE nit = :nit AND activo = true
        """
        usuarios = db.session.execute(db.text(query_usuarios), {'nit': nit}).fetchall()
        
        for usuario in usuarios:
            email = usuario[0]
            if email not in docs_por_usuario:
                docs_por_usuario[email] = []
            docs_por_usuario[email].extend(docs)
    
    # 6. Enviar emails consolidados
    for email, docs in docs_por_usuario.items():
        self._enviar_email_consolidado(
            destinatario=email,
            asunto=f"⏰ Documentos pendientes - {len(docs)} facturas",
            documentos=docs,
            tipo='PENDIENTES_DIAS',
            dias_min=config.dias_minimos
        )
```

##### 4. `_enviar_email_consolidado(destinatario, asunto, documentos, tipo, **kwargs)`
**Propósito:** Envía email con lista de documentos (HTML + Excel si > 50).

**Características:**
```python
def _enviar_email_consolidado(self, destinatario, asunto, documentos, tipo, **kwargs):
    total_docs = len(documentos)
    
    # ⭐ LIMITAR HTML A 50 DOCUMENTOS
    docs_para_html = documentos[:50] if total_docs > 50 else documentos
    
    # Generar HTML (con advertencia si > 50)
    html = self._generar_html_email(docs_para_html, tipo, total_documentos=total_docs, **kwargs)
    
    # Crear mensaje
    msg = MIMEMultipart('mixed')  # 'mixed' para soportar adjuntos
    msg['From'] = self.smtp_config['username']
    msg['To'] = destinatario
    msg['Subject'] = asunto
    
    # Agregar HTML
    msg_html = MIMEMultipart('alternative')
    msg_html.attach(MIMEText(html, 'html'))
    msg.attach(msg_html)
    
    # ⭐ SI HAY MÁS DE 50 DOCUMENTOS, GENERAR EXCEL ADJUNTO
    if total_docs > 50:
        excel_content = self._generar_excel_documentos(documentos, tipo, **kwargs)
        from email.mime.application import MIMEApplication
        excel_adjunto = MIMEApplication(excel_content, _subtype='xlsx')
        fecha_archivo = datetime.now().strftime('%Y%m%d_%H%M%S')
        excel_adjunto.add_header('Content-Disposition', 'attachment', 
                                filename=f'Documentos_Pendientes_{fecha_archivo}.xlsx')
        msg.attach(excel_adjunto)
        logger.info(f"   📎 Excel adjunto generado con {total_docs} documentos")
    
    # Enviar según configuración (SSL puerto 465 o TLS puerto 587)
    if self.smtp_config['use_ssl']:
        with smtplib.SMTP_SSL(self.smtp_config['server'], self.smtp_config['port']) as server:
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.send_message(msg)
    else:
        with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
            if self.smtp_config['use_tls']:
                server.starttls()
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.send_message(msg)
```

##### 5. `_generar_html_email(documentos, tipo, **kwargs)`
**Propósito:** Genera HTML profesional del email.

**Características:**
- Diseño responsivo con estilos inline
- Tabla con documentos (máximo 50 en HTML)
- ⚠️ Advertencia amarilla si hay más de 50 totales
- Resumen con total de documentos y valor
- Links a DIAN para ver documentos
- Footer corporativo

**Advertencia cuando > 50 documentos:**
```html
<div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
    <strong>⚠️ Se muestran los primeros 50 documentos de {total_documentos} totales.</strong><br>
    📎 Consulte el archivo Excel adjunto para ver el listado completo.
</div>
```

##### 6. `_generar_excel_documentos(documentos, tipo, **kwargs)`
**Propósito:** Genera Excel profesional con TODOS los documentos.

**Características:**
```python
def _generar_excel_documentos(self, documentos, tipo, **kwargs):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from io import BytesIO
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Documentos Pendientes"
    
    # ⭐ ESTILOS CORPORATIVOS
    header_fill = PatternFill(start_color="00C875", end_color="00C875", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    
    # Encabezados
    encabezados = ['#', 'NIT', 'Proveedor', 'Factura', 'Fecha Emisión', 
                   'Valor', 'Días Pendientes', 'Estado', 'CUFE']
    
    # Datos con hipervínculos en CUFE
    for i, doc in enumerate(documentos, 1):
        cufe = doc.cufe or ''
        
        # ... agregar datos ...
        
        # ⭐ COLUMNA CUFE CON HIPERVÍNCULO
        if cufe:
            cell = ws.cell(row=i+1, column=9)
            cell.value = cufe
            cell.hyperlink = f"https://catalogo-vpfe.dian.gov.co/User/SearchDocument?DocumentKey={cufe}"
            cell.style = "Hyperlink"  # Azul con subrayado
    
    # Anchos de columna optimizados
    ws.column_dimensions['A'].width = 5   # #
    ws.column_dimensions['B'].width = 12  # NIT
    ws.column_dimensions['C'].width = 35  # Proveedor
    ws.column_dimensions['D'].width = 15  # Factura
    ws.column_dimensions['E'].width = 12  # Fecha
    ws.column_dimensions['F'].width = 15  # Valor
    ws.column_dimensions['G'].width = 12  # Días
    ws.column_dimensions['H'].width = 15  # Estado
    ws.column_dimensions['I'].width = 60  # CUFE (con hipervínculo)
    
    # Fila de totales
    total_row = len(documentos) + 2
    ws.cell(row=total_row, column=5).value = "TOTAL:"
    ws.cell(row=total_row, column=6).value = sum(float(doc.valor or 0) for doc in documentos)
    ws.cell(row=total_row, column=6).number_format = '$#,##0'
    
    # Auto filtro
    ws.auto_filter.ref = f"A1:I{len(documentos) + 1}"
    
    # Retornar bytes
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()
```

---

## 🔄 FLUJOS DE TRABAJO

### Flujo 1: Envío Programado Automático

```mermaid
graph TD
    A[Scheduler iniciado] --> B[Espera hora configurada]
    B --> C{Hora programada?}
    C -->|No| B
    C -->|Sí| D[ejecutar_envio_programado]
    D --> E[Consultar documentos con filtros]
    E --> F[Ordenar por días DESC]
    F --> G[Agrupar por NIT]
    G --> H[Buscar usuarios por NIT]
    H --> I{Hay documentos?}
    I -->|No| J[Registrar: 0 emails enviados]
    I -->|Sí| K{Total > 50?}
    K -->|No| L[Generar HTML completo]
    K -->|Sí| M[Generar HTML primeros 50]
    M --> N[Generar Excel con todos]
    L --> O[Enviar email]
    N --> O
    O --> P[Registrar en historial]
    P --> Q[Calcular próxima ejecución]
```

### Flujo 2: Envío Manual desde Interfaz

```
1. Usuario ingresa a /dian_vs_erp/configuracion
2. Ve lista de envíos programados
3. Click en botón "Ejecutar" de un envío
4. POST /dian_vs_erp/api/config/envios/{id}/ejecutar
5. Sistema crea thread para ejecutar en background
6. Respuesta inmediata: "Ejecución iniciada. Revise el historial..."
7. Thread ejecuta: scheduler.ejecutar_envio_programado(id)
8. Logs en consola del servidor
9. Registro en historial_envios_dian_vs_erp
```

### Flujo 3: Configuración de Nuevo Envío

```
1. Usuario ingresa a /dian_vs_erp/configuracion
2. Click en "Nueva Configuración"
3. Llena formulario:
   - Nombre del envío
   - Tipo (Pendientes días / Crédito sin acuses)
   - Días mínimos
   - Estados a excluir
   - Frecuencia (Diario / Semanal)
   - Hora de envío
4. Click "Guardar"
5. POST /dian_vs_erp/api/config/envios (CREATE)
6. Sistema valida datos
7. Guarda en tabla envios_programados_dian_vs_erp
8. Reinicia scheduler para aplicar cambios
9. Nuevo job aparece en lista
```

---

## ⚙️ CONFIGURACIÓN Y USO

### Variables de Entorno Requeridas

**Archivo:** `.env`

```env
# Base de datos PostgreSQL
DATABASE_URL=postgresql://gestor_user:password@localhost:5432/gestor_documental

# Email SMTP (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=gestordocumentalsc01@gmail.com
MAIL_PASSWORD=urjrkjlogcfdtynq  # App Password (2FA habilitado)
MAIL_DEFAULT_SENDER=gestordocumentalsc01@gmail.com
```

### Instalación de Dependencias

```bash
# Activar virtualenv
.\.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Dependencias específicas del módulo:
# - Flask==3.0.0
# - Flask-Mail==0.9.1
# - APScheduler==3.10.4
# - openpyxl==3.1.2
# - psycopg2-binary==2.9.9
# - SQLAlchemy==2.0.23
```

### Inicialización del Sistema

**En `app.py`:**

```python
# Importar scheduler
from modules.dian_vs_erp.scheduler_envios import iniciar_scheduler_dian_vs_erp

# Iniciar scheduler al arrancar app (después de registrar blueprints)
if __name__ == '__main__':
    with app.app_context():
        scheduler_dian_vs_erp_global = iniciar_scheduler_dian_vs_erp(app)
    
    app.run(host='0.0.0.0', port=8099, debug=True)
```

### Uso desde Interfaz Web

#### 1. Acceder al Módulo
```
URL: http://localhost:8099/dian_vs_erp/configuracion
```

#### 2. Pestaña "Envíos Programados"
- Ver lista de envíos configurados
- Ver estado (Activo/Inactivo)
- Ver próxima ejecución
- Botón "Ejecutar" para envío manual inmediato
- Botón "Editar" para modificar configuración
- Botón "Eliminar" para borrar envío

#### 3. Nueva Configuración
**Ejemplo: Alerta documentos sin causar > 5 días**

```json
{
  "nombre": "Alerta sin causar 5 dias",
  "tipo_envio": "PENDIENTES_DIAS",
  "dias_minimos": 5,
  "estados_excluidos": ["Causada"],
  "frecuencia": "DIARIO",
  "hora_envio": "08:00",
  "activo": true
}
```

**Significado:**
- Enviar alerta diaria a las 08:00 AM
- Incluir documentos con 5 o más días de antigüedad
- Excluir documentos ya causados
- Enviar solo a usuarios con documentos pendientes

#### 4. Gestión de Usuarios por NIT

**URL:** `/dian_vs_erp/configuracion` → Pestaña "Usuarios por NIT"

**Agregar usuario:**
1. Click "Agregar Usuario"
2. Ingresar NIT (autocomplete busca razón social)
3. Ingresar nombres, apellidos, correo
4. Seleccionar tipo: APROBADOR o SOLICITANTE
5. Marcar "Activo"
6. Guardar

**Ejemplo:**
```
NIT: 805013653
Razón Social: LA GALERIA Y CIA SAS (autocomplete)
Nombres: RICARDO
Apellidos: RIASCOS BURGOS
Correo: ricardoriascos07@gmail.com
Tipo: APROBADOR
Activo: ✓
```

---

## 📊 LOGS Y AUDITORÍA

### Logs del Scheduler

**Ubicación:** `logs/scheduler_dian_vs_erp.log`

**Ejemplo de ejecución exitosa:**
```
2025-12-26 20:55:03 - INFO - 🚀 Iniciando envío programado ID=6
2025-12-26 20:55:03 - INFO - 📧 Email enviado a ricardoriascos07@gmail.com
2025-12-26 20:55:03 - INFO -    ✅ Email enviado a ricardoriascos07@gmail.com (139 docs)
2025-12-26 20:55:03 - INFO -    📎 Excel adjunto generado con 139 documentos
2025-12-26 20:55:30 - INFO - ✅ Envío programado ID=6 completado en 27.04s
2025-12-26 20:55:30 - INFO -    📧 Emails enviados: 1
2025-12-26 20:55:30 - INFO -    📄 Documentos incluidos: 139
```

**Ejemplo de error:**
```
2025-12-26 21:00:15 - ERROR - ❌ Error en _procesar_pendientes_dias: SMTP authentication failed
2025-12-26 21:00:15 - INFO - ✅ Envío programado ID=3 completado en 0.05s
2025-12-26 21:00:15 - INFO -    📧 Emails enviados: 0
2025-12-26 21:00:15 - INFO -    📄 Documentos incluidos: 0
```

### Tabla de Historial

**Consulta SQL para ver últimos 10 envíos:**
```sql
SELECT 
    h.id,
    e.nombre AS envio_nombre,
    h.fecha_ejecucion,
    h.estado,
    h.docs_procesados,
    h.emails_enviados,
    h.tiempo_ejecucion
FROM historial_envios_dian_vs_erp h
JOIN envios_programados_dian_vs_erp e ON h.envio_programado_id = e.id
ORDER BY h.fecha_ejecucion DESC
LIMIT 10;
```

---

## 🔧 TROUBLESHOOTING

### Problema 1: No se envían correos

**Síntoma:**
```
INFO: ✅ Envío programado ID=6 completado en 27.04s
INFO:    📧 Emails enviados: 0
INFO:    📄 Documentos incluidos: 0
```

**Posibles causas:**
1. **Tabla `usuarios_asignados` vacía** → Agregar usuarios por NIT
2. **Usuarios inactivos** → Verificar campo `activo = true`
3. **NIT no coincide** → Verificar que `nit` en usuarios = `nit_emisor` en documentos
4. **No hay documentos que cumplan criterios** → Revisar filtros de configuración

**Solución:**
```sql
-- Verificar usuarios activos
SELECT nit, correo, nombres, apellidos, activo 
FROM usuarios_asignados 
WHERE activo = true;

-- Si está vacío, agregar usuario
INSERT INTO usuarios_asignados (nit, nombres, apellidos, correo, tipo_usuario, activo)
VALUES ('805013653', 'RICARDO', 'RIASCOS BURGOS', 'ricardoriascos07@gmail.com', 'APROBADOR', true);
```

### Problema 2: Error SMTP

**Síntoma:**
```
ERROR: SMTP authentication failed
ERROR: Connection refused (port 465)
```

**Soluciones:**
1. **Gmail:** Verificar App Password (no usar contraseña normal)
2. **Puerto:** Verificar puerto correcto (465 SSL o 587 TLS)
3. **Variables:** Verificar `.env` tiene `MAIL_USERNAME` y `MAIL_PASSWORD`
4. **Firewall:** Verificar puerto 465/587 no está bloqueado

**Probar configuración:**
```python
python probar_envio_correo.py
```

### Problema 3: Excel no se genera

**Síntoma:**
```
ERROR: openpyxl requerido para generar Excel
```

**Solución:**
```bash
pip install openpyxl==3.1.2
```

### Problema 4: Scheduler no inicia

**Síntoma:**
```
ERROR: cannot import name 'scheduler_dian_vs_erp_global'
```

**Solución:**
Verificar en `app.py`:
```python
from modules.dian_vs_erp.scheduler_envios import iniciar_scheduler_dian_vs_erp

# Al final del archivo, en if __name__ == '__main__':
with app.app_context():
    scheduler_dian_vs_erp_global = iniciar_scheduler_dian_vs_erp(app)
```

### Problema 5: Hipervínculos en Excel no funcionan

**Síntoma:** Al hacer click en CUFE del Excel, no abre la DIAN.

**Solución verificada:**
```python
# ✅ URL CORRECTA (funciona)
url = f"https://catalogo-vpfe.dian.gov.co/User/SearchDocument?DocumentKey={cufe}"

# ❌ URL INCORRECTA (no funciona)
url = f"https://catalogo-vpfe-hab.dian.gov.co/document/searchqr?documentkey={cufe}"
```

---

## 📈 MÉTRICAS DE RENDIMIENTO

### Tiempos Promedio
- **Consulta de documentos:** < 1 segundo
- **Generación HTML:** < 0.5 segundos
- **Generación Excel (139 docs):** 1-2 segundos
- **Envío SMTP:** 3-5 segundos por email
- **Total (139 docs, 1 email):** 27 segundos

### Límites del Sistema
- **Documentos en HTML:** Máximo 50 (por peso del email)
- **Documentos en Excel:** Ilimitado (probado hasta 1000+)
- **Tamaño archivo Excel:** ~50 KB por cada 100 documentos
- **Usuarios por NIT:** Ilimitado
- **Envíos programados:** Ilimitado
- **Emails simultáneos:** Depende de límite SMTP (Gmail: 500/día)

---

## 🎯 PRÓXIMAS MEJORAS (ROADMAP)

### Corto Plazo (1-2 semanas)
- [ ] Dashboard de estadísticas de envíos
- [ ] Previsualización de email antes de enviar
- [ ] Exportar historial a Excel
- [ ] Notificaciones push en interfaz

### Mediano Plazo (1-3 meses)
- [ ] Plantillas personalizables de email
- [ ] Envíos a múltiples destinatarios con CC/BCC
- [ ] Integración con WhatsApp Business
- [ ] Reportes automáticos mensuales

### Largo Plazo (3-6 meses)
- [ ] Machine Learning para predecir documentos problemáticos
- [ ] Integración directa con API DIAN
- [ ] App móvil para recibir alertas
- [ ] Sistema de recordatorios escalonados

---

## 📞 SOPORTE Y CONTACTO

**Desarrollador:** Ricardo Riascos  
**Email:** ricardoriascos07@gmail.com  
**Empresa:** Supertiendas Cañaveral  
**Versión del Sistema:** 1.0.0 (Diciembre 2025)  
**Estado:** ✅ PRODUCTIVO Y FUNCIONAL

---

## 📝 NOTAS FINALES

Este módulo ha sido completamente implementado y probado en ambiente productivo desde Diciembre 26, 2025. Todas las funcionalidades documentadas aquí están operativas y en uso.

**Últimas actualizaciones:**
- ✅ 26/12/2025: Implementado ordenamiento por días (más antiguo primero)
- ✅ 26/12/2025: Implementado límite de 50 docs en HTML + Excel adjunto
- ✅ 26/12/2025: Implementado hipervínculos en Excel a DIAN (URL correcta)
- ✅ 26/12/2025: Corrección de tabla de usuarios a `usuarios_asignados`
- ✅ 26/12/2025: Sistema de envíos automáticos completamente funcional

---

**FIN DEL DOCUMENTO**
