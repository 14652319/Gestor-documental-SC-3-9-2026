-- ============================================================================
-- ESQUEMA DE TABLAS PARA MÓDULO DIAN VS ERP
-- Sistema de Reconciliación DIAN vs ERP (Comercial y Financiero)
-- Fecha: 30 de Diciembre de 2025
-- ============================================================================

-- ============================================================================
-- TABLA: dian
-- Descripción: Facturas electrónicas reportadas por DIAN
-- ============================================================================
CREATE TABLE IF NOT EXISTS dian (
    id SERIAL PRIMARY KEY,
    
    -- CAMPOS CARGADOS DESDE ARCHIVOS DIAN
    tipo_documento VARCHAR(50),
    cufe_cude VARCHAR(255),
    folio VARCHAR(50),
    prefijo VARCHAR(20),
    divisa VARCHAR(10),
    forma_pago VARCHAR(50),
    medio_pago VARCHAR(50),
    fecha_emision DATE,
    fecha_recepcion DATE,
    nit_emisor VARCHAR(20),
    nombre_emisor VARCHAR(255),
    nit_receptor VARCHAR(20),
    nombre_receptor VARCHAR(255),
    iva NUMERIC(15,2) DEFAULT 0,
    ica NUMERIC(15,2) DEFAULT 0,
    ic NUMERIC(15,2) DEFAULT 0,
    inc NUMERIC(15,2) DEFAULT 0,
    timbre NUMERIC(15,2) DEFAULT 0,
    inc_bolsas NUMERIC(15,2) DEFAULT 0,
    in_carbono NUMERIC(15,2) DEFAULT 0,
    in_combustibles NUMERIC(15,2) DEFAULT 0,
    ic_datos NUMERIC(15,2) DEFAULT 0,
    icl NUMERIC(15,2) DEFAULT 0,
    inpp NUMERIC(15,2) DEFAULT 0,
    ibua NUMERIC(15,2) DEFAULT 0,
    icui NUMERIC(15,2) DEFAULT 0,
    rete_iva NUMERIC(15,2) DEFAULT 0,
    rete_renta NUMERIC(15,2) DEFAULT 0,
    rete_ica NUMERIC(15,2) DEFAULT 0,
    total NUMERIC(15,2) DEFAULT 0,
    estado VARCHAR(50),
    grupo VARCHAR(100),
    
    -- CAMPOS CALCULADOS AUTOMÁTICAMENTE
    clave VARCHAR(100),  -- NIT Emisor + Prefijo + Folio
    clave_acuse VARCHAR(255),  -- CUFE/CUDE (para relación con acuses)
    modulo VARCHAR(50) DEFAULT 'DIAN',
    tipo_tercero VARCHAR(50),
    n_dias INTEGER,  -- Fecha actual - Fecha Emisión (calculado diariamente)
    
    -- AUDITORÍA
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- ÍNDICES ÚNICOS
    CONSTRAINT uk_dian_clave UNIQUE (clave)
);

-- Índices para optimizar búsquedas
CREATE INDEX IF NOT EXISTS idx_dian_nit_emisor ON dian(nit_emisor);
CREATE INDEX IF NOT EXISTS idx_dian_prefijo_folio ON dian(prefijo, folio);
CREATE INDEX IF NOT EXISTS idx_dian_fecha_emision ON dian(fecha_emision);
CREATE INDEX IF NOT EXISTS idx_dian_clave_acuse ON dian(clave_acuse);
CREATE INDEX IF NOT EXISTS idx_dian_estado ON dian(estado);

