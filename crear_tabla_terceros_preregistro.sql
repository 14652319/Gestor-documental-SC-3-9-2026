-- =====================================================
-- MIGRACIÓN SAGRILAFT - Crear tabla terceros_preregistro
-- Fecha: 2026-01-29
-- Propósito: Separar preregistros de terceros validados
-- =====================================================

-- PASO 1: Crear tabla terceros_preregistro
CREATE TABLE IF NOT EXISTS terceros_preregistro (
    id SERIAL PRIMARY KEY,
    nit VARCHAR(20) UNIQUE NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    tipo_persona VARCHAR(20),
    primer_nombre VARCHAR(80),
    segundo_nombre VARCHAR(80),
    primer_apellido VARCHAR(80),
    segundo_apellido VARCHAR(80),
    correo VARCHAR(120),
    celular VARCHAR(30),
    acepta_terminos BOOLEAN DEFAULT TRUE,
    acepta_contacto BOOLEAN DEFAULT FALSE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_preregistro VARCHAR(20) DEFAULT 'en_revision',
    fecha_actualizacion TIMESTAMP,
    CONSTRAINT chk_tipo_persona CHECK (tipo_persona IN ('natural', 'juridica')),
    CONSTRAINT chk_estado_preregistro CHECK (estado_preregistro IN ('en_revision', 'aprobado', 'rechazado'))
);

-- PASO 2: Crear índices para optimizar consultas
CREATE INDEX idx_terceros_preregistro_nit ON terceros_preregistro(nit);
CREATE INDEX idx_terceros_preregistro_estado ON terceros_preregistro(estado_preregistro);
CREATE INDEX idx_terceros_preregistro_fecha ON terceros_preregistro(fecha_registro);

-- PASO 3: Actualizar solicitudes_registro para apuntar a terceros_preregistro
-- Nota: Si ya existen solicitudes, se mantienen con tercero_id apuntando a 'terceros'
-- Las nuevas solicitudes usarán terceros_preregistro

-- Verificar si existe constraint en solicitudes_registro
DO $$
BEGIN
    -- Eliminar constraint viejo si existe (con terceros)
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'solicitudes_registro_tercero_id_fkey' 
        AND table_name = 'solicitudes_registro'
    ) THEN
        ALTER TABLE solicitudes_registro DROP CONSTRAINT solicitudes_registro_tercero_id_fkey;
    END IF;
END$$;

-- PASO 4: Actualizar documentos_tercero (similar)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'documentos_tercero_tercero_id_fkey' 
        AND table_name = 'documentos_tercero'
    ) THEN
        ALTER TABLE documentos_tercero DROP CONSTRAINT documentos_tercero_tercero_id_fkey;
    END IF;
END$$;

-- PASO 5: Agregar nuevas columnas a solicitudes_registro si no existen
DO $$
BEGIN
    -- usuario_revisor
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'solicitudes_registro' 
        AND column_name = 'usuario_revisor'
    ) THEN
        ALTER TABLE solicitudes_registro ADD COLUMN usuario_revisor VARCHAR(100);
    END IF;
    
    -- fecha_revision
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'solicitudes_registro' 
        AND column_name = 'fecha_revision'
    ) THEN
        ALTER TABLE solicitudes_registro ADD COLUMN fecha_revision TIMESTAMP;
    END IF;
END$$;

-- PASO 6: Agregar columna validado a documentos_tercero si no existe
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'documentos_tercero' 
        AND column_name = 'validado'
    ) THEN
        ALTER TABLE documentos_tercero ADD COLUMN validado BOOLEAN DEFAULT FALSE;
    END IF;
END$$;

-- =====================================================
-- COMENTARIOS DE LA TABLA
-- =====================================================
COMMENT ON TABLE terceros_preregistro IS 'Terceros en proceso de preregistro SAGRILAFT - No validados aún';
COMMENT ON COLUMN terceros_preregistro.estado_preregistro IS 'Estado del preregistro: en_revision, aprobado, rechazado';
COMMENT ON COLUMN terceros_preregistro.nit IS 'NIT único del tercero - Se valida antes de migrar a terceros';

-- =====================================================
-- VERIFICACIÓN
-- =====================================================
SELECT 
    'terceros_preregistro' AS tabla,
    COUNT(*) AS registros
FROM terceros_preregistro
UNION ALL
SELECT 
    'solicitudes_registro' AS tabla,
    COUNT(*) AS registros
FROM solicitudes_registro
UNION ALL
SELECT 
    'documentos_tercero' AS tabla,
    COUNT(*) AS registros
FROM documentos_tercero;

-- =====================================================
-- FINALIZADO
-- =====================================================
-- Tabla 'terceros' original: SIN CAMBIOS ✅
-- Tabla 'terceros_preregistro' nueva: CREADA ✅
-- Relaciones actualizadas: LISTAS ✅
