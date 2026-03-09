-- ============================================================================
-- SCRIPT SQL: MÓDULO DE RECEPCIÓN DE FACTURAS DIGITALES
-- ============================================================================
-- Descripción: Crea todas las tablas necesarias para el módulo de recepción
--              de facturas digitales con control de acceso y auditoría
-- ============================================================================

-- Tabla de configuración de rutas de almacenamiento
CREATE TABLE IF NOT EXISTS config_rutas_facturas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    ruta_local TEXT NOT NULL,
    ruta_red TEXT,
    activa BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(100),
    observaciones TEXT
);

-- Tabla principal de facturas digitales recibidas
CREATE TABLE IF NOT EXISTS facturas_digitales (
    id SERIAL PRIMARY KEY,
    numero_factura VARCHAR(50) NOT NULL,
    nit_proveedor VARCHAR(20) NOT NULL,
    razon_social_proveedor VARCHAR(255) NOT NULL,
    fecha_emision DATE NOT NULL,
    fecha_vencimiento DATE,
    valor_total DECIMAL(15,2) NOT NULL,
    valor_iva DECIMAL(15,2) DEFAULT 0,
    valor_base DECIMAL(15,2) NOT NULL,
    
    -- Información del archivo
    nombre_archivo_original VARCHAR(255) NOT NULL,
    nombre_archivo_sistema VARCHAR(255) NOT NULL,
    ruta_archivo TEXT NOT NULL,
    tipo_archivo VARCHAR(10) NOT NULL, -- pdf, xml, zip
    tamanio_kb DECIMAL(10,2),
    
    -- Estado y control
    estado VARCHAR(20) DEFAULT 'pendiente', -- pendiente, aprobado, rechazado, en_revision
    motivo_rechazo TEXT,
    observaciones TEXT,
    
    -- Usuario que carga (puede ser externo o interno)
    usuario_carga VARCHAR(100) NOT NULL,
    tipo_usuario VARCHAR(20) NOT NULL, -- externo, interno
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_carga VARCHAR(45),
    
    -- Usuario que revisa (solo interno)
    usuario_revision VARCHAR(100),
    fecha_revision TIMESTAMP,
    
    -- Metadatos
    hash_archivo VARCHAR(64), -- SHA256 para evitar duplicados
    activo BOOLEAN DEFAULT TRUE,
    
    CONSTRAINT uk_factura_proveedor UNIQUE (numero_factura, nit_proveedor)
);

-- Tabla de histórico de cambios de estado
CREATE TABLE IF NOT EXISTS facturas_digitales_historial (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL REFERENCES facturas_digitales(id) ON DELETE CASCADE,
    estado_anterior VARCHAR(20),
    estado_nuevo VARCHAR(20) NOT NULL,
    usuario VARCHAR(100) NOT NULL,
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    motivo TEXT,
    observaciones TEXT
);

-- Tabla de archivos adjuntos adicionales (por si una factura tiene múltiples archivos)
CREATE TABLE IF NOT EXISTS facturas_digitales_adjuntos (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL REFERENCES facturas_digitales(id) ON DELETE CASCADE,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo TEXT NOT NULL,
    tipo_archivo VARCHAR(10) NOT NULL,
    tamanio_kb DECIMAL(10,2),
    descripcion VARCHAR(255),
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_carga VARCHAR(100) NOT NULL
);

-- Tabla de notificaciones (para alertar a usuarios sobre cambios)
CREATE TABLE IF NOT EXISTS facturas_digitales_notificaciones (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL REFERENCES facturas_digitales(id) ON DELETE CASCADE,
    usuario_destino VARCHAR(100) NOT NULL,
    tipo_notificacion VARCHAR(50) NOT NULL, -- nueva_factura, aprobada, rechazada, revision_pendiente
    mensaje TEXT NOT NULL,
    leida BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_lectura TIMESTAMP
);

-- Tabla de estadísticas y métricas
CREATE TABLE IF NOT EXISTS facturas_digitales_metricas (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    total_facturas_cargadas INTEGER DEFAULT 0,
    total_facturas_aprobadas INTEGER DEFAULT 0,
    total_facturas_rechazadas INTEGER DEFAULT 0,
    total_facturas_pendientes INTEGER DEFAULT 0,
    valor_total_facturas DECIMAL(15,2) DEFAULT 0,
    tiempo_promedio_revision_minutos INTEGER DEFAULT 0,
    CONSTRAINT uk_metricas_fecha UNIQUE (fecha)
);

-- Índices para optimizar búsquedas
CREATE INDEX IF NOT EXISTS idx_facturas_digitales_nit ON facturas_digitales(nit_proveedor);
CREATE INDEX IF NOT EXISTS idx_facturas_digitales_estado ON facturas_digitales(estado);
CREATE INDEX IF NOT EXISTS idx_facturas_digitales_fecha_carga ON facturas_digitales(fecha_carga DESC);
CREATE INDEX IF NOT EXISTS idx_facturas_digitales_usuario ON facturas_digitales(usuario_carga);
CREATE INDEX IF NOT EXISTS idx_facturas_digitales_hash ON facturas_digitales(hash_archivo);
CREATE INDEX IF NOT EXISTS idx_historial_factura ON facturas_digitales_historial(factura_id, fecha_cambio DESC);
CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario ON facturas_digitales_notificaciones(usuario_destino, leida, fecha_creacion DESC);

-- Insertar configuración de ruta por defecto
INSERT INTO config_rutas_facturas (nombre, ruta_local, ruta_red, activa, usuario_creacion, observaciones)
VALUES (
    'Ruta Principal Facturas',
    'D:/facturas_digitales',
    NULL,
    TRUE,
    'sistema',
    'Ruta por defecto para almacenamiento de facturas digitales. Puede ser modificada desde la configuración.'
) ON CONFLICT (nombre) DO NOTHING;

-- Comentarios en las tablas
COMMENT ON TABLE facturas_digitales IS 'Registro de facturas digitales recibidas de proveedores';
COMMENT ON TABLE facturas_digitales_historial IS 'Histórico de cambios de estado de las facturas';
COMMENT ON TABLE config_rutas_facturas IS 'Configuración de rutas de almacenamiento';
COMMENT ON TABLE facturas_digitales_notificaciones IS 'Sistema de notificaciones para usuarios';
COMMENT ON TABLE facturas_digitales_metricas IS 'Métricas y estadísticas del módulo';

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================
