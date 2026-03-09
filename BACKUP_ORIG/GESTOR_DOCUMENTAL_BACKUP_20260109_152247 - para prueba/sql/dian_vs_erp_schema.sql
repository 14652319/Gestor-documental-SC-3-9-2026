-- ================================================
-- SCRIPT DE CREACIÓN DE TABLAS PARA MÓDULO DIAN vs ERP
-- ================================================
-- Fecha: 13 de Noviembre de 2025
-- Descripción: Tablas para validación de facturas DIAN contra ERP
-- ================================================

-- Tabla para almacenar reportes de facturas desde la DIAN
CREATE TABLE IF NOT EXISTS reportes_dian (
    id SERIAL PRIMARY KEY,
    periodo VARCHAR(7) NOT NULL,                 -- Formato YYYY-MM (2025-11)
    nit_tercero VARCHAR(20),                     -- NIT del tercero
    nombre_tercero VARCHAR(255),                 -- Nombre/razón social
    prefijo VARCHAR(10),                         -- Prefijo de la factura
    folio VARCHAR(20) NOT NULL,                  -- Número de folio
    fecha_factura DATE,                          -- Fecha de la factura
    valor_factura DECIMAL(15,2),                 -- Valor total de la factura
    datos_adicionales JSONB,                     -- Datos adicionales del reporte DIAN
    archivo_origen VARCHAR(255),                 -- Nombre del archivo origen
    fecha_carga TIMESTAMP DEFAULT NOW(),        -- Fecha de carga del registro
    usuario_carga VARCHAR(100),                 -- Usuario que cargó el registro
    activo BOOLEAN DEFAULT TRUE,                 -- Si el registro está activo
    
    -- Índices
    CONSTRAINT uk_reportes_dian_periodo_prefijo_folio UNIQUE (periodo, prefijo, folio)
);

-- Índices para mejor performance
CREATE INDEX IF NOT EXISTS idx_reportes_dian_periodo ON reportes_dian(periodo);
CREATE INDEX IF NOT EXISTS idx_reportes_dian_nit ON reportes_dian(nit_tercero);
CREATE INDEX IF NOT EXISTS idx_reportes_dian_fecha_factura ON reportes_dian(fecha_factura);
CREATE INDEX IF NOT EXISTS idx_reportes_dian_valor ON reportes_dian(valor_factura);

-- Tabla para almacenar facturas desde el ERP interno
CREATE TABLE IF NOT EXISTS facturas_erp (
    id SERIAL PRIMARY KEY,
    periodo VARCHAR(7) NOT NULL,                 -- Formato YYYY-MM (2025-11)
    nit_tercero VARCHAR(20),                     -- NIT del tercero
    nombre_tercero VARCHAR(255),                 -- Nombre/razón social
    prefijo VARCHAR(10),                         -- Prefijo de la factura
    folio VARCHAR(20) NOT NULL,                  -- Número de folio
    fecha_factura DATE,                          -- Fecha de la factura
    valor_factura DECIMAL(15,2),                 -- Valor total de la factura
    datos_adicionales JSONB,                     -- Datos adicionales del ERP
    archivo_origen VARCHAR(255),                 -- Nombre del archivo origen
    fecha_carga TIMESTAMP DEFAULT NOW(),        -- Fecha de carga del registro
    usuario_carga VARCHAR(100),                 -- Usuario que cargó el registro
    activo BOOLEAN DEFAULT TRUE,                 -- Si el registro está activo
    
    -- Índices
    CONSTRAINT uk_facturas_erp_periodo_prefijo_folio UNIQUE (periodo, prefijo, folio)
);

-- Índices para mejor performance
CREATE INDEX IF NOT EXISTS idx_facturas_erp_periodo ON facturas_erp(periodo);
CREATE INDEX IF NOT EXISTS idx_facturas_erp_nit ON facturas_erp(nit_tercero);
CREATE INDEX IF NOT EXISTS idx_facturas_erp_fecha_factura ON facturas_erp(fecha_factura);
CREATE INDEX IF NOT EXISTS idx_facturas_erp_valor ON facturas_erp(valor_factura);

