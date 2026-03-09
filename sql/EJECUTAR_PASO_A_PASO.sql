-- ========================================
-- EJECUCIÓN PASO A PASO: Recibir Facturas Mejorado
-- Copiar y pegar cada bloque en pgAdmin o DBeaver
-- Fecha: 18 de Octubre 2025
-- ========================================

-- ============================================================
-- PASO 1: CREAR TABLA CENTROS DE OPERACIÓN
-- ============================================================
CREATE TABLE IF NOT EXISTS centros_operacion (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- PASO 2: INSERTAR DATOS POR DEFECTO
-- ============================================================
INSERT INTO centros_operacion (codigo, nombre, descripcion) VALUES
('01', 'PRINCIPAL', 'Centro de operación principal'),
('02', 'ALMACÉN CENTRAL', 'Almacén y bodega central'),
('03', 'PUNTO VENTA 1', 'Punto de venta 1'),
('04', 'PUNTO VENTA 2', 'Punto de venta 2'),
('05', 'ADMINISTRATIVO', 'Área administrativa')
ON CONFLICT (codigo) DO NOTHING;

-- ============================================================
-- PASO 3: AGREGAR COLUMNAS A FACTURAS (UNA POR UNA)
-- ============================================================
ALTER TABLE facturas ADD COLUMN IF NOT EXISTS prefijo VARCHAR(10);
ALTER TABLE facturas ADD COLUMN IF NOT EXISTS folio VARCHAR(50);
ALTER TABLE facturas ADD COLUMN IF NOT EXISTS comprador VARCHAR(200);
ALTER TABLE facturas ADD COLUMN IF NOT EXISTS usuario_solicita VARCHAR(200);
ALTER TABLE facturas ADD COLUMN IF NOT EXISTS quien_recibe VARCHAR(200);
ALTER TABLE facturas ADD COLUMN IF NOT EXISTS centro_operacion_id INTEGER;
ALTER TABLE facturas ADD COLUMN IF NOT EXISTS fecha_radicacion DATE DEFAULT CURRENT_DATE;
ALTER TABLE facturas ADD COLUMN IF NOT EXISTS usuario_nombre VARCHAR(200);
ALTER TABLE facturas ADD COLUMN IF NOT EXISTS centro_operacion VARCHAR(200);

-- ============================================================
-- PASO 4: HACER FECHA_VENCIMIENTO OPCIONAL
-- ============================================================
ALTER TABLE facturas ALTER COLUMN fecha_vencimiento DROP NOT NULL;

-- ============================================================
-- PASO 5: AGREGAR FOREIGN KEY
-- ============================================================
ALTER TABLE facturas DROP CONSTRAINT IF EXISTS fk_facturas_centro_operacion;

ALTER TABLE facturas 
ADD CONSTRAINT fk_facturas_centro_operacion 
FOREIGN KEY (centro_operacion_id) 
REFERENCES centros_operacion(id) 
ON DELETE SET NULL;

-- ============================================================
-- PASO 6: CREAR VISTA COMPLETA
-- ============================================================
CREATE OR REPLACE VIEW vista_facturas_completa AS
SELECT 
    f.id,
    f.numero_factura,
    f.prefijo,
    f.folio,
    f.nit,
    f.razon_social,
    f.tercero_id,
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
LEFT JOIN centros_operacion co ON f.centro_operacion_id = co.id;

-- ============================================================
-- PASO 7: CREAR FUNCIÓN DE ESTADÍSTICAS
-- ============================================================
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

-- ============================================================
-- PASO 8: CREAR TRIGGER PARA SINCRONIZAR C.O.
-- ============================================================
CREATE OR REPLACE FUNCTION sync_centro_operacion()
RETURNS TRIGGER AS $$
BEGIN
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

-- ============================================================
-- PASO 9: DAR PERMISOS
-- ============================================================
GRANT ALL PRIVILEGES ON centros_operacion TO gestor_user;
GRANT USAGE, SELECT ON SEQUENCE centros_operacion_id_seq TO gestor_user;
GRANT SELECT ON vista_facturas_completa TO gestor_user;

-- ============================================================
-- PASO 10: VERIFICACIÓN
-- ============================================================
SELECT 'VERIFICACIÓN: Centros de Operación' AS info;
SELECT id, codigo, nombre FROM centros_operacion ORDER BY id;

SELECT 'VERIFICACIÓN: Estadísticas' AS info;
SELECT * FROM obtener_estadisticas_facturas();

SELECT 'VERIFICACIÓN: Columnas de facturas' AS info;
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'facturas' 
AND column_name IN ('prefijo', 'folio', 'comprador', 'usuario_solicita', 'quien_recibe', 'centro_operacion_id', 'fecha_radicacion', 'usuario_nombre', 'centro_operacion')
ORDER BY column_name;
