-- =====================================================
-- SISTEMA RECIBIR FACTURAS - SOLO CREACIÓN DE TABLAS
-- Fecha: 18 de Octubre 2025
-- Versión simplificada sin modificar tabla terceros
-- =====================================================

-- =====================================================
-- PASO 1: CREAR TABLA centros_operacion
-- =====================================================

DROP TABLE IF EXISTS centros_operacion CASCADE;

CREATE TABLE centros_operacion (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    ciudad VARCHAR(50),
    direccion VARCHAR(255),
    estado VARCHAR(20) DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'INACTIVO')),
    tipo_propiedad VARCHAR(20) DEFAULT 'PROPIO' CHECK (tipo_propiedad IN ('PROPIO', 'ARRENDADO', 'MIXTO')),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar centros de operación iniciales
INSERT INTO centros_operacion (codigo, nombre, ciudad) VALUES
('01', 'CAÑAVERAL', 'FLORENCIA'),
('02', 'MONTERIA', 'MONTERIA'),
('03', 'VALLEDUPAR', 'VALLEDUPAR'),
('04', 'NEIVA', 'NEIVA'),
('05', 'PASTO', 'PASTO');

COMMENT ON TABLE centros_operacion IS 'Centros de operación (tiendas)';

-- =====================================================
-- PASO 2: CREAR TABLA facturas_temporales
-- =====================================================

DROP TABLE IF EXISTS observaciones_factura_temporal CASCADE;
DROP TABLE IF EXISTS facturas_temporales CASCADE;

CREATE TABLE facturas_temporales (
    id SERIAL PRIMARY KEY,
    
    -- Clave única de factura
    nit VARCHAR(20) NOT NULL,
    prefijo VARCHAR(10) NOT NULL,
    folio VARCHAR(50) NOT NULL,
    
    -- Información del proveedor
    razon_social VARCHAR(200) NOT NULL,
    
    -- Información de fechas
    fecha_expedicion DATE,
    fecha_radicacion DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_vencimiento DATE,
    
    -- Valores monetarios
    valor_bruto DECIMAL(15,2) NOT NULL,
    descuento DECIMAL(15,2) DEFAULT 0,
    iva DECIMAL(15,2) DEFAULT 0,
    retencion_fuente DECIMAL(15,2) DEFAULT 0,
    rete_iva DECIMAL(15,2) DEFAULT 0,
    rete_ica DECIMAL(15,2) DEFAULT 0,
    valor_neto DECIMAL(15,2) NOT NULL,
    
    -- Centro de operación
    centro_operacion_id INTEGER REFERENCES centros_operacion(id),
    centro_operacion VARCHAR(200),
    
    -- Información adicional
    forma_pago VARCHAR(50) DEFAULT 'CREDITO', -- EFECTIVO, CREDITO
    plazo INTEGER DEFAULT 30, -- Días de plazo
    comprador VARCHAR(200),
    usuario_solicita VARCHAR(200),
    quien_recibe VARCHAR(200),
    
    -- Observaciones (última observación visible)
    observaciones TEXT,
    
    -- Auditoría
    usuario_nombre VARCHAR(200) NOT NULL,
    usuario_id INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP,
    
    -- Constraint de clave única (NIT + Prefijo + Folio)
    CONSTRAINT uk_factura_temporal UNIQUE (nit, prefijo, folio)
);

-- Índices para mejorar búsquedas
CREATE INDEX idx_temp_nit ON facturas_temporales(nit);
CREATE INDEX idx_temp_usuario ON facturas_temporales(usuario_id);
CREATE INDEX idx_temp_fecha_creacion ON facturas_temporales(fecha_creacion);

COMMENT ON TABLE facturas_temporales IS 'Facturas en proceso de captura antes de ser confirmadas';
COMMENT ON COLUMN facturas_temporales.folio IS 'Últimos 8 dígitos del número de factura sin ceros a la izquierda';
COMMENT ON COLUMN facturas_temporales.valor_neto IS 'Valor final: bruto - descuento + iva - retenciones';

-- =====================================================
-- PASO 3: CREAR TABLA facturas_recibidas
-- =====================================================

DROP TABLE IF EXISTS observaciones_factura CASCADE;
DROP TABLE IF EXISTS facturas_recibidas CASCADE;

