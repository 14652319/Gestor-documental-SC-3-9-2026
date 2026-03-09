-- =====================================================
-- SCHEMA PARA MÓDULO DE NOTAS CONTABLES
-- Fecha: 17 de Octubre 2025
-- Descripción: Tablas para gestión de documentos contables
--              con tipos, centros de operación y adjuntos
-- =====================================================

-- =====================================================
-- TABLA: tipos_documento
-- Descripción: Catálogo de tipos de documentos (NOC, NCM, NTN, LEG, etc.)
-- =====================================================
CREATE TABLE IF NOT EXISTS tipos_documento (
    id SERIAL PRIMARY KEY,
    siglas VARCHAR(10) NOT NULL UNIQUE,  -- NOC, NCM, NTN, LEG
    nombre VARCHAR(100) NOT NULL,        -- Nota de Contabilidad
    modulo VARCHAR(50) NOT NULL,         -- Contabilidad, Tesorería, Legal
    estado VARCHAR(20) NOT NULL DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    created_by VARCHAR(50) NOT NULL,     -- Usuario que creó el registro
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(50),
    updated_at TIMESTAMP
);

-- Índices para búsquedas rápidas
CREATE INDEX idx_tipos_documento_estado ON tipos_documento(estado);
CREATE INDEX idx_tipos_documento_modulo ON tipos_documento(modulo);

-- Datos iniciales
INSERT INTO tipos_documento (siglas, nombre, modulo, estado, created_by) VALUES
('NOC', 'Nota de Contabilidad', 'Contabilidad', 'activo', 'admin'),
('NCM', 'Nota Contable de Mayor', 'Contabilidad', 'activo', 'admin'),
('NTN', 'Nota de Tesorería', 'Tesorería', 'activo', 'admin'),
('LEG', 'Documento Legal', 'Legal', 'activo', 'admin')
ON CONFLICT (siglas) DO NOTHING;

-- =====================================================
-- TABLA: centros_operacion
-- Descripción: Catálogo de centros de operación (C.O.)
-- =====================================================
CREATE TABLE IF NOT EXISTS centros_operacion (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,  -- 001, 002, 003
    nombre VARCHAR(100) NOT NULL,        -- Centro Principal
    direccion VARCHAR(200),
    ciudad VARCHAR(50),
    telefono VARCHAR(20),
    estado VARCHAR(20) NOT NULL DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    tipo_propiedad VARCHAR(20) NOT NULL DEFAULT 'propio' CHECK (tipo_propiedad IN ('propio', 'arrendado')),
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(50),
    updated_at TIMESTAMP
);

-- Índices para búsquedas rápidas
CREATE INDEX idx_centros_operacion_estado ON centros_operacion(estado);
CREATE INDEX idx_centros_operacion_ciudad ON centros_operacion(ciudad);

-- Datos iniciales
INSERT INTO centros_operacion (codigo, nombre, direccion, ciudad, telefono, estado, tipo_propiedad, created_by) VALUES
('001', 'Centro Principal', 'Calle 123 #45-67', 'Cali', '555-1234', 'activo', 'propio', 'admin'),
('002', 'Sucursal Norte', 'Avenida 9 #12-34', 'Cali', '555-5678', 'activo', 'arrendado', 'admin'),
('003', 'Centro Logístico', 'Carrera 50 #80-90', 'Yumbo', '555-9012', 'inactivo', 'arrendado', 'admin')
ON CONFLICT (codigo) DO NOTHING;

-- =====================================================
-- TABLA: documentos_contables
-- Descripción: Registro principal de documentos contables cargados
-- =====================================================
CREATE TABLE IF NOT EXISTS documentos_contables (
    id SERIAL PRIMARY KEY,
    tipo_documento_id INTEGER NOT NULL REFERENCES tipos_documento(id),
    centro_operacion_id INTEGER NOT NULL REFERENCES centros_operacion(id),
    consecutivo VARCHAR(20) NOT NULL,     -- 00000123 (8 dígitos con padding)
    fecha_documento DATE NOT NULL,
    empresa VARCHAR(10) NOT NULL,         -- SC (Supertiendas Cañaveral) o LG (Legran)
    nombre_archivo VARCHAR(255) NOT NULL, -- CO-TIPO-CONSECUTIVO.pdf (editable por usuario)
    ruta_archivo VARCHAR(500) NOT NULL,   -- Ruta completa: EMPRESA/AÑO/MES/TIPO/CO/DOCUMENTO/
    observaciones TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo' CHECK (estado IN ('activo', 'anulado', 'eliminado')),
    created_by VARCHAR(50) NOT NULL,      -- Usuario que cargó el documento
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(50),
    updated_at TIMESTAMP,
    
    -- Constraint: consecutivo único por tipo y C.O.
    UNIQUE(tipo_documento_id, centro_operacion_id, consecutivo)
);

-- Índices para búsquedas y filtros
CREATE INDEX idx_documentos_fecha ON documentos_contables(fecha_documento);
CREATE INDEX idx_documentos_tipo ON documentos_contables(tipo_documento_id);
CREATE INDEX idx_documentos_centro ON documentos_contables(centro_operacion_id);
CREATE INDEX idx_documentos_empresa ON documentos_contables(empresa);
CREATE INDEX idx_documentos_estado ON documentos_contables(estado);
CREATE INDEX idx_documentos_created_by ON documentos_contables(created_by);

-- =====================================================
-- TABLA: adjuntos_documentos
-- Descripción: Archivos adjuntos asociados a cada documento
--              (Excel, imágenes, PDFs adicionales)
-- =====================================================
CREATE TABLE IF NOT EXISTS adjuntos_documentos (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documentos_contables(id) ON DELETE CASCADE,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    tipo_archivo VARCHAR(50),             -- xlsx, jpg, png, pdf
    tamano_bytes INTEGER,
    descripcion VARCHAR(255),
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para búsqueda rápida por documento
CREATE INDEX idx_adjuntos_documento ON adjuntos_documentos(documento_id);

-- =====================================================
-- TABLA: historial_documentos
-- Descripción: Auditoría completa de cambios en documentos
-- =====================================================
CREATE TABLE IF NOT EXISTS historial_documentos (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documentos_contables(id) ON DELETE CASCADE,
    accion VARCHAR(50) NOT NULL,          -- CREADO, EDITADO, ANULADO, ELIMINADO
    campo_modificado VARCHAR(100),        -- observaciones, nombre_archivo, estado
    valor_anterior TEXT,
    valor_nuevo TEXT,
    motivo TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para auditoría
CREATE INDEX idx_historial_documento ON historial_documentos(documento_id);
CREATE INDEX idx_historial_fecha ON historial_documentos(created_at);
CREATE INDEX idx_historial_usuario ON historial_documentos(created_by);
CREATE INDEX idx_historial_accion ON historial_documentos(accion);

-- =====================================================
-- COMENTARIOS DE TABLAS (documentación en BD)
-- =====================================================
COMMENT ON TABLE tipos_documento IS 'Catálogo de tipos de documentos contables (NOC, NCM, NTN, LEG)';
COMMENT ON TABLE centros_operacion IS 'Catálogo de centros de operación con ubicación y tipo de propiedad';
COMMENT ON TABLE documentos_contables IS 'Registro principal de documentos contables cargados al sistema';
COMMENT ON TABLE adjuntos_documentos IS 'Archivos adjuntos adicionales asociados a cada documento';
COMMENT ON TABLE historial_documentos IS 'Auditoría completa de todas las operaciones sobre documentos';

-- =====================================================
-- PERMISOS (ajustar según usuario de la aplicación)
-- =====================================================
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO gestor_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO gestor_user;
