-- =====================================================
-- TABLA: clase_docto_erp
-- Creada: 30 de diciembre de 2025
-- Propósito: Clasificación de tipos de tercero según
--            la "Clase docto." en archivos ERP
-- =====================================================

CREATE TABLE IF NOT EXISTS clase_docto_erp (
    id SERIAL PRIMARY KEY,
    clase_docto VARCHAR(255) NOT NULL UNIQUE,
    tipo_tercero VARCHAR(50) NOT NULL,  -- 'PROVEEDOR' o 'ACREEDOR'
    modulo_origen VARCHAR(50) NOT NULL,  -- 'COMERCIAL' o 'FINANCIERO'
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_tipo_tercero CHECK (tipo_tercero IN ('PROVEEDOR', 'ACREEDOR')),
    CONSTRAINT chk_modulo_origen CHECK (modulo_origen IN ('COMERCIAL', 'FINANCIERO'))
);

-- Índices para búsqueda rápida
CREATE INDEX IF NOT EXISTS idx_clase_docto ON clase_docto_erp(clase_docto);
CREATE INDEX IF NOT EXISTS idx_tipo_tercero ON clase_docto_erp(tipo_tercero);
CREATE INDEX IF NOT EXISTS idx_modulo_origen ON clase_docto_erp(modulo_origen);

-- Comentarios
COMMENT ON TABLE clase_docto_erp IS 'Catálogo de clases de documento ERP para clasificación de terceros';
COMMENT ON COLUMN clase_docto_erp.clase_docto IS 'Descripción de la clase de documento (ej: "Factura de proveedor")';
COMMENT ON COLUMN clase_docto_erp.tipo_tercero IS 'Clasificación del tercero: PROVEEDOR o ACREEDOR';
COMMENT ON COLUMN clase_docto_erp.modulo_origen IS 'Módulo ERP donde se usa: COMERCIAL o FINANCIERO';
