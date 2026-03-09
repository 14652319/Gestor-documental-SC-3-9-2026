-- =====================================================
-- ACTUALIZACION FACTURAS DIGITALES - FASE 1
-- Agrega campos para workflow de firma y causacion
-- =====================================================

-- 1. Agregar campo DEPARTAMENTO
ALTER TABLE facturas_digitales 
ADD COLUMN IF NOT EXISTS departamento VARCHAR(50) NOT NULL DEFAULT 'FINANCIERO';

COMMENT ON COLUMN facturas_digitales.departamento IS 'Departamento que carga la factura: FINANCIERO, TECNOLOGIA, COMPRAS_Y_SUMINISTROS, MERCADEO, MVP_ESTRATEGICA, DOMICILIOS';

-- 2. Agregar campo FORMA_PAGO
ALTER TABLE facturas_digitales 
ADD COLUMN IF NOT EXISTS forma_pago VARCHAR(20) NOT NULL DEFAULT 'ESTANDAR';

COMMENT ON COLUMN facturas_digitales.forma_pago IS 'Forma de pago: ESTANDAR o TARJETA_CREDITO';

-- 3. Agregar campos para WORKFLOW DE FIRMA
ALTER TABLE facturas_digitales 
ADD COLUMN IF NOT EXISTS estado_firma VARCHAR(30) DEFAULT 'PENDIENTE_FIRMA';

COMMENT ON COLUMN facturas_digitales.estado_firma IS 'Estados: PENDIENTE_FIRMA, ENVIADO_FIRMA, FIRMADO, CAUSADO, PAGADO';

ALTER TABLE facturas_digitales 
ADD COLUMN IF NOT EXISTS fecha_envio_firma TIMESTAMP;

ALTER TABLE facturas_digitales 
ADD COLUMN IF NOT EXISTS usuario_envio_firma VARCHAR(100);

ALTER TABLE facturas_digitales 
ADD COLUMN IF NOT EXISTS fecha_firmado TIMESTAMP;

ALTER TABLE facturas_digitales 
ADD COLUMN IF NOT EXISTS usuario_carga_firmado VARCHAR(100);

-- 4. Agregar campo para documento FIRMADO
ALTER TABLE facturas_digitales 
ADD COLUMN IF NOT EXISTS archivo_firmado_path TEXT;

COMMENT ON COLUMN facturas_digitales.archivo_firmado_path IS 'Ruta del PDF firmado con Adobe Sign';

-- 5. Agregar campos de CAUSACION
ALTER TABLE facturas_digitales 
ADD COLUMN IF NOT EXISTS numero_causacion VARCHAR(50);

ALTER TABLE facturas_digitales 
ADD COLUMN IF NOT EXISTS fecha_causacion TIMESTAMP;

ALTER TABLE facturas_digitales 
ADD COLUMN IF NOT EXISTS usuario_causacion VARCHAR(100);

-- 6. Agregar campo de PAGO
ALTER TABLE facturas_digitales 
ADD COLUMN IF NOT EXISTS fecha_pago TIMESTAMP;

ALTER TABLE facturas_digitales 
ADD COLUMN IF NOT EXISTS usuario_pago VARCHAR(100);

-- 7. Crear INDICES para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_facturas_digitales_departamento ON facturas_digitales(departamento);
CREATE INDEX IF NOT EXISTS idx_facturas_digitales_forma_pago ON facturas_digitales(forma_pago);
CREATE INDEX IF NOT EXISTS idx_facturas_digitales_estado_firma ON facturas_digitales(estado_firma);
CREATE INDEX IF NOT EXISTS idx_facturas_digitales_fecha_envio_firma ON facturas_digitales(fecha_envio_firma);
CREATE INDEX IF NOT EXISTS idx_facturas_digitales_numero_causacion ON facturas_digitales(numero_causacion);

-- 8. Actualizar registros existentes con valores por defecto
UPDATE facturas_digitales 
SET departamento = 'FINANCIERO', 
    forma_pago = 'ESTANDAR',
    estado_firma = 'PENDIENTE_FIRMA'
WHERE departamento IS NULL OR forma_pago IS NULL OR estado_firma IS NULL;

-- 9. Mensaje de confirmacion
DO $$
BEGIN
    RAISE NOTICE '====================================';
    RAISE NOTICE 'ACTUALIZACION COMPLETADA';
    RAISE NOTICE '====================================';
    RAISE NOTICE 'Nuevos campos agregados:';
    RAISE NOTICE '  - departamento (FINANCIERO, TECNOLOGIA, etc)';
    RAISE NOTICE '  - forma_pago (ESTANDAR, TARJETA_CREDITO)';
    RAISE NOTICE '  - estado_firma (PENDIENTE_FIRMA, ENVIADO_FIRMA, FIRMADO, CAUSADO, PAGADO)';
    RAISE NOTICE '  - fecha_envio_firma, usuario_envio_firma';
    RAISE NOTICE '  - fecha_firmado, usuario_carga_firmado';
    RAISE NOTICE '  - archivo_firmado_path';
    RAISE NOTICE '  - numero_causacion, fecha_causacion, usuario_causacion';
    RAISE NOTICE '  - fecha_pago, usuario_pago';
    RAISE NOTICE '====================================';
END $$;
