-- =============================================
-- 📦 SCHEMA: SISTEMA DE RECEPCIÓN DIGITAL DE RELACIONES
-- =============================================
-- Autor: Sistema Gestor Documental
-- Fecha: Octubre 20, 2025
-- Descripción: Tablas para recepción digital de relaciones con firma digital
--             Permite validar facturas sin impresión física
-- =============================================

-- -------------------------------------------------
-- 📊 TABLA: RECEPCIONES_DIGITALES
-- -------------------------------------------------
-- Almacena cada recepción digital de una relación
-- Registra quién, cuándo y desde dónde se recibió
CREATE TABLE IF NOT EXISTS recepciones_digitales (
    id SERIAL PRIMARY KEY,
    numero_relacion VARCHAR(20) NOT NULL,
    
    -- Datos del receptor
    usuario_receptor VARCHAR(100) NOT NULL,
    nombre_receptor VARCHAR(255),
    
    -- Datos de la recepción
    fecha_recepcion TIMESTAMP NOT NULL DEFAULT NOW(),
    ip_recepcion VARCHAR(50),
    user_agent TEXT,
    
    -- Estado de recepción
    facturas_recibidas INTEGER DEFAULT 0,
    facturas_totales INTEGER DEFAULT 0,
    completa BOOLEAN DEFAULT FALSE,
    
    -- Firma digital
    firma_digital VARCHAR(255),
    
    -- Auditoría
    fecha_registro TIMESTAMP DEFAULT NOW(),
    
    -- Índices
    CONSTRAINT idx_recepciones_relacion UNIQUE (numero_relacion, usuario_receptor, fecha_recepcion)
);

-- Índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_recepciones_numero_relacion ON recepciones_digitales(numero_relacion);
CREATE INDEX IF NOT EXISTS idx_recepciones_usuario ON recepciones_digitales(usuario_receptor);
CREATE INDEX IF NOT EXISTS idx_recepciones_fecha ON recepciones_digitales(fecha_recepcion);


-- -------------------------------------------------
-- 📊 TABLA: FACTURAS_RECIBIDAS_DIGITALES
-- -------------------------------------------------
-- Detalle de cada factura recibida digitalmente
-- Registra el check individual de cada factura
CREATE TABLE IF NOT EXISTS facturas_recibidas_digitales (
    id SERIAL PRIMARY KEY,
    
    -- Relación con recepción
    recepcion_id INTEGER NOT NULL REFERENCES recepciones_digitales(id) ON DELETE CASCADE,
    numero_relacion VARCHAR(20) NOT NULL,
    
    -- Datos de la factura
    nit VARCHAR(20) NOT NULL,
    razon_social VARCHAR(255),
    prefijo VARCHAR(10) NOT NULL,
    folio VARCHAR(50) NOT NULL,
    co VARCHAR(10),
    valor_total NUMERIC(15, 2),
    fecha_factura DATE,
    
    -- Datos de recepción
    recibida BOOLEAN DEFAULT FALSE,
    fecha_check TIMESTAMP,
    usuario_check VARCHAR(100),
    observaciones TEXT,
    
    -- Auditoría
    fecha_registro TIMESTAMP DEFAULT NOW(),
    
    -- Índices
    CONSTRAINT idx_facturas_recibidas_unico UNIQUE (recepcion_id, prefijo, folio)
);

-- Índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_facturas_recibidas_recepcion ON facturas_recibidas_digitales(recepcion_id);
CREATE INDEX IF NOT EXISTS idx_facturas_recibidas_numero_relacion ON facturas_recibidas_digitales(numero_relacion);
CREATE INDEX IF NOT EXISTS idx_facturas_recibidas_nit ON facturas_recibidas_digitales(nit);
CREATE INDEX IF NOT EXISTS idx_facturas_recibidas_folio ON facturas_recibidas_digitales(prefijo, folio);


-- -------------------------------------------------
-- 📝 COMENTARIOS DE DOCUMENTACIÓN
-- -------------------------------------------------
COMMENT ON TABLE recepciones_digitales IS 'Registro de recepciones digitales de relaciones de facturas con firma digital';
COMMENT ON COLUMN recepciones_digitales.numero_relacion IS 'Número de relación recibida (ej: REL-001)';
COMMENT ON COLUMN recepciones_digitales.usuario_receptor IS 'Usuario que recibió la relación';
COMMENT ON COLUMN recepciones_digitales.firma_digital IS 'Hash SHA256 para validación de integridad';
COMMENT ON COLUMN recepciones_digitales.completa IS 'TRUE si se recibieron todas las facturas de la relación';

COMMENT ON TABLE facturas_recibidas_digitales IS 'Detalle de facturas recibidas digitalmente con check individual';
COMMENT ON COLUMN facturas_recibidas_digitales.recibida IS 'TRUE si la factura tiene check de recibido';
COMMENT ON COLUMN facturas_recibidas_digitales.fecha_check IS 'Fecha y hora del check de recepción';
COMMENT ON COLUMN facturas_recibidas_digitales.observaciones IS 'Observaciones al recibir (ej: documento dañado, ilegible, etc.)';


-- -------------------------------------------------
-- 📊 DATOS INICIALES (opcional)
-- -------------------------------------------------
-- No se requieren datos iniciales


-- -------------------------------------------------
-- ✅ VERIFICACIÓN
-- -------------------------------------------------
-- Verificar creación de tablas
SELECT table_name, 
       (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columnas
FROM information_schema.tables t
WHERE table_schema = 'public' 
  AND table_name IN ('recepciones_digitales', 'facturas_recibidas_digitales')
ORDER BY table_name;

-- Verificar índices
SELECT tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('recepciones_digitales', 'facturas_recibidas_digitales')
ORDER BY tablename, indexname;
