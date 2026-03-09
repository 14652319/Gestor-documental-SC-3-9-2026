-- =============================================
-- 📊 SCHEMA: Módulo Relaciones de Facturas
-- Fecha: Octubre 19, 2025
-- Descripción: Tablas para gestionar relaciones de facturas para contabilidad/pagos
-- =============================================

-- -------------------------------------------------
-- 📋 TABLA: relaciones_facturas
-- -------------------------------------------------
-- Almacena todas las facturas que han sido incluidas en relaciones generadas
CREATE TABLE IF NOT EXISTS relaciones_facturas (
    id SERIAL PRIMARY KEY,
    numero_relacion VARCHAR(20) NOT NULL,                  -- Ej: REL-001, REL-002
    nit VARCHAR(20) NOT NULL,                              -- NIT del tercero
    prefijo VARCHAR(10),                                    -- Prefijo de la factura
    folio VARCHAR(20) NOT NULL,                            -- Folio de la factura
    co VARCHAR(10),                                         -- Centro de operación (tienda/bodega)
    fecha_radicacion DATE,                                  -- Fecha de radicación de la factura
    valor NUMERIC(15, 2),                                   -- Valor total de la factura
    destino VARCHAR(50),                                    -- CONTABILIDAD, PAGOS, SUMINISTROS, OTRO
    formato VARCHAR(10),                                    -- Excel, PDF
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Fecha de creación de la relación
    usuario_creador VARCHAR(100),                          -- Usuario que creó la relación
    
    -- Índices para mejorar performance
    INDEX idx_numero_relacion (numero_relacion),
    INDEX idx_nit (nit),
    INDEX idx_fecha_generacion (fecha_generacion),
    INDEX idx_clave_factura (nit, prefijo, folio),         -- Búsqueda rápida de factura específica
    
    -- Unicidad: Una factura solo puede estar en UNA relación
    UNIQUE(nit, prefijo, folio)
);

-- -------------------------------------------------
-- 📋 TABLA: consecutivos
-- -------------------------------------------------
-- Maneja la generación de números consecutivos para diferentes tipos de documentos
CREATE TABLE IF NOT EXISTS consecutivos (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,                             -- Tipo de documento: 'RELACION', 'FACTURA', etc.
    prefijo VARCHAR(10),                                    -- Prefijo opcional: 'REL', 'FAC', etc.
    ultimo_numero INT NOT NULL DEFAULT 0,                  -- Último número generado
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Última actualización
    
    -- Unicidad: Un consecutivo por cada combinación tipo + prefijo
    UNIQUE(tipo, prefijo)
);

-- -------------------------------------------------
-- 🔧 DATOS INICIALES
-- -------------------------------------------------
-- Inicializar el consecutivo de relaciones si no existe
INSERT INTO consecutivos (tipo, prefijo, ultimo_numero)
VALUES ('RELACION', 'REL', 0)
ON CONFLICT (tipo, prefijo) DO NOTHING;

-- -------------------------------------------------
-- 📝 COMENTARIOS SOBRE LAS TABLAS
-- -------------------------------------------------
COMMENT ON TABLE relaciones_facturas IS 'Registra todas las facturas incluidas en relaciones generadas para contabilidad/pagos';
COMMENT ON TABLE consecutivos IS 'Maneja números consecutivos para diferentes tipos de documentos del sistema';

COMMENT ON COLUMN relaciones_facturas.numero_relacion IS 'Número único de la relación generada (REL-001, REL-002, etc.)';
COMMENT ON COLUMN relaciones_facturas.destino IS 'Área destino de la relación: CONTABILIDAD, PAGOS, SUMINISTROS, OTRO';
COMMENT ON COLUMN relaciones_facturas.formato IS 'Formato de exportación solicitado: Excel o PDF';
COMMENT ON COLUMN relaciones_facturas.usuario_creador IS 'Usuario que generó la relación';

COMMENT ON COLUMN consecutivos.tipo IS 'Tipo de documento: RELACION, FACTURA, NOTA, etc.';
COMMENT ON COLUMN consecutivos.prefijo IS 'Prefijo del consecutivo (REL, FAC, NOT, etc.)';
COMMENT ON COLUMN consecutivos.ultimo_numero IS 'Último número consecutivo generado (incrementa automáticamente)';

-- -------------------------------------------------
-- 📊 CONSULTAS ÚTILES
-- -------------------------------------------------

-- Ver todas las relaciones generadas:
-- SELECT numero_relacion, COUNT(*) as facturas, SUM(valor) as total_valor, fecha_generacion 
-- FROM relaciones_facturas 
-- GROUP BY numero_relacion, fecha_generacion 
-- ORDER BY fecha_generacion DESC;

-- Ver facturas de una relación específica:
-- SELECT nit, prefijo, folio, valor, fecha_radicacion 
-- FROM relaciones_facturas 
-- WHERE numero_relacion = 'REL-001';

-- Verificar si una factura ya está relacionada:
-- SELECT numero_relacion, fecha_generacion 
-- FROM relaciones_facturas 
-- WHERE nit = '123456789' AND prefijo = 'FV' AND folio = '001';

-- Ver consecutivos actuales:
-- SELECT * FROM consecutivos;

-- Resetear consecutivo de relaciones (USAR CON PRECAUCIÓN):
-- UPDATE consecutivos SET ultimo_numero = 0 WHERE tipo = 'RELACION' AND prefijo = 'REL';