-- Tabla para almacenar los resultados de validaciones
CREATE TABLE IF NOT EXISTS validaciones_facturas (
    id SERIAL PRIMARY KEY,
    periodo VARCHAR(7) NOT NULL,                 -- Periodo de la validación
    
    -- Referencias a las tablas origen (pueden ser NULL si solo existe en uno)
    reporte_dian_id INTEGER REFERENCES reportes_dian(id) ON DELETE SET NULL,
    factura_erp_id INTEGER REFERENCES facturas_erp(id) ON DELETE SET NULL,
    
    -- Datos consolidados de la factura
    nit_tercero VARCHAR(20),
    nombre_tercero VARCHAR(255),
    prefijo VARCHAR(10),
    folio VARCHAR(20) NOT NULL,
    fecha_factura DATE,
    valor_factura DECIMAL(15,2),
    
    -- Resultado de la validación
    tipo_validacion VARCHAR(20) NOT NULL,       -- 'coincidente', 'discrepante', 'solo_dian', 'solo_erp'
    coincide BOOLEAN DEFAULT FALSE,             -- TRUE si los valores coinciden
    
    -- Detalles de discrepancias
    discrepancias JSONB,                        -- Array de discrepancias encontradas
    datos_dian JSONB,                           -- Datos de la factura en DIAN
    datos_erp JSONB,                            -- Datos de la factura en ERP
    
    -- Auditoría
    fecha_validacion TIMESTAMP DEFAULT NOW(),   -- Cuándo se hizo la validación
    usuario_validacion VARCHAR(100),           -- Quién ejecutó la validación
    observaciones TEXT,                         -- Observaciones adicionales
    
    -- Índice único por periodo y factura
    CONSTRAINT uk_validaciones_periodo_prefijo_folio UNIQUE (periodo, prefijo, folio)
);

-- Índices para mejor performance
CREATE INDEX IF NOT EXISTS idx_validaciones_periodo ON validaciones_facturas(periodo);
CREATE INDEX IF NOT EXISTS idx_validaciones_tipo ON validaciones_facturas(tipo_validacion);
CREATE INDEX IF NOT EXISTS idx_validaciones_nit ON validaciones_facturas(nit_tercero);
CREATE INDEX IF NOT EXISTS idx_validaciones_coincide ON validaciones_facturas(coincide);
CREATE INDEX IF NOT EXISTS idx_validaciones_fecha ON validaciones_facturas(fecha_validacion);

-- Tabla para controlar el procesamiento de periodos
CREATE TABLE IF NOT EXISTS procesamientos_periodo (
    id SERIAL PRIMARY KEY,
    periodo VARCHAR(7) NOT NULL UNIQUE,         -- Periodo procesado (YYYY-MM)
    
    -- Estadísticas del procesamiento
    total_dian INTEGER DEFAULT 0,               -- Total de facturas en DIAN
    total_erp INTEGER DEFAULT 0,                -- Total de facturas en ERP
    total_coincidentes INTEGER DEFAULT 0,       -- Total de coincidencias
    total_discrepantes INTEGER DEFAULT 0,       -- Total de discrepancias
    total_solo_dian INTEGER DEFAULT 0,          -- Solo en DIAN
    total_solo_erp INTEGER DEFAULT 0,           -- Solo en ERP
    
    -- Control de estado
    estado_procesamiento VARCHAR(20) DEFAULT 'iniciado',  -- 'iniciado', 'validando', 'completado', 'error'
    
    -- Auditoría
    fecha_inicio TIMESTAMP DEFAULT NOW(),       -- Cuándo se inició el procesamiento
    fecha_finalizacion TIMESTAMP,              -- Cuándo se finalizó
    usuario_procesamiento VARCHAR(100),        -- Usuario que ejecutó el procesamiento
    observaciones TEXT,                         -- Observaciones del procesamiento
    
    -- Detalles técnicos
    tiempo_procesamiento INTEGER,              -- Segundos que tomó el procesamiento
    archivos_procesados JSONB                  -- Lista de archivos procesados
);

-- Índices para mejor performance
CREATE INDEX IF NOT EXISTS idx_procesamientos_periodo ON procesamientos_periodo(periodo);
CREATE INDEX IF NOT EXISTS idx_procesamientos_estado ON procesamientos_periodo(estado_procesamiento);
CREATE INDEX IF NOT EXISTS idx_procesamientos_fecha ON procesamientos_periodo(fecha_inicio);

