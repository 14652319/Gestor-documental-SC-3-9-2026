-- =====================================================
-- SCHEMA PARA MÓDULO CAUSACIONES
-- Fecha: Octubre 23, 2025
-- Sistema de gestión de documentos de causación
-- con extracción automática de datos de facturas
-- =====================================================

-- ✅ TABLA: documentos_causacion
-- Gestiona los PDFs de facturas electrónicas para causación
CREATE TABLE IF NOT EXISTS documentos_causacion (
    id SERIAL PRIMARY KEY,
    
    -- Información del archivo
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    tamano_archivo INTEGER,  -- En bytes
    
    -- Datos extraídos del PDF (automáticos)
    nit VARCHAR(20),
    razon_social VARCHAR(255),
    prefijo VARCHAR(10),
    folio VARCHAR(20),
    cufe VARCHAR(255),  -- Código Único de Factura Electrónica (50+ chars)
    
    -- Valores monetarios
    subtotal NUMERIC(15,2),
    iva NUMERIC(15,2),
    total_factura NUMERIC(15,2),
    
    -- Resolución DIAN
    numero_resolucion VARCHAR(50),
    rango_desde INTEGER,
    rango_hasta INTEGER,
    
    -- Tipo de documento
    tipo_documento VARCHAR(50) DEFAULT 'FACTURA ELECTRONICA',
    
    -- Estado del documento
    estado VARCHAR(20) DEFAULT 'pendiente',  -- pendiente, causado, rechazado
    
    -- Centro de operación
    centro_operacion_id INTEGER REFERENCES centros_operacion(id),
    
    -- Colaboración en tiempo real
    siendo_visualizado_por VARCHAR(100),
    fecha_inicio_visualizacion TIMESTAMP,
    
    -- Auditoría
    cargado_por VARCHAR(100) NOT NULL,
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_causacion TIMESTAMP,
    causado_por VARCHAR(100),
    ip_address VARCHAR(50),
    user_agent TEXT,
    
    -- Índices para búsquedas rápidas
    CONSTRAINT uk_prefijo_folio UNIQUE (prefijo, folio),
    CONSTRAINT uk_cufe UNIQUE (cufe)
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_documentos_causacion_estado ON documentos_causacion(estado);
CREATE INDEX idx_documentos_causacion_nit ON documentos_causacion(nit);
CREATE INDEX idx_documentos_causacion_centro ON documentos_causacion(centro_operacion_id);
CREATE INDEX idx_documentos_causacion_fecha_carga ON documentos_causacion(fecha_carga);
CREATE INDEX idx_documentos_causacion_siendo_visualizado ON documentos_causacion(siendo_visualizado_por);

-- Comentarios de documentación
COMMENT ON TABLE documentos_causacion IS 'Gestión de documentos de causación con extracción automática de datos de facturas electrónicas';
COMMENT ON COLUMN documentos_causacion.cufe IS 'Código Único de Factura Electrónica de 50+ caracteres';
COMMENT ON COLUMN documentos_causacion.estado IS 'Estados: pendiente (recién cargado), causado (procesado), rechazado (no procede)';
COMMENT ON COLUMN documentos_causacion.siendo_visualizado_por IS 'Usuario que está visualizando el documento actualmente (NULL si nadie lo ve)';

-- ✅ TABLA: observaciones_causacion
-- Sistema de observaciones para documentos de causación
CREATE TABLE IF NOT EXISTS observaciones_causacion (
    id SERIAL PRIMARY KEY,
    
    -- Relación con documento
    documento_id INTEGER NOT NULL REFERENCES documentos_causacion(id) ON DELETE CASCADE,
    
    -- Contenido de la observación
    observacion TEXT NOT NULL,
    
    -- Origen de la observación (módulo que la creó)
    origen VARCHAR(50) DEFAULT 'causaciones',  -- causaciones, archivo_digital, etc.
    
    -- Auditoría
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent TEXT
);

-- Índices
CREATE INDEX idx_observaciones_causacion_documento ON observaciones_causacion(documento_id);
CREATE INDEX idx_observaciones_causacion_origen ON observaciones_causacion(origen);
CREATE INDEX idx_observaciones_causacion_fecha ON observaciones_causacion(created_at);

-- Comentarios
COMMENT ON TABLE observaciones_causacion IS 'Sistema de observaciones para documentos de causación con soporte cross-módulo';
COMMENT ON COLUMN observaciones_causacion.origen IS 'Módulo que creó la observación (permite observaciones desde otros módulos)';

-- =====================================================
-- DATOS INICIALES (OPCIONAL)
-- =====================================================

-- Ejemplo de estados válidos
-- Los estados se manejan en el código, pero aquí documentamos los válidos:
-- - pendiente: Documento recién cargado, esperando causación
-- - causado: Documento causado exitosamente
-- - rechazado: Documento rechazado por algún motivo (explicar en observaciones)

-- =====================================================
-- CONSULTAS DE VERIFICACIÓN
-- =====================================================

-- Verificar estructura de tablas
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name IN ('documentos_causacion', 'observaciones_causacion')
ORDER BY table_name, ordinal_position;

-- Contar documentos por estado
-- SELECT estado, COUNT(*) as total
-- FROM documentos_causacion
-- GROUP BY estado;

-- Ver documentos siendo visualizados
-- SELECT id, nombre_archivo, siendo_visualizado_por, fecha_inicio_visualizacion
-- FROM documentos_causacion
-- WHERE siendo_visualizado_por IS NOT NULL;

-- Ver documentos con observaciones
-- SELECT 
--     d.id,
--     d.nombre_archivo,
--     d.estado,
--     COUNT(o.id) as total_observaciones
-- FROM documentos_causacion d
-- LEFT JOIN observaciones_causacion o ON d.id = o.documento_id
-- GROUP BY d.id, d.nombre_archivo, d.estado
-- HAVING COUNT(o.id) > 0;

-- =====================================================
-- FIN DEL SCHEMA
-- =====================================================
