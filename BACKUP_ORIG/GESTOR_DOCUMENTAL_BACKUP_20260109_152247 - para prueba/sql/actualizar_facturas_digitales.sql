-- Actualización de tabla facturas_digitales con nuevos campos requeridos
-- Fecha: 25 Noviembre 2025

-- Agregar nuevos campos a facturas_digitales
ALTER TABLE facturas_digitales
ADD COLUMN IF NOT EXISTS fecha_radicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS empresa VARCHAR(10) NOT NULL DEFAULT 'SC', -- SC o LG
ADD COLUMN IF NOT EXISTS prefijo VARCHAR(20) NOT NULL DEFAULT '',
ADD COLUMN IF NOT EXISTS folio VARCHAR(50) NOT NULL DEFAULT '',
ADD COLUMN IF NOT EXISTS tipo_documento VARCHAR(20) NOT NULL DEFAULT 'factura', -- factura o nota_credito
ADD COLUMN IF NOT EXISTS tipo_servicio VARCHAR(20) NOT NULL DEFAULT 'servicio', -- servicio, compra, ambos
ADD COLUMN IF NOT EXISTS archivo_zip_path TEXT,
ADD COLUMN IF NOT EXISTS archivo_seguridad_social_path TEXT,
ADD COLUMN IF NOT EXISTS archivos_soportes_paths TEXT[],
ADD COLUMN IF NOT EXISTS historial_observaciones JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS fecha_ultima_modificacion TIMESTAMP,
ADD COLUMN IF NOT EXISTS usuario_ultima_modificacion VARCHAR(100);

-- Crear índices únicos compuestos para evitar duplicados (NIT + PREFIJO + FOLIO)
CREATE UNIQUE INDEX IF NOT EXISTS idx_factura_digital_unica 
ON facturas_digitales (nit_proveedor, prefijo, folio);

-- Índices para búsqueda rápida
CREATE INDEX IF NOT EXISTS idx_facturas_digitales_empresa ON facturas_digitales(empresa);
CREATE INDEX IF NOT EXISTS idx_facturas_digitales_fecha_radicacion ON facturas_digitales(fecha_radicacion);
CREATE INDEX IF NOT EXISTS idx_facturas_digitales_tipo_documento ON facturas_digitales(tipo_documento);
CREATE INDEX IF NOT EXISTS idx_facturas_digitales_nit ON facturas_digitales(nit_proveedor);

-- Comentarios en las columnas
COMMENT ON COLUMN facturas_digitales.fecha_radicacion IS 'Fecha y hora automática de radicación, no modificable';
COMMENT ON COLUMN facturas_digitales.empresa IS 'Código de empresa: SC=Supertiendas, LG=La Galeria';
COMMENT ON COLUMN facturas_digitales.prefijo IS 'Prefijo de la factura (obligatorio)';
COMMENT ON COLUMN facturas_digitales.folio IS 'Número de folio de la factura (obligatorio)';
COMMENT ON COLUMN facturas_digitales.tipo_documento IS 'Tipo: factura o nota_credito';
COMMENT ON COLUMN facturas_digitales.tipo_servicio IS 'Clasificación: servicio, compra o ambos';
COMMENT ON COLUMN facturas_digitales.archivo_zip_path IS 'Ruta del archivo ZIP (XML y PSD) opcional';
COMMENT ON COLUMN facturas_digitales.archivo_seguridad_social_path IS 'Ruta del archivo de seguridad social opcional';
COMMENT ON COLUMN facturas_digitales.archivos_soportes_paths IS 'Array de rutas de archivos de soporte (fotos, excel, pdf)';
COMMENT ON COLUMN facturas_digitales.historial_observaciones IS 'JSON con histórico de observaciones [{fecha, hora, usuario, texto}]';

-- Actualizar registros existentes con valores por defecto
UPDATE facturas_digitales 
SET empresa = 'SC' 
WHERE empresa IS NULL;

