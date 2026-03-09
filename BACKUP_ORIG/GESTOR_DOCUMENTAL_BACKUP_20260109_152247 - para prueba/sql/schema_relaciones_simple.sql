-- =============================================
-- SCHEMA: Modulo Relaciones de Facturas
-- Fecha: Octubre 19, 2025
-- Descripcion: Tablas para gestionar relaciones de facturas para contabilidad/pagos
-- =============================================

-- -------------------------------------------------
-- TABLA: relaciones_facturas
-- -------------------------------------------------
-- Almacena todas las facturas que han sido incluidas en relaciones generadas
CREATE TABLE IF NOT EXISTS relaciones_facturas (
    id SERIAL PRIMARY KEY,
    numero_relacion VARCHAR(20) NOT NULL,
    nit VARCHAR(20) NOT NULL,
    prefijo VARCHAR(10),
    folio VARCHAR(20) NOT NULL,
    co VARCHAR(10),
    fecha_radicacion DATE,
    valor NUMERIC(15, 2),
    destino VARCHAR(50),
    formato VARCHAR(10),
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creador VARCHAR(100)
);

-- Indices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_numero_relacion ON relaciones_facturas(numero_relacion);
CREATE INDEX IF NOT EXISTS idx_nit ON relaciones_facturas(nit);
CREATE INDEX IF NOT EXISTS idx_fecha_generacion ON relaciones_facturas(fecha_generacion);
CREATE INDEX IF NOT EXISTS idx_clave_factura ON relaciones_facturas(nit, prefijo, folio);

-- Unicidad: Una factura solo puede estar en UNA relacion
CREATE UNIQUE INDEX IF NOT EXISTS idx_factura_unica ON relaciones_facturas(nit, prefijo, folio);

-- -------------------------------------------------
-- TABLA: consecutivos
-- -------------------------------------------------
-- Maneja la generacion de numeros consecutivos para diferentes tipos de documentos
CREATE TABLE IF NOT EXISTS consecutivos (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    prefijo VARCHAR(10),
    ultimo_numero INT NOT NULL DEFAULT 0,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Unicidad: Un consecutivo por cada combinacion tipo + prefijo
CREATE UNIQUE INDEX IF NOT EXISTS idx_consecutivo_unico ON consecutivos(tipo, prefijo);

-- -------------------------------------------------
-- DATOS INICIALES
-- -------------------------------------------------
-- Inicializar el consecutivo de relaciones si no existe
INSERT INTO consecutivos (tipo, prefijo, ultimo_numero)
VALUES ('RELACION', 'REL', 0)
ON CONFLICT DO NOTHING;
