-- =============================================
-- ?? SCHEMA COMPLETO - Gestor Documental
-- Sistema de Autenticación y Gestión de Proveedores
-- Supertiendas Cañaveral SAS
-- =============================================
-- Fecha de creación: Enero 2025
-- Base de datos: PostgreSQL 12+
-- =============================================

-- -------------------------------------------------
-- ??? LIMPIEZA PREVIA (OPCIONAL - CUIDADO EN PRODUCCIÓN)
-- -------------------------------------------------
-- DROP TABLE IF EXISTS contrasenas_usadas CASCADE;
-- DROP TABLE IF EXISTS tokens_recuperacion CASCADE;
-- DROP TABLE IF EXISTS accesos CASCADE;
-- DROP TABLE IF EXISTS ips_negras CASCADE;
-- DROP TABLE IF EXISTS ips_blancas CASCADE;
-- DROP TABLE IF EXISTS ips_sospechosas CASCADE;
-- DROP TABLE IF EXISTS documentos_tercero CASCADE;
-- DROP TABLE IF EXISTS solicitudes_registro CASCADE;
-- DROP TABLE IF EXISTS usuarios CASCADE;
-- DROP TABLE IF EXISTS terceros CASCADE;

-- -------------------------------------------------
-- ?? TABLA: terceros
-- Almacena información de proveedores y terceros
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS terceros (
    id SERIAL PRIMARY KEY,
    nit VARCHAR(20) UNIQUE NOT NULL,
    tipo_persona VARCHAR(10) NOT NULL CHECK (tipo_persona IN ('natural', 'juridica')),
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
    estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'aprobado', 'rechazado', 'en_revision'))
);

-- Índices para terceros
CREATE INDEX idx_terceros_nit ON terceros(nit);
CREATE INDEX idx_terceros_estado ON terceros(estado);
CREATE INDEX idx_terceros_fecha_registro ON terceros(fecha_registro);