-- ============================================================================
-- TABLA: erp_comercial
-- Descripción: Facturas del módulo comercial del ERP
-- ============================================================================
CREATE TABLE IF NOT EXISTS erp_comercial (
    id SERIAL PRIMARY KEY,
    
    -- CAMPOS CARGADOS DESDE ARCHIVOS ERP COMERCIAL
    proveedor VARCHAR(20) NOT NULL,
    razon_social_proveedor VARCHAR(255),
    fecha_docto_prov DATE,
    docto_proveedor VARCHAR(100),
    valor_bruto NUMERIC(15,2) DEFAULT 0,
    valor_imptos NUMERIC(15,2) DEFAULT 0,
    co VARCHAR(50),  -- Centro de Operación
    usuario_creacion VARCHAR(100),
    clase_docto VARCHAR(50),
    nro_documento VARCHAR(50),
    
    -- CAMPOS CALCULADOS AUTOMÁTICAMENTE
    prefijo VARCHAR(20),  -- Parte izquierda del guion en Docto. proveedor
    folio VARCHAR(50),  -- Parte derecha del guion en Docto. proveedor (sin ceros)
    clave_erp_comercial VARCHAR(100),  -- Proveedor + Prefijo + Folio
    modulo VARCHAR(50) DEFAULT 'Comercial',
    doc_causado_por VARCHAR(200),  -- C.O. + Usuario creación + Nro documento
    
    -- AUDITORÍA
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- ÍNDICE ÚNICO
    CONSTRAINT uk_erp_comercial_clave UNIQUE (clave_erp_comercial)
);

-- Índices para optimizar búsquedas
CREATE INDEX IF NOT EXISTS idx_erp_comercial_proveedor ON erp_comercial(proveedor);
CREATE INDEX IF NOT EXISTS idx_erp_comercial_prefijo_folio ON erp_comercial(prefijo, folio);
CREATE INDEX IF NOT EXISTS idx_erp_comercial_fecha ON erp_comercial(fecha_docto_prov);
CREATE INDEX IF NOT EXISTS idx_erp_comercial_co ON erp_comercial(co);

-- ============================================================================
-- TABLA: erp_financiero
-- Descripción: Facturas del módulo financiero del ERP
-- ============================================================================
CREATE TABLE IF NOT EXISTS erp_financiero (
    id SERIAL PRIMARY KEY,
    
    -- CAMPOS CARGADOS DESDE ARCHIVOS ERP FINANCIERO
    proveedor VARCHAR(20) NOT NULL,
    razon_social_proveedor VARCHAR(255),
    fecha_proveedor DATE,
    docto_proveedor VARCHAR(100),
    valor_subtotal NUMERIC(15,2) DEFAULT 0,
    valor_impuestos NUMERIC(15,2) DEFAULT 0,
    co VARCHAR(50),  -- Centro de Operación
    usuario_creacion VARCHAR(100),
    clase_docto VARCHAR(50),
    nro_documento VARCHAR(50),
    
    -- CAMPOS CALCULADOS AUTOMÁTICAMENTE
    prefijo VARCHAR(20),  -- Parte izquierda del guion en Docto. proveedor
    folio VARCHAR(50),  -- Parte derecha del guion en Docto. proveedor (sin ceros)
    clave_erp_financiero VARCHAR(100),  -- Proveedor + Prefijo + Folio
    modulo VARCHAR(50) DEFAULT 'Financiero',
    doc_causado_por VARCHAR(200),  -- C.O. + Usuario creación + Nro documento
    
    -- AUDITORÍA
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- ÍNDICE ÚNICO
    CONSTRAINT uk_erp_financiero_clave UNIQUE (clave_erp_financiero)
);

-- Índices para optimizar búsquedas
CREATE INDEX IF NOT EXISTS idx_erp_financiero_proveedor ON erp_financiero(proveedor);
CREATE INDEX IF NOT EXISTS idx_erp_financiero_prefijo_folio ON erp_financiero(prefijo, folio);
CREATE INDEX IF NOT EXISTS idx_erp_financiero_fecha ON erp_financiero(fecha_proveedor);
CREATE INDEX IF NOT EXISTS idx_erp_financiero_co ON erp_financiero(co);

-- ============================================================================
-- TABLA: acuses
-- Descripción: Acuses de recibo de facturas electrónicas
-- ============================================================================
CREATE TABLE IF NOT EXISTS acuses (
    id SERIAL PRIMARY KEY,
    
    -- CAMPOS CARGADOS DESDE ARCHIVOS DE ACUSES
    fecha DATE,
    adquiriente VARCHAR(255),
    factura VARCHAR(100),
    emisor VARCHAR(255),
    nit_emisor VARCHAR(20),
    nit_pt VARCHAR(20),
    estado_docto VARCHAR(100),
    descripcion_reclamo TEXT,
    tipo_documento VARCHAR(50),
    cufe VARCHAR(255),
    valor NUMERIC(15,2) DEFAULT 0,
    acuse_recibido VARCHAR(50),
    recibo_bien_servicio VARCHAR(50),
    aceptacion_expresa VARCHAR(50),
    reclamo VARCHAR(50),
    aceptacion_tacita VARCHAR(50),
    
    -- CAMPO CALCULADO AUTOMÁTICAMENTE
    clave_acuse VARCHAR(255),  -- CUFE (para relación con dian)
    
    -- AUDITORÍA
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimizar búsquedas
CREATE INDEX IF NOT EXISTS idx_acuses_clave ON acuses(clave_acuse);
CREATE INDEX IF NOT EXISTS idx_acuses_nit_emisor ON acuses(nit_emisor);
CREATE INDEX IF NOT EXISTS idx_acuses_fecha ON acuses(fecha);
CREATE INDEX IF NOT EXISTS idx_acuses_factura ON acuses(factura);

-- ============================================================================
-- RELACIONES ENTRE TABLAS
-- ============================================================================

-- Nota: Las relaciones se establecen mediante las claves calculadas:
-- - erp_comercial.clave_erp_comercial relaciona con dian.clave
-- - erp_financiero.clave_erp_financiero relaciona con dian.clave  
-- - acuses.clave_acuse relaciona con dian.clave_acuse
--
-- No se usan FK explícitas porque no todos los registros de ERP 
-- necesariamente tienen correspondencia en DIAN y viceversa.
-- La reconciliación se hace por JOIN en las consultas.

-- ============================================================================
-- FUNCIONES AUXILIARES PARA CÁLCULO DE CAMPOS
-- ============================================================================

-- Función para extraer prefijo de Docto. proveedor
CREATE OR REPLACE FUNCTION extraer_prefijo(docto_proveedor VARCHAR)
RETURNS VARCHAR AS $$
BEGIN
    IF docto_proveedor IS NULL OR docto_proveedor = '' THEN
        RETURN '';
    END IF;
    
    IF POSITION('-' IN docto_proveedor) > 1 THEN
        RETURN SPLIT_PART(docto_proveedor, '-', 1);
    ELSE
        RETURN '';
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Función para extraer folio de Docto. proveedor (sin ceros a la izquierda)
CREATE OR REPLACE FUNCTION extraer_folio(docto_proveedor VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    folio_raw VARCHAR;
BEGIN
    IF docto_proveedor IS NULL OR docto_proveedor = '' THEN
        RETURN '';
    END IF;
    
    IF POSITION('-' IN docto_proveedor) > 0 THEN
        folio_raw := SPLIT_PART(docto_proveedor, '-', 2);
        -- Remover ceros a la izquierda
        RETURN LTRIM(folio_raw, '0');
    ELSE
        RETURN '';
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Función para calcular N_días (fecha actual - fecha emisión)
CREATE OR REPLACE FUNCTION calcular_dias_desde_emision(fecha_emision DATE)
RETURNS INTEGER AS $$
BEGIN
    IF fecha_emision IS NULL THEN
        RETURN NULL;
    END IF;
    
    RETURN (CURRENT_DATE - fecha_emision)::INTEGER;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- TRIGGERS PARA CALCULAR CAMPOS AUTOMÁTICAMENTE
-- ============================================================================

-- Trigger para tabla DIAN
CREATE OR REPLACE FUNCTION trigger_calcular_campos_dian()
RETURNS TRIGGER AS $$
BEGIN
    -- Calcular clave: NIT Emisor + Prefijo + Folio
    NEW.clave := CONCAT(
        COALESCE(NEW.nit_emisor, ''),
        COALESCE(NEW.prefijo, ''),
        COALESCE(NEW.folio, '')
    );
    
    -- Clave_acuse es el CUFE/CUDE
    NEW.clave_acuse := NEW.cufe_cude;
    
    -- Calcular N_días
    NEW.n_dias := calcular_dias_desde_emision(NEW.fecha_emision);
    
    -- Actualizar timestamp
    NEW.fecha_actualizacion := CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_dian_before_insert_update
BEFORE INSERT OR UPDATE ON dian
FOR EACH ROW
EXECUTE FUNCTION trigger_calcular_campos_dian();

-- Trigger para tabla ERP_COMERCIAL
CREATE OR REPLACE FUNCTION trigger_calcular_campos_erp_comercial()
RETURNS TRIGGER AS $$
BEGIN
    -- Extraer prefijo y folio
    NEW.prefijo := extraer_prefijo(NEW.docto_proveedor);
    NEW.folio := extraer_folio(NEW.docto_proveedor);
    
    -- Calcular clave: Proveedor + Prefijo + Folio
    NEW.clave_erp_comercial := CONCAT(
        COALESCE(NEW.proveedor, ''),
        COALESCE(NEW.prefijo, ''),
        COALESCE(NEW.folio, '')
    );
    
    -- Calcular Doc_causado_por: C.O. + Usuario creación + Nro documento
    NEW.doc_causado_por := CONCAT(
        COALESCE(NEW.co, ''), ' | ',
        COALESCE(NEW.usuario_creacion, ''), ' | ',
        COALESCE(NEW.nro_documento, '')
    );
    
    -- Actualizar timestamp
    NEW.fecha_actualizacion := CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_erp_comercial_before_insert_update
BEFORE INSERT OR UPDATE ON erp_comercial
FOR EACH ROW
EXECUTE FUNCTION trigger_calcular_campos_erp_comercial();

-- Trigger para tabla ERP_FINANCIERO
CREATE OR REPLACE FUNCTION trigger_calcular_campos_erp_financiero()
RETURNS TRIGGER AS $$
BEGIN
    -- Extraer prefijo y folio
    NEW.prefijo := extraer_prefijo(NEW.docto_proveedor);
    NEW.folio := extraer_folio(NEW.docto_proveedor);
    
    -- Calcular clave: Proveedor + Prefijo + Folio
    NEW.clave_erp_financiero := CONCAT(
        COALESCE(NEW.proveedor, ''),
        COALESCE(NEW.prefijo, ''),
        COALESCE(NEW.folio, '')
    );
    
    -- Calcular Doc_causado_por: C.O. + Usuario creación + Nro documento
    NEW.doc_causado_por := CONCAT(
        COALESCE(NEW.co, ''), ' | ',
        COALESCE(NEW.usuario_creacion, ''), ' | ',
        COALESCE(NEW.nro_documento, '')
    );
    
    -- Actualizar timestamp
    NEW.fecha_actualizacion := CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_erp_financiero_before_insert_update
BEFORE INSERT OR UPDATE ON erp_financiero
FOR EACH ROW
EXECUTE FUNCTION trigger_calcular_campos_erp_financiero();

-- Trigger para tabla ACUSES
CREATE OR REPLACE FUNCTION trigger_calcular_campos_acuses()
RETURNS TRIGGER AS $$
BEGIN
    -- Clave_acuse es el CUFE
    NEW.clave_acuse := NEW.cufe;
    
    -- Actualizar timestamp
    NEW.fecha_actualizacion := CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_acuses_before_insert_update
BEFORE INSERT OR UPDATE ON acuses
FOR EACH ROW
EXECUTE FUNCTION trigger_calcular_campos_acuses();

-- ============================================================================
-- VISTAS PARA RECONCILIACIÓN
-- ============================================================================

-- Vista: Facturas DIAN vs ERP Comercial
CREATE OR REPLACE VIEW v_reconciliacion_dian_comercial AS
SELECT 
    d.id AS dian_id,
    d.nit_emisor,
    d.nombre_emisor,
    d.prefijo,
    d.folio,
    d.clave AS clave_dian,
    d.fecha_emision,
    d.total AS total_dian,
    d.estado AS estado_dian,
    ec.id AS erp_comercial_id,
    ec.proveedor,
    ec.razon_social_proveedor,
    ec.clave_erp_comercial,
    ec.fecha_docto_prov,
    ec.valor_bruto AS total_erp_comercial,
    ec.co,
    ec.usuario_creacion,
    -- Estado de reconciliación
    CASE 
        WHEN ec.id IS NULL THEN 'Solo en DIAN'
        WHEN d.id IS NULL THEN 'Solo en ERP Comercial'
        WHEN ABS(d.total - ec.valor_bruto) < 0.01 THEN 'Reconciliado'
        ELSE 'Diferencia en Valores'
    END AS estado_reconciliacion,
    ABS(COALESCE(d.total, 0) - COALESCE(ec.valor_bruto, 0)) AS diferencia
FROM dian d
FULL OUTER JOIN erp_comercial ec ON d.clave = ec.clave_erp_comercial;

-- Vista: Facturas DIAN vs ERP Financiero
CREATE OR REPLACE VIEW v_reconciliacion_dian_financiero AS
SELECT 
    d.id AS dian_id,
    d.nit_emisor,
    d.nombre_emisor,
    d.prefijo,
    d.folio,
    d.clave AS clave_dian,
    d.fecha_emision,
    d.total AS total_dian,
    d.estado AS estado_dian,
    ef.id AS erp_financiero_id,
    ef.proveedor,
    ef.razon_social_proveedor,
    ef.clave_erp_financiero,
    ef.fecha_proveedor,
    ef.valor_subtotal AS total_erp_financiero,
    ef.co,
    ef.usuario_creacion,
    -- Estado de reconciliación
    CASE 
        WHEN ef.id IS NULL THEN 'Solo en DIAN'
        WHEN d.id IS NULL THEN 'Solo en ERP Financiero'
        WHEN ABS(d.total - ef.valor_subtotal) < 0.01 THEN 'Reconciliado'
        ELSE 'Diferencia en Valores'
    END AS estado_reconciliacion,
    ABS(COALESCE(d.total, 0) - COALESCE(ef.valor_subtotal, 0)) AS diferencia
FROM dian d
FULL OUTER JOIN erp_financiero ef ON d.clave = ef.clave_erp_financiero;

-- Vista: Facturas DIAN con Acuses
CREATE OR REPLACE VIEW v_dian_con_acuses AS
SELECT 
    d.id AS dian_id,
    d.nit_emisor,
    d.nombre_emisor,
    d.prefijo,
    d.folio,
    d.clave AS clave_dian,
    d.cufe_cude,
    d.fecha_emision,
    d.total,
    d.estado AS estado_dian,
    a.id AS acuse_id,
    a.fecha AS fecha_acuse,
    a.estado_docto AS estado_acuse,
    a.acuse_recibido,
    a.recibo_bien_servicio,
    a.aceptacion_expresa,
    a.reclamo,
    a.aceptacion_tacita,
    -- Estado de acuse
    CASE 
        WHEN a.id IS NULL THEN 'Sin Acuse'
        WHEN a.aceptacion_expresa = 'Sí' THEN 'Aceptado Expresamente'
        WHEN a.reclamo = 'Sí' THEN 'Reclamado'
        WHEN a.acuse_recibido = 'Sí' THEN 'Acuse Recibido'
        ELSE 'Pendiente'
    END AS estado_acuse_completo
FROM dian d
LEFT JOIN acuses a ON d.clave_acuse = a.clave_acuse;

-- ============================================================================
-- COMENTARIOS FINALES
-- ============================================================================

COMMENT ON TABLE dian IS 'Facturas electrónicas reportadas por la DIAN';
COMMENT ON TABLE erp_comercial IS 'Facturas del módulo comercial del ERP interno';
COMMENT ON TABLE erp_financiero IS 'Facturas del módulo financiero del ERP interno';
COMMENT ON TABLE acuses IS 'Acuses de recibo de facturas electrónicas';

COMMENT ON COLUMN dian.clave IS 'Clave única: NIT Emisor + Prefijo + Folio';
COMMENT ON COLUMN dian.clave_acuse IS 'CUFE/CUDE para relacionar con tabla acuses';
COMMENT ON COLUMN dian.n_dias IS 'Días desde la emisión hasta hoy (calculado diariamente)';

COMMENT ON COLUMN erp_comercial.clave_erp_comercial IS 'Clave única: Proveedor + Prefijo + Folio';
COMMENT ON COLUMN erp_comercial.doc_causado_por IS 'Identificador de documento causante: C.O. + Usuario + Nro Doc';

COMMENT ON COLUMN erp_financiero.clave_erp_financiero IS 'Clave única: Proveedor + Prefijo + Folio';
COMMENT ON COLUMN erp_financiero.doc_causado_por IS 'Identificador de documento causante: C.O. + Usuario + Nro Doc';

COMMENT ON COLUMN acuses.clave_acuse IS 'CUFE para relacionar con tabla dian';

-- ============================================================================
-- FIN DEL ESQUEMA
-- ============================================================================
