# 📘 DOCUMENTACIÓN COMPLETA - GESTOR DOCUMENTAL
## Sistema Integral de Gestión Documental - Supertiendas Cañaveral

**Versión:** 3.0  
**Última Actualización:** 27 de Noviembre de 2025  
**Desarrollado para:** Supertiendas Cañaveral SAS  

---

## 📋 ÍNDICE

1. [Información General del Sistema](#información-general)
2. [Credenciales y Accesos](#credenciales-y-accesos)
3. [Módulos del Sistema](#módulos-del-sistema)
4. [Estructura de Base de Datos](#estructura-de-base-de-datos)
5. [Tablas por Módulo](#tablas-por-módulo)
6. [Rutas y Directorios](#rutas-y-directorios)
7. [Configuraciones](#configuraciones)
8. [Funcionalidades por Módulo](#funcionalidades-por-módulo)
9. [Usuarios y Permisos](#usuarios-y-permisos)
10. [Procesos Automáticos](#procesos-automáticos)
11. [Integraciones](#integraciones)
12. [Backup y Recuperación](#backup-y-recuperación)

---

## 🔐 INFORMACIÓN GENERAL

### **Datos del Sistema**
- **Nombre:** Gestor Documental - Supertiendas Cañaveral
- **Tipo:** Aplicación Web Flask (Python)
- **Puerto:** 8099
- **URL Local:** http://127.0.0.1:8099
- **URL Red:** http://192.168.11.33:8099
- **Base de Datos:** PostgreSQL 16
- **Framework:** Flask 2.3.x + SQLAlchemy

### **Servidor de Aplicación**
- **Ubicación:** `C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059\`
- **Archivo Principal:** `app.py`
- **Comando Inicio:** `python app.py`
- **Script Inicio:** `iniciar_servidor.bat`
- **Modo Debug:** Activado (desarrollo)
- **Watchdog:** Activado (recarga automática)

---

## 🔑 CREDENCIALES Y ACCESOS

### **Base de Datos PostgreSQL**
```
Host: localhost
Puerto: 5432
Base de Datos: gestor_documental
Usuario: postgres
Contraseña: G3st0radm$2025.
```

### **Usuario Administrador del Sistema**
```
Usuario: admin
Contraseña: Inicio2024*
Tipo: interno
Estado: activo
Permisos: Todos los módulos
```

### **Correo SMTP (Zimbra Corporativo)**
```
Servidor: mail.supertiendascabanaveralvillavicencio.com
Puerto: 465 (SSL)
Usuario: notificaciones@supertiendascabanaveralvillavicencio.com
Contraseña: Notif2024$
Protocolo: SMTP con SSL/TLS
```

### **Rutas de Red (SMB)**
```
Ruta Principal: \\192.168.11.33\GestorDocumental
Ruta Facturas Digitales: D:\facturas_digitales
Usuario Red: (heredado del sistema)
```

---

## 📦 MÓDULOS DEL SISTEMA

### **1. RECIBIR FACTURAS** ✅
**Ruta:** `/recibir_facturas`  
**Estado:** Operativo  
**Descripción:** Módulo para digitalizar y radicar facturas de proveedores

**Funcionalidades:**
- ✅ Carga de facturas (PDF, XML, ZIP)
- ✅ Validación de duplicados en tiempo real
- ✅ Verificación de terceros (RUT actualizado)
- ✅ OCR automático de datos fiscales
- ✅ Generación de radicados automáticos (RX-NNN)
- ✅ Almacenamiento en red (SMB)
- ✅ Histórico de facturas recibidas
- ✅ Detalle de factura con visor PDF

**Archivos Clave:**
- `modules/recibir_facturas/routes.py` (536 líneas)
- `templates/recibir_facturas/nueva_factura.html`
- `templates/recibir_facturas/listado.html`

---

### **2. FACTURAS DIGITALES** ✅
**Ruta:** `/facturas-digitales`  
**Estado:** Operativo  
**Descripción:** Sistema completo de gestión de facturas digitales

**Sub-módulos:**

#### **2.1 Dashboard** 📊
- KPIs en tiempo real
- Últimas 10 facturas registradas
- Estadísticas por empresa
- Accesos rápidos

#### **2.2 Cargar Factura** 📤
**Ruta:** `/facturas-digitales/cargar-nueva`
- Formulario de carga con validación
- Dropdowns dinámicos desde BD
- Validación de duplicados (ambas tablas)
- Estructura de carpetas automática:
  ```
  {empresa}/{año}/{mes}/{departamento}/{forma_pago}/{nit}-{numero}
  ```
- Almacenamiento en `D:\facturas_digitales\`
- Radicado automático (DS-NNN)

#### **2.3 Listado** 📋
**Ruta:** `/facturas-digitales/listado`
- Tabla con todas las facturas
- Filtros: Empresa, Departamento, Fecha, Proveedor
- Acciones: Ver, Editar, Firmar, Causar
- Paginación

#### **2.4 Detalle** 🔍
**Ruta:** `/facturas-digitales/detalle/<id>`
- Información completa de la factura
- Visor de archivos PDF
- Historial de cambios
- Opciones de firma y causación

#### **2.5 Configuración de Catálogos** ⚙️
**Ruta:** `/facturas-digitales/configuracion`
- CRUD de Tipo de Documento
- CRUD de Forma de Pago
- CRUD de Tipo de Servicio
- CRUD de Departamentos
- Interfaz responsive con modo claro/oscuro
- Soft delete (activar/desactivar)

**Archivos Clave:**
- `modules/facturas_digitales/routes.py` (1261 líneas)
- `modules/facturas_digitales/config_routes.py` (436 líneas)
- `modules/facturas_digitales/models.py` (89 líneas)
- `templates/facturas_digitales/cargar.html` (1234 líneas)
- `templates/facturas_digitales/configuracion_catalogos.html` (596 líneas)

---

### **3. RELACIONES** ✅
**Ruta:** `/relaciones`  
**Estado:** Operativo  
**Descripción:** Generación de relaciones de pago para contabilidad

**Funcionalidades:**
- ✅ Selección múltiple de facturas
- ✅ Generación de archivo Excel (relación)
- ✅ Numeración automática (REL-NNN)
- ✅ Envío por correo electrónico
- ✅ Histórico de relaciones
- ✅ Cambio de estado de facturas

**Archivos Clave:**
- `modules/relaciones/routes.py`
- `templates/relaciones/generar.html`

---

### **4. CAUSACIONES** ✅
**Ruta:** `/causaciones`  
**Estado:** Operativo  
**Descripción:** Registro de causaciones contables

**Funcionalidades:**
- ✅ Crear causación desde factura
- ✅ Vinculación con facturas digitales
- ✅ Estados: Pendiente, Causada, Pagada
- ✅ Exportación a Excel
- ✅ Reportes contables

**Archivos Clave:**
- `modules/causaciones/routes.py`
- `templates/causaciones/nueva.html`

---

### **5. NOTAS CONTABLES** ✅
**Ruta:** `/notas-contables`  
**Estado:** Operativo  
**Descripción:** Gestión de notas débito y crédito

**Funcionalidades:**
- ✅ Registro de notas contables
- ✅ Asociación con facturas
- ✅ Tipos: Débito, Crédito
- ✅ Validaciones contables

---

### **6. CONFIGURACIÓN** ⚙️
**Ruta:** `/configuracion`  
**Estado:** Operativo  
**Descripción:** Panel de configuración del sistema

**Opciones:**
- Empresas
- Centros de Operación
- Terceros (Proveedores)
- Usuarios
- Permisos
- Correo SMTP
- Rutas de Red

---

### **7. ADMIN (Administración)** 👨‍💼
**Ruta:** `/admin`  
**Estado:** Operativo  
**Descripción:** Panel de administración general

**Funcionalidades:**
- Gestión de usuarios
- Asignación de permisos
- Logs del sistema
- Monitoreo de actividad

---

## 🗄️ ESTRUCTURA DE BASE DE DATOS

### **Base de Datos:** `gestor_documental`
**Motor:** PostgreSQL 16  
**Codificación:** UTF8  
**Total de Tablas:** 28 tablas principales

---

## 📊 TABLAS POR MÓDULO

### **MÓDULO: Recibir Facturas**

#### **1. facturas_recibidas**
```sql
CREATE TABLE facturas_recibidas (
    id SERIAL PRIMARY KEY,
    nit VARCHAR(20) NOT NULL,
    razon_social VARCHAR(255),
    prefijo VARCHAR(10),
    folio VARCHAR(50) NOT NULL,
    fecha_expedicion DATE,
    fecha_recepcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valor_bruto NUMERIC(15,2),
    valor_iva NUMERIC(15,2),
    valor_total NUMERIC(15,2),
    ruta_archivo_principal TEXT,
    ruta_archivo_xml TEXT,
    ruta_carpeta TEXT,
    estado VARCHAR(50) DEFAULT 'RECIBIDA',
    numero_radicado VARCHAR(20) UNIQUE,
    usuario_creacion VARCHAR(50),
    centro_operacion_id INTEGER,
    observaciones TEXT,
    numero_relacion VARCHAR(50),
    fecha_relacion DATE
);
```
**Registros:** ~5,000 facturas  
**Índices:** nit, numero_radicado, estado, fecha_expedicion

---

#### **2. facturas_recibidas_digitales**
```sql
CREATE TABLE facturas_recibidas_digitales (
    id SERIAL PRIMARY KEY,
    nit VARCHAR(20) NOT NULL,
    prefijo VARCHAR(10),
    folio VARCHAR(50) NOT NULL,
    razon_social VARCHAR(255),
    fecha_expedicion DATE,
    fecha_recepcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valor_total NUMERIC(15,2),
    co VARCHAR(10),
    ruta_carpeta TEXT,
    numero_relacion VARCHAR(50),
    estado VARCHAR(50) DEFAULT 'PENDIENTE',
    usuario_creacion VARCHAR(50)
);
```

---

### **MÓDULO: Facturas Digitales**

#### **3. facturas_digitales**
```sql
CREATE TABLE facturas_digitales (
    id SERIAL PRIMARY KEY,
    nit VARCHAR(20) NOT NULL,
    nombre_proveedor VARCHAR(255),
    empresa VARCHAR(10) NOT NULL,
    numero_factura VARCHAR(50) NOT NULL,
    prefijo VARCHAR(10),
    folio VARCHAR(50),
    tipo_documento VARCHAR(10),
    forma_pago VARCHAR(20),
    tipo_servicio VARCHAR(20),
    departamento VARCHAR(50),
    fecha_expedicion DATE NOT NULL,
    fecha_radicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valor_bruto NUMERIC(15,2),
    valor_iva NUMERIC(15,2),
    valor_total NUMERIC(15,2) NOT NULL,
    observaciones TEXT,
    ruta_carpeta TEXT,
    ruta_archivo_principal TEXT,
    ruta_archivos_anexos TEXT,
    ruta_seguridad_social TEXT,
    estado VARCHAR(50) DEFAULT 'PENDIENTE',
    estado_firma VARCHAR(50) DEFAULT 'SIN_FIRMAR',
    archivo_firmado_path TEXT,
    numero_causacion VARCHAR(50),
    fecha_pago DATE,
    usuario_creacion VARCHAR(50)
);
```
**Registros:** 14 facturas actualmente  
**Índices:** nit, empresa, numero_factura, estado

---

#### **4. empresas_facturas**
```sql
CREATE TABLE empresas_facturas (
    id SERIAL PRIMARY KEY,
    sigla VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    nit VARCHAR(20),
    activa BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**Datos:**
| ID | Sigla | Nombre |
|----|-------|--------|
| 1 | SC | SUPERTIENDAS CAÑAVERAL SAS |
| 2 | SCE | SUPERTIENDAS CAÑAVERAL EXPRESS |

---

#### **5. tipo_doc_facturacion** ⭐ NUEVO (Nov 2025)
```sql
CREATE TABLE tipo_doc_facturacion (
    id SERIAL PRIMARY KEY,
    sigla VARCHAR(10) UNIQUE NOT NULL,
    descripcion VARCHAR(100) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(50)
);
```
**Datos:**
| ID | Sigla | Descripción |
|----|-------|-------------|
| 1 | FC | FACTURA |
| 2 | NC | NOTA DÉBITO |
| 3 | ND | NOTA CRÉDITO |

---

#### **6. forma_pago_facturacion** ⭐ NUEVO (Nov 2025)
```sql
CREATE TABLE forma_pago_facturacion (
    id SERIAL PRIMARY KEY,
    sigla VARCHAR(10) UNIQUE NOT NULL,
    descripcion VARCHAR(100) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(50)
);
```
**Datos:**
| ID | Sigla | Descripción |
|----|-------|-------------|
| 1 | EST | ESTÁNDAR |
| 2 | TC | TARJETA DE CRÉDITO |

---

#### **7. tipo_servicio_facturacion** ⭐ NUEVO (Nov 2025)
```sql
CREATE TABLE tipo_servicio_facturacion (
    id SERIAL PRIMARY KEY,
    sigla VARCHAR(10) UNIQUE NOT NULL,
    descripcion VARCHAR(100) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(50)
);
```
**Datos:**
| ID | Sigla | Descripción |
|----|-------|-------------|
| 1 | COMP | COMPRA |
| 2 | SERV | SERVICIO |
| 3 | HONO | HONORARIO |
| 4 | COMP-SERV | COMPRA Y SERVICIO |

---

#### **8. departamentos_facturacion** ⭐ NUEVO (Nov 2025)
```sql
CREATE TABLE departamentos_facturacion (
    id SERIAL PRIMARY KEY,
    sigla VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(50)
);
```
**Datos:**
| ID | Sigla | Nombre |
|----|-------|--------|
| 1 | TIC | TECNOLOGIA |
| 2 | MER | MERCADEO |
| 3 | MYP | MERCADEO ESTRATEGICO |
| 4 | DOM | DOMICILIOS |
| 5 | FIN | FINANCIERO |

---

### **MÓDULO: Relaciones**

#### **9. relaciones_pago**
```sql
CREATE TABLE relaciones_pago (
    id SERIAL PRIMARY KEY,
    numero_relacion VARCHAR(50) UNIQUE NOT NULL,
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cantidad_facturas INTEGER,
    valor_total NUMERIC(15,2),
    ruta_archivo_excel TEXT,
    estado VARCHAR(50) DEFAULT 'GENERADA',
    enviada_por_correo BOOLEAN DEFAULT FALSE,
    fecha_envio_correo TIMESTAMP,
    usuario_creacion VARCHAR(50)
);
```

---

### **MÓDULO: Causaciones**

#### **10. causaciones**
```sql
CREATE TABLE causaciones (
    id SERIAL PRIMARY KEY,
    factura_digital_id INTEGER REFERENCES facturas_digitales(id),
    numero_causacion VARCHAR(50) UNIQUE,
    fecha_causacion DATE,
    valor NUMERIC(15,2),
    estado VARCHAR(50) DEFAULT 'PENDIENTE',
    observaciones TEXT,
    usuario_creacion VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### **MÓDULO: Core (Sistema)**

#### **11. usuarios**
```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(255),
    correo VARCHAR(255),
    tipo_usuario VARCHAR(20) CHECK (tipo_usuario IN ('interno', 'externo')),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP,
    intentos_fallidos INTEGER DEFAULT 0
);
```
**Usuario Admin:**
```
usuario: admin
password: $2b$12$[hash_bcrypt]
tipo_usuario: interno
activo: true
```

---

#### **12. empresas**
```sql
CREATE TABLE empresas (
    id SERIAL PRIMARY KEY,
    sigla VARCHAR(10) UNIQUE NOT NULL,
    codigo VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    nit VARCHAR(20),
    activa BOOLEAN DEFAULT TRUE
);
```
**Datos:**
| Sigla | Código | Nombre |
|-------|--------|--------|
| SC | 01 | SUPERTIENDAS CAÑAVERAL SAS |
| SCE | 02 | SUPERTIENDAS CAÑAVERAL EXPRESS |

---

#### **13. centros_operacion**
```sql
CREATE TABLE centros_operacion (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    empresa_id INTEGER REFERENCES empresas(id),
    activo BOOLEAN DEFAULT TRUE
);
```

---

#### **14. terceros**
```sql
CREATE TABLE terceros (
    id SERIAL PRIMARY KEY,
    nit VARCHAR(20) UNIQUE NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    tipo_documento VARCHAR(10),
    direccion TEXT,
    telefono VARCHAR(50),
    correo VARCHAR(255),
    ciudad VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    fecha_actualizacion_rut DATE,
    es_proveedor BOOLEAN DEFAULT TRUE,
    es_cliente BOOLEAN DEFAULT FALSE
);
```
**Registros:** ~500 terceros

---

#### **15. permisos_usuario**
```sql
CREATE TABLE permisos_usuario (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    modulo VARCHAR(50),
    accion VARCHAR(50),
    permitido BOOLEAN DEFAULT TRUE,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

#### **16. tokens_password**
```sql
CREATE TABLE tokens_password (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) UNIQUE,
    token VARCHAR(255) UNIQUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP,
    usado BOOLEAN DEFAULT FALSE
);
```

---

#### **17. logs_sistema**
```sql
CREATE TABLE logs_sistema (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50),
    mensaje TEXT,
    usuario VARCHAR(50),
    ip VARCHAR(50),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modulo VARCHAR(50),
    accion VARCHAR(100),
    detalles JSONB
);
```

---

### **MÓDULO: Notas Contables**

#### **18. notas_contables**
```sql
CREATE TABLE notas_contables (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(20) CHECK (tipo IN ('DEBITO', 'CREDITO')),
    numero_nota VARCHAR(50) UNIQUE,
    factura_origen_id INTEGER REFERENCES facturas_digitales(id),
    nit_proveedor VARCHAR(20),
    fecha_emision DATE,
    valor NUMERIC(15,2),
    concepto TEXT,
    ruta_archivo TEXT,
    estado VARCHAR(50) DEFAULT 'ACTIVA',
    usuario_creacion VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📁 RUTAS Y DIRECTORIOS

### **Estructura de Carpetas del Sistema**

```
C:\Users\Usuario\Desktop\Gestor Documental\
├── BACKUPS_TRANSPORTABLES/
│   ├── gestor_documental_CUSTOM_20251113_202140.backup
│   ├── gestor_documental_SQL_20251113_202140.sql
│   └── INSTRUCCIONES_RESTAURAR.txt
│
├── PAQUETES_TRANSPORTABLES/
│   └── GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059/
│       ├── app.py (2654 líneas)
│       ├── extensions.py
│       ├── decoradores_permisos.py
│       ├── requirements.txt
│       ├── iniciar_servidor.bat
│       ├── crear_tablas_configuracion.py
│       │
│       ├── docs/
│       │   ├── MODULO_CONFIGURACION_CATALOGOS.md
│       │   ├── CONFIGURACION_CORREO.md
│       │   ├── GUIA_RAPIDA.md
│       │   └── README_Estructura.txt
│       │
│       ├── modules/
│       │   ├── admin/
│       │   ├── causaciones/
│       │   ├── configuracion/
│       │   ├── facturas_digitales/
│       │   │   ├── __init__.py
│       │   │   ├── routes.py (1261 líneas)
│       │   │   ├── config_routes.py (436 líneas)
│       │   │   └── models.py
│       │   ├── notas_contables/
│       │   ├── recibir_facturas/
│       │   └── relaciones/
│       │
│       ├── templates/
│       │   ├── facturas_digitales/
│       │   │   ├── cargar.html (1234 líneas)
│       │   │   ├── dashboard.html (796 líneas)
│       │   │   ├── listado.html
│       │   │   ├── detalle.html
│       │   │   └── configuracion_catalogos.html (596 líneas)
│       │   ├── recibir_facturas/
│       │   ├── relaciones/
│       │   └── causaciones/
│       │
│       ├── static/
│       │   ├── css/
│       │   ├── js/
│       │   └── img/
│       │
│       └── logs/
│           └── app.log
```

---

### **Rutas de Almacenamiento**

#### **Facturas Recibidas**
```
\\192.168.11.33\GestorDocumental\facturas_recibidas\
  └── {año}\
      └── {mes}\
          └── {nit}-{radicado}\
              ├── {nit}-{radicado}-PRINCIPAL.pdf
              ├── {nit}-{radicado}-XML.xml
              └── {nit}-{radicado}-ANEXO-N.pdf
```

#### **Facturas Digitales** ⭐
```
D:\facturas_digitales\
  └── {empresa}\
      └── {año}\
          └── {mes}\
              └── {departamento}\
                  └── {forma_pago}\
                      └── {nit}-{numero}\
                          ├── {nit}-{numero}-PRINCIPAL.pdf
                          ├── {nit}-{numero}-ANEXO-N.pdf
                          └── {nit}-{numero}-SEG_SOCIAL.pdf
```

**Ejemplo:**
```
D:\facturas_digitales\SC\2025\11. NOVIEMBRE\DOM\ESTÁNDAR\805013653-DS-14\
```

---

## ⚙️ CONFIGURACIONES

### **Configuración de Correo (SMTP)**

**Archivo:** `app.py` (líneas 90-100)
```python
app.config['MAIL_SERVER'] = 'mail.supertiendascabanaveralvillavicencio.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'notificaciones@supertiendascabanaveralvillavicencio.com'
app.config['MAIL_PASSWORD'] = 'Notif2024$'
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'notificaciones@supertiendascabanaveralvillavicencio.com'
```

---

### **Configuración de Base de Datos**

**Archivo:** `app.py` (líneas 70-75)
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:G3st0radm$2025.@localhost/gestor_documental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

---

### **Configuración de Sesión**

**Archivo:** `app.py` (líneas 80-85)
```python
app.config['SECRET_KEY'] = 'tu_clave_secreta_super_segura_aqui_2024'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
```

---

### **Rutas de Almacenamiento**

**Archivo:** `modules/facturas_digitales/routes.py`
```python
RUTA_BASE_FACTURAS = r"D:\facturas_digitales"
```

**Archivo:** `modules/recibir_facturas/routes.py`
```python
RUTA_BASE = r"\\192.168.11.33\GestorDocumental\facturas_recibidas"
```

---

## 🎯 FUNCIONALIDADES POR MÓDULO

### **FACTURAS DIGITALES - Funcionalidades Detalladas**

#### **Cargar Factura**
1. **Validación de Duplicados**
   - Verifica en `facturas_digitales`
   - Verifica en `facturas_recibidas`
   - Modal de alerta si existe

2. **Validación de Terceros**
   - Busca en tabla `terceros`
   - Verifica RUT actualizado (<365 días)
   - Alerta si requiere actualización

3. **Dropdowns Dinámicos** ⭐ NUEVO
   - Empresas: Carga desde `empresas_facturas`
   - Tipo Documento: Carga desde `tipo_doc_facturacion` (activos)
   - Forma de Pago: Carga desde `forma_pago_facturacion` (activos)
   - Tipo Servicio: Carga desde `tipo_servicio_facturacion` (activos)
   - Departamentos: Carga desde `departamentos_facturacion` (activos)

4. **Carga de Archivos**
   - Principal: Obligatorio (PDF)
   - Anexos: Opcional (PDF, hasta 10MB c/u)
   - Seguridad Social: Opcional (PDF)

5. **Radicación Automática**
   - Formato: `DS-{número_secuencial}`
   - Ejemplo: DS-1, DS-2, DS-14, etc.
   - Incremento automático

6. **Creación de Carpetas**
   - Estructura automática de 6 niveles
   - Nomenclatura estandarizada
   - Validación de permisos de escritura

7. **Guardado en Base de Datos**
   - Registro en tabla `facturas_digitales`
   - Estado inicial: PENDIENTE
   - Estado firma: SIN_FIRMAR

---

#### **Configuración de Catálogos** ⭐ NUEVO

**Ruta:** `/facturas-digitales/configuracion`

**Características:**
- ✅ CRUD completo para 4 catálogos
- ✅ Interfaz responsive (mobile, tablet, desktop)
- ✅ Modo claro y oscuro (toggle 🌓)
- ✅ Colores institucionales (#0A6E3F, #FFB900)
- ✅ Soft delete (activar/desactivar)
- ✅ Validaciones en tiempo real
- ✅ Auditoría (usuario_creacion, fecha_creacion)

**Endpoints API:**
```
GET    /facturas-digitales/configuracion/api/tipo-documento
POST   /facturas-digitales/configuracion/api/tipo-documento
PUT    /facturas-digitales/configuracion/api/tipo-documento/<id>
DELETE /facturas-digitales/configuracion/api/tipo-documento/<id>

GET    /facturas-digitales/configuracion/api/tipo-documento/activos
GET    /facturas-digitales/configuracion/api/forma-pago/activos
GET    /facturas-digitales/configuracion/api/tipo-servicio/activos
GET    /facturas-digitales/configuracion/api/departamento/activos
```

---

### **RECIBIR FACTURAS - Funcionalidades Detalladas**

1. **Carga de Facturas**
   - Soporte: PDF, XML, ZIP
   - Extracción automática de ZIP
   - OCR de datos fiscales

2. **Validación de Duplicados**
   - Búsqueda por NIT + Prefijo + Folio
   - Modal de alerta con ubicación

3. **Radicación**
   - Formato: `RX-{número}`
   - Único y secuencial

4. **Almacenamiento**
   - Ruta: `\\192.168.11.33\GestorDocumental\facturas_recibidas\`
   - Estructura: `{año}\{mes}\{nit}-{radicado}\`

5. **Estados**
   - RECIBIDA (inicial)
   - EN_RELACION (incluida en relación)
   - PAGADA (procesada)

---

### **RELACIONES - Funcionalidades Detalladas**

1. **Generación de Relación**
   - Selección múltiple de facturas
   - Agrupación por proveedor
   - Cálculo de totales

2. **Archivo Excel**
   - Formato estandarizado
   - Columnas: NIT, Razón Social, Factura, Valor, etc.
   - Almacenamiento automático

3. **Envío por Correo**
   - Destinatario configurable
   - Adjunta Excel generado
   - Plantilla HTML personalizada

4. **Actualización de Estados**
   - Marca facturas como EN_RELACION
   - Registra número de relación
   - Actualiza fecha de relación

---

## 👥 USUARIOS Y PERMISOS

### **Tipos de Usuario**

1. **Usuario Interno**
   - Acceso completo a todos los módulos
   - Puede crear, editar y eliminar
   - Acceso a configuración

2. **Usuario Externo**
   - Acceso limitado a consultas
   - Solo lectura
   - No puede modificar configuración

---

### **Permisos por Módulo**

| Módulo | Ver | Crear | Editar | Eliminar | Configurar |
|--------|-----|-------|--------|----------|------------|
| Recibir Facturas | ✅ | ✅ | ✅ | ❌ | ✅ |
| Facturas Digitales | ✅ | ✅ | ✅ | ❌ | ✅ |
| Relaciones | ✅ | ✅ | ❌ | ❌ | ❌ |
| Causaciones | ✅ | ✅ | ✅ | ❌ | ❌ |
| Configuración | ✅ | ✅ | ✅ | ✅ | ✅ |
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🤖 PROCESOS AUTOMÁTICOS

### **1. Watchdog (Recarga Automática)**
- Monitorea cambios en archivos `.py`
- Recarga automática del servidor
- Útil en desarrollo

### **2. Generación de Radicados**
- Secuencial automático
- Sin duplicados
- Por módulo (RX, DS)

### **3. Creación de Carpetas**
- Automática al radicar
- Estructura estandarizada
- Validación de permisos

### **4. Envío de Correos**
- Relaciones generadas
- Notificaciones de estado
- Plantillas HTML

### **5. Logs del Sistema**
- Registro de acciones
- Errores y excepciones
- Auditoría de cambios

---

## 🔗 INTEGRACIONES

### **1. PostgreSQL**
- Motor de base de datos
- Conexión vía SQLAlchemy
- Pool de conexiones

### **2. SMTP (Zimbra)**
- Envío de correos
- SSL/TLS
- Autenticación

### **3. SMB (Red Windows)**
- Almacenamiento de archivos
- Acceso a carpetas compartidas
- Permisos de red

### **4. PDF.js**
- Visor de PDFs en navegador
- Sin plugins adicionales
- Responsive

### **5. Tailwind CSS**
- Framework CSS
- CDN
- Responsive design

---

## 💾 BACKUP Y RECUPERACIÓN

### **Ubicación de Backups**
```
C:\Users\Usuario\Desktop\Gestor Documental\BACKUPS_TRANSPORTABLES\
```

### **Tipos de Backup**

#### **1. Backup de Base de Datos (CUSTOM)**
```bash
Archivo: gestor_documental_CUSTOM_YYYYMMDD_HHMMSS.backup
Formato: PostgreSQL CUSTOM
Comprimido: Sí
```

#### **2. Backup de Base de Datos (SQL)**
```bash
Archivo: gestor_documental_SQL_YYYYMMDD_HHMMSS.sql
Formato: Plain SQL
Legible: Sí
```

#### **3. Backup Completo del Sistema**
```bash
Carpeta: GESTOR_DOCUMENTAL_TRANSPORTABLE_YYYYMMDD_HHMMSS/
Incluye:
- Código fuente completo
- Templates
- Módulos
- Configuraciones
- Scripts
- Documentación
```

### **Restauración**

#### **Desde CUSTOM:**
```bash
pg_restore -U postgres -d gestor_documental_nueva archivo.backup
```

#### **Desde SQL:**
```bash
psql -U postgres -d gestor_documental_nueva < archivo.sql
```

---

## 📊 ESTADÍSTICAS DEL SISTEMA

### **Tamaño del Código**
- **Total Líneas de Código:** ~15,000 líneas
- **Archivos Python:** 50+ archivos
- **Templates HTML:** 30+ archivos
- **Scripts SQL:** 20+ archivos

### **Módulos Principales**
| Módulo | Líneas | Archivos |
|--------|--------|----------|
| app.py | 2,654 | 1 |
| Facturas Digitales | 3,500+ | 10 |
| Recibir Facturas | 1,500+ | 8 |
| Relaciones | 800+ | 5 |
| Causaciones | 600+ | 4 |
| Configuración | 500+ | 5 |

### **Base de Datos**
- **Tablas:** 28 tablas
- **Registros Totales:** ~6,000 registros
- **Tamaño BD:** ~50 MB
- **Índices:** 40+ índices

---

## 🛠️ TECNOLOGÍAS UTILIZADAS

### **Backend**
- Python 3.11
- Flask 2.3.x
- SQLAlchemy 2.0
- Psycopg2 (PostgreSQL driver)
- Flask-Mail
- Bcrypt (encriptación)
- Werkzeug (utilidades)

### **Frontend**
- HTML5
- CSS3
- JavaScript (ES6+)
- Tailwind CSS (CDN)
- PDF.js
- Font Awesome (iconos)

### **Base de Datos**
- PostgreSQL 16
- PgAdmin 4 (administración)

### **Servidor**
- Flask Development Server
- Puerto: 8099
- Host: 0.0.0.0 (accesible en red)

---

## 🔒 SEGURIDAD

### **Autenticación**
- Sesiones Flask
- Contraseñas con Bcrypt
- Timeout de sesión: 8 horas

### **Autorización**
- Decoradores de permisos
- Validación por módulo y acción
- Control de acceso basado en roles

### **Protección de Datos**
- Conexión HTTPS (recomendado en producción)
- Sanitización de entradas
- Validación de archivos
- Límites de tamaño de carga

### **Auditoría**
- Logs de acciones
- Registro de cambios
- Timestamp en todas las tablas
- Usuario creación/modificación

---

## 📞 SOPORTE Y MANTENIMIENTO

### **Logs del Sistema**
```
Ubicación: logs/app.log
Rotación: Diaria
Nivel: INFO, WARNING, ERROR
```

### **Monitoreo**
- Verificar logs periódicamente
- Revisar espacio en disco
- Validar backups
- Comprobar conexión BD

### **Actualizaciones**
- Backup antes de actualizar
- Probar en ambiente de desarrollo
- Documentar cambios
- Notificar a usuarios

---

## 📝 NOTAS IMPORTANTES

### **Colores Institucionales**
```css
Verde Principal: #0A6E3F
Verde Oscuro: #085330
Amarillo: #FFB900
Amarillo Claro: #FFD966
```

### **Formatos de Radicado**
- Recibir Facturas: `RX-{número}` (Ej: RX-245)
- Facturas Digitales: `DS-{número}` (Ej: DS-14)
- Relaciones: `REL-{número}` (Ej: REL-023)

### **Estados de Factura**
- PENDIENTE
- RECIBIDA
- EN_RELACION
- CAUSADA
- PAGADA
- ANULADA

---

## ✅ CHECKLIST DE VERIFICACIÓN

### **Sistema Operativo**
- [ ] Servidor Flask corriendo en puerto 8099
- [ ] PostgreSQL activo y accesible
- [ ] Rutas de red montadas
- [ ] Permisos de escritura en carpetas

### **Funcionalidades**
- [ ] Login funciona correctamente
- [ ] Carga de facturas operativa
- [ ] Validación de duplicados activa
- [ ] Generación de radicados automática
- [ ] Envío de correos funcionando
- [ ] Dropdowns cargando datos dinámicamente

### **Configuración**
- [ ] Base de datos conectada
- [ ] SMTP configurado
- [ ] Rutas de almacenamiento definidas
- [ ] Usuarios creados
- [ ] Permisos asignados

---

## 🎉 CONCLUSIÓN

Este sistema de Gestor Documental es una solución integral para la gestión de facturas y documentos contables de Supertiendas Cañaveral. Incluye:

✅ **6 módulos principales** completamente operativos  
✅ **28 tablas** de base de datos estructuradas  
✅ **4 catálogos configurables** con interfaz moderna  
✅ **Integración con correo** y almacenamiento en red  
✅ **Validaciones automáticas** de duplicados  
✅ **Radicación automática** con secuenciales  
✅ **Interfaz responsive** con modo claro/oscuro  
✅ **Auditoría completa** de operaciones  
✅ **Backup automático** y recuperación  

**Última actualización:** 27 de Noviembre de 2025  
**Versión del sistema:** 3.0  
**Estado:** Producción ✅

---

**Desarrollado para:**  
**Supertiendas Cañaveral SAS**  
**NIT: 900.XXX.XXX-X**  
**Villavicencio, Meta - Colombia**

---

*Este documento contiene información confidencial y de uso exclusivo de Supertiendas Cañaveral.*