-- -------------------------------------------------
-- ?? TABLA: usuarios
-- Almacena credenciales y datos de acceso
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    tercero_id INTEGER NOT NULL REFERENCES terceros(id) ON DELETE CASCADE,
    usuario VARCHAR(60) NOT NULL,
    correo VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    rol VARCHAR(30) DEFAULT 'externo' CHECK (rol IN ('admin', 'externo', 'interno', 'supervisor')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para usuarios
CREATE INDEX idx_usuarios_tercero_id ON usuarios(tercero_id);
CREATE INDEX idx_usuarios_usuario ON usuarios(usuario);
CREATE INDEX idx_usuarios_correo ON usuarios(correo);
CREATE INDEX idx_usuarios_activo ON usuarios(activo);
CREATE INDEX idx_usuarios_rol ON usuarios(rol);

-- -------------------------------------------------
-- ?? TABLA: accesos
-- Auditoría de intentos de login
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS accesos (
id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    ip VARCHAR(45),
    user_agent TEXT,
    exito BOOLEAN DEFAULT FALSE,
    motivo TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para accesos
CREATE INDEX idx_accesos_usuario_id ON accesos(usuario_id);
CREATE INDEX idx_accesos_ip ON accesos(ip);
CREATE INDEX idx_accesos_fecha ON accesos(fecha DESC);
CREATE INDEX idx_accesos_exito ON accesos(exito);

-- -------------------------------------------------
-- ?? TABLA: tokens_recuperacion
-- Tokens para recuperación de contraseña
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS tokens_recuperacion (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    token VARCHAR(64) UNIQUE NOT NULL,
    creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expira TIMESTAMP NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    nit VARCHAR(20),
    nombre_usuario VARCHAR(60),
 intentos_validacion INTEGER DEFAULT 0
);

-- Índices para tokens_recuperacion
CREATE INDEX idx_tokens_recuperacion_token ON tokens_recuperacion(token);
CREATE INDEX idx_tokens_recuperacion_usuario_id ON tokens_recuperacion(usuario_id);
CREATE INDEX idx_tokens_recuperacion_usado ON tokens_recuperacion(usado);
CREATE INDEX idx_tokens_recuperacion_expira ON tokens_recuperacion(expira);

-- -------------------------------------------------
-- ?? TABLA: contrasenas_usadas
-- Historial de contraseñas para prevenir reutilización
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS contrasenas_usadas (
 id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    password_hash VARCHAR(255) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para contrasenas_usadas
CREATE INDEX idx_contrasenas_usadas_usuario_id ON contrasenas_usadas(usuario_id);
CREATE INDEX idx_contrasenas_usadas_fecha ON contrasenas_usadas(fecha DESC);

-- -------------------------------------------------
-- ?? TABLA: ips_sospechosas
-- Tracking de IPs con intentos fallidos
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS ips_sospechosas (
    ip VARCHAR(45) PRIMARY KEY,
    intentos INTEGER DEFAULT 0,
ultima_actividad TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    bloqueada BOOLEAN DEFAULT FALSE,
    motivo_bloqueo TEXT
);

-- Índices para ips_sospechosas
CREATE INDEX idx_ips_sospechosas_bloqueada ON ips_sospechosas(bloqueada);
CREATE INDEX idx_ips_sospechosas_ultima_actividad ON ips_sospechosas(ultima_actividad);

-- -------------------------------------------------
-- ? TABLA: ips_blancas
-- Lista blanca de IPs permitidas
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS ips_blancas (
    ip VARCHAR(45) PRIMARY KEY
);

-- -------------------------------------------------
-- ?? TABLA: ips_negras
-- Lista negra de IPs bloqueadas permanentemente
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS ips_negras (
    ip VARCHAR(45) PRIMARY KEY,
    motivo TEXT,
    fecha_bloqueo TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para ips_negras
CREATE INDEX idx_ips_negras_fecha_bloqueo ON ips_negras(fecha_bloqueo DESC);

-- -------------------------------------------------
-- ?? TABLA: documentos_tercero
-- Almacena referencias a documentos cargados
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS documentos_tercero (
    id SERIAL PRIMARY KEY,
    tercero_id INTEGER NOT NULL REFERENCES terceros(id) ON DELETE CASCADE,
    radicado VARCHAR(20) NOT NULL,
    tipo_documento VARCHAR(100) NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    tamaño_archivo INTEGER,
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  estado VARCHAR(20) DEFAULT 'cargado' CHECK (estado IN ('cargado', 'validado', 'rechazado', 'pendiente'))
);

-- Índices para documentos_tercero
CREATE INDEX idx_documentos_tercero_tercero_id ON documentos_tercero(tercero_id);
CREATE INDEX idx_documentos_tercero_radicado ON documentos_tercero(radicado);
CREATE INDEX idx_documentos_tercero_tipo_documento ON documentos_tercero(tipo_documento);
CREATE INDEX idx_documentos_tercero_estado ON documentos_tercero(estado);

-- -------------------------------------------------
-- ?? TABLA: solicitudes_registro
-- Tracking del proceso de registro de proveedores
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS solicitudes_registro (
    id SERIAL PRIMARY KEY,
    tercero_id INTEGER NOT NULL REFERENCES terceros(id) ON DELETE CASCADE,
    radicado VARCHAR(20) UNIQUE NOT NULL,
  estado VARCHAR(30) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'en_revision', 'aprobado', 'rechazado')),
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    documentos_completos BOOLEAN DEFAULT FALSE,
    usuarios_creados BOOLEAN DEFAULT FALSE
);

-- Índices para solicitudes_registro
CREATE INDEX idx_solicitudes_registro_tercero_id ON solicitudes_registro(tercero_id);
CREATE INDEX idx_solicitudes_registro_radicado ON solicitudes_registro(radicado);
CREATE INDEX idx_solicitudes_registro_estado ON solicitudes_registro(estado);
CREATE INDEX idx_solicitudes_registro_fecha_solicitud ON solicitudes_registro(fecha_solicitud DESC);

-- -------------------------------------------------
-- ?? FUNCIONES Y TRIGGERS
-- -------------------------------------------------

-- Función para actualizar fecha_actualizacion automáticamente
CREATE OR REPLACE FUNCTION actualizar_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para solicitudes_registro
DROP TRIGGER IF EXISTS trigger_actualizar_fecha_solicitud ON solicitudes_registro;
CREATE TRIGGER trigger_actualizar_fecha_solicitud
    BEFORE UPDATE ON solicitudes_registro
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- -------------------------------------------------
-- ?? DATOS INICIALES (SEEDS)
-- -------------------------------------------------

-- Usuario administrador por defecto (NIT interno de Supertiendas Cañaveral)
-- Contraseña: Admin2025! (debe cambiarse en producción)
INSERT INTO terceros (nit, tipo_persona, razon_social, estado)
VALUES ('805028041', 'juridica', 'Supertiendas Cañaveral SAS', 'aprobado')
ON CONFLICT (nit) DO NOTHING;

-- Usuario admin por defecto
-- Contraseña hasheada con bcrypt: Admin2025!
INSERT INTO usuarios (tercero_id, usuario, correo, password_hash, activo, rol)
SELECT 
    t.id,
  'ADMIN',
    'admin@supertiendascanaveral.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztP.CKqU2EKi', -- Admin2025!
    TRUE,
    'admin'
FROM terceros t
WHERE t.nit = '805028041'
ON CONFLICT (correo) DO NOTHING;

-- IPs blancas corporativas (ejemplos - ajustar según necesidad)
INSERT INTO ips_blancas (ip) VALUES 
    ('127.0.0.1'),
    ('::1'),
    ('192.168.1.1')
ON CONFLICT (ip) DO NOTHING;

-- -------------------------------------------------
-- ?? COMENTARIOS EN TABLAS Y COLUMNAS
-- -------------------------------------------------

COMMENT ON TABLE terceros IS 'Almacena información de proveedores y terceros del sistema';
COMMENT ON COLUMN terceros.nit IS 'Número de Identificación Tributaria único';
COMMENT ON COLUMN terceros.tipo_persona IS 'Tipo de persona: natural o juridica';
COMMENT ON COLUMN terceros.estado IS 'Estado del tercero: pendiente, aprobado, rechazado, en_revision';

COMMENT ON TABLE usuarios IS 'Credenciales de acceso al sistema';
COMMENT ON COLUMN usuarios.activo IS 'Indica si el usuario puede acceder al sistema';
COMMENT ON COLUMN usuarios.rol IS 'Rol del usuario: admin, externo, interno, supervisor';

COMMENT ON TABLE accesos IS 'Auditoría de intentos de login (exitosos y fallidos)';
COMMENT ON TABLE tokens_recuperacion IS 'Tokens temporales para recuperación de contraseña (validez 10 minutos)';
COMMENT ON TABLE contrasenas_usadas IS 'Historial de contraseñas para prevenir reutilización';

COMMENT ON TABLE ips_sospechosas IS 'Tracking de IPs con intentos fallidos de login';
COMMENT ON TABLE ips_blancas IS 'Lista de IPs permitidas sin restricciones';
COMMENT ON TABLE ips_negras IS 'Lista de IPs bloqueadas permanentemente';

COMMENT ON TABLE documentos_tercero IS 'Referencias a documentos PDF cargados por terceros';
COMMENT ON TABLE solicitudes_registro IS 'Tracking del proceso de registro de nuevos proveedores';

-- -------------------------------------------------
-- ?? VISTAS ÚTILES
-- -------------------------------------------------

-- Vista: Usuarios con información del tercero
CREATE OR REPLACE VIEW v_usuarios_completos AS
SELECT 
    u.id as usuario_id,
    u.usuario,
 u.correo,
    u.activo,
    u.rol,
    u.fecha_creacion,
  t.nit,
 t.razon_social,
    t.tipo_persona,
    t.estado as estado_tercero
FROM usuarios u
INNER JOIN terceros t ON u.tercero_id = t.id;

-- Vista: Solicitudes con información del tercero
CREATE OR REPLACE VIEW v_solicitudes_completas AS
SELECT 
    s.id as solicitud_id,
    s.radicado,
    s.estado,
    s.fecha_solicitud,
    s.fecha_actualizacion,
    s.observaciones,
    s.documentos_completos,
    s.usuarios_creados,
    t.nit,
    t.razon_social,
    t.correo,
    t.celular,
    (SELECT COUNT(*) FROM documentos_tercero WHERE tercero_id = t.id) as total_documentos,
    (SELECT COUNT(*) FROM usuarios WHERE tercero_id = t.id) as total_usuarios
FROM solicitudes_registro s
INNER JOIN terceros t ON s.tercero_id = t.id;

-- Vista: Últimos accesos al sistema
CREATE OR REPLACE VIEW v_ultimos_accesos AS
SELECT 
    a.id,
    a.fecha,
    a.ip,
    a.exito,
    a.motivo,
    u.usuario,
    t.nit,
 t.razon_social
FROM accesos a
LEFT JOIN usuarios u ON a.usuario_id = u.id
LEFT JOIN terceros t ON u.tercero_id = t.id
ORDER BY a.fecha DESC
LIMIT 100;

-- -------------------------------------------------
-- ? VERIFICACIÓN FINAL
-- -------------------------------------------------

-- Listar todas las tablas creadas
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- Mostrar estadísticas
SELECT 
    'Terceros' as tabla, COUNT(*) as registros FROM terceros
UNION ALL
SELECT 'Usuarios', COUNT(*) FROM usuarios
UNION ALL
SELECT 'Accesos', COUNT(*) FROM accesos
UNION ALL
SELECT 'Solicitudes', COUNT(*) FROM solicitudes_registro
UNION ALL
SELECT 'Documentos', COUNT(*) FROM documentos_tercero
UNION ALL
SELECT 'IPs Blancas', COUNT(*) FROM ips_blancas
UNION ALL
SELECT 'IPs Negras', COUNT(*) FROM ips_negras
UNION ALL
SELECT 'IPs Sospechosas', COUNT(*) FROM ips_sospechosas;

-- -------------------------------------------------
-- ?? NOTAS IMPORTANTES
-- -------------------------------------------------
/*
1. CONTRASEÑA DEL ADMIN POR DEFECTO:
   Usuario: ADMIN
   Correo: admin@supertiendascanaveral.com
   Contraseña: Admin2025!
   ?? CAMBIAR INMEDIATAMENTE EN PRODUCCIÓN

2. LÍMITES Y CONFIGURACIONES:
   - Máximo 5 usuarios por tercero (configurable en .env)
   - Tokens de recuperación válidos por 10 minutos
   - Máximo 3 intentos de validación de token
   - Bloqueo automático después de 5 intentos fallidos de login

3. MANTENIMIENTO:
   - Limpiar tokens expirados periódicamente:
     DELETE FROM tokens_recuperacion WHERE expira < CURRENT_TIMESTAMP AND usado = TRUE;
   
   - Limpiar intentos de acceso antiguos (más de 6 meses):
     DELETE FROM accesos WHERE fecha < CURRENT_TIMESTAMP - INTERVAL '6 months';

4. BACKUP:
   - Realizar backups diarios de la base de datos
   - Comando: pg_dump -U gestor_user gestor_documental > backup_$(date +%Y%m%d).sql

5. PERMISOS:
   - El usuario gestor_user debe tener permisos completos en el schema public
   - GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gestor_user;
   - GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gestor_user;
*/
