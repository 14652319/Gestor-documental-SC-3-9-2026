-- ============================================================================
-- TABLA: usuario_departamento_firma
-- Descripción: Gestiona la asignación de usuarios a departamentos y sus permisos
-- Fecha creación: 8 de Diciembre 2025
-- ============================================================================

-- Crear tabla si no existe
CREATE TABLE IF NOT EXISTS usuario_departamento_firma (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    departamento VARCHAR(10) NOT NULL,
    
    -- Permisos (en orden: Recibir, Aprobar, Rechazar, Firmar)
    puede_recibir BOOLEAN DEFAULT false,
    puede_aprobar BOOLEAN DEFAULT false,
    puede_rechazar BOOLEAN DEFAULT false,
    puede_firmar BOOLEAN DEFAULT false,
    
    -- Legacy: campo para compatibilidad con sistema anterior
    es_firmador BOOLEAN DEFAULT false,
    
    -- Estado
    activo BOOLEAN DEFAULT true,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint: un usuario solo puede tener una configuración por departamento
    UNIQUE(usuario_id, departamento)
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_udf_usuario ON usuario_departamento_firma(usuario_id);
CREATE INDEX IF NOT EXISTS idx_udf_departamento ON usuario_departamento_firma(departamento);
CREATE INDEX IF NOT EXISTS idx_udf_activo ON usuario_departamento_firma(activo);
CREATE INDEX IF NOT EXISTS idx_udf_firmador ON usuario_departamento_firma(es_firmador, activo);

-- Comentarios
COMMENT ON TABLE usuario_departamento_firma IS 'Gestiona la asignación de usuarios a departamentos y sus permisos de facturación';
COMMENT ON COLUMN usuario_departamento_firma.puede_recibir IS 'Permiso para recibir facturas y documentos digitales';
COMMENT ON COLUMN usuario_departamento_firma.puede_aprobar IS 'Permiso para aprobar facturas revisadas';
COMMENT ON COLUMN usuario_departamento_firma.puede_rechazar IS 'Permiso para rechazar facturas con observaciones';
COMMENT ON COLUMN usuario_departamento_firma.puede_firmar IS 'Permiso para firmar digitalmente facturas aprobadas';
COMMENT ON COLUMN usuario_departamento_firma.es_firmador IS 'Campo legacy - se sincroniza con puede_firmar';

-- ============================================================================
-- EJEMPLOS DE INSERCIÓN
-- ============================================================================

-- Ejemplo 1: Usuario con todos los permisos (Admin de departamento)
-- INSERT INTO usuario_departamento_firma (usuario_id, departamento, puede_recibir, puede_aprobar, puede_rechazar, puede_firmar, es_firmador)
-- VALUES (1, 'TIC', true, true, true, true, true);

-- Ejemplo 2: Usuario solo para recibir y aprobar
-- INSERT INTO usuario_departamento_firma (usuario_id, departamento, puede_recibir, puede_aprobar, puede_rechazar, puede_firmar, es_firmador)
-- VALUES (2, 'MER', true, true, false, false, false);

-- Ejemplo 3: Usuario solo para firmar
-- INSERT INTO usuario_departamento_firma (usuario_id, departamento, puede_recibir, puede_aprobar, puede_rechazar, puede_firmar, es_firmador)
-- VALUES (3, 'FIN', false, false, false, true, true);

-- ============================================================================
-- CONSULTAS ÚTILES
-- ============================================================================

-- Ver todos los usuarios con sus permisos
-- SELECT 
--     u.usuario,
--     udf.departamento,
--     udf.puede_recibir as recibir,
--     udf.puede_aprobar as aprobar,
--     udf.puede_rechazar as rechazar,
--     udf.puede_firmar as firmar
-- FROM usuario_departamento_firma udf
-- JOIN usuarios u ON u.id = udf.usuario_id
-- WHERE udf.activo = true
-- ORDER BY udf.departamento, u.usuario;

-- Ver firmadores activos por departamento
-- SELECT 
--     departamento,
--     COUNT(*) as total_firmadores,
--     STRING_AGG(u.usuario, ', ') as usuarios
-- FROM usuario_departamento_firma udf
-- JOIN usuarios u ON u.id = udf.usuario_id
-- WHERE udf.puede_firmar = true AND udf.activo = true
-- GROUP BY departamento;
