-- ============================================================================
-- SISTEMA DE BACKUP AUTOMÁTICO
-- Gestor Documental - Supertiendas Cañaveral
-- Fecha: Diciembre 1, 2025
-- ============================================================================

-- Tabla de configuración de backups
CREATE TABLE IF NOT EXISTS configuracion_backup (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL UNIQUE,  -- 'base_datos', 'archivos', 'codigo'
    habilitado BOOLEAN DEFAULT TRUE,
    destino VARCHAR(500) NOT NULL,
    horario_cron VARCHAR(50) DEFAULT '0 2 * * *',
    dias_retencion INTEGER DEFAULT 7,
    ultima_ejecucion TIMESTAMP,
    proximo_backup TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para búsqueda por tipo
CREATE INDEX IF NOT EXISTS idx_config_backup_tipo ON configuracion_backup(tipo);

-- Tabla de historial de backups
CREATE TABLE IF NOT EXISTS historial_backup (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP,
    estado VARCHAR(20) NOT NULL,  -- 'exitoso', 'fallido', 'en_progreso'
    ruta_archivo VARCHAR(500),
    tamano_bytes BIGINT,
    duracion_segundos INTEGER,
    mensaje VARCHAR(1000),
    error VARCHAR(2000),
    usuario VARCHAR(50)
);

-- Índices para mejorar consultas
CREATE INDEX IF NOT EXISTS idx_historial_tipo ON historial_backup(tipo);
CREATE INDEX IF NOT EXISTS idx_historial_fecha ON historial_backup(fecha_inicio DESC);
CREATE INDEX IF NOT EXISTS idx_historial_estado ON historial_backup(estado);

-- Insertar configuración por defecto
INSERT INTO configuracion_backup (tipo, destino, horario_cron, dias_retencion, habilitado)
VALUES 
    ('base_datos', 'C:\Backups_GestorDocumental\base_datos', '0 2 * * *', 7, TRUE),
    ('archivos', 'C:\Backups_GestorDocumental\documentos', '0 3 * * *', 14, TRUE),
    ('codigo', 'C:\Backups_GestorDocumental\codigo', '0 4 * * 0', 30, TRUE)
ON CONFLICT (tipo) DO NOTHING;

-- Comentarios
COMMENT ON TABLE configuracion_backup IS 'Configuración del sistema de backups automáticos';
COMMENT ON TABLE historial_backup IS 'Historial de ejecuciones de backups';
COMMENT ON COLUMN configuracion_backup.horario_cron IS 'Expresión cron para programar backups (ej: 0 2 * * * = 2 AM diario)';
COMMENT ON COLUMN configuracion_backup.dias_retencion IS 'Días que se conservan los backups antes de eliminarse';
COMMENT ON COLUMN historial_backup.tamano_bytes IS 'Tamaño del archivo de backup en bytes';

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================
