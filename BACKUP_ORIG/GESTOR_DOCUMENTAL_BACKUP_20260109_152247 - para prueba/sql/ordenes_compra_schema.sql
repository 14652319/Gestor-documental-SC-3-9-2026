-- =====================================================
-- ESQUEMA DE ÓRDENES DE COMPRA (OCR)
-- Fecha: 9 de Diciembre 2025
-- =====================================================

-- Tabla de Consecutivos para Órdenes de Compra
CREATE TABLE IF NOT EXISTS consecutivos_ordenes_compra (
    id SERIAL PRIMARY KEY,
    prefijo VARCHAR(10) NOT NULL DEFAULT 'OCR',
    ultimo_numero INTEGER NOT NULL DEFAULT 0,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(prefijo)
);

-- Insertar registro inicial
INSERT INTO consecutivos_ordenes_compra (prefijo, ultimo_numero)
VALUES ('OCR', 0)
ON CONFLICT (prefijo) DO NOTHING;

-- Tabla de Unidades de Negocio
CREATE TABLE IF NOT EXISTS unidades_negocio (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Datos iniciales de Unidades de Negocio (según imagen)
INSERT INTO unidades_negocio (codigo, nombre) VALUES
('06 PGC', 'Productos de Gran Consumo')
ON CONFLICT (codigo) DO NOTHING;

-- Tabla de Centros de Costo
CREATE TABLE IF NOT EXISTS centros_costo (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla Principal: Órdenes de Compra
CREATE TABLE IF NOT EXISTS ordenes_compra (
    id SERIAL PRIMARY KEY,
    
    -- Información del consecutivo
    numero_orden VARCHAR(50) NOT NULL UNIQUE,  -- Ej: OCR-000000001
    
    -- Información del tercero/proveedor
    tercero_nit VARCHAR(20) NOT NULL,
    tercero_nombre VARCHAR(255) NOT NULL,
    tercero_direccion VARCHAR(255),
    tercero_telefono VARCHAR(50),
    tercero_email VARCHAR(100),
    
    -- Información de la orden
    fecha_elaboracion DATE NOT NULL,
    motivo TEXT,  -- Campo "MATERIAL POP TODAS LAS SEDES" según imagen
    
    -- Totales
    subtotal NUMERIC(15, 2) DEFAULT 0,
    iva NUMERIC(15, 2) DEFAULT 0,
    retefuente NUMERIC(15, 2) DEFAULT 0,
    total NUMERIC(15, 2) DEFAULT 0,
    
    -- Observaciones finales
    observaciones TEXT,
    
    -- Información de auditoría
    usuario_creador VARCHAR(100) NOT NULL,
    usuario_id INTEGER,
    empresa_id INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Estado de la orden
    estado VARCHAR(50) DEFAULT 'PENDIENTE',  -- PENDIENTE, ENVIADA, APROBADA, ANULADA
    
    -- Información de envío
    correo_enviado BOOLEAN DEFAULT FALSE,
    fecha_envio_correo TIMESTAMP,
    correo_destino VARCHAR(100),
    
    -- Relaciones
    FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE SET NULL
);

-- Tabla de Detalle de Órdenes de Compra (Items/Productos)
CREATE TABLE IF NOT EXISTS ordenes_compra_detalle (
    id SERIAL PRIMARY KEY,
    orden_compra_id INTEGER NOT NULL,
    
    -- Información del centro de operación
    centro_operacion_codigo VARCHAR(20),
    centro_operacion_nombre VARCHAR(255),
    
    -- Información de unidad de negocio
    unidad_negocio_codigo VARCHAR(20),
    unidad_negocio_nombre VARCHAR(100),
    
    -- Información de centro de costo
    centro_costo_codigo VARCHAR(20),
    centro_costo_nombre VARCHAR(100),
    
    -- Cantidad y precios
    cantidad INTEGER NOT NULL DEFAULT 1,
    precio_unitario NUMERIC(15, 2) NOT NULL DEFAULT 0,
    valor_total NUMERIC(15, 2) NOT NULL DEFAULT 0,
    
    -- Orden de visualización
    orden INTEGER DEFAULT 0,
    
    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (orden_compra_id) REFERENCES ordenes_compra(id) ON DELETE CASCADE
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_ordenes_compra_nit ON ordenes_compra(tercero_nit);
CREATE INDEX IF NOT EXISTS idx_ordenes_compra_fecha ON ordenes_compra(fecha_elaboracion);
CREATE INDEX IF NOT EXISTS idx_ordenes_compra_estado ON ordenes_compra(estado);
CREATE INDEX IF NOT EXISTS idx_ordenes_compra_usuario ON ordenes_compra(usuario_creador);
CREATE INDEX IF NOT EXISTS idx_ordenes_compra_empresa ON ordenes_compra(empresa_id);
CREATE INDEX IF NOT EXISTS idx_ordenes_compra_detalle_orden ON ordenes_compra_detalle(orden_compra_id);

-- Función para actualizar fecha de modificación
CREATE OR REPLACE FUNCTION actualizar_fecha_modificacion_orden_compra()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar fecha_actualizacion
CREATE TRIGGER trigger_actualizar_orden_compra
    BEFORE UPDATE ON ordenes_compra
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion_orden_compra();

-- Comentarios de documentación
COMMENT ON TABLE ordenes_compra IS 'Tabla principal de órdenes de compra generadas por el sistema';
COMMENT ON TABLE ordenes_compra_detalle IS 'Detalle de items/productos de cada orden de compra';
COMMENT ON TABLE unidades_negocio IS 'Catálogo de unidades de negocio para clasificación';
COMMENT ON TABLE centros_costo IS 'Catálogo de centros de costo para distribución contable';
COMMENT ON COLUMN ordenes_compra.numero_orden IS 'Consecutivo único de la orden (OCR-000000001)';
COMMENT ON COLUMN ordenes_compra.motivo IS 'Descripción del motivo de la orden de compra';
COMMENT ON COLUMN ordenes_compra_detalle.orden IS 'Orden de visualización de los items en el PDF';