-- Tabla de configuración para el módulo
CREATE TABLE IF NOT EXISTS configuracion_validacion (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(100) NOT NULL UNIQUE,        -- Clave de configuración
    valor TEXT,                                 -- Valor de configuración
    descripcion TEXT,                           -- Descripción de la configuración
    tipo VARCHAR(20) DEFAULT 'string',         -- Tipo: string, number, boolean, json
    categoria VARCHAR(50) DEFAULT 'general',   -- Categoría de configuración
    activo BOOLEAN DEFAULT TRUE,               -- Si está activa
    fecha_actualizacion TIMESTAMP DEFAULT NOW(), -- Última actualización
    usuario_actualizacion VARCHAR(100)         -- Usuario que actualizó
);

-- Configuraciones por defecto
INSERT INTO configuracion_validacion (clave, valor, descripcion, tipo, categoria) 
VALUES 
    ('tolerancia_valor', '0.01', 'Tolerancia permitida en diferencias de valor (decimal)', 'number', 'validacion'),
    ('tolerancia_fecha', '1', 'Tolerancia permitida en diferencias de fecha (días)', 'number', 'validacion'),
    ('email_notificaciones', 'true', 'Activar notificaciones por email', 'boolean', 'notificaciones'),
    ('email_destinatarios', '', 'Lista de emails para notificaciones (separados por coma)', 'string', 'notificaciones'),
    ('auto_procesamiento', 'false', 'Activar procesamiento automático al cargar archivos', 'boolean', 'automatizacion'),
    ('retener_archivos_dias', '30', 'Días para retener archivos históricos', 'number', 'limpieza'),
    ('columnas_dian', '["nit", "nombre", "prefijo", "folio", "fecha", "valor"]', 'Columnas esperadas en archivos DIAN', 'json', 'mapeo'),
    ('columnas_erp', '["nit", "nombre", "prefijo", "folio", "fecha", "valor"]', 'Columnas esperadas en archivos ERP', 'json', 'mapeo')
ON CONFLICT (clave) DO NOTHING;

-- Comentarios en las tablas
COMMENT ON TABLE reportes_dian IS 'Almacena facturas reportadas ante la DIAN';
COMMENT ON TABLE facturas_erp IS 'Almacena facturas del sistema ERP interno';
COMMENT ON TABLE validaciones_facturas IS 'Resultados de validaciones DIAN vs ERP';
COMMENT ON TABLE procesamientos_periodo IS 'Control y estadísticas de procesamientos por periodo';
COMMENT ON TABLE configuracion_validacion IS 'Configuración del módulo de validación';

-- Crear vista para estadísticas generales
CREATE OR REPLACE VIEW v_estadisticas_validacion AS
SELECT 
    COUNT(DISTINCT periodo) as total_periodos,
    COUNT(*) as total_validaciones,
    SUM(CASE WHEN tipo_validacion = 'coincidente' THEN 1 ELSE 0 END) as total_coincidentes,
    SUM(CASE WHEN tipo_validacion = 'discrepante' THEN 1 ELSE 0 END) as total_discrepantes,
    SUM(CASE WHEN tipo_validacion = 'solo_dian' THEN 1 ELSE 0 END) as total_solo_dian,
    SUM(CASE WHEN tipo_validacion = 'solo_erp' THEN 1 ELSE 0 END) as total_solo_erp,
    ROUND(
        SUM(CASE WHEN tipo_validacion = 'coincidente' THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(COUNT(*), 0), 2
    ) as porcentaje_coincidencia
FROM validaciones_facturas;

COMMENT ON VIEW v_estadisticas_validacion IS 'Vista con estadísticas generales de validaciones';

-- ================================================
-- FIN DEL SCRIPT
-- ================================================

-- Verificar creación de tablas
DO $$
BEGIN
    RAISE NOTICE 'Módulo DIAN vs ERP - Tablas creadas exitosamente:';
    RAISE NOTICE '✓ reportes_dian';
    RAISE NOTICE '✓ facturas_erp';
    RAISE NOTICE '✓ validaciones_facturas';
    RAISE NOTICE '✓ procesamientos_periodo';
    RAISE NOTICE '✓ configuracion_validacion';
    RAISE NOTICE '✓ v_estadisticas_validacion (vista)';
    RAISE NOTICE '';
    RAISE NOTICE 'El módulo está listo para usar desde /dian_vs_erp/';
END
$$;