UPDATE facturas_digitales 
SET prefijo = COALESCE(SPLIT_PART(numero_factura, '-', 1), '')
WHERE prefijo = '';

UPDATE facturas_digitales 
SET folio = COALESCE(SPLIT_PART(numero_factura, '-', 2), numero_factura)
WHERE folio = '';

UPDATE facturas_digitales 
SET tipo_documento = 'factura'
WHERE tipo_documento IS NULL;

UPDATE facturas_digitales 
SET tipo_servicio = 'servicio'
WHERE tipo_servicio IS NULL;

-- Crear función para validar factura duplicada
CREATE OR REPLACE FUNCTION validar_factura_duplicada(
    p_nit VARCHAR(20),
    p_prefijo VARCHAR(20),
    p_folio VARCHAR(50)
) RETURNS TABLE(
    existe BOOLEAN,
    id_factura INTEGER,
    fecha_carga TIMESTAMP,
    tabla_origen VARCHAR(50)
) AS $$
BEGIN
    -- Buscar en facturas_digitales
    RETURN QUERY
    SELECT 
        TRUE as existe,
        fd.id as id_factura,
        fd.fecha_radicacion as fecha_carga,
        'facturas_digitales'::VARCHAR(50) as tabla_origen
    FROM facturas_digitales fd
    WHERE fd.nit_proveedor = p_nit
      AND fd.prefijo = p_prefijo
      AND fd.folio = p_folio
    LIMIT 1;
    
    -- Si no existe en facturas_digitales, buscar en recibir_facturas (si la tabla existe)
    IF NOT FOUND THEN
        RETURN QUERY
        SELECT 
            TRUE as existe,
            rf.id_radicado as id_factura,
            rf.fecha_radicacion as fecha_carga,
            'recibir_facturas'::VARCHAR(50) as tabla_origen
        FROM recibir_facturas rf
        WHERE rf.nit_proveedor = p_nit
          AND rf.prefijo_factura = p_prefijo
          AND rf.numero_factura = p_folio
        LIMIT 1;
    END IF;
    
    -- Si no existe en ninguna tabla
    IF NOT FOUND THEN
        RETURN QUERY
        SELECT 
            FALSE as existe,
            NULL::INTEGER as id_factura,
            NULL::TIMESTAMP as fecha_carga,
            NULL::VARCHAR(50) as tabla_origen;
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION validar_factura_duplicada IS 'Valida si una factura ya existe en facturas_digitales o recibir_facturas';

-- Trigger para actualizar fecha_ultima_modificacion
CREATE OR REPLACE FUNCTION actualizar_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_ultima_modificacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_actualizar_fecha_modificacion ON facturas_digitales;

CREATE TRIGGER trigger_actualizar_fecha_modificacion
    BEFORE UPDATE ON facturas_digitales
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

COMMENT ON TRIGGER trigger_actualizar_fecha_modificacion ON facturas_digitales IS 'Actualiza automáticamente la fecha de última modificación';

-- Crear vista consolidada de facturas (ambas tablas)
CREATE OR REPLACE VIEW v_facturas_consolidadas AS
SELECT 
    'digital' as origen,
    id,
    nit_proveedor,
    prefijo,
    folio,
    fecha_radicacion,
    razon_social_proveedor,
    valor_total,
    tipo_documento,
    estado
FROM facturas_digitales
UNION ALL
SELECT 
    'tradicional' as origen,
    id_radicado as id,
    nit_proveedor,
    prefijo_factura as prefijo,
    numero_factura as folio,
    fecha_radicacion,
    razon_social as razon_social_proveedor,
    valor_total,
    'factura' as tipo_documento,
    estado
FROM recibir_facturas
WHERE EXISTS (SELECT 1 FROM recibir_facturas LIMIT 1);

COMMENT ON VIEW v_facturas_consolidadas IS 'Vista consolidada de facturas digitales y tradicionales';

COMMIT;

-- Verificación final
SELECT 
    'Campos actualizados correctamente' as mensaje,
    COUNT(*) as total_facturas
FROM facturas_digitales;