CREATE TABLE facturas_recibidas (
    id SERIAL PRIMARY KEY,
    
    -- Clave única de factura
    nit VARCHAR(20) NOT NULL,
    prefijo VARCHAR(10) NOT NULL,
    folio VARCHAR(50) NOT NULL,
    numero_factura VARCHAR(100) GENERATED ALWAYS AS (prefijo || folio) STORED,
    
    -- Información del proveedor
    razon_social VARCHAR(200) NOT NULL,
    
    -- Información de fechas
    fecha_expedicion DATE,
    fecha_radicacion DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_vencimiento DATE,
    
    -- Valores monetarios
    valor_bruto DECIMAL(15,2) NOT NULL,
    descuento DECIMAL(15,2) DEFAULT 0,
    iva DECIMAL(15,2) DEFAULT 0,
    retencion_fuente DECIMAL(15,2) DEFAULT 0,
    rete_iva DECIMAL(15,2) DEFAULT 0,
    rete_ica DECIMAL(15,2) DEFAULT 0,
    valor_neto DECIMAL(15,2) NOT NULL,
    
    -- Centro de operación
    centro_operacion_id INTEGER REFERENCES centros_operacion(id),
    centro_operacion VARCHAR(200),
    
    -- Información adicional
    forma_pago VARCHAR(50) DEFAULT 'CREDITO',
    plazo INTEGER DEFAULT 30,
    comprador VARCHAR(200),
    usuario_solicita VARCHAR(200),
    quien_recibe VARCHAR(200),
    
    -- Estado de la factura
    estado VARCHAR(30) DEFAULT 'RECIBIDA', -- RECIBIDA, VALIDADA, RECHAZADA, PAGADA
    
    -- Observaciones (última observación visible)
    observaciones TEXT,
    
    -- Auditoría
    usuario_nombre VARCHAR(200) NOT NULL,
    usuario_id INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP,
    fecha_guardado TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Cuándo se guardó desde temporal
    
    -- Constraint de clave única (NIT + Prefijo + Folio)
    CONSTRAINT uk_factura_recibida UNIQUE (nit, prefijo, folio)
);

-- Índices para mejorar búsquedas y reportes
CREATE INDEX idx_recib_nit ON facturas_recibidas(nit);
CREATE INDEX idx_recib_estado ON facturas_recibidas(estado);
CREATE INDEX idx_recib_fecha_radicacion ON facturas_recibidas(fecha_radicacion);
CREATE INDEX idx_recib_fecha_vencimiento ON facturas_recibidas(fecha_vencimiento);
CREATE INDEX idx_recib_co ON facturas_recibidas(centro_operacion_id);
CREATE INDEX idx_recib_usuario ON facturas_recibidas(usuario_id);

COMMENT ON TABLE facturas_recibidas IS 'Facturas confirmadas y guardadas definitivamente';
COMMENT ON COLUMN facturas_recibidas.numero_factura IS 'Número completo de factura (generado automáticamente)';
COMMENT ON COLUMN facturas_recibidas.fecha_guardado IS 'Fecha y hora en que se guardó desde temporales';

-- =====================================================
-- PASO 4: CREAR TABLA observaciones_factura
-- =====================================================

CREATE TABLE observaciones_factura (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL REFERENCES facturas_recibidas(id) ON DELETE CASCADE,
    
    observacion TEXT NOT NULL,
    
    -- Auditoría
    usuario_nombre VARCHAR(200) NOT NULL,
    usuario_id INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ordenar por más reciente primero
    CONSTRAINT observaciones_order CHECK (fecha_creacion IS NOT NULL)
);

CREATE INDEX idx_obs_factura ON observaciones_factura(factura_id);
CREATE INDEX idx_obs_fecha ON observaciones_factura(fecha_creacion DESC);

COMMENT ON TABLE observaciones_factura IS 'Historial completo de observaciones por factura';

-- =====================================================
-- PASO 5: CREAR TABLA retenciones
-- =====================================================

DROP TABLE IF EXISTS retenciones CASCADE;

CREATE TABLE retenciones (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    porcentaje DECIMAL(5,2) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO retenciones (codigo, nombre, porcentaje) VALUES
('RF01', 'RETEFUENTE SERVICIOS', 4.00),
('RF02', 'RETEFUENTE COMPRAS', 2.50),
('RI01', 'RETEIVA', 15.00),
('RICA', 'RETEICA', 1.00);

COMMENT ON TABLE retenciones IS 'Catálogo de retenciones aplicables';

-- =====================================================
-- FIN DEL SCHEMA
-- =====================================================

-- Verificar tablas creadas
SELECT 'Tablas creadas exitosamente:' AS mensaje;
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('facturas_recibidas', 'facturas_temporales', 'centros_operacion', 'retenciones', 'observaciones_factura')
ORDER BY table_name;
