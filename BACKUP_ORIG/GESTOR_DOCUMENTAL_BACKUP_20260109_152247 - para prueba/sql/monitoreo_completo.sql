-- ============================================================================
-- SISTEMA DE MONITOREO COMPLETO
-- Fecha: 28 Noviembre 2025
-- ============================================================================

-- Tabla: sesiones_activas (usuarios conectados en tiempo real)
CREATE TABLE IF NOT EXISTS sesiones_activas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    usuario VARCHAR(100) NOT NULL,
    nit VARCHAR(20),
    ip VARCHAR(50),
    user_agent TEXT,
    ultimo_ping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modulo_actual VARCHAR(100),
    ruta_actual VARCHAR(500),
    fecha_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activa BOOLEAN DEFAULT TRUE,
    CONSTRAINT uk_sesion_usuario UNIQUE (usuario_id, ip)
);

CREATE INDEX idx_sesiones_activas_usuario ON sesiones_activas(usuario_id);
CREATE INDEX idx_sesiones_activas_activa ON sesiones_activas(activa);
CREATE INDEX idx_sesiones_ultimo_ping ON sesiones_activas(ultimo_ping);

-- Tabla: logs_sistema (logs de aplicación separados)
CREATE TABLE IF NOT EXISTS logs_sistema (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL, -- 'ERROR', 'WARNING', 'INFO', 'DEBUG'
    modulo VARCHAR(100) NOT NULL,
    mensaje TEXT NOT NULL,
    usuario VARCHAR(100),
    ip VARCHAR(50),
    detalles JSONB,
    stack_trace TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_sistema_tipo ON logs_sistema(tipo);
CREATE INDEX idx_logs_sistema_modulo ON logs_sistema(modulo);
CREATE INDEX idx_logs_sistema_fecha ON logs_sistema(fecha);

-- Tabla: logs_auditoria (auditoría de cambios)
CREATE TABLE IF NOT EXISTS logs_auditoria (
    id SERIAL PRIMARY KEY,
    tabla VARCHAR(100) NOT NULL,
    accion VARCHAR(20) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    registro_id INTEGER,
    usuario_id INTEGER REFERENCES usuarios(id),
    usuario VARCHAR(100),
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    ip VARCHAR(50),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_auditoria_tabla ON logs_auditoria(tabla);
CREATE INDEX idx_logs_auditoria_usuario ON logs_auditoria(usuario);
CREATE INDEX idx_logs_auditoria_fecha ON logs_auditoria(fecha);

-- Tabla: alertas_sistema (alertas configurables)
CREATE TABLE IF NOT EXISTS alertas_sistema (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL, -- 'SEGURIDAD', 'RENDIMIENTO', 'ESPACIO', 'ERROR'
    severidad VARCHAR(20) NOT NULL, -- 'CRITICA', 'ALTA', 'MEDIA', 'BAJA'
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    detalles JSONB,
    estado VARCHAR(20) DEFAULT 'pendiente', -- 'pendiente', 'vista', 'resuelta', 'ignorada'
    usuario_responsable VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_resolucion TIMESTAMP,
    activa BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_alertas_tipo ON alertas_sistema(tipo);
CREATE INDEX idx_alertas_severidad ON alertas_sistema(severidad);
CREATE INDEX idx_alertas_estado ON alertas_sistema(estado);
CREATE INDEX idx_alertas_fecha ON alertas_sistema(fecha_creacion);

-- Tabla: metricas_rendimiento (métricas del sistema)
CREATE TABLE IF NOT EXISTS metricas_rendimiento (
    id SERIAL PRIMARY KEY,
    cpu_percent DECIMAL(5,2),
    memoria_percent DECIMAL(5,2),
    memoria_usada_mb BIGINT,
    memoria_total_mb BIGINT,
    disco_percent DECIMAL(5,2),
    disco_usado_gb DECIMAL(10,2),
    disco_total_gb DECIMAL(10,2),
    conexiones_bd INTEGER,
    requests_por_minuto INTEGER,
    tiempo_respuesta_avg_ms DECIMAL(10,2),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metricas_fecha ON metricas_rendimiento(fecha);

-- Tabla: ips_blancas (IPs autorizadas permanentemente)
CREATE TABLE IF NOT EXISTS ips_blancas (
    id SERIAL PRIMARY KEY,
    ip VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    usuario_agrego VARCHAR(100),
    fecha_agregada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activa BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_ips_blancas_ip ON ips_blancas(ip);
CREATE INDEX idx_ips_blancas_activa ON ips_blancas(activa);

-- Comentarios de tablas
COMMENT ON TABLE sesiones_activas IS 'Sesiones de usuarios activas en tiempo real con ping cada 30 segundos';
COMMENT ON TABLE logs_sistema IS 'Logs de errores, warnings e info de la aplicación (separado de security.log)';
COMMENT ON TABLE logs_auditoria IS 'Auditoría de cambios en tablas críticas (usuarios, permisos, facturas)';
COMMENT ON TABLE alertas_sistema IS 'Alertas configurables que requieren atención del administrador';
COMMENT ON TABLE metricas_rendimiento IS 'Métricas de CPU, RAM, disco recolectadas cada 5 minutos';
COMMENT ON TABLE ips_blancas IS 'IPs en lista blanca (nunca se bloquean)';

-- ============================================================================
-- DATOS INICIALES
-- ============================================================================

-- IPs blancas iniciales (localhost)
INSERT INTO ips_blancas (ip, descripcion, usuario_agrego) VALUES
('127.0.0.1', 'Localhost', 'sistema'),
('::1', 'Localhost IPv6', 'sistema')
ON CONFLICT (ip) DO NOTHING;

-- Alerta de ejemplo
INSERT INTO alertas_sistema (tipo, severidad, titulo, descripcion) VALUES
('SEGURIDAD', 'MEDIA', 'Sistema de monitoreo activado', 'El módulo de monitoreo se ha inicializado correctamente.')
ON CONFLICT DO NOTHING;
