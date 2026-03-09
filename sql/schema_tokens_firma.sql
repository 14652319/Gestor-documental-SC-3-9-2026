-- =============================================
-- 🔐 ESQUEMA: TOKENS DE FIRMA DIGITAL
-- Sistema de validación por correo electrónico
-- Fecha: Octubre 20, 2025
-- =============================================

-- Tabla: tokens_firma_digital
CREATE TABLE IF NOT EXISTS tokens_firma_digital (
    id SERIAL PRIMARY KEY,
    token VARCHAR(6) NOT NULL,
    usuario VARCHAR(100) NOT NULL,
    numero_relacion VARCHAR(20) NOT NULL,
    correo_destino VARCHAR(255) NOT NULL,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    intentos_validacion INTEGER DEFAULT 0,
    fecha_uso TIMESTAMP,
    ip_creacion VARCHAR(50),
    ip_uso VARCHAR(50)
);

-- Índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_token_firma_token ON tokens_firma_digital(token);
CREATE INDEX IF NOT EXISTS idx_token_firma_usuario ON tokens_firma_digital(usuario);
CREATE INDEX IF NOT EXISTS idx_token_firma_relacion ON tokens_firma_digital(numero_relacion);
CREATE INDEX IF NOT EXISTS idx_token_firma_vigencia ON tokens_firma_digital(usado, fecha_expiracion);

-- Comentarios
COMMENT ON TABLE tokens_firma_digital IS 'Tokens de 6 dígitos para firmar recepciones digitales';
COMMENT ON COLUMN tokens_firma_digital.token IS 'Token de 6 dígitos enviado por correo';
COMMENT ON COLUMN tokens_firma_digital.fecha_expiracion IS 'Token válido por 10 minutos';
COMMENT ON COLUMN tokens_firma_digital.intentos_validacion IS 'Máximo 3 intentos permitidos';

-- Verificación
SELECT 'Tabla tokens_firma_digital creada exitosamente' AS status;
SELECT COUNT(*) AS total_registros FROM tokens_firma_digital;
