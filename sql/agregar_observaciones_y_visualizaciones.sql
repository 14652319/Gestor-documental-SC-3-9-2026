-- =====================================================
-- AGREGAR TABLA DE OBSERVACIONES CON AUDITORÍA
-- Fecha: 2025-10-22
-- =====================================================

CREATE TABLE IF NOT EXISTS observaciones_documentos (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documentos_contables(id) ON DELETE CASCADE,
    observacion TEXT NOT NULL,
    momento VARCHAR(20) NOT NULL,  -- CARGA, EDICION
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_obs_documento ON observaciones_documentos(documento_id);
CREATE INDEX IF NOT EXISTS idx_obs_fecha ON observaciones_documentos(created_at DESC);

-- =====================================================
-- ACTUALIZAR TABLA DE HISTORIAL PARA VISUALIZACIONES
-- =====================================================

-- La tabla historial_documentos ya existe, solo agregamos comentario
COMMENT ON COLUMN historial_documentos.accion IS 'CREADO, EDITADO, ANULADO, VISUALIZADO, ANEXO_AGREGADO';

-- =====================================================
-- VERIFICACIÓN
-- =====================================================

SELECT 
    'observaciones_documentos' as tabla,
    COUNT(*) as registros
FROM observaciones_documentos
UNION ALL
SELECT 
    'historial_documentos' as tabla,
    COUNT(*) as registros
FROM historial_documentos;
