-- ============================================================================
-- TABLA: tokens_password
-- Descripción: Almacena tokens para establecer/recuperar contraseñas
-- ============================================================================

CREATE TABLE IF NOT EXISTS tokens_password (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expiracion TIMESTAMP NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_usuario_token UNIQUE (usuario_id)
);

CREATE INDEX IF NOT EXISTS idx_tokens_password_token ON tokens_password(token);
CREATE INDEX IF NOT EXISTS idx_tokens_password_usuario ON tokens_password(usuario_id);
CREATE INDEX IF NOT EXISTS idx_tokens_password_expiracion ON tokens_password(expiracion);

COMMENT ON TABLE tokens_password IS 'Tokens para establecer o recuperar contraseñas de usuarios';
COMMENT ON COLUMN tokens_password.usuario_id IS 'Usuario al que pertenece el token';
COMMENT ON COLUMN tokens_password.token IS 'Token único generado';
COMMENT ON COLUMN tokens_password.expiracion IS 'Fecha y hora de expiración del token';
COMMENT ON COLUMN tokens_password.usado IS 'Indica si el token ya fue utilizado';
