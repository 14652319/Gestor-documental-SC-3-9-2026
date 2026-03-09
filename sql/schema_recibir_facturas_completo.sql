-- =====================================================
-- SISTEMA COMPLETO RECIBIR FACTURAS - POSTGRESQL
-- Autor: Sistema Gestor Documental
-- Fecha: 18 de Octubre 2025
-- Descripción: Schema completo para módulo Recibir Facturas
-- =====================================================

-- =====================================================
-- PASO 1: AGREGAR CAMPO estado_documentacion A terceros
-- =====================================================

-- Verificar si la columna ya existe antes de agregarla
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'terceros' 
        AND column_name = 'estado_documentacion'
    ) THEN
        ALTER TABLE terceros 
        ADD COLUMN estado_documentacion VARCHAR(20) DEFAULT 'actualizado';
        
        RAISE NOTICE '✅ Columna estado_documentacion agregada a terceros';
    ELSE
        RAISE NOTICE '⚠️ Columna estado_documentacion ya existe en terceros';
    END IF;
END $$;

-- Actualizar estados existentes basado en fecha_actualizacion
UPDATE terceros
SET estado_documentacion = CASE
    WHEN fecha_actualizacion IS NULL THEN 'actualizado'
    WHEN (CURRENT_DATE - fecha_actualizacion::date) >= 365 THEN 'desactualizado'
    ELSE 'actualizado'
END;

COMMENT ON COLUMN terceros.estado_documentacion IS 'Estado de documentación del tercero: actualizado (<1 año) o desactualizado (>=1 año)';

-- =====================================================
-- PASO 2: CREAR TABLA facturas_temporales
-- =====================================================

DROP TABLE IF EXISTS observaciones_factura_temporal CASCADE;
DROP TABLE IF EXISTS facturas_temporales CASCADE;

CREATE TABLE facturas_temporales (
    id SERIAL PRIMARY KEY,
    
    -- Clave única de factura
    nit VARCHAR(20) NOT NULL,
    prefijo VARCHAR(10) NOT NULL,
    folio VARCHAR(50) NOT NULL,
    
    -- Información del proveedor
    razon_social VARCHAR(200) NOT NULL,
    
    -- Información de fechas
    fecha_expedicion DATE,
    fecha_radicacion DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_vencimiento DATE,
    
    -- Valores monetarios
    valor_bruto DECIMAL(15,2) NOT NULL,
    descuento DECIMAL(15,2) DEFAULT 0,
    iva DECIMAL(15,2) DEFAULT 0,
    retencion_fuente DECIMAL(15,2) DEFAULT 0,
    rete_iva DECIMAL(15,2) DEFAULT 0,
    rete_ica DECIMAL(15,2) DEFAULT 0,
    valor_neto DECIMAL(15,2) NOT NULL,
    
    -- Centro de operación
    centro_operacion_id INTEGER REFERENCES centros_operacion(id),
    centro_operacion VARCHAR(200),
    
    -- Información adicional
    forma_pago VARCHAR(50) DEFAULT 'CREDITO', -- EFECTIVO, CREDITO
    plazo INTEGER DEFAULT 30, -- Días de plazo
    comprador VARCHAR(200),
    usuario_solicita VARCHAR(200),
    quien_recibe VARCHAR(200),
    
    -- Observaciones (última observación visible)
    observaciones TEXT,
    
    -- Auditoría
    usuario_nombre VARCHAR(200) NOT NULL,
    usuario_id INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP,
    
    -- Constraint de clave única (NIT + Prefijo + Folio)
    CONSTRAINT uk_factura_temporal UNIQUE (nit, prefijo, folio)
);

-- Índices para mejorar búsquedas
CREATE INDEX idx_temp_nit ON facturas_temporales(nit);
CREATE INDEX idx_temp_usuario ON facturas_temporales(usuario_id);
CREATE INDEX idx_temp_fecha_creacion ON facturas_temporales(fecha_creacion);

