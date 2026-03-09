-- =============================================
-- 🗄️ CREACIÓN DE TABLA: tipos_documento
-- =============================================
-- Fecha: Octubre 22, 2025
-- Propósito: Almacenar los tipos de documentos para el módulo de Archivo Digital
-- Autor: Sistema

-- Eliminar tabla si existe (para desarrollo, comentar en producción)
-- DROP TABLE IF EXISTS tipos_documento CASCADE;

-- Crear tabla tipos_documento
CREATE TABLE IF NOT EXISTS tipos_documento (
    -- Clave primaria
    id SERIAL PRIMARY KEY,
    
    -- Siglas del tipo (ej: NOC, NCM, FAC)
    siglas VARCHAR(10) NOT NULL UNIQUE,
    
    -- Nombre descriptivo
    nombre VARCHAR(200) NOT NULL,
    
    -- Módulo al que pertenece
    modulo VARCHAR(100) NOT NULL,
    
    -- Descripción opcional
    descripcion TEXT,
    
    -- Estado (activo/inactivo)
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    
    -- Auditoría de creación
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Auditoría de modificación
    updated_by VARCHAR(100),
    updated_at TIMESTAMP,
    
    -- Índices
    CONSTRAINT chk_estado_tipo CHECK (estado IN ('activo', 'inactivo'))
);

-- Crear índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_tipos_documento_estado ON tipos_documento(estado);
CREATE INDEX IF NOT EXISTS idx_tipos_documento_modulo ON tipos_documento(modulo);
CREATE INDEX IF NOT EXISTS idx_tipos_documento_siglas ON tipos_documento(siglas);

-- Comentarios descriptivos
COMMENT ON TABLE tipos_documento IS 'Catálogo de tipos de documentos para el sistema de Archivo Digital';
COMMENT ON COLUMN tipos_documento.siglas IS 'Código corto único del tipo de documento (ej: NOC, FAC)';
COMMENT ON COLUMN tipos_documento.nombre IS 'Nombre completo del tipo de documento';
COMMENT ON COLUMN tipos_documento.modulo IS 'Módulo al que pertenece (Contabilidad, Tesorería, Legal, etc)';
COMMENT ON COLUMN tipos_documento.estado IS 'Estado del tipo: activo o inactivo';

-- =============================================
-- 📝 REGISTROS INICIALES
-- =============================================
INSERT INTO tipos_documento (siglas, nombre, modulo, descripcion, estado, created_by, created_at) VALUES
('NOC', 'Nota de Contabilidad', 'Contabilidad', 'Notas contables generales para ajustes y reclasificaciones', 'activo', 'sistema', NOW()),
('NCM', 'Nota Crédito Mercancía', 'Contabilidad', 'Notas de crédito por devoluciones de mercancía', 'activo', 'sistema', NOW()),
('NTN', 'Nota de Tesorería', 'Tesorería', 'Documentos de movimientos de caja y bancos', 'activo', 'sistema', NOW()),
('LEG', 'Documento Legal', 'Legal', 'Contratos, acuerdos y documentos legales', 'activo', 'sistema', NOW()),
('FAC', 'Factura de Compra', 'Compras', 'Facturas de proveedores y compras', 'activo', 'sistema', NOW()),
('NDB', 'Nota Débito Bancaria', 'Tesorería', 'Notas débito de entidades bancarias', 'activo', 'sistema', NOW()),
('NCB', 'Nota Crédito Bancaria', 'Tesorería', 'Notas crédito de entidades bancarias', 'activo', 'sistema', NOW()),
('RCI', 'Recibo de Caja Interno', 'Tesorería', 'Recibos de caja para movimientos internos', 'activo', 'sistema', NOW()),
('CEG', 'Comprobante de Egreso', 'Tesorería', 'Comprobantes de pagos y egresos', 'activo', 'sistema', NOW()),
('ACT', 'Acta', 'Legal', 'Actas de reuniones, juntas y asambleas', 'activo', 'sistema', NOW())
ON CONFLICT (siglas) DO NOTHING;

-- Mensaje de confirmación
SELECT 
    '✅ Tabla tipos_documento creada exitosamente' AS mensaje,
    COUNT(*) AS "Total de tipos",
    COUNT(*) FILTER (WHERE estado = 'activo') AS "Tipos activos"
FROM tipos_documento;
