-- =====================================================
-- SCRIPT: Crear tablas catálogo de configuración
-- Formas de Pago, Tipos de Servicio, Departamentos
-- =====================================================

-- 1. FORMAS DE PAGO
CREATE TABLE IF NOT EXISTS formas_pago (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(30) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Datos iniciales Formas de Pago
INSERT INTO formas_pago (codigo, nombre, created_by) VALUES
('ESTANDAR', 'Estándar', 'sistema'),
('TARJETA_CREDITO', 'Tarjeta de Crédito', 'sistema')
ON CONFLICT (codigo) DO NOTHING;

-- 2. TIPOS DE SERVICIO
CREATE TABLE IF NOT EXISTS tipos_servicio (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Datos iniciales Tipos de Servicio
INSERT INTO tipos_servicio (codigo, nombre, created_by) VALUES
('servicio', 'Servicio', 'sistema'),
('compra', 'Compra', 'sistema'),
('ambos', 'Ambos', 'sistema')
ON CONFLICT (codigo) DO NOTHING;

-- 3. DEPARTAMENTOS
CREATE TABLE IF NOT EXISTS departamentos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Datos iniciales Departamentos
INSERT INTO departamentos (codigo, nombre, created_by) VALUES
('FINANCIERO', 'Financiero', 'sistema'),
('TECNOLOGIA', 'Tecnología', 'sistema'),
('COMPRAS_Y_SUMINISTROS', 'Compras y Suministros', 'sistema'),
('MERCADEO', 'Mercadeo', 'sistema'),
('MVP_ESTRATEGICA', 'MVP Estratégica', 'sistema'),
('DOMICILIOS', 'Domicilios', 'sistema')
ON CONFLICT (codigo) DO NOTHING;

-- Verificación
SELECT 'Formas de Pago creadas:' as info, COUNT(*) as total FROM formas_pago;
SELECT 'Tipos de Servicio creados:' as info, COUNT(*) as total FROM tipos_servicio;
SELECT 'Departamentos creados:' as info, COUNT(*) as total FROM departamentos;
