-- ======================================================
-- 📦 MÓDULO: RECIBIR FACTURAS
-- Descripción: Sistema completo para recepción, validación y gestión de facturas
-- Fecha: Octubre 18, 2025
-- ======================================================

-- ======================================================
-- 📊 TABLA PRINCIPAL: FACTURAS
-- ======================================================
CREATE TABLE IF NOT EXISTS facturas (
    id SERIAL PRIMARY KEY,
    numero_factura VARCHAR(50) NOT NULL UNIQUE, -- Número de factura del proveedor
    tercero_id INTEGER REFERENCES terceros(id) ON DELETE CASCADE,
    nit VARCHAR(20) NOT NULL, -- NIT del proveedor
    razon_social VARCHAR(200) NOT NULL, -- Nombre del proveedor
    centro_operacion_id INTEGER, -- FK a centros_operacion (si existe)
    fecha_factura DATE NOT NULL, -- Fecha de emisión de la factura
    fecha_recepcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Fecha en que se registró en el sistema
    fecha_vencimiento DATE, -- Fecha de vencimiento de pago
    valor_bruto NUMERIC(15, 2) NOT NULL, -- Valor antes de impuestos
    valor_descuento NUMERIC(15, 2) DEFAULT 0, -- Descuentos aplicados
    valor_iva NUMERIC(15, 2) DEFAULT 0, -- Valor del IVA
    valor_retefuente NUMERIC(15, 2) DEFAULT 0, -- Retención en la fuente
    valor_reteiva NUMERIC(15, 2) DEFAULT 0, -- Retención de IVA
    valor_reteica NUMERIC(15, 2) DEFAULT 0, -- Retención de ICA
    valor_neto NUMERIC(15, 2) NOT NULL, -- Valor final a pagar
    forma_pago VARCHAR(50), -- Contado, Crédito, etc.
    plazo_pago INTEGER, -- Días de plazo si es crédito
    estado VARCHAR(30) DEFAULT 'RECIBIDA', -- RECIBIDA, VALIDADA, RECHAZADA, CONTABILIZADA, PAGADA
    observaciones TEXT, -- Notas adicionales
    archivo_pdf VARCHAR(500), -- Ruta del PDF de la factura
    archivo_xml VARCHAR(500), -- Ruta del XML de factura electrónica (opcional)
    usuario_registro_id INTEGER, -- Usuario que registró la factura
    usuario_validacion_id INTEGER, -- Usuario que validó/rechazó
    fecha_validacion TIMESTAMP, -- Fecha de validación/rechazo
    fecha_contabilizacion TIMESTAMP, -- Fecha en que se contabilizó
    fecha_pago TIMESTAMP, -- Fecha en que se pagó
    motivo_rechazo TEXT, -- Motivo si es rechazada
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ======================================================
-- 📝 TABLA: ITEMS DE FACTURA (Detalle de productos/servicios)
-- ======================================================
CREATE TABLE IF NOT EXISTS facturas_items (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER REFERENCES facturas(id) ON DELETE CASCADE,
    linea INTEGER NOT NULL, -- Número de línea en la factura
    codigo_producto VARCHAR(50), -- Código del producto/servicio
    descripcion TEXT NOT NULL, -- Descripción del ítem
    cantidad NUMERIC(15, 3) NOT NULL, -- Cantidad
    unidad_medida VARCHAR(20), -- Unidad (UND, KG, etc.)
    valor_unitario NUMERIC(15, 2) NOT NULL, -- Precio unitario
    porcentaje_descuento NUMERIC(5, 2) DEFAULT 0, -- % de descuento
    valor_descuento NUMERIC(15, 2) DEFAULT 0, -- Valor del descuento
    porcentaje_iva NUMERIC(5, 2) DEFAULT 0, -- % de IVA
    valor_iva NUMERIC(15, 2) DEFAULT 0, -- Valor del IVA
    valor_subtotal NUMERIC(15, 2) NOT NULL, -- Subtotal de la línea
    valor_total NUMERIC(15, 2) NOT NULL, -- Total de la línea con IVA
    centro_costo VARCHAR(50), -- Centro de costo para contabilidad
    cuenta_contable VARCHAR(20), -- Cuenta contable asociada
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ======================================================
-- 🔐 TABLA: HISTORIAL DE FACTURAS (Auditoría)
-- ======================================================
CREATE TABLE IF NOT EXISTS facturas_historial (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER REFERENCES facturas(id) ON DELETE CASCADE,
    accion VARCHAR(50) NOT NULL, -- CREADA, VALIDADA, RECHAZADA, MODIFICADA, CONTABILIZADA, PAGADA
    estado_anterior VARCHAR(30), -- Estado antes del cambio
    estado_nuevo VARCHAR(30), -- Estado después del cambio
    usuario_id INTEGER, -- Usuario que realizó la acción
    usuario_nombre VARCHAR(200), -- Nombre del usuario
    ip_address VARCHAR(45), -- IP desde donde se hizo el cambio
    user_agent TEXT, -- Navegador/SO del usuario
    observaciones TEXT, -- Detalle de la acción
    valores_modificados JSONB, -- JSON con campos modificados
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ======================================================
-- 📎 TABLA: DOCUMENTOS ADJUNTOS A FACTURAS
-- ======================================================
CREATE TABLE IF NOT EXISTS facturas_documentos (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER REFERENCES facturas(id) ON DELETE CASCADE,
    tipo_documento VARCHAR(50) NOT NULL, -- FACTURA, REMISION, ORDEN_COMPRA, ACTA_ENTREGA, OTRO
    nombre_archivo VARCHAR(255) NOT NULL, -- Nombre del archivo
    ruta_archivo VARCHAR(500) NOT NULL, -- Ruta completa del archivo
    tamaño_archivo INTEGER, -- Tamaño en bytes
    extension VARCHAR(10), -- PDF, XML, JPG, etc.
    usuario_carga_id INTEGER, -- Usuario que subió el documento
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT
);

-- ======================================================
-- 🔔 TABLA: ALERTAS Y NOTIFICACIONES DE FACTURAS
-- ======================================================
CREATE TABLE IF NOT EXISTS facturas_alertas (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER REFERENCES facturas(id) ON DELETE CASCADE,
    tipo_alerta VARCHAR(50) NOT NULL, -- VENCIMIENTO_PROXIMO, VENCIDA, MONTO_ALTO, RECHAZO, REVISION_PENDIENTE
    descripcion TEXT NOT NULL,
    fecha_alerta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento DATE, -- Si aplica para alertas de vencimiento
    dias_restantes INTEGER, -- Días restantes para vencimiento
    prioridad VARCHAR(20) DEFAULT 'MEDIA', -- BAJA, MEDIA, ALTA, CRITICA
    leida BOOLEAN DEFAULT FALSE,
    usuario_destino_id INTEGER, -- Usuario al que va dirigida la alerta
    fecha_lectura TIMESTAMP -- Fecha en que se marcó como leída
);

-- ======================================================
-- 📊 ÍNDICES PARA OPTIMIZACIÓN DE CONSULTAS
-- ======================================================
CREATE INDEX IF NOT EXISTS idx_facturas_numero ON facturas(numero_factura);
CREATE INDEX IF NOT EXISTS idx_facturas_nit ON facturas(nit);
CREATE INDEX IF NOT EXISTS idx_facturas_tercero ON facturas(tercero_id);
CREATE INDEX IF NOT EXISTS idx_facturas_estado ON facturas(estado);
CREATE INDEX IF NOT EXISTS idx_facturas_fecha_factura ON facturas(fecha_factura);
CREATE INDEX IF NOT EXISTS idx_facturas_fecha_vencimiento ON facturas(fecha_vencimiento);
CREATE INDEX IF NOT EXISTS idx_facturas_items_factura ON facturas_items(factura_id);
CREATE INDEX IF NOT EXISTS idx_facturas_historial_factura ON facturas_historial(factura_id);
CREATE INDEX IF NOT EXISTS idx_facturas_documentos_factura ON facturas_documentos(factura_id);
CREATE INDEX IF NOT EXISTS idx_facturas_alertas_factura ON facturas_alertas(factura_id);
CREATE INDEX IF NOT EXISTS idx_facturas_alertas_usuario ON facturas_alertas(usuario_destino_id);

-- ======================================================
-- 🎯 VISTAS PARA CONSULTAS FRECUENTES
-- ======================================================

-- Vista: Facturas con información completa del proveedor
CREATE OR REPLACE VIEW v_facturas_completas AS
SELECT 
    f.id,
    f.numero_factura,
    f.nit,
    f.razon_social,
    t.correo AS proveedor_correo,
    t.celular AS proveedor_telefono,
    f.fecha_factura,
    f.fecha_recepcion,
    f.fecha_vencimiento,
    CASE 
        WHEN f.fecha_vencimiento IS NULL THEN NULL
        WHEN f.fecha_vencimiento < CURRENT_DATE THEN 'VENCIDA'
        WHEN f.fecha_vencimiento - CURRENT_DATE <= 2 THEN 'CRITICA'
        WHEN f.fecha_vencimiento - CURRENT_DATE <= 7 THEN 'URGENTE'
        WHEN f.fecha_vencimiento - CURRENT_DATE <= 15 THEN 'PROXIMO'
        ELSE 'NORMAL'
    END AS estado_vencimiento,
    f.fecha_vencimiento - CURRENT_DATE AS dias_para_vencimiento,
    f.valor_bruto,
    f.valor_iva,
    f.valor_neto,
    f.estado,
    f.forma_pago,
    f.plazo_pago,
    f.archivo_pdf,
    f.archivo_xml,
    f.observaciones,
    f.motivo_rechazo,
    f.created_at,
    f.updated_at,
    (SELECT COUNT(*) FROM facturas_items WHERE factura_id = f.id) AS cantidad_items,
    (SELECT COUNT(*) FROM facturas_documentos WHERE factura_id = f.id) AS cantidad_documentos
FROM facturas f
LEFT JOIN terceros t ON f.tercero_id = t.id;

-- Vista: Facturas pendientes de validación
CREATE OR REPLACE VIEW v_facturas_pendientes AS
SELECT * FROM v_facturas_completas
WHERE estado = 'RECIBIDA'
ORDER BY fecha_recepcion ASC;

-- Vista: Facturas próximas a vencer
CREATE OR REPLACE VIEW v_facturas_proximas_vencer AS
SELECT * FROM v_facturas_completas
WHERE estado IN ('RECIBIDA', 'VALIDADA', 'CONTABILIZADA')
  AND fecha_vencimiento IS NOT NULL
  AND fecha_vencimiento - CURRENT_DATE <= 7
ORDER BY dias_para_vencimiento ASC;

-- Vista: Resumen de facturas por proveedor
CREATE OR REPLACE VIEW v_facturas_por_proveedor AS
SELECT 
    nit,
    razon_social,
    COUNT(*) AS total_facturas,
    SUM(CASE WHEN estado = 'RECIBIDA' THEN 1 ELSE 0 END) AS facturas_recibidas,
    SUM(CASE WHEN estado = 'VALIDADA' THEN 1 ELSE 0 END) AS facturas_validadas,
    SUM(CASE WHEN estado = 'RECHAZADA' THEN 1 ELSE 0 END) AS facturas_rechazadas,
    SUM(CASE WHEN estado = 'PAGADA' THEN 1 ELSE 0 END) AS facturas_pagadas,
    SUM(valor_neto) AS monto_total,
    SUM(CASE WHEN estado != 'PAGADA' THEN valor_neto ELSE 0 END) AS monto_pendiente_pago,
    MAX(fecha_factura) AS ultima_factura
FROM facturas
GROUP BY nit, razon_social
ORDER BY monto_total DESC;

-- ======================================================
-- ⚙️ TRIGGERS PARA AUDITORÍA AUTOMÁTICA
-- ======================================================

-- Trigger: Actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_facturas_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_facturas_timestamp
BEFORE UPDATE ON facturas
FOR EACH ROW
EXECUTE FUNCTION update_facturas_timestamp();

-- Trigger: Registrar cambios en historial
CREATE OR REPLACE FUNCTION facturas_registrar_historial()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO facturas_historial (factura_id, accion, estado_nuevo, observaciones)
        VALUES (NEW.id, 'CREADA', NEW.estado, 'Factura registrada en el sistema');
    ELSIF (TG_OP = 'UPDATE') THEN
        IF (OLD.estado != NEW.estado) THEN
            INSERT INTO facturas_historial (
                factura_id, accion, estado_anterior, estado_nuevo, 
                observaciones
            ) VALUES (
                NEW.id, 
                'CAMBIO_ESTADO', 
                OLD.estado, 
                NEW.estado,
                CASE 
                    WHEN NEW.estado = 'VALIDADA' THEN 'Factura validada'
                    WHEN NEW.estado = 'RECHAZADA' THEN CONCAT('Factura rechazada: ', NEW.motivo_rechazo)
                    WHEN NEW.estado = 'CONTABILIZADA' THEN 'Factura contabilizada'
                    WHEN NEW.estado = 'PAGADA' THEN 'Factura pagada'
                    ELSE 'Estado actualizado'
                END
            );
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_facturas_historial
AFTER INSERT OR UPDATE ON facturas
FOR EACH ROW
EXECUTE FUNCTION facturas_registrar_historial();

-- Trigger: Generar alertas automáticas de vencimiento
CREATE OR REPLACE FUNCTION facturas_generar_alertas_vencimiento()
RETURNS TRIGGER AS $$
DECLARE
    dias_restantes INTEGER;
BEGIN
    IF (NEW.fecha_vencimiento IS NOT NULL AND NEW.estado IN ('RECIBIDA', 'VALIDADA', 'CONTABILIZADA')) THEN
        dias_restantes := NEW.fecha_vencimiento - CURRENT_DATE;
        
        -- Alerta a 7 días de vencimiento
        IF (dias_restantes = 7) THEN
            INSERT INTO facturas_alertas (
                factura_id, tipo_alerta, descripcion, fecha_vencimiento, 
                dias_restantes, prioridad
            ) VALUES (
                NEW.id, 'VENCIMIENTO_PROXIMO', 
                CONCAT('La factura ', NEW.numero_factura, ' vence en 7 días'),
                NEW.fecha_vencimiento, dias_restantes, 'MEDIA'
            );
        END IF;
        
        -- Alerta a 2 días de vencimiento
        IF (dias_restantes = 2) THEN
            INSERT INTO facturas_alertas (
                factura_id, tipo_alerta, descripcion, fecha_vencimiento, 
                dias_restantes, prioridad
            ) VALUES (
                NEW.id, 'VENCIMIENTO_PROXIMO', 
                CONCAT('La factura ', NEW.numero_factura, ' vence en 2 días'),
                NEW.fecha_vencimiento, dias_restantes, 'ALTA'
            );
        END IF;
        
        -- Alerta de factura vencida
        IF (dias_restantes < 0) THEN
            INSERT INTO facturas_alertas (
                factura_id, tipo_alerta, descripcion, fecha_vencimiento, 
                dias_restantes, prioridad
            ) VALUES (
                NEW.id, 'VENCIDA', 
                CONCAT('La factura ', NEW.numero_factura, ' está vencida hace ', ABS(dias_restantes), ' días'),
                NEW.fecha_vencimiento, dias_restantes, 'CRITICA'
            );
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_facturas_alertas_vencimiento
AFTER INSERT OR UPDATE ON facturas
FOR EACH ROW
EXECUTE FUNCTION facturas_generar_alertas_vencimiento();

-- ======================================================
-- 📊 DATOS INICIALES DE EJEMPLO (OPCIONAL - Para Testing)
-- ======================================================

-- Comentado por defecto. Descomentar para insertar datos de prueba
/*
INSERT INTO facturas (
    numero_factura, tercero_id, nit, razon_social, fecha_factura, 
    fecha_vencimiento, valor_bruto, valor_iva, valor_neto, forma_pago, 
    plazo_pago, estado
) VALUES 
(
    'FACT-2025-001', 1, '900123456-7', 'COMERCIALIZADORA ABC SAS', 
    '2025-10-01', '2025-10-31', 1000000.00, 190000.00, 1190000.00, 
    'Crédito', 30, 'RECIBIDA'
),
(
    'FACT-2025-002', 1, '900987654-3', 'TECNOLOGIA XYZ LTDA', 
    '2025-10-10', '2025-11-09', 2500000.00, 475000.00, 2975000.00, 
    'Crédito', 30, 'VALIDADA'
);
*/

-- ======================================================
-- ✅ VALIDACIONES Y CONSTRAINTS
-- ======================================================

-- Asegurar que valor_neto sea positivo
ALTER TABLE facturas ADD CONSTRAINT chk_facturas_valor_neto_positivo 
CHECK (valor_neto > 0);

-- Asegurar que fecha_vencimiento sea posterior a fecha_factura
ALTER TABLE facturas ADD CONSTRAINT chk_facturas_fechas_coherentes 
CHECK (fecha_vencimiento IS NULL OR fecha_vencimiento >= fecha_factura);

-- Asegurar estados válidos
ALTER TABLE facturas ADD CONSTRAINT chk_facturas_estado_valido 
CHECK (estado IN ('RECIBIDA', 'VALIDADA', 'RECHAZADA', 'CONTABILIZADA', 'PAGADA', 'ANULADA'));

-- ======================================================
-- 📝 COMENTARIOS EN TABLAS Y COLUMNAS
-- ======================================================

COMMENT ON TABLE facturas IS 'Tabla principal de facturas recibidas de proveedores';
COMMENT ON TABLE facturas_items IS 'Detalle de ítems/líneas de cada factura';
COMMENT ON TABLE facturas_historial IS 'Auditoría completa de cambios en facturas';
COMMENT ON TABLE facturas_documentos IS 'Archivos adjuntos relacionados con facturas';
COMMENT ON TABLE facturas_alertas IS 'Sistema de alertas y notificaciones de facturas';

COMMENT ON COLUMN facturas.estado IS 'RECIBIDA (nueva), VALIDADA (aprobada), RECHAZADA, CONTABILIZADA, PAGADA, ANULADA';
COMMENT ON COLUMN facturas.valor_neto IS 'Valor final a pagar = bruto + IVA - descuentos - retenciones';
COMMENT ON COLUMN facturas_items.centro_costo IS 'Centro de costo para distribución contable';
COMMENT ON COLUMN facturas_alertas.prioridad IS 'BAJA, MEDIA, ALTA, CRITICA según urgencia';
