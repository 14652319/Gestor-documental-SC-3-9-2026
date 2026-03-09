-- ======================================================
-- 📘 ESTRUCTURA BASE DEL GESTOR LOGIN SEGURO
-- ======================================================

CREATE TABLE IF NOT EXISTS personas (
    id SERIAL PRIMARY KEY,
    tipo_persona VARCHAR(10) NOT NULL, -- 'natural' o 'juridica'
    primer_nombre VARCHAR(100),       -- Solo para Persona Natural
    segundo_nombre VARCHAR(100),      -- Opcional para Persona Natural
    primer_apellido VARCHAR(100),     -- Solo para Persona Natural
    segundo_apellido VARCHAR(100),    -- Opcional para Persona Natural
    razon_social VARCHAR(200),        -- Solo para Persona Jurídica
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS terceros (
    id SERIAL PRIMARY KEY,
    nit VARCHAR(20) UNIQUE NOT NULL,
    tipo_persona VARCHAR(10) NOT NULL,
    razon_social VARCHAR(150),
    primer_nombre VARCHAR(80),
    segundo_nombre VARCHAR(80),
    primer_apellido VARCHAR(80),
    segundo_apellido VARCHAR(80),
    correo VARCHAR(120),
    celular VARCHAR(30),
    acepta_terminos BOOLEAN DEFAULT TRUE,
    acepta_contacto BOOLEAN DEFAULT FALSE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'pendiente'
);

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    tercero_id INTEGER REFERENCES terceros(id),
    usuario VARCHAR(60) NOT NULL,
    correo VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    rol VARCHAR(30) DEFAULT 'externo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accesos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    ip VARCHAR(45),
    user_agent TEXT,
    exito BOOLEAN DEFAULT FALSE,
    motivo TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tokens_recuperacion (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    token VARCHAR(64) UNIQUE NOT NULL,
    creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expira TIMESTAMP NOT NULL,
    usado BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS contrasenas_usadas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    password_hash VARCHAR(255) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ips_sospechosas (
    ip VARCHAR(45) PRIMARY KEY,
    intentos INTEGER DEFAULT 0,
    ultima_actividad TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    bloqueada BOOLEAN DEFAULT FALSE,
    motivo_bloqueo TEXT
);

CREATE TABLE IF NOT EXISTS ips_blancas (
    ip VARCHAR(45) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS ips_negras (
    ip VARCHAR(45) PRIMARY KEY,
    motivo TEXT,
    fecha_bloqueo TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear el usuario admin inicial
INSERT INTO terceros (nit, tipo_persona, razon_social, correo, celular, estado)
VALUES ('900000000', 'juridica', 'Superusuario Gestor', 'admin@gestor.com', '0000000000', 'activo')
ON CONFLICT (nit) DO NOTHING;

-- ======================================================
-- 📁 TABLAS PARA GESTIÓN DE DOCUMENTOS Y RADICADOS
-- ======================================================

CREATE TABLE IF NOT EXISTS documentos_tercero (
    id SERIAL PRIMARY KEY,
    tercero_id INTEGER REFERENCES terceros(id),
    radicado VARCHAR(20) NOT NULL, -- RAD-XXXXXX
    tipo_documento VARCHAR(100) NOT NULL, -- RUT, CAMARA_COMERCIO, etc.
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    tamaño_archivo INTEGER,
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'cargado' -- cargado, validado, rechazado
);

CREATE TABLE IF NOT EXISTS solicitudes_registro (
    id SERIAL PRIMARY KEY,
    tercero_id INTEGER REFERENCES terceros(id),
    radicado VARCHAR(20) UNIQUE NOT NULL, -- RAD-XXXXXX
    estado VARCHAR(30) DEFAULT 'pendiente', -- pendiente, en_revision, aprobado, rechazado
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    documentos_completos BOOLEAN DEFAULT FALSE,
    usuarios_creados BOOLEAN DEFAULT FALSE
);

-- ======================================================
-- 📧 TABLAS PARA CÓDIGOS DE RECUPERACIÓN MEJORADOS
-- ======================================================

-- Actualizar tabla de tokens para incluir más contexto
ALTER TABLE tokens_recuperacion ADD COLUMN IF NOT EXISTS nit VARCHAR(20);
ALTER TABLE tokens_recuperacion ADD COLUMN IF NOT EXISTS nombre_usuario VARCHAR(60);
ALTER TABLE tokens_recuperacion ADD COLUMN IF NOT EXISTS intentos_validacion INTEGER DEFAULT 0;

INSERT INTO usuarios (tercero_id, usuario, correo, password_hash, activo, rol)
VALUES (
    1,
    'admin',
    'admin@gestor.com',
    '$2b$12$ZbHq0M9G3PYWcEAYy7HqEuzqOGoEXZrrthtNRYuAMX3X64O6.znJC', -- Contraseña: Admin2025*
    TRUE,
    'admin'
)
ON CONFLICT (correo) DO NOTHING;
