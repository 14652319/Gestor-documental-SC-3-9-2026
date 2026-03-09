-- =====================================================
-- TABLA DE RELACIÓN: USUARIO - DEPARTAMENTO
-- Permite que un usuario tenga múltiples departamentos
-- =====================================================

CREATE TABLE IF NOT EXISTS usuario_departamento (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    departamento VARCHAR(10) NOT NULL,
    puede_recibir BOOLEAN DEFAULT false,
    puede_aprobar BOOLEAN DEFAULT false,
    puede_rechazar BOOLEAN DEFAULT false,
    puede_firmar BOOLEAN DEFAULT false,
    activo BOOLEAN DEFAULT true,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT ck_departamento CHECK (departamento IN ('TIC', 'MER', 'FIN', 'DOM', 'MYP')),
    CONSTRAINT uk_usuario_departamento UNIQUE (usuario_id, departamento)
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_usuario_departamento_usuario ON usuario_departamento(usuario_id);
CREATE INDEX IF NOT EXISTS idx_usuario_departamento_depto ON usuario_departamento(departamento);
CREATE INDEX IF NOT EXISTS idx_usuario_departamento_activo ON usuario_departamento(activo);

-- Comentarios
COMMENT ON TABLE usuario_departamento IS 'Relación muchos a muchos: usuarios pueden tener múltiples departamentos con permisos diferentes';
COMMENT ON COLUMN usuario_departamento.usuario_id IS 'ID del usuario (FK a usuarios.id)';
COMMENT ON COLUMN usuario_departamento.departamento IS 'Código del departamento: TIC, MER, FIN, DOM, MYP';
COMMENT ON COLUMN usuario_departamento.puede_recibir IS 'Puede recibir facturas en este departamento';
COMMENT ON COLUMN usuario_departamento.puede_aprobar IS 'Puede aprobar facturas en este departamento';
COMMENT ON COLUMN usuario_departamento.puede_rechazar IS 'Puede rechazar facturas en este departamento';
COMMENT ON COLUMN usuario_departamento.puede_firmar IS 'Puede firmar facturas en este departamento';
COMMENT ON COLUMN usuario_departamento.activo IS 'Departamento activo para este usuario';
COMMENT ON COLUMN usuario_departamento.fecha_asignacion IS 'Fecha de asignación del departamento al usuario';
