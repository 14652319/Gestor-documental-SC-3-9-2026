-- =====================================================
-- Script de actualización de Base de Datos
-- Agregar campos necesarios para sincronización en tiempo real
-- Fecha: 28 de Diciembre de 2025
-- =====================================================

-- 1. Agregar campos de sincronización a maestro_dian_vs_erp
ALTER TABLE maestro_dian_vs_erp 
ADD COLUMN IF NOT EXISTS usuario_recibio VARCHAR(100),
ADD COLUMN IF NOT EXISTS origen_sincronizacion VARCHAR(50),
ADD COLUMN IF NOT EXISTS rechazada BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS motivo_rechazo TEXT,
ADD COLUMN IF NOT EXISTS fecha_rechazo TIMESTAMP;

-- 2. Agregar comentarios para documentación
COMMENT ON COLUMN maestro_dian_vs_erp.usuario_recibio IS 'Usuario que recibió la factura manualmente';
COMMENT ON COLUMN maestro_dian_vs_erp.origen_sincronizacion IS 'Módulo de origen: FACTURAS_TEMPORALES, FACTURAS_RECIBIDAS, RELACIONES, CAUSACIONES';
COMMENT ON COLUMN maestro_dian_vs_erp.rechazada IS 'Si la factura fue rechazada en algún módulo';
COMMENT ON COLUMN maestro_dian_vs_erp.motivo_rechazo IS 'Motivo del rechazo';
COMMENT ON COLUMN maestro_dian_vs_erp.fecha_rechazo IS 'Fecha y hora del rechazo';

-- 3. Crear índice compuesto para búsquedas rápidas por clave
CREATE INDEX IF NOT EXISTS idx_maestro_clave 
ON maestro_dian_vs_erp(nit_emisor, prefijo, folio);

-- 4. Crear índice para búsquedas por origen
CREATE INDEX IF NOT EXISTS idx_maestro_origen 
ON maestro_dian_vs_erp(origen_sincronizacion);

-- 5. Agregar campos de rechazo a relaciones_facturas
ALTER TABLE relaciones_facturas
ADD COLUMN IF NOT EXISTS rechazada BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS motivo_rechazo TEXT,
ADD COLUMN IF NOT EXISTS fecha_rechazo TIMESTAMP,
ADD COLUMN IF NOT EXISTS usuario_rechazo VARCHAR(100);

-- 6. Agregar comentarios para relaciones
COMMENT ON COLUMN relaciones_facturas.rechazada IS 'Si la factura en la relación fue rechazada';
COMMENT ON COLUMN relaciones_facturas.motivo_rechazo IS 'Motivo del rechazo en relación';
COMMENT ON COLUMN relaciones_facturas.fecha_rechazo IS 'Fecha y hora del rechazo';
COMMENT ON COLUMN relaciones_facturas.usuario_rechazo IS 'Usuario que rechazó';

-- 7. Agregar campo de novedad a documentos_causacion
ALTER TABLE documentos_causacion
ADD COLUMN IF NOT EXISTS tiene_novedad BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS descripcion_novedad TEXT,
ADD COLUMN IF NOT EXISTS fecha_novedad TIMESTAMP,
ADD COLUMN IF NOT EXISTS usuario_novedad VARCHAR(100),
ADD COLUMN IF NOT EXISTS novedad_resuelta BOOLEAN DEFAULT FALSE;

-- 8. Comentarios para causaciones
COMMENT ON COLUMN documentos_causacion.tiene_novedad IS 'Si el documento tiene alguna novedad/problema';
COMMENT ON COLUMN documentos_causacion.descripcion_novedad IS 'Descripción de la novedad';
COMMENT ON COLUMN documentos_causacion.fecha_novedad IS 'Fecha de reporte de novedad';
COMMENT ON COLUMN documentos_causacion.usuario_novedad IS 'Usuario que reportó la novedad';
COMMENT ON COLUMN documentos_causacion.novedad_resuelta IS 'Si la novedad ya fue resuelta';

-- 9. Crear tabla de logs de sincronización
CREATE TABLE IF NOT EXISTS logs_sincronizacion (
    id SERIAL PRIMARY KEY,
    fecha_sincronizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modulo_origen VARCHAR(50) NOT NULL,
    accion VARCHAR(50) NOT NULL, -- INSERTAR, ACTUALIZAR, ELIMINAR
    nit VARCHAR(20),
    prefijo VARCHAR(10),
    folio VARCHAR(20),
    estado_anterior VARCHAR(100),
    estado_nuevo VARCHAR(100),
    usuario VARCHAR(100),
    detalles TEXT,
    exito BOOLEAN DEFAULT TRUE,
    mensaje_error TEXT
);

-- 10. Índices para logs
CREATE INDEX IF NOT EXISTS idx_logs_fecha ON logs_sincronizacion(fecha_sincronizacion);
CREATE INDEX IF NOT EXISTS idx_logs_modulo ON logs_sincronizacion(modulo_origen);

-- 11. Verificar campos creados
SELECT 
    'maestro_dian_vs_erp' as tabla,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'maestro_dian_vs_erp'
AND column_name IN ('usuario_recibio', 'origen_sincronizacion', 'rechazada', 'motivo_rechazo', 'fecha_rechazo')
ORDER BY ordinal_position;

-- 12. Verificar índices creados
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('maestro_dian_vs_erp', 'relaciones_facturas')
ORDER BY tablename, indexname;

-- =====================================================
-- FIN DEL SCRIPT
-- =====================================================
