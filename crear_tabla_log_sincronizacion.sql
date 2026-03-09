-- Tabla para almacenar el log de sincronizaciones del visor
CREATE TABLE IF NOT EXISTS log_sincronizacion_visor (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    fecha_sincronizacion TIMESTAMP DEFAULT NOW(),
    registros_verificados INTEGER DEFAULT 0,
    tipo VARCHAR(50) DEFAULT 'manual',  -- 'manual', 'automatica'
    datos_resumen JSONB,  -- Guardar resumen de la sincronización
    ip_origen VARCHAR(50),
    user_agent TEXT
);

-- Índice para consultas rápidas por usuario
CREATE INDEX IF NOT EXISTS idx_log_sync_usuario ON log_sincronizacion_visor(usuario_id);

-- Índice para consultas por fecha
CREATE INDEX IF NOT EXISTS idx_log_sync_fecha ON log_sincronizacion_visor(fecha_sincronizacion DESC);

-- Comentarios
COMMENT ON TABLE log_sincronizacion_visor IS 'Log de sincronizaciones del Visor v2 - Guarda fecha y hora de cada sincronización';
COMMENT ON COLUMN log_sincronizacion_visor.datos_resumen IS 'JSON con resumen: {total_dian, total_temporales, total_recibidas, etc}';
