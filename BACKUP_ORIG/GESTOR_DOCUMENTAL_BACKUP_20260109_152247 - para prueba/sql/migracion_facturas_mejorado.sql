-- ========================================
-- MIGRACIÓN: Módulo Recibir Facturas Mejorado
-- Fecha: 18 de Octubre 2025
-- Descripción: Agrega campos requeridos para la nueva interfaz
-- ========================================

-- 1. CREAR TABLA CENTROS DE OPERACIÓN
-- ========================================
CREATE TABLE IF NOT EXISTS centros_operacion (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar centros de operación por defecto
INSERT INTO centros_operacion (codigo, nombre, descripcion) VALUES
('01', 'PRINCIPAL', 'Centro de operación principal'),
('02', 'ALMACÉN CENTRAL', 'Almacén y bodega central'),
('03', 'PUNTO VENTA 1', 'Punto de venta 1'),
('04', 'PUNTO VENTA 2', 'Punto de venta 2'),
('05', 'ADMINISTRATIVO', 'Área administrativa')
ON CONFLICT (codigo) DO NOTHING;

-- 2. MODIFICAR TABLA FACTURAS
-- ========================================

-- Agregar columnas nuevas si no existen
DO $$ 
BEGIN
    -- Prefijo del número de factura
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='facturas' AND column_name='prefijo') THEN
        ALTER TABLE facturas ADD COLUMN prefijo VARCHAR(10);
    END IF;

    -- Folio del número de factura
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='facturas' AND column_name='folio') THEN
        ALTER TABLE facturas ADD COLUMN folio VARCHAR(50);
    END IF;

    -- Comprador
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='facturas' AND column_name='comprador') THEN
        ALTER TABLE facturas ADD COLUMN comprador VARCHAR(200);
    END IF;

    -- Usuario que solicita
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='facturas' AND column_name='usuario_solicita') THEN
        ALTER TABLE facturas ADD COLUMN usuario_solicita VARCHAR(200);
    END IF;

    -- Quien recibe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='facturas' AND column_name='quien_recibe') THEN
        ALTER TABLE facturas ADD COLUMN quien_recibe VARCHAR(200);
    END IF;

    -- Centro de operación (FK)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='facturas' AND column_name='centro_operacion_id') THEN
        ALTER TABLE facturas ADD COLUMN centro_operacion_id INTEGER;
    END IF;

    -- Fecha de radicación
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='facturas' AND column_name='fecha_radicacion') THEN
        ALTER TABLE facturas ADD COLUMN fecha_radicacion DATE DEFAULT CURRENT_DATE;
    END IF;

    -- Nombre del usuario que registró
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='facturas' AND column_name='usuario_nombre') THEN
        ALTER TABLE facturas ADD COLUMN usuario_nombre VARCHAR(200);
    END IF;

    -- Nombre del centro de operación (desnormalizado para consultas rápidas)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='facturas' AND column_name='centro_operacion') THEN
        ALTER TABLE facturas ADD COLUMN centro_operacion VARCHAR(200);
    END IF;
END $$;

-- Hacer fecha_vencimiento opcional (nullable)
ALTER TABLE facturas ALTER COLUMN fecha_vencimiento DROP NOT NULL;

-- Agregar foreign key a centros_operacion
ALTER TABLE facturas 
DROP CONSTRAINT IF EXISTS fk_facturas_centro_operacion;

ALTER TABLE facturas 
ADD CONSTRAINT fk_facturas_centro_operacion 
FOREIGN KEY (centro_operacion_id) 
REFERENCES centros_operacion(id) 
ON DELETE SET NULL;

-- 3. MIGRAR DATOS EXISTENTES
-- ========================================

-- Dividir numero_factura en prefijo y folio para registros existentes
UPDATE facturas 
SET prefijo = CASE 
    WHEN numero_factura LIKE '%-%' THEN SPLIT_PART(numero_factura, '-', 1)
    ELSE NULL
END,
folio = CASE 
    WHEN numero_factura LIKE '%-%' THEN SPLIT_PART(numero_factura, '-', 2)
    ELSE numero_factura
END
WHERE prefijo IS NULL AND folio IS NULL;

-- Asignar centro de operación por defecto a registros sin C.O.
UPDATE facturas 
SET centro_operacion_id = 1,
    centro_operacion = 'PRINCIPAL'
WHERE centro_operacion_id IS NULL;

-- Asignar fecha de radicación por defecto si no existe
UPDATE facturas 
SET fecha_radicacion = fecha_registro
WHERE fecha_radicacion IS NULL;

-- 4. CREAR VISTA OPTIMIZADA PARA CONSULTAS
-- ========================================

CREATE OR REPLACE VIEW vista_facturas_completa AS
SELECT 
    f.id,
    f.numero_factura,
    f.prefijo,
    f.folio,
    f.nit,
    f.razon_social,
    f.tercero_id,
    t.razon_social AS tercero_razon_social,
    f.fecha_factura,
    f.fecha_vencimiento,
    f.fecha_radicacion,
    f.fecha_registro,
    f.valor_bruto,
    f.valor_iva,
    f.valor_neto,
    f.estado,
    f.observaciones,
    f.comprador,
    f.usuario_solicita,
    f.quien_recibe,
    f.centro_operacion_id,
    co.codigo AS centro_operacion_codigo,
    co.nombre AS centro_operacion_nombre,
    f.centro_operacion,
    f.usuario_registro_id,
    f.usuario_nombre,
    u.usuario AS usuario_registro_usuario,
    -- Cálculos útiles
    CASE 
        WHEN f.fecha_vencimiento IS NULL THEN NULL
        WHEN f.fecha_vencimiento < CURRENT_DATE THEN 'vencida'
        WHEN f.fecha_vencimiento <= CURRENT_DATE + INTERVAL '7 days' THEN 'proxima'
        ELSE 'vigente'
    END AS estado_vencimiento,
    CASE 
        WHEN f.fecha_vencimiento IS NULL THEN NULL
        ELSE f.fecha_vencimiento - CURRENT_DATE
    END AS dias_para_vencimiento
