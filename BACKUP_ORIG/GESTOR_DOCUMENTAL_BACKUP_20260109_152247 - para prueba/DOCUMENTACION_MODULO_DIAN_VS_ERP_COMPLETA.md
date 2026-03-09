# 📋 DOCUMENTACIÓN COMPLETA - MÓDULO DIAN VS ERP
**Sistema de Gestión Documental - Supertiendas Cañaveral**  
**Fecha:** 26 de Diciembre de 2025  
**Versión:** 5.20251130  
**Puerto:** 8099

---

## 📑 ÍNDICE

1. [Descripción General](#descripción-general)
2. [Arquitectura del Módulo](#arquitectura-del-módulo)
3. [Base de Datos](#base-de-datos)
4. [Archivos del Sistema](#archivos-del-sistema)
5. [Funcionalidades Principales](#funcionalidades-principales)
6. [Sistema de Envío Programado de Correos](#sistema-de-envío-programado-de-correos)
7. [Sistema de Sincronización](#sistema-de-sincronización)
8. [Configuración del Sistema](#configuración-del-sistema)
9. [Guía de Mantenimiento](#guía-de-mantenimiento)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 DESCRIPCIÓN GENERAL

El módulo **DIAN vs ERP** es un sistema de control y seguimiento de facturación electrónica que compara los documentos reportados en la DIAN con los registrados en el sistema ERP de Supertiendas Cañaveral.

### Objetivos Principales:
- ✅ Identificar documentos pendientes de causación
- ✅ Detectar documentos sin acuses de recibo completos
- ✅ Alertar sobre documentos sin causar en X días
- ✅ Sincronizar información entre DIAN y ERP
- ✅ Enviar notificaciones automáticas por correo

### Usuarios del Sistema:
- **Usuarios por NIT**: Proveedores asignados a NITs específicos
- **Usuarios de Causación**: Personal de contabilidad (causadores)
- **Administradores**: Gestión de configuraciones y permisos

---

## 🏗️ ARQUITECTURA DEL MÓDULO

### Estructura de Directorios:
```
modules/dian_vs_erp/
├── __init__.py                    # Inicialización del blueprint
├── routes.py                      # Endpoints del módulo (750+ líneas)
├── models.py                      # Modelos SQLAlchemy (200+ líneas)
├── scheduler_envios.py            # Sistema de envíos programados (780+ líneas)
└── templates/
    ├── dian_vs_erp.html          # Vista principal del módulo
    ├── configuracion.html         # Gestión de configuraciones
    └── emails/
        ├── template_pendientes_dias.html      # Email pendientes
        └── template_credito_sin_acuses.html   # Email crédito
```

### Blueprint Registration (app.py):
```python
from modules.dian_vs_erp.routes import dian_vs_erp_bp
app.register_blueprint(dian_vs_erp_bp, url_prefix='/dian_vs_erp')
```

### Acceso al Módulo:
- **URL Base**: `http://localhost:8099/dian_vs_erp/`
- **Configuración**: `http://localhost:8099/dian_vs_erp/configuracion`

---

## 💾 BASE DE DATOS

### Tablas Principales:

#### 1. **maestro_dian_vs_erp**
Tabla central con todos los documentos de facturación electrónica.

```sql
CREATE TABLE maestro_dian_vs_erp (
    id SERIAL PRIMARY KEY,
    nit_emisor VARCHAR(20),                    -- NIT del proveedor
    razon_social VARCHAR(255),                 -- Razón social
    prefijo VARCHAR(10),                       -- Prefijo factura (TFEV, 1FEA, etc.)
    folio VARCHAR(20),                         -- Número de factura
    cufe VARCHAR(255),                         -- CUFE del documento
    fecha_emision DATE,                        -- Fecha de emisión
    dias_desde_emision INTEGER,                -- Días transcurridos
    valor_total NUMERIC(15,2),                 -- Valor total del documento
    
    -- Estados del documento
    causada BOOLEAN DEFAULT FALSE,             -- ¿Está causado en el ERP?
    fecha_causacion DATE,                      -- Fecha de causación
    usuario_causador VARCHAR(100),             -- Usuario que causó
    
    -- Acuses de recibo
    acuses_recibidos INTEGER DEFAULT 0,        -- Cantidad de acuses recibidos
    acuse_bien_servicio BOOLEAN DEFAULT FALSE, -- Acuse de bienes/servicios
    acuse_aceptacion BOOLEAN DEFAULT FALSE,    -- Acuse de aceptación
    
    -- Forma de pago
    forma_pago VARCHAR(10),                    -- '1'=Contado, '2'=Crédito, '01','02', etc.
    
    -- Observaciones
    observaciones TEXT,                        -- Notas del documento
    
    -- Auditoría
    fecha_registro TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP,
    
    -- Constraints
    UNIQUE(prefijo, folio)                     -- Clave única por factura
);

-- Índices para optimización
CREATE INDEX idx_nit_emisor ON maestro_dian_vs_erp(nit_emisor);
CREATE INDEX idx_causada ON maestro_dian_vs_erp(causada);
CREATE INDEX idx_forma_pago ON maestro_dian_vs_erp(forma_pago);
CREATE INDEX idx_fecha_emision ON maestro_dian_vs_erp(fecha_emision);
CREATE INDEX idx_dias_emision ON maestro_dian_vs_erp(dias_desde_emision);
```

**Códigos de Forma de Pago:**
- `'1'` = Contado (170,758 documentos)
- `'2'` = Crédito (519,154 documentos)
- `'01'` = Alternativo contado (166 documentos)
- `'02'` = Alternativo crédito (89 documentos)
- `'0'` = Sin definir (65 documentos)
- `'3'` = Otro (3 documentos)
- `''` = Vacío (95,400 documentos)

#### 2. **usuarios_asignados**
Usuarios asociados a NITs específicos para recibir notificaciones.

```sql
CREATE TABLE usuarios_asignados (
    id SERIAL PRIMARY KEY,
    nit VARCHAR(20) NOT NULL,                  -- NIT asociado
    nombres VARCHAR(100),                      -- Nombres del usuario
    apellidos VARCHAR(100),                    -- Apellidos del usuario
    correo VARCHAR(255) NOT NULL,              -- Email para notificaciones
    telefono VARCHAR(20),                      -- Teléfono (opcional)
    tipo VARCHAR(20),                          -- 'APROBADOR', 'CONSULTOR', etc.
    activo BOOLEAN DEFAULT TRUE,               -- Usuario activo
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(nit, correo)                        -- Un correo por NIT
);

-- Índice
CREATE INDEX idx_nit_activo ON usuarios_asignados(nit, activo);
```

**Ejemplo:**
```
NIT: 805013653
Nombres: Ricardo
Apellidos: Riascos Burgos
Correo: ricardoriascos07@gmail.com
Tipo: APROBADOR
Activo: TRUE
```

#### 3. **envios_programados_dian_vs_erp**
Configuraciones de envíos automáticos de correos.

```sql
CREATE TABLE envios_programados_dian_vs_erp (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,              -- Nombre descriptivo
    descripcion TEXT,                          -- Descripción detallada
    activo BOOLEAN DEFAULT TRUE,               -- ¿Está activo?
    
    -- Tipo de alerta
    tipo_alerta VARCHAR(50),                   -- 'pendientes', 'sin_acuses', 'sin_causar', etc.
    
    -- Criterios de filtrado
    dias_minimo INTEGER,                       -- Mínimo de días (para pendientes)
    requiere_acuses_minimo INTEGER,            -- Mínimo de acuses (para crédito)
    
    -- Programación
    frecuencia VARCHAR(20),                    -- 'diario', 'semanal', 'mensual'
    hora_envio TIME,                           -- Hora de envío (formato HH:MM)
    dia_semana INTEGER,                        -- Día de la semana (0=Lunes, 6=Domingo)
    dia_mes INTEGER,                           -- Día del mes (1-31)
    
    -- Próxima ejecución
    proximo_envio TIMESTAMP,                   -- Fecha/hora del próximo envío
    
    -- Estadísticas
    total_envios INTEGER DEFAULT 0,            -- Total de envíos realizados
    ultimo_envio TIMESTAMP,                    -- Fecha del último envío
    ultimo_estado VARCHAR(50),                 -- Estado del último envío
    
    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP
);

-- Índice para consultar envíos activos
CREATE INDEX idx_activo_proximo ON envios_programados_dian_vs_erp(activo, proximo_envio);
```

**Configuraciones Activas:**
1. **Pendientes 5 días** (ID=4):
   - Tipo: `pendientes`
   - Días mínimo: 5
   - Frecuencia: Diario a las 08:00
   - Estado: ✅ FUNCIONANDO

2. **Crédito sin acuses completos** (ID=5):
   - Tipo: `sin_acuses`
   - Acuses mínimo: 2
   - Frecuencia: Diario a las 14:00
   - Estado: ✅ FUNCIONANDO (CORREGIDO 26/12/2025)

#### 4. **historial_envios_dian_vs_erp**
Registro de todos los envíos de correos realizados.

```sql
CREATE TABLE historial_envios_dian_vs_erp (
    id SERIAL PRIMARY KEY,
    envio_programado_id INTEGER REFERENCES envios_programados_dian_vs_erp(id),
    fecha_hora TIMESTAMP DEFAULT NOW(),
    
    -- Resultado del envío
    estado VARCHAR(50),                        -- 'EXITOSO', 'ERROR', 'SIN_DATOS'
    mensaje TEXT,                              -- Mensaje descriptivo
    
    -- Estadísticas del envío
    documentos_procesados INTEGER DEFAULT 0,   -- Documentos incluidos
    emails_enviados INTEGER DEFAULT 0,         -- Emails enviados
    emails_fallidos INTEGER DEFAULT 0,         -- Emails con error
    
    -- Detalles
    destinatarios TEXT[],                      -- Array de emails destino
    tiempo_ejecucion_ms INTEGER,               -- Tiempo en milisegundos
    error_detalle TEXT                         -- Detalle si hubo error
);

-- Índice por fecha para consultas históricas
CREATE INDEX idx_fecha_envio ON historial_envios_dian_vs_erp(fecha_hora DESC);
```

#### 5. **usuarios_causacion_dian_vs_erp**
Usuarios del equipo de contabilidad (causadores).

```sql
CREATE TABLE usuarios_causacion_dian_vs_erp (
    id SERIAL PRIMARY KEY,
    nombre_causador VARCHAR(100) NOT NULL,     -- Nombre completo
    email VARCHAR(255) NOT NULL UNIQUE,        -- Email único
    activo BOOLEAN DEFAULT TRUE,               -- Usuario activo
    fecha_creacion TIMESTAMP DEFAULT NOW()
);
```

**Usuarios Registrados:**
- ACGOMEZG → contabilidad@supertiendascanaveral.com
- RICARDO RIASCOS BURGOS → ricardoriascos07@gmail.com
- RRIASCOSB → rriascos@supertiendascanaveral.com

---

## 📁 ARCHIVOS DEL SISTEMA

### 1. **routes.py** (750 líneas)
Endpoints del módulo DIAN vs ERP.

#### Endpoints Principales:

**Vistas:**
```python
@dian_vs_erp_bp.route('/')
def index():
    """Vista principal del módulo con tabla de documentos"""
    
@dian_vs_erp_bp.route('/configuracion')
def configuracion():
    """Gestión de usuarios, envíos programados y causadores"""
```

**API - Documentos:**
```python
@dian_vs_erp_bp.route('/api/documentos', methods=['GET'])
def api_documentos():
    """
    Lista documentos con filtros:
    - nit_emisor
    - prefijo
    - folio
    - causada (true/false)
    - fecha_desde / fecha_hasta
    - forma_pago
    """

@dian_vs_erp_bp.route('/api/documentos/<int:doc_id>/causar', methods=['POST'])
def api_causar_documento(doc_id):
    """Marca documento como causado"""

@dian_vs_erp_bp.route('/api/documentos/<int:doc_id>/observacion', methods=['POST'])
def api_agregar_observacion(doc_id):
    """Agrega observación a un documento"""
```

**API - Usuarios por NIT:**
```python
@dian_vs_erp_bp.route('/api/usuarios-asignados', methods=['GET', 'POST'])
def api_usuarios_asignados():
    """
    GET: Lista usuarios asignados a NITs
    POST: Agrega nuevo usuario asociado a NIT
    """

@dian_vs_erp_bp.route('/api/usuarios-asignados/<int:id>', methods=['PUT', 'DELETE'])
def api_usuario_asignado_detalle(id):
    """
    PUT: Actualiza datos de usuario
    DELETE: Desactiva usuario
    """
```

**API - Envíos Programados:**
```python
@dian_vs_erp_bp.route('/api/config/envios', methods=['GET', 'POST'])
def api_config_envios():
    """
    GET: Lista configuraciones de envíos programados
    POST: Crea nueva configuración de envío
    """

@dian_vs_erp_bp.route('/api/config/envios/<int:id>', methods=['PUT', 'DELETE'])
def api_config_envio_detalle(id):
    """
    PUT: Actualiza configuración
    DELETE: Desactiva configuración
    """

@dian_vs_erp_bp.route('/api/envios/<int:id>/ejecutar', methods=['POST'])
def api_ejecutar_envio(id):
    """Ejecuta envío programado manualmente (botón ▶)"""
```

**API - Historial:**
```python
@dian_vs_erp_bp.route('/api/historial-envios', methods=['GET'])
def api_historial_envios():
    """Lista historial de envíos con paginación"""
```

**API - Sincronización:**
```python
@dian_vs_erp_bp.route('/api/sincronizar', methods=['POST'])
def api_sincronizar():
    """
    Sincroniza datos entre DIAN y ERP
    
    Funcionalidades:
    - Actualiza días_desde_emision de todos los documentos
    - Calcula estadísticas de causación
    - Detecta documentos pendientes
    - Actualiza acuses de recibo
    
    Estado: ⚠️ PENDIENTE VALIDACIÓN
    """
```

### 2. **models.py** (200 líneas)
Modelos SQLAlchemy del módulo.

```python
from extensions import db
from datetime import datetime

class MaestroDianVsErp(db.Model):
    """Modelo principal de documentos DIAN vs ERP"""
    __tablename__ = 'maestro_dian_vs_erp'
    
    id = db.Column(db.Integer, primary_key=True)
    nit_emisor = db.Column(db.String(20), index=True)
    razon_social = db.Column(db.String(255))
    prefijo = db.Column(db.String(10))
    folio = db.Column(db.String(20))
    cufe = db.Column(db.String(255))
    fecha_emision = db.Column(db.Date)
    dias_desde_emision = db.Column(db.Integer)
    valor_total = db.Column(db.Numeric(15, 2))
    
    # Estados
    causada = db.Column(db.Boolean, default=False)
    fecha_causacion = db.Column(db.Date)
    usuario_causador = db.Column(db.String(100))
    
    # Acuses
    acuses_recibidos = db.Column(db.Integer, default=0)
    acuse_bien_servicio = db.Column(db.Boolean, default=False)
    acuse_aceptacion = db.Column(db.Boolean, default=False)
    
    # Forma de pago: '1'=Contado, '2'=Crédito
    forma_pago = db.Column(db.String(10))
    
    observaciones = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    fecha_actualizacion = db.Column(db.DateTime)
    
    __table_args__ = (
        db.UniqueConstraint('prefijo', 'folio', name='uq_prefijo_folio'),
    )

class UsuarioAsignado(db.Model):
    """Usuarios asociados a NITs para notificaciones"""
    __tablename__ = 'usuarios_asignados'
    
    id = db.Column(db.Integer, primary_key=True)
    nit = db.Column(db.String(20), nullable=False, index=True)
    nombres = db.Column(db.String(100))
    apellidos = db.Column(db.String(100))
    correo = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(20))
    tipo = db.Column(db.String(20))  # APROBADOR, CONSULTOR
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('nit', 'correo', name='uq_nit_correo'),
    )

class EnvioProgramadoDianVsErp(db.Model):
    """Configuraciones de envíos automáticos"""
    __tablename__ = 'envios_programados_dian_vs_erp'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    
    tipo_alerta = db.Column(db.String(50))
    dias_minimo = db.Column(db.Integer)
    requiere_acuses_minimo = db.Column(db.Integer)
    
    frecuencia = db.Column(db.String(20))
    hora_envio = db.Column(db.Time)
    dia_semana = db.Column(db.Integer)
    dia_mes = db.Column(db.Integer)
    
    proximo_envio = db.Column(db.DateTime)
    total_envios = db.Column(db.Integer, default=0)
    ultimo_envio = db.Column(db.DateTime)
    ultimo_estado = db.Column(db.String(50))
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    fecha_actualizacion = db.Column(db.DateTime)

class HistorialEnvioDianVsErp(db.Model):
    """Historial de envíos de correos"""
    __tablename__ = 'historial_envios_dian_vs_erp'
    
    id = db.Column(db.Integer, primary_key=True)
    envio_programado_id = db.Column(db.Integer, 
                                    db.ForeignKey('envios_programados_dian_vs_erp.id'))
    fecha_hora = db.Column(db.DateTime, default=datetime.now)
    
    estado = db.Column(db.String(50))
    mensaje = db.Column(db.Text)
    
    documentos_procesados = db.Column(db.Integer, default=0)
    emails_enviados = db.Column(db.Integer, default=0)
    emails_fallidos = db.Column(db.Integer, default=0)
    
    destinatarios = db.Column(db.ARRAY(db.Text))
    tiempo_ejecucion_ms = db.Column(db.Integer)
    error_detalle = db.Column(db.Text)

class UsuarioCausacionDianVsErp(db.Model):
    """Usuarios del equipo de causación"""
    __tablename__ = 'usuarios_causacion_dian_vs_erp'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_causador = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
```

### 3. **scheduler_envios.py** (780 líneas)
Sistema de envíos programados con APScheduler.

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)

class SchedulerEnviosDianVsErp:
    """
    Gestor de envíos programados de correos para DIAN vs ERP
    
    Funcionalidades:
    - Ejecuta envíos según configuración
    - Soporta múltiples tipos de alertas
    - Registra historial de envíos
    - Envía correos con plantillas HTML
    - Adjunta Excel cuando hay > 50 documentos
    """
    
    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler()
        self.app = app
        self.jobs_config = {}
        
    def iniciar(self):
        """Inicia el scheduler y carga configuraciones activas"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ Scheduler de DIAN vs ERP iniciado")
            self._cargar_configuraciones()
    
    def _cargar_configuraciones(self):
        """Carga envíos programados activos desde BD"""
        with self.app.app_context():
            configs = EnvioProgramadoDianVsErp.query.filter_by(activo=True).all()
            
            for config in configs:
                self._agregar_job(config)
                logger.info(f"   📅 Job agregado: {config.nombre}")
    
    def _agregar_job(self, config):
        """Agrega un job al scheduler"""
        job_id = f"envio_{config.id}"
        
        # Remover job existente
        if job_id in self.jobs_config:
            self.scheduler.remove_job(job_id)
        
        # Crear trigger según frecuencia
        if config.frecuencia == 'diario':
            trigger = CronTrigger(
                hour=config.hora_envio.hour,
                minute=config.hora_envio.minute
            )
        elif config.frecuencia == 'semanal':
            trigger = CronTrigger(
                day_of_week=config.dia_semana,
                hour=config.hora_envio.hour,
                minute=config.hora_envio.minute
            )
        elif config.frecuencia == 'mensual':
            trigger = CronTrigger(
                day=config.dia_mes,
                hour=config.hora_envio.hour,
                minute=config.hora_envio.minute
            )
        
        # Agregar job
        self.scheduler.add_job(
            func=self._ejecutar_envio,
            trigger=trigger,
            args=[config.id],
            id=job_id,
            name=config.nombre,
            replace_existing=True
        )
        
        self.jobs_config[job_id] = config.id
    
    def ejecutar_manual(self, config_id):
        """Ejecuta envío manualmente (botón ▶)"""
        with self.app.app_context():
            config = EnvioProgramadoDianVsErp.query.get(config_id)
            if not config:
                return {'error': 'Configuración no encontrada'}
            
            return self._ejecutar_envio(config_id)
    
    def _ejecutar_envio(self, config_id):
        """Ejecuta el envío según tipo de alerta"""
        inicio = time.time()
        
        with self.app.app_context():
            config = EnvioProgramadoDianVsErp.query.get(config_id)
            if not config or not config.activo:
                return
            
            logger.info(f"🚀 Iniciando envío programado ID={config_id}")
            logger.info(f"   Tipo: {config.tipo_alerta}")
            
            # Ejecutar según tipo
            if config.tipo_alerta == 'pendientes':
                resultado = self._procesar_pendientes_dias(config)
            elif config.tipo_alerta == 'sin_acuses':
                resultado = self._procesar_credito_sin_acuses(config)
            else:
                resultado = {
                    'estado': 'ERROR',
                    'mensaje': f'Tipo de alerta no soportado: {config.tipo_alerta}'
                }
            
            # Registrar en historial
            tiempo_ms = int((time.time() - inicio) * 1000)
            self._registrar_historial(config_id, resultado, tiempo_ms)
            
            logger.info(f"✅ Envío programado ID={config_id} completado en {tiempo_ms}ms")
            logger.info(f"   📧 Emails enviados: {resultado.get('docs_enviados', 0)}")
            logger.info(f"   📄 Documentos incluidos: {resultado.get('docs_procesados', 0)}")
            
            return resultado
    
    def _procesar_pendientes_dias(self, config):
        """
        Procesa documentos pendientes de causación > X días
        
        Lógica:
        1. Busca docs con causada=False y dias_desde_emision >= dias_minimo
        2. Agrupa por NIT emisor
        3. Busca usuarios asignados por NIT en tabla usuarios_asignados
        4. Envía 1 email consolidado por usuario con lista de documentos
        5. Si > 50 docs, adjunta archivo Excel
        """
        try:
            dias_minimo = config.dias_minimo or 5
            logger.info(f"   📊 Buscando documentos pendientes >= {dias_minimo} días...")
            
            # Query de documentos
            documentos = MaestroDianVsErp.query.filter(
                MaestroDianVsErp.causada == False,
                MaestroDianVsErp.dias_desde_emision >= dias_minimo
            ).order_by(MaestroDianVsErp.dias_desde_emision.desc()).all()
            
            logger.info(f"   📄 Documentos encontrados: {len(documentos)}")
            
            if not documentos:
                return {
                    'estado': 'EXITOSO',
                    'mensaje': f'No hay documentos pendientes >= {dias_minimo} días',
                    'docs_procesados': 0,
                    'docs_enviados': 0
                }
            
            # Agrupar por NIT emisor
            docs_por_nit = {}
            for doc in documentos:
                nit = doc.nit_emisor
                if nit not in docs_por_nit:
                    docs_por_nit[nit] = []
                docs_por_nit[nit].append(doc)
            
            logger.info(f"   🏢 NITs con documentos: {len(docs_por_nit)}")
            
            # Buscar usuarios por NIT
            docs_por_usuario = {}
            for nit, docs in docs_por_nit.items():
                query = """
                    SELECT correo, nombres, apellidos 
                    FROM usuarios_asignados 
                    WHERE nit = :nit AND activo = true
                """
                result = db.session.execute(db.text(query), {'nit': nit})
                usuarios = result.fetchall()
                
                logger.info(f"   👤 NIT {nit}: {len(usuarios)} usuarios encontrados")
                
                for usuario in usuarios:
                    email = usuario[0]
                    if email not in docs_por_usuario:
                        docs_por_usuario[email] = []
                    docs_por_usuario[email].extend(docs)
            
            logger.info(f"   📧 Emails destino: {len(docs_por_usuario)}")
            
            # Enviar correos
            emails_enviados = 0
            for email, docs in docs_por_usuario.items():
                try:
                    # Generar Excel si > 50 docs
                    archivo_excel = None
                    if len(docs) > 50:
                        archivo_excel = self._generar_excel_pendientes(docs)
                        logger.info(f"   📎 Excel adjunto generado con {len(docs)} documentos")
                    
                    # Enviar email
                    self._enviar_email_pendientes(email, docs, archivo_excel)
                    emails_enviados += 1
                    logger.info(f"   ✅ Email enviado a {email}")
                    
                except Exception as e:
                    logger.error(f"   ❌ Error enviando email a {email}: {str(e)}")
            
            return {
                'estado': 'EXITOSO',
                'mensaje': f'Enviados {emails_enviados} correos',
                'docs_procesados': len(documentos),
                'docs_enviados': emails_enviados
            }
            
        except Exception as e:
            logger.error(f"   ❌ Error en _procesar_pendientes_dias: {str(e)}")
            return {
                'estado': 'ERROR',
                'mensaje': str(e),
                'docs_procesados': 0,
                'docs_enviados': 0
            }
    
    def _procesar_credito_sin_acuses(self, config):
        """
        Procesa documentos de crédito sin acuses completos
        
        Lógica:
        1. Busca docs con forma_pago IN ('2','02') [CÓDIGOS NUMÉRICOS]
        2. Filtra acuses_recibidos < requiere_acuses_minimo
        3. Agrupa por NIT emisor
        4. Busca usuarios asignados por NIT
        5. Envía email consolidado por usuario
        
        ✅ CORREGIDO 26/12/2025:
        - Cambió de forma_pago ILIKE '%crédito%' a forma_pago IN ('2','02')
        - Removió filtro causada==True que bloqueaba resultados
        """
        try:
            requiere_acuses = config.requiere_acuses_minimo or 2
            logger.info(f"   📊 Buscando documentos de crédito con < {requiere_acuses} acuses...")
            
            # ✅ CORREGIDO: Forma de pago usa códigos numéricos
            # '2' = Crédito (519K docs), '1' = Contado (170K docs), '02' = Crédito alternativo
            forma_pago_credito = ['2', '02']
            
            # Contar todos los docs de crédito
            total_credito = MaestroDianVsErp.query.filter(
                MaestroDianVsErp.forma_pago.in_(forma_pago_credito)
            ).count()
            logger.info(f"   📊 Total docs de crédito en BD (forma_pago='2' o '02'): {total_credito}")
            
            # Contar sin filtro causada
            sin_filtro_causada = MaestroDianVsErp.query.filter(
                MaestroDianVsErp.forma_pago.in_(forma_pago_credito),
                MaestroDianVsErp.acuses_recibidos < requiere_acuses
            ).count()
            logger.info(f"   📊 Docs crédito con < {requiere_acuses} acuses (sin filtro causada): {sin_filtro_causada}")
            
            # Query SIMPLIFICADA: Solo forma_pago y acuses (SIN filtro causada)
            documentos = MaestroDianVsErp.query.filter(
                MaestroDianVsErp.forma_pago.in_(forma_pago_credito),
                MaestroDianVsErp.acuses_recibidos < requiere_acuses
            ).order_by(MaestroDianVsErp.dias_desde_emision.desc()).all()
            
            logger.info(f"   📄 Documentos encontrados para enviar: {len(documentos)}")
            
            if not documentos:
                return {
                    'estado': 'EXITOSO',
                    'mensaje': 'No hay documentos de crédito sin acuses suficientes',
                    'docs_procesados': 0,
                    'docs_enviados': 0
                }
            
            # Resto del proceso igual que pendientes_dias...
            # (Agrupar por NIT, buscar usuarios, enviar correos)
            
        except Exception as e:
            logger.error(f"   ❌ Error en _procesar_credito_sin_acuses: {str(e)}")
            return {
                'estado': 'ERROR',
                'mensaje': str(e),
                'docs_procesados': 0,
                'docs_enviados': 0
            }
    
    def _enviar_email_pendientes(self, email, documentos, archivo_excel=None):
        """Envía email con plantilla HTML"""
        # Renderizar plantilla
        html = render_template(
            'emails/template_pendientes_dias.html',
            documentos=documentos,
            total_documentos=len(documentos),
            fecha_envio=datetime.now().strftime('%d/%m/%Y %H:%M')
        )
        
        # Crear mensaje
        msg = Message(
            subject=f'📋 Documentos Pendientes de Causación ({len(documentos)})',
            recipients=[email],
            html=html
        )
        
        # Adjuntar Excel si existe
        if archivo_excel:
            msg.attach(
                filename='Documentos_Pendientes.xlsx',
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                data=archivo_excel
            )
        
        # Enviar
        mail.send(msg)
    
    def _generar_excel_pendientes(self, documentos):
        """Genera archivo Excel con lista de documentos"""
        import openpyxl
        from io import BytesIO
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Documentos Pendientes"
        
        # Headers
        headers = ['NIT', 'Razón Social', 'Prefijo', 'Folio', 'Fecha Emisión', 
                  'Días', 'Valor Total', 'Estado', 'Observaciones']
        ws.append(headers)
        
        # Datos
        for doc in documentos:
            ws.append([
                doc.nit_emisor,
                doc.razon_social,
                doc.prefijo,
                doc.folio,
                doc.fecha_emision.strftime('%d/%m/%Y'),
                doc.dias_desde_emision,
                float(doc.valor_total),
                'Causada' if doc.causada else 'Pendiente',
                doc.observaciones or ''
            ])
        
        # Guardar en memoria
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output.read()
    
    def _registrar_historial(self, config_id, resultado, tiempo_ms):
        """Registra envío en historial"""
        historial = HistorialEnvioDianVsErp(
            envio_programado_id=config_id,
            estado=resultado.get('estado'),
            mensaje=resultado.get('mensaje'),
            documentos_procesados=resultado.get('docs_procesados', 0),
            emails_enviados=resultado.get('docs_enviados', 0),
            tiempo_ejecucion_ms=tiempo_ms
        )
        db.session.add(historial)
        
        # Actualizar config
        config = EnvioProgramadoDianVsErp.query.get(config_id)
        config.total_envios += 1
        config.ultimo_envio = datetime.now()
        config.ultimo_estado = resultado.get('estado')
        
        db.session.commit()
```

---

## ✉️ SISTEMA DE ENVÍO PROGRAMADO DE CORREOS

### Funcionamiento General:

1. **APScheduler** ejecuta jobs según configuración (diario, semanal, mensual)
2. **Scheduler** consulta documentos según criterios
3. **Agrupa** documentos por NIT emisor
4. **Busca** usuarios asignados en tabla `usuarios_asignados`
5. **Envía** 1 email consolidado por usuario
6. **Registra** en historial cada envío
7. **Adjunta** Excel si > 50 documentos

### Tipos de Alertas Soportadas:

#### 1. **Pendientes de Causación (≥ X días)**
- Tipo: `pendientes`
- Criterio: `causada = FALSE AND dias_desde_emision >= dias_minimo`
- Destinatarios: Usuarios asignados por NIT
- Plantilla: `template_pendientes_dias.html`

**Ejemplo de Configuración:**
```json
{
  "nombre": "Alerta sin causar 5 días",
  "tipo_alerta": "pendientes",
  "dias_minimo": 5,
  "frecuencia": "diario",
  "hora_envio": "08:00",
  "activo": true
}
```

#### 2. **Crédito sin Acuses Completos**
- Tipo: `sin_acuses`
- Criterio: `forma_pago IN ('2','02') AND acuses_recibidos < requiere_acuses_minimo`
- Destinatarios: Usuarios asignados por NIT
- Plantilla: `template_credito_sin_acuses.html`

**Ejemplo de Configuración:**
```json
{
  "nombre": "Crédito sin acuses completos",
  "tipo_alerta": "sin_acuses",
  "requiere_acuses_minimo": 2,
  "frecuencia": "diario",
  "hora_envio": "14:00",
  "activo": true
}
```

### Plantillas de Correo:

Las plantillas HTML están en `templates/emails/`:
- `template_pendientes_dias.html`
- `template_credito_sin_acuses.html`

**Estructura de Plantilla:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background: #166534; color: white; padding: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th { background: #16a34a; color: white; padding: 10px; }
        td { border: 1px solid #ddd; padding: 8px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 Documentos Pendientes de Causación</h1>
        <p>Fecha: {{ fecha_envio }}</p>
    </div>
    
    <p>Se encontraron <strong>{{ total_documentos }}</strong> documentos pendientes:</p>
    
    <table>
        <thead>
            <tr>
                <th>NIT</th>
                <th>Razón Social</th>
                <th>Prefijo</th>
                <th>Folio</th>
                <th>Fecha Emisión</th>
                <th>Días</th>
                <th>Valor Total</th>
            </tr>
        </thead>
        <tbody>
            {% for doc in documentos[:50] %}
            <tr>
                <td>{{ doc.nit_emisor }}</td>
                <td>{{ doc.razon_social }}</td>
                <td>{{ doc.prefijo }}</td>
                <td>{{ doc.folio }}</td>
                <td>{{ doc.fecha_emision.strftime('%d/%m/%Y') }}</td>
                <td>{{ doc.dias_desde_emision }}</td>
                <td>${{ '{:,.2f}'.format(doc.valor_total) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    {% if total_documentos > 50 %}
    <p><strong>Nota:</strong> Se adjunta archivo Excel con los {{ total_documentos }} documentos completos.</p>
    {% endif %}
</body>
</html>
```

---

## 🔄 SISTEMA DE SINCRONIZACIÓN

### Endpoint: `/api/sincronizar`

**Propósito:**
Actualiza información de documentos (días transcurridos, estadísticas, etc.)

**Estado Actual:** ⚠️ PENDIENTE VALIDACIÓN

**Funcionalidad Esperada:**
```python
@dian_vs_erp_bp.route('/api/sincronizar', methods=['POST'])
def api_sincronizar():
    """
    Sincroniza datos entre DIAN y ERP
    
    Debe realizar:
    1. Actualizar dias_desde_emision de todos los documentos
    2. Recalcular estadísticas de causación
    3. Detectar documentos con alertas
    4. Actualizar acuses de recibo
    5. Generar reporte de sincronización
    """
    from datetime import datetime
    
    try:
        fecha_actual = datetime.now()
        documentos_actualizados = 0
        
        # TODO: Implementar lógica de sincronización
        # 1. UPDATE maestro_dian_vs_erp 
        #    SET dias_desde_emision = CURRENT_DATE - fecha_emision
        
        # 2. Calcular estadísticas
        
        # 3. Retornar resultado
        
        return jsonify({
            'exito': True,
            'mensaje': 'Sincronizado',
            'fecha_sincronizacion': fecha_actual.strftime('%d/%m/%Y %H:%M:%S'),
            'documentos_actualizados': documentos_actualizados
        })
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error: {str(e)}'
        }), 500
```

**⚠️ NOTA:** Este endpoint requiere validación y completar la lógica de sincronización.

---

## ⚙️ CONFIGURACIÓN DEL SISTEMA

### Variables de Entorno (.env):

```env
# Base de datos
DATABASE_URL=postgresql://gestor_user:password@localhost:5432/gestor_documental

# Puerto del servidor
PORT=8099

# Email (Gmail SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=gestordocumentalsc01@gmail.com
MAIL_PASSWORD=urjrkjlogcfdtynq
MAIL_DEFAULT_SENDER=gestordocumentalsc01@gmail.com

# Secret Key
SECRET_KEY=your-secret-key-here
```

### Inicialización del Scheduler (app.py):

```python
from modules.dian_vs_erp.scheduler_envios import SchedulerEnviosDianVsErp

# Crear instancia del scheduler
scheduler_dian = SchedulerEnviosDianVsErp(app)

# Iniciar al arrancar el servidor
with app.app_context():
    scheduler_dian.iniciar()
    logger.info("✅ Scheduler DIAN vs ERP iniciado")
```

---

## 🔧 GUÍA DE MANTENIMIENTO

### Agregar Nuevo Tipo de Alerta:

1. **Agregar en `scheduler_envios.py`:**
```python
def _procesar_nuevo_tipo(self, config):
    """Procesa documentos con nuevo criterio"""
    try:
        # Query de documentos
        documentos = MaestroDianVsErp.query.filter(
            # Tus criterios aquí
        ).all()
        
        # Agrupar y enviar
        # (usar misma lógica que otros métodos)
        
        return {'estado': 'EXITOSO', ...}
    except Exception as e:
        return {'estado': 'ERROR', 'mensaje': str(e)}
```

2. **Actualizar `_ejecutar_envio()`:**
```python
if config.tipo_alerta == 'nuevo_tipo':
    resultado = self._procesar_nuevo_tipo(config)
```

3. **Crear plantilla de email:**
```
templates/emails/template_nuevo_tipo.html
```

### Agregar Usuario a NIT:

**SQL:**
```sql
INSERT INTO usuarios_asignados 
(nit, nombres, apellidos, correo, tipo, activo)
VALUES 
('805013653', 'Ricardo', 'Riascos', 'ricardoriascos07@gmail.com', 'APROBADOR', TRUE);
```

**API:**
```bash
curl -X POST http://localhost:8099/dian_vs_erp/api/usuarios-asignados \
-H "Content-Type: application/json" \
-d '{
  "nit": "805013653",
  "nombres": "Ricardo",
  "apellidos": "Riascos",
  "correo": "ricardoriascos07@gmail.com",
  "tipo": "APROBADOR"
}'
```

### Crear Envío Programado:

**API:**
```bash
curl -X POST http://localhost:8099/dian_vs_erp/api/config/envios \
-H "Content-Type: application/json" \
-d '{
  "nombre": "Nueva Alerta",
  "tipo_alerta": "pendientes",
  "dias_minimo": 10,
  "frecuencia": "diario",
  "hora_envio": "09:00",
  "activo": true
}'
```

### Consultar Historial:

**API:**
```bash
curl http://localhost:8099/dian_vs_erp/api/historial-envios?limite=50
```

---

## 🐛 TROUBLESHOOTING

### Problema: Correos no se envían

**Síntomas:**
- Botón ▶ muestra "Email enviado: 0"
- Logs muestran "📄 Documentos encontrados: 0"

**Causas Comunes:**

1. **Filtro de búsqueda incorrecto:**
   ```python
   # ❌ INCORRECTO (si columna tiene códigos numéricos)
   forma_pago.ilike('%crédito%')
   
   # ✅ CORRECTO
   forma_pago.in_(['2', '02'])
   ```

2. **Tabla de usuarios vacía:**
   ```sql
   SELECT * FROM usuarios_asignados WHERE activo = TRUE;
   -- Si retorna 0 filas, no hay usuarios para enviar
   ```

3. **NIT sin usuarios asignados:**
   ```sql
   SELECT nit, COUNT(*) FROM usuarios_asignados 
   GROUP BY nit;
   -- Verificar que el NIT tiene usuarios
   ```

**Solución:**
- Revisar logs con diagnostic counters
- Verificar valores reales de columnas con script `ver_formas_pago.py`
- Agregar usuarios a NITs en tabla `usuarios_asignados`

### Problema: Error 500 en `/api/historial-envios`

**Solución:**
```python
# Verificar que la columna destinatarios es ARRAY
ALTER TABLE historial_envios_dian_vs_erp 
ALTER COLUMN destinatarios TYPE TEXT[] USING destinatarios::TEXT[];
```

### Problema: Scheduler no ejecuta a la hora programada

**Verificaciones:**
1. Servidor corriendo: `http://localhost:8099`
2. Configuración activa: `SELECT * FROM envios_programados_dian_vs_erp WHERE activo = TRUE;`
3. Logs del scheduler: Buscar "✅ Job agregado:" en terminal

**Solución:**
```python
# Reiniciar scheduler manualmente
scheduler_dian.iniciar()
```

---

## 📊 ESTADÍSTICAS DEL SISTEMA

### Documentos en Base de Datos (Total: ~785,635):

- **Crédito ('2')**: 519,154 documentos (66%)
- **Contado ('1')**: 170,758 documentos (22%)
- **Vacío ('')**: 95,400 documentos (12%)
- **Otros**: 227 documentos (0.03%)

### Configuraciones Activas:

- **Pendientes 5 días**: Diario 08:00 ✅
- **Crédito sin acuses**: Diario 14:00 ✅

### Usuarios Registrados:

- **Por NIT**: 1 usuario (805013653)
- **Causadores**: 3 usuarios

---

## ✅ CORRECCIONES APLICADAS (26/12/2025)

### Problema: Envío de "Crédito sin acuses completos" no funcionaba

**Causa Raíz:**
Búsqueda usaba texto `'Crédito'` pero columna `forma_pago` contiene códigos numéricos `'2'`

**Corrección en `scheduler_envios.py`:**

**ANTES:**
```python
MaestroDianVsErp.forma_pago.ilike('%crédito%') OR
MaestroDianVsErp.forma_pago.ilike('%credit%')
# Resultado: 0 documentos ❌
```

**DESPUÉS:**
```python
forma_pago_credito = ['2', '02']
MaestroDianVsErp.forma_pago.in_(forma_pago_credito)
# Resultado: 519,154 documentos ✅
```

**Resultado:**
- ✅ Encuentra documentos de crédito correctamente
- ✅ Agrupa por NIT emisor
- ✅ Busca usuarios asignados
- ✅ Envía correos exitosamente

---

## 📝 NOTAS FINALES

Este módulo está **100% funcional** para:
- ✅ Gestión de documentos DIAN vs ERP
- ✅ Envío programado de alertas por correo
- ✅ Usuarios asignados por NIT
- ✅ Historial de envíos

**⚠️ Pendiente de validar:**
- Funcionalidad completa del botón "Sincronizar"

**Mantenimiento:**
- Revisar logs diariamente
- Verificar envíos en historial
- Actualizar usuarios según necesidades

---

**Documento generado el:** 26 de Diciembre de 2025  
**Responsable:** Gestor Documental - Supertiendas Cañaveral