COMMENT ON TABLE facturas_temporales IS 'Facturas en proceso de captura antes de ser confirmadas';
COMMENT ON COLUMN facturas_temporales.folio IS 'Últimos 8 dígitos del número de factura sin ceros a la izquierda';
COMMENT ON COLUMN facturas_temporales.valor_neto IS 'Valor final: bruto - descuento + iva - retenciones';

-- =====================================================
-- PASO 3: CREAR TABLA facturas_recibidas
-- =====================================================

DROP TABLE IF EXISTS observaciones_factura CASCADE;
DROP TABLE IF EXISTS facturas_recibidas CASCADE;

CREATE TABLE facturas_recibidas (
    id SERIAL PRIMARY KEY,
    
    -- Clave única de factura
    nit VARCHAR(20) NOT NULL,
    prefijo VARCHAR(10) NOT NULL,
    folio VARCHAR(50) NOT NULL,
    numero_factura VARCHAR(100) GENERATED ALWAYS AS (prefijo || folio) STORED,
    
    -- Información del proveedor
    razon_social VARCHAR(200) NOT NULL,
    
    -- Información de fechas
    fecha_expedicion DATE,
    fecha_radicacion DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_vencimiento DATE,
    
    -- Valores monetarios
    valor_bruto DECIMAL(15,2) NOT NULL,
    descuento DECIMAL(15,2) DEFAULT 0,
    iva DECIMAL(15,2) DEFAULT 0,
    retencion_fuente DECIMAL(15,2) DEFAULT 0,
    rete_iva DECIMAL(15,2) DEFAULT 0,
    rete_ica DECIMAL(15,2) DEFAULT 0,
    valor_neto DECIMAL(15,2) NOT NULL,
    
    -- Centro de operación
    centro_operacion_id INTEGER REFERENCES centros_operacion(id),
    centro_operacion VARCHAR(200),
    
    -- Información adicional
    forma_pago VARCHAR(50) DEFAULT 'CREDITO',
    plazo INTEGER DEFAULT 30,
    comprador VARCHAR(200),
    usuario_solicita VARCHAR(200),
    quien_recibe VARCHAR(200),
    
    -- Estado de la factura
    estado VARCHAR(30) DEFAULT 'RECIBIDA', -- RECIBIDA, VALIDADA, RECHAZADA, PAGADA
    
    -- Observaciones (última observación visible)
    observaciones TEXT,
    
    -- Auditoría
    usuario_nombre VARCHAR(200) NOT NULL,
    usuario_id INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP,
    fecha_guardado TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Cuándo se guardó desde temporal
    
    -- Constraint de clave única (NIT + Prefijo + Folio)
    CONSTRAINT uk_factura_recibida UNIQUE (nit, prefijo, folio)
);

-- Índices para mejorar búsquedas y reportes
CREATE INDEX idx_recib_nit ON facturas_recibidas(nit);
CREATE INDEX idx_recib_estado ON facturas_recibidas(estado);
CREATE INDEX idx_recib_fecha_radicacion ON facturas_recibidas(fecha_radicacion);
CREATE INDEX idx_recib_fecha_vencimiento ON facturas_recibidas(fecha_vencimiento);
CREATE INDEX idx_recib_co ON facturas_recibidas(centro_operacion_id);
CREATE INDEX idx_recib_usuario ON facturas_recibidas(usuario_id);

COMMENT ON TABLE facturas_recibidas IS 'Facturas confirmadas y guardadas definitivamente';
COMMENT ON COLUMN facturas_recibidas.numero_factura IS 'Número completo de factura (generado automáticamente)';
COMMENT ON COLUMN facturas_recibidas.fecha_guardado IS 'Fecha y hora en que se guardó desde temporales';

-- =====================================================
-- PASO 4: CREAR TABLA observaciones_factura
-- =====================================================

CREATE TABLE observaciones_factura (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL REFERENCES facturas_recibidas(id) ON DELETE CASCADE,
    
    observacion TEXT NOT NULL,
    
    -- Auditoría
    usuario_nombre VARCHAR(200) NOT NULL,
    usuario_id INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ordenar por más reciente primero
    CONSTRAINT observaciones_order CHECK (fecha_creacion IS NOT NULL)
);