FROM facturas f
LEFT JOIN terceros t ON f.tercero_id = t.id
LEFT JOIN centros_operacion co ON f.centro_operacion_id = co.id
LEFT JOIN usuarios u ON f.usuario_registro_id = u.id;

-- 5. CREAR ÍNDICES PARA OPTIMIZACIÓN
-- ========================================

CREATE INDEX IF NOT EXISTS idx_facturas_centro_operacion 
ON facturas(centro_operacion_id);

CREATE INDEX IF NOT EXISTS idx_facturas_fecha_radicacion 
ON facturas(fecha_radicacion);

CREATE INDEX IF NOT EXISTS idx_facturas_prefijo_folio 
ON facturas(prefijo, folio);

CREATE INDEX IF NOT EXISTS idx_facturas_estado_vencimiento 
ON facturas(estado, fecha_vencimiento);

CREATE INDEX IF NOT EXISTS idx_facturas_comprador 
ON facturas(comprador) WHERE comprador IS NOT NULL;

-- 6. TRIGGER PARA SINCRONIZAR CENTRO_OPERACION (DESNORMALIZACIÓN)
-- ========================================

CREATE OR REPLACE FUNCTION sync_centro_operacion()
RETURNS TRIGGER AS $$
BEGIN
    -- Actualizar nombre del centro de operación desde la tabla relacionada
    IF NEW.centro_operacion_id IS NOT NULL THEN
        SELECT codigo || ' - ' || nombre INTO NEW.centro_operacion
        FROM centros_operacion
        WHERE id = NEW.centro_operacion_id;
    ELSE
        NEW.centro_operacion := NULL;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sync_centro_operacion ON facturas;

CREATE TRIGGER trg_sync_centro_operacion
BEFORE INSERT OR UPDATE OF centro_operacion_id ON facturas
FOR EACH ROW
EXECUTE FUNCTION sync_centro_operacion();

-- 7. FUNCIÓN PARA OBTENER ESTADÍSTICAS
-- ========================================

CREATE OR REPLACE FUNCTION obtener_estadisticas_facturas()
RETURNS TABLE (
    pendientes BIGINT,
    proximas_vencer BIGINT,
    vencidas BIGINT,
    monto_pendiente NUMERIC(15,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) FILTER (WHERE estado IN ('pendiente', 'recibida')) AS pendientes,
        COUNT(*) FILTER (
            WHERE fecha_vencimiento IS NOT NULL 
            AND fecha_vencimiento > CURRENT_DATE 
            AND fecha_vencimiento <= CURRENT_DATE + INTERVAL '7 days'
        ) AS proximas_vencer,
        COUNT(*) FILTER (
            WHERE fecha_vencimiento IS NOT NULL 
            AND fecha_vencimiento < CURRENT_DATE
            AND estado NOT IN ('pagada', 'rechazada')
        ) AS vencidas,
        COALESCE(SUM(valor_neto) FILTER (WHERE estado IN ('pendiente', 'recibida', 'aprobada')), 0) AS monto_pendiente
    FROM facturas;
END;
$$ LANGUAGE plpgsql;

-- 8. PERMISOS
-- ========================================

-- Dar permisos al usuario gestor_user
GRANT ALL PRIVILEGES ON centros_operacion TO gestor_user;
GRANT USAGE, SELECT ON SEQUENCE centros_operacion_id_seq TO gestor_user;
GRANT SELECT ON vista_facturas_completa TO gestor_user;

-- 9. VERIFICACIÓN
-- ========================================

-- Verificar que las columnas se crearon correctamente
DO $$ 
BEGIN
    RAISE NOTICE 'Verificando columnas creadas...';
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='facturas' AND column_name='prefijo') THEN
        RAISE NOTICE '✓ Columna prefijo creada';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='facturas' AND column_name='folio') THEN
        RAISE NOTICE '✓ Columna folio creada';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='facturas' AND column_name='comprador') THEN
        RAISE NOTICE '✓ Columna comprador creada';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='facturas' AND column_name='usuario_solicita') THEN
        RAISE NOTICE '✓ Columna usuario_solicita creada';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='facturas' AND column_name='quien_recibe') THEN
        RAISE NOTICE '✓ Columna quien_recibe creada';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='facturas' AND column_name='centro_operacion_id') THEN
        RAISE NOTICE '✓ Columna centro_operacion_id creada';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='facturas' AND column_name='fecha_radicacion') THEN
        RAISE NOTICE '✓ Columna fecha_radicacion creada';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='centros_operacion') THEN
        RAISE NOTICE '✓ Tabla centros_operacion creada';
    END IF;
    
    RAISE NOTICE 'Migración completada exitosamente!';
END $$;

-- Mostrar resumen de centros de operación
SELECT '=== CENTROS DE OPERACIÓN ===' AS info;
SELECT id, codigo, nombre, activo FROM centros_operacion ORDER BY id;

-- Mostrar estadísticas
SELECT '=== ESTADÍSTICAS ===' AS info;
SELECT * FROM obtener_estadisticas_facturas();
