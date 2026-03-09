-- ============================================
-- SISTEMA HÍBRIDO: SQLite + CSV
-- Base de Datos para Control Facturas DIAN vs ERP
-- Integrado al Gestor Documental - v5
-- ============================================

-- TABLA PRINCIPAL: DIAN (Facturas electrónicas DIAN)
-- PRIMARY KEY: cufe (único por factura electrónica)
-- INDEX: clave para JOIN con ERP
CREATE TABLE IF NOT EXISTS dian (
    -- Identificadores únicos
    cufe TEXT PRIMARY KEY,                  -- CUFE único de factura electrónica
    clave TEXT NOT NULL,                    -- NIT+PREFIJO+FOLIO8 (para JOIN con ERP)
    
    -- Datos del emisor
    nit_emisor TEXT,
    nombre_emisor TEXT,
    
    -- Datos del documento
    prefijo TEXT,
    folio TEXT,
    folio_limpio TEXT,                      -- Últimos 8 dígitos sin ceros izquierda
    tipo_documento TEXT,                    -- FE, NCE, NDE, etc (siglas)
    
    -- Fechas
    fecha_emision TEXT,                     -- Formato YYYY-MM-DD
    dias_desde_emision INTEGER,
    
    -- Valores
    valor REAL,
    
    -- Estado contable (calculado)
    estado_contable TEXT,                   -- Causada, Recibida (F), Recibida (D), No Registrada
    
    -- Datos de ERP (desde JOIN)
    modulo TEXT,                            -- COMERCIAL o FINANCIERO
    doc_causado_por TEXT,                   -- Compañía - Usuario - Número
    
    -- Estado de aprobación (desde ACUSES)
    estado_aprobacion TEXT,                 -- Aprobado, Rechazado, etc
    
    -- Metadatos
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ÍNDICES para DIAN (optimización de queries)
CREATE INDEX IF NOT EXISTS idx_dian_clave ON dian(clave);
CREATE INDEX IF NOT EXISTS idx_dian_nit ON dian(nit_emisor);
CREATE INDEX IF NOT EXISTS idx_dian_fecha ON dian(fecha_emision);
CREATE INDEX IF NOT EXISTS idx_dian_estado ON dian(estado_contable);
CREATE INDEX IF NOT EXISTS idx_dian_modulo ON dian(modulo);

-- ============================================

-- TABLA ERP: Facturas causadas en sistema ERP
-- PRIMARY KEY: clave (NIT+PREFIJO+FOLIO8)
-- Consolida datos de ERP_FN, ERP_CM y errores
CREATE TABLE IF NOT EXISTS erp (
    -- Identificador único
    clave TEXT PRIMARY KEY,                 -- NIT+PREFIJO+FOLIO8 (último 8 dígitos sin ceros)
    
    -- Datos del proveedor
    proveedor TEXT,                         -- NIT del proveedor
    nombre_proveedor TEXT,
    
    -- Datos del documento
    prefijo TEXT,
    folio_limpio TEXT,                      -- Últimos 8 dígitos sin ceros izquierda
    docto_proveedor TEXT,                   -- Documento original (con prefijo)
    
    -- Clasificación
    clase_documento TEXT,                   -- Factura de proveedor, Nota débito, etc
    modulo TEXT NOT NULL,                   -- COMERCIAL o FINANCIERO
    
    -- Documento causante
    compania TEXT,
    usuario TEXT,
    numero_documento TEXT,
    doc_causado_por TEXT,                   -- Formato: Compañía - Usuario - Número
    
    -- Metadatos
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ÍNDICES para ERP
CREATE INDEX IF NOT EXISTS idx_erp_clave ON erp(clave);
CREATE INDEX IF NOT EXISTS idx_erp_proveedor ON erp(proveedor);
CREATE INDEX IF NOT EXISTS idx_erp_modulo ON erp(modulo);

-- ============================================

-- TABLA ACUSES: Estados de aprobación de documentos DIAN
-- PRIMARY KEY: cufe (relacionado con dian.cufe)
CREATE TABLE IF NOT EXISTS acuses (
    -- Identificador único
    cufe TEXT PRIMARY KEY,                  -- CUFE de la factura electrónica
    
    -- Estado del documento
    estado_documento TEXT,                  -- Aprobado, Rechazado, Aprobado con Notificación
    descripcion TEXT,
    
    -- Fechas
    fecha_acuse TEXT,                       -- Fecha del acuse
    
    -- Metadatos
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ÍNDICE para ACUSES
CREATE INDEX IF NOT EXISTS idx_acuses_cufe ON acuses(cufe);
CREATE INDEX IF NOT EXISTS idx_acuses_estado ON acuses(estado_documento);

-- ============================================

-- TABLA RECEPCION_FISICA: Control de documentos físicos recibidos
CREATE TABLE IF NOT EXISTS recepcion_fisica (
    cufe TEXT PRIMARY KEY,
    fecha_recepcion TEXT,
    observaciones TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABLA RECEPCION_DIGITAL: Control de documentos digitales recibidos
CREATE TABLE IF NOT EXISTS recepcion_digital (
    cufe TEXT PRIMARY KEY,
    fecha_recepcion TEXT,
    observaciones TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ÍNDICES para recepciones
CREATE INDEX IF NOT EXISTS idx_fisica_cufe ON recepcion_fisica(cufe);
CREATE INDEX IF NOT EXISTS idx_digital_cufe ON recepcion_digital(cufe);

-- ============================================

-- VISTA CONSOLIDADA: Datos completos para la API
-- JOIN de todas las tablas con relaciones correctas
CREATE VIEW IF NOT EXISTS vista_consolidada AS
SELECT 
    d.cufe,
    d.clave,
    d.nit_emisor,
    d.nombre_emisor,
    d.prefijo,
    d.folio,
    d.folio_limpio,
    d.tipo_documento,
    d.fecha_emision,
    d.dias_desde_emision,
    d.valor,
    
    -- Estado contable (calculado en Python, guardado aquí)
    d.estado_contable,
    
    -- Datos de ERP (JOIN por clave)
    COALESCE(e.modulo, d.modulo) as modulo,
    COALESCE(e.doc_causado_por, d.doc_causado_por) as doc_causado_por,
    
    -- Estado de aprobación (JOIN por CUFE)
    a.estado_documento as estado_aprobacion,
    
    -- Indicadores de recepción
    CASE WHEN rf.cufe IS NOT NULL THEN 1 ELSE 0 END as recibido_fisico,
    CASE WHEN rd.cufe IS NOT NULL THEN 1 ELSE 0 END as recibido_digital,
    
    -- Metadatos
    d.fecha_carga,
    d.ultima_actualizacion

FROM dian d
LEFT JOIN erp e ON d.clave = e.clave
LEFT JOIN acuses a ON d.cufe = a.cufe
LEFT JOIN recepcion_fisica rf ON d.cufe = rf.cufe
LEFT JOIN recepcion_digital rd ON d.cufe = rd.cufe;

-- ============================================

-- TRIGGERS: Actualizar timestamp en modificaciones
CREATE TRIGGER IF NOT EXISTS update_dian_timestamp 
AFTER UPDATE ON dian
BEGIN
    UPDATE dian SET ultima_actualizacion = CURRENT_TIMESTAMP WHERE cufe = NEW.cufe;
END;

CREATE TRIGGER IF NOT EXISTS update_erp_timestamp 
AFTER UPDATE ON erp
BEGIN
    UPDATE erp SET ultima_actualizacion = CURRENT_TIMESTAMP WHERE clave = NEW.clave;
END;

CREATE TRIGGER IF NOT EXISTS update_acuses_timestamp 
AFTER UPDATE ON acuses
BEGIN
    UPDATE acuses SET ultima_actualizacion = CURRENT_TIMESTAMP WHERE cufe = NEW.cufe;
END;

-- ============================================
-- TABLAS ADICIONALES PARA GESTIÓN DE USUARIOS
-- ============================================

-- TABLA USUARIOS: Gestión de usuarios por NIT
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nit TEXT NOT NULL,
    razon_social TEXT,
    tipo_usuario TEXT NOT NULL,            -- SOLICITANTE, APROBADOR
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    correo TEXT NOT NULL,
    telefono TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ÍNDICES para usuarios
CREATE INDEX IF NOT EXISTS idx_usuarios_nit ON usuarios(nit);
CREATE INDEX IF NOT EXISTS idx_usuarios_tipo ON usuarios(tipo_usuario);
CREATE INDEX IF NOT EXISTS idx_usuarios_activo ON usuarios(activo);

-- TABLA HISTORIAL_ENVIOS_EMAIL: Tracking de envíos de correo
CREATE TABLE IF NOT EXISTS historial_envios_email (
    id_envio INTEGER PRIMARY KEY AUTOINCREMENT,
    cufe TEXT NOT NULL,
    destinatario_correo TEXT NOT NULL,
    destinatario_nombre TEXT,
    tipo_destinatario TEXT,                 -- SOLICITANTE, APROBADOR
    estado TEXT NOT NULL,                   -- ENVIADO, FALLIDO
    error_mensaje TEXT,
    tipo_envio TEXT DEFAULT 'MANUAL',       -- MANUAL, AUTOMATICO
    usuario_envio TEXT,
    cantidad_facturas INTEGER DEFAULT 1,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_intento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ÍNDICES para historial de emails
CREATE INDEX IF NOT EXISTS idx_email_cufe ON historial_envios_email(cufe);
CREATE INDEX IF NOT EXISTS idx_email_destinatario ON historial_envios_email(destinatario_correo);
CREATE INDEX IF NOT EXISTS idx_email_fecha ON historial_envios_email(fecha_envio);