CREATE INDEX idx_obs_factura ON observaciones_factura(factura_id);
CREATE INDEX idx_obs_fecha ON observaciones_factura(fecha_creacion DESC);

COMMENT ON TABLE observaciones_factura IS 'Historial completo de observaciones por factura';
COMMENT ON COLUMN observaciones_factura.observacion IS 'Hasta 5000 caracteres por observación';

-- =====================================================
-- PASO 5: CREAR TABLA observaciones_factura_temporal
-- =====================================================

CREATE TABLE observaciones_factura_temporal (
    id SERIAL PRIMARY KEY,
    factura_temporal_id INTEGER NOT NULL REFERENCES facturas_temporales(id) ON DELETE CASCADE,
    
    observacion TEXT NOT NULL,
    
    -- Auditoría
    usuario_nombre VARCHAR(200) NOT NULL,
    usuario_id INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_obs_temp_factura ON observaciones_factura_temporal(factura_temporal_id);
CREATE INDEX idx_obs_temp_fecha ON observaciones_factura_temporal(fecha_creacion DESC);

COMMENT ON TABLE observaciones_factura_temporal IS 'Observaciones de facturas temporales';

-- =====================================================
-- PASO 6: FUNCIÓN PARA ACTUALIZAR estado_documentacion
-- =====================================================

CREATE OR REPLACE FUNCTION actualizar_estado_documentacion_terceros()
RETURNS void AS $$
BEGIN
    UPDATE terceros
    SET estado_documentacion = CASE
        WHEN fecha_actualizacion IS NULL THEN 'actualizado'
        WHEN (CURRENT_DATE - fecha_actualizacion::date) >= 365 THEN 'desactualizado'
        ELSE 'actualizado'
    END;
    
    RAISE NOTICE '✅ Estados de documentación actualizados';
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION actualizar_estado_documentacion_terceros() IS 'Actualiza estado_documentacion basado en fecha_actualizacion (>= 1 año = desactualizado)';

-- =====================================================
-- PASO 7: FUNCIÓN PARA CALCULAR DÍAS HASTA VENCIMIENTO
-- =====================================================

CREATE OR REPLACE FUNCTION calcular_dias_vencimiento(fecha_venc DATE)
RETURNS INTEGER AS $$
BEGIN
    IF fecha_venc IS NULL THEN
        RETURN NULL;
    END IF;
    
    RETURN fecha_venc - CURRENT_DATE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calcular_dias_vencimiento(DATE) IS 'Calcula días restantes hasta vencimiento (positivo = futuro, negativo = vencida)';

-- =====================================================
-- PASO 8: VISTA COMPLETA DE FACTURAS RECIBIDAS
-- =====================================================

CREATE OR REPLACE VIEW vista_facturas_recibidas_completa AS
SELECT 
    fr.id,
    fr.nit,
    fr.prefijo,
    fr.folio,
    fr.numero_factura,
    fr.razon_social,
    fr.fecha_expedicion,
    fr.fecha_radicacion,
    fr.fecha_vencimiento,
    calcular_dias_vencimiento(fr.fecha_vencimiento) as dias_vencimiento,
    CASE
        WHEN fr.fecha_vencimiento IS NULL THEN 'SIN_VENCIMIENTO'
        WHEN calcular_dias_vencimiento(fr.fecha_vencimiento) < 0 THEN 'VENCIDA'
        WHEN calcular_dias_vencimiento(fr.fecha_vencimiento) <= 7 THEN 'PROXIMA_VENCER'
        ELSE 'VIGENTE'
    END as estado_vencimiento,
    fr.valor_bruto,
    fr.descuento,
    fr.iva,
    fr.retencion_fuente,
    fr.rete_iva,
    fr.rete_ica,
    fr.valor_neto,
    fr.centro_operacion_id,
    co.codigo as centro_operacion_codigo,
    co.nombre as centro_operacion_nombre,
    fr.forma_pago,
    fr.plazo,
    fr.comprador,
    fr.usuario_solicita,
    fr.quien_recibe,
    fr.estado,
    fr.observaciones,
    fr.usuario_nombre,
    fr.usuario_id,
    fr.fecha_creacion,
    fr.fecha_modificacion,
    fr.fecha_guardado,
    -- Estado del tercero
    t.estado_documentacion as tercero_estado_doc,
    t.fecha_actualizacion as tercero_fecha_actualizacion,
    -- Contar observaciones
    (SELECT COUNT(*) FROM observaciones_factura WHERE factura_id = fr.id) as total_observaciones
FROM facturas_recibidas fr
LEFT JOIN centros_operacion co ON fr.centro_operacion_id = co.id
LEFT JOIN terceros t ON fr.nit = t.nit
ORDER BY fr.fecha_creacion DESC;

COMMENT ON VIEW vista_facturas_recibidas_completa IS 'Vista completa con cálculos de vencimiento y estado del tercero';

-- =====================================================
-- PASO 9: FUNCIÓN PARA OBTENER ESTADÍSTICAS (KPIs)
-- =====================================================

CREATE OR REPLACE FUNCTION obtener_kpis_facturas()
RETURNS TABLE(
    total_recibidas BIGINT,
    total_pendientes BIGINT,
    total_proximas_vencer BIGINT,
    total_vencidas BIGINT,
    monto_total_pendiente NUMERIC,
    monto_vencido NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_recibidas,
        COUNT(*) FILTER (WHERE estado = 'RECIBIDA') as total_pendientes,
        COUNT(*) FILTER (WHERE fecha_vencimiento IS NOT NULL 
                         AND calcular_dias_vencimiento(fecha_vencimiento) BETWEEN 0 AND 7) as total_proximas_vencer,
        COUNT(*) FILTER (WHERE fecha_vencimiento IS NOT NULL 
                         AND calcular_dias_vencimiento(fecha_vencimiento) < 0) as total_vencidas,
        COALESCE(SUM(valor_neto) FILTER (WHERE estado IN ('RECIBIDA', 'VALIDADA')), 0) as monto_total_pendiente,
        COALESCE(SUM(valor_neto) FILTER (WHERE fecha_vencimiento IS NOT NULL 
                                          AND calcular_dias_vencimiento(fecha_vencimiento) < 0), 0) as monto_vencido
    FROM facturas_recibidas;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION obtener_kpis_facturas() IS 'Obtiene métricas clave para el dashboard';

-- =====================================================
-- PASO 10: FUNCIÓN PARA VALIDAR CLAVE ÚNICA DE FACTURA
-- =====================================================

CREATE OR REPLACE FUNCTION validar_clave_factura(
    p_nit VARCHAR(20),
    p_prefijo VARCHAR(10),
    p_folio VARCHAR(50)
)
RETURNS TABLE(
    existe BOOLEAN,
    en_temporal BOOLEAN,
    en_recibidas BOOLEAN,
    fecha_registro TIMESTAMP,
    mensaje TEXT
) AS $$
DECLARE
    v_existe_temp BOOLEAN := FALSE;
    v_existe_recib BOOLEAN := FALSE;
    v_fecha TIMESTAMP;
    v_mensaje TEXT := '';
BEGIN
    -- Buscar en temporales
    SELECT EXISTS(
        SELECT 1 FROM facturas_temporales 
        WHERE nit = p_nit 
        AND prefijo = p_prefijo 
        AND folio = p_folio
    ) INTO v_existe_temp;
    
    -- Buscar en recibidas
    SELECT fecha_guardado INTO v_fecha
    FROM facturas_recibidas 
    WHERE nit = p_nit 
    AND prefijo = p_prefijo 
    AND folio = p_folio;
    
    v_existe_recib := FOUND;
    
    -- Construir mensaje
    IF v_existe_recib THEN
        v_mensaje := 'La factura ya fue registrada el ' || TO_CHAR(v_fecha, 'DD/MM/YYYY a las HH24:MI');
    ELSIF v_existe_temp THEN
        v_mensaje := 'La factura ya existe en el listado temporal';
    ELSE
        v_mensaje := 'Factura disponible para registrar';
    END IF;
    
    RETURN QUERY SELECT 
        (v_existe_temp OR v_existe_recib),
        v_existe_temp,
        v_existe_recib,
        v_fecha,
        v_mensaje;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION validar_clave_factura(VARCHAR, VARCHAR, VARCHAR) IS 'Valida si la clave NIT+Prefijo+Folio ya existe';

-- =====================================================
-- PASO 11: TRIGGER PARA ACTUALIZAR fecha_modificacion
-- =====================================================

CREATE OR REPLACE FUNCTION actualizar_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_modificacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar a facturas_temporales
DROP TRIGGER IF EXISTS trigger_actualizar_fecha_temp ON facturas_temporales;
CREATE TRIGGER trigger_actualizar_fecha_temp
    BEFORE UPDATE ON facturas_temporales
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- Aplicar a facturas_recibidas
DROP TRIGGER IF EXISTS trigger_actualizar_fecha_recib ON facturas_recibidas;
CREATE TRIGGER trigger_actualizar_fecha_recib
    BEFORE UPDATE ON facturas_recibidas
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- =====================================================
-- PASO 12: INSERTAR CENTROS DE OPERACIÓN (SI NO EXISTEN)
-- =====================================================

INSERT INTO centros_operacion (codigo, nombre, descripcion, activo)
VALUES 
    ('001', 'Administración', 'Centro de operación principal', TRUE),
    ('002', 'Compras', 'Centro de operación de compras', TRUE),
    ('003', 'Ventas', 'Centro de operación de ventas', TRUE),
    ('004', 'Logística', 'Centro de operación de logística', TRUE),
    ('005', 'Finanzas', 'Centro de operación de finanzas', TRUE)
ON CONFLICT (codigo) DO NOTHING;

-- =====================================================
-- VERIFICACIÓN FINAL
-- =====================================================

-- Verificar tablas creadas
SELECT 
    schemaname as esquema,
    tablename as tabla,
    'OK' as estado
FROM pg_tables 
WHERE tablename IN ('facturas_temporales', 'facturas_recibidas', 'observaciones_factura', 'observaciones_factura_temporal')
ORDER BY tablename;

-- Verificar columna en terceros
SELECT 
    column_name as columna,
    data_type as tipo,
    column_default as valor_defecto
FROM information_schema.columns
WHERE table_name = 'terceros'
AND column_name = 'estado_documentacion';

-- Verificar centros de operación
SELECT COUNT(*) as total_centros_operacion FROM centros_operacion;

-- Verificar funciones
SELECT 
    routine_name as funcion,
    'OK' as estado
FROM information_schema.routines
WHERE routine_name IN (
    'actualizar_estado_documentacion_terceros',
    'calcular_dias_vencimiento',
    'obtener_kpis_facturas',
    'validar_clave_factura'
)
ORDER BY routine_name;

-- =====================================================
-- INSTRUCCIONES FINALES
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ SCHEMA COMPLETADO EXITOSAMENTE';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Tablas creadas:';
    RAISE NOTICE '  ✓ facturas_temporales (para "Adicionar")';
    RAISE NOTICE '  ✓ facturas_recibidas (para "Guardar")';
    RAISE NOTICE '  ✓ observaciones_factura';
    RAISE NOTICE '  ✓ observaciones_factura_temporal';
    RAISE NOTICE '';
    RAISE NOTICE 'Funciones creadas:';
    RAISE NOTICE '  ✓ actualizar_estado_documentacion_terceros()';
    RAISE NOTICE '  ✓ calcular_dias_vencimiento()';
    RAISE NOTICE '  ✓ obtener_kpis_facturas()';
    RAISE NOTICE '  ✓ validar_clave_factura()';
    RAISE NOTICE '';
    RAISE NOTICE 'Próximo paso:';
    RAISE NOTICE '  → Ejecutar script de migración de CSV';
    RAISE NOTICE '  → Crear modelos SQLAlchemy';
    RAISE NOTICE '  → Crear backend Flask';
    RAISE NOTICE '  → Crear frontend completo';
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
END $$;
