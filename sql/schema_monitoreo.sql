-- =====================================================
-- TABLAS PARA MÓDULO DE MONITOREO Y ADMINISTRACIÓN
-- Fecha: Octubre 23, 2025
-- =====================================================

-- Tabla: Alertas de Seguridad
CREATE TABLE IF NOT EXISTS alertas_seguridad (
    id SERIAL PRIMARY KEY,
    tipo_alerta VARCHAR(50) NOT NULL,
    ip VARCHAR(50),
    usuario VARCHAR(100),
    nit VARCHAR(20),
    detalles TEXT,
    enviada_telegram BOOLEAN DEFAULT FALSE,
    fecha_alerta TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resuelta BOOLEAN DEFAULT FALSE,
    fecha_resolucion TIMESTAMP,
    notas_resolucion TEXT
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_alertas_fecha ON alertas_seguridad(fecha_alerta DESC);
CREATE INDEX IF NOT EXISTS idx_alertas_tipo ON alertas_seguridad(tipo_alerta);
CREATE INDEX IF NOT EXISTS idx_alertas_resuelta ON alertas_seguridad(resuelta);
CREATE INDEX IF NOT EXISTS idx_alertas_ip ON alertas_seguridad(ip);

-- Comentarios
COMMENT ON TABLE alertas_seguridad IS 'Registro de alertas de seguridad enviadas por Telegram';
COMMENT ON COLUMN alertas_seguridad.tipo_alerta IS 'IP_BLOQUEADA, ATAQUE_BRUTE_FORCE, USUARIO_BLOQUEADO, INTENTOS_FALLIDOS, etc.';
COMMENT ON COLUMN alertas_seguridad.enviada_telegram IS 'Indica si la alerta fue enviada exitosamente por Telegram';
COMMENT ON COLUMN alertas_seguridad.resuelta IS 'Indica si la alerta ya fue atendida por un administrador';


-- Tabla: Logs de Acciones Administrativas
CREATE TABLE IF NOT EXISTS logs_acciones_admin (
    id SERIAL PRIMARY KEY,
    usuario_admin VARCHAR(100) NOT NULL,
    accion VARCHAR(100) NOT NULL,
    objetivo VARCHAR(255),
    detalles TEXT,
    resultado VARCHAR(20),
    fecha_accion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_admin VARCHAR(50)
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_logs_admin_fecha ON logs_acciones_admin(fecha_accion DESC);
CREATE INDEX IF NOT EXISTS idx_logs_admin_usuario ON logs_acciones_admin(usuario_admin);
CREATE INDEX IF NOT EXISTS idx_logs_admin_accion ON logs_acciones_admin(accion);
CREATE INDEX IF NOT EXISTS idx_logs_admin_resultado ON logs_acciones_admin(resultado);

-- Comentarios
COMMENT ON TABLE logs_acciones_admin IS 'Auditoría de acciones realizadas desde el panel de monitoreo';
COMMENT ON COLUMN logs_acciones_admin.accion IS 'BLOQUEAR_IP, DESBLOQUEAR_IP, ACTIVAR_USUARIO, DESACTIVAR_USUARIO, RESOLVER_ALERTA, etc.';
COMMENT ON COLUMN logs_acciones_admin.objetivo IS 'IP o usuario afectado por la acción';
COMMENT ON COLUMN logs_acciones_admin.resultado IS 'EXITOSO, ERROR';


-- Consultas de verificación
SELECT 'Tabla alertas_seguridad creada ✅' AS status;
SELECT 'Tabla logs_acciones_admin creada ✅' AS status;

-- Consultas de ejemplo
SELECT COUNT(*) AS total_alertas FROM alertas_seguridad;
SELECT COUNT(*) AS total_logs_admin FROM logs_acciones_admin;
