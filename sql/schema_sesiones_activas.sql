-- ==============================================
-- TABLA: sesiones_activas
-- PROPÓSITO: Trackear sesiones de usuarios en tiempo real
-- FECHA: Octubre 23, 2025
-- ==============================================

CREATE TABLE IF NOT EXISTS sesiones_activas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    usuario_nombre VARCHAR(100) NOT NULL,
    session_id VARCHAR(255) NOT NULL UNIQUE,  -- ID de sesión de Flask
    ip_address VARCHAR(50) NOT NULL,
    user_agent TEXT,
    modulo_actual VARCHAR(100),  -- Nombre del módulo donde está trabajando
    ruta_actual VARCHAR(255),  -- URL actual del usuario
    conectado BOOLEAN DEFAULT TRUE,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultima_actividad TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_desconexion TIMESTAMP,
    pais VARCHAR(100),  -- País de la IP (obtenido de API)
    ciudad VARCHAR(100),  -- Ciudad de la IP
    latitud DECIMAL(10, 8),  -- Coordenadas para mapas
    longitud DECIMAL(11, 8),
    
    -- Índices para consultas rápidas
    INDEX idx_usuario_id (usuario_id),
    INDEX idx_session_id (session_id),
    INDEX idx_conectado (conectado),
    INDEX idx_ip_address (ip_address),
    INDEX idx_modulo_actual (modulo_actual)
);

COMMENT ON TABLE sesiones_activas IS 'Sesiones de usuarios activas en tiempo real para monitoreo';
COMMENT ON COLUMN sesiones_activas.session_id IS 'ID de sesión de Flask (session.sid)';
COMMENT ON COLUMN sesiones_activas.modulo_actual IS 'Módulo donde el usuario está trabajando (recibir_facturas, relaciones, etc)';
COMMENT ON COLUMN sesiones_activas.conectado IS 'TRUE si el usuario está actualmente conectado';
COMMENT ON COLUMN sesiones_activas.fecha_ultima_actividad IS 'Timestamp de la última petición del usuario (se actualiza cada 30 seg)';
