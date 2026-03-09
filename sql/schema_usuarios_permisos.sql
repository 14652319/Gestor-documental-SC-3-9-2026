-- ==============================================
-- SCHEMA: SISTEMA DE USUARIOS Y PERMISOS
-- ==============================================
-- 
-- Sistema avanzado de gestion de usuarios y permisos granulares
-- Autor: GitHub Copilot
-- Fecha: Octubre 23, 2025
-- Base: PostgreSQL 18.0+
--
-- ==============================================

-- Verificar y crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================================
-- 📊 TABLA: PERMISOS_USUARIO
-- ==============================================
-- Permisos granulares por usuario, módulo y acción específica

CREATE TABLE IF NOT EXISTS permisos_usuario (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    accion VARCHAR(100) NOT NULL,
    permitido BOOLEAN DEFAULT FALSE,
    asignado_por VARCHAR(100),
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    comentario TEXT,
    
    -- Índices y constraints
    CONSTRAINT fk_permisos_usuario_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT uk_permisos_usuario_unico UNIQUE (usuario_id, modulo, accion)
);

-- Índices para rendimiento
CREATE INDEX IF NOT EXISTS idx_permisos_usuario_usuario_id ON permisos_usuario(usuario_id);
CREATE INDEX IF NOT EXISTS idx_permisos_usuario_modulo ON permisos_usuario(modulo);
CREATE INDEX IF NOT EXISTS idx_permisos_usuario_permitido ON permisos_usuario(permitido);
CREATE INDEX IF NOT EXISTS idx_permisos_usuario_modulo_accion ON permisos_usuario(modulo, accion);

-- Trigger para actualizar fecha_actualizacion
CREATE OR REPLACE FUNCTION update_permisos_usuario_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_permisos_usuario_timestamp ON permisos_usuario;
CREATE TRIGGER trigger_update_permisos_usuario_timestamp
    BEFORE UPDATE ON permisos_usuario
    FOR EACH ROW
    EXECUTE FUNCTION update_permisos_usuario_timestamp();

-- ==============================================
-- 🎭 TABLA: ROLES_USUARIO
-- ==============================================
-- Plantillas de roles con permisos predefinidos

CREATE TABLE IF NOT EXISTS roles_usuario (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    color VARCHAR(7) DEFAULT '#166534', -- Color hex para UI
    icono VARCHAR(50) DEFAULT 'bi-person-badge',
    activo BOOLEAN DEFAULT TRUE,
    es_sistema BOOLEAN DEFAULT FALSE, -- Roles del sistema (no editables)
    creado_por VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_roles_usuario_activo ON roles_usuario(activo);
CREATE INDEX IF NOT EXISTS idx_roles_usuario_sistema ON roles_usuario(es_sistema);

-- Trigger para actualizar fecha
CREATE OR REPLACE FUNCTION update_roles_usuario_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_roles_usuario_timestamp ON roles_usuario;
CREATE TRIGGER trigger_update_roles_usuario_timestamp
    BEFORE UPDATE ON roles_usuario
    FOR EACH ROW
    EXECUTE FUNCTION update_roles_usuario_timestamp();

-- ==============================================
-- 🔗 TABLA: USUARIO_ROLES
-- ==============================================
-- Relación many-to-many entre usuarios y roles

CREATE TABLE IF NOT EXISTS usuario_roles (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    rol_id INTEGER NOT NULL,
    asignado_por VARCHAR(100),
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    
    -- Constraints
    CONSTRAINT fk_usuario_roles_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT fk_usuario_roles_rol FOREIGN KEY (rol_id) REFERENCES roles_usuario(id) ON DELETE CASCADE,
    CONSTRAINT uk_usuario_roles_unico UNIQUE (usuario_id, rol_id)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_usuario_roles_usuario_id ON usuario_roles(usuario_id);
CREATE INDEX IF NOT EXISTS idx_usuario_roles_rol_id ON usuario_roles(rol_id);
CREATE INDEX IF NOT EXISTS idx_usuario_roles_activo ON usuario_roles(activo);

-- ==============================================
-- 📧 TABLA: INVITACIONES_USUARIO
-- ==============================================
-- Sistema de invitaciones por correo electrónico

CREATE TABLE IF NOT EXISTS invitaciones_usuario (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    token_invitacion VARCHAR(255) NOT NULL UNIQUE,
    correo_enviado VARCHAR(255) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    fecha_uso TIMESTAMP,
    ip_uso VARCHAR(50),
    enviado_por VARCHAR(100),
    intentos_uso INTEGER DEFAULT 0,
    
    -- Constraints
    CONSTRAINT fk_invitaciones_usuario_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_invitaciones_usuario_token ON invitaciones_usuario(token_invitacion);
CREATE INDEX IF NOT EXISTS idx_invitaciones_usuario_usado ON invitaciones_usuario(usado);
CREATE INDEX IF NOT EXISTS idx_invitaciones_usuario_expiracion ON invitaciones_usuario(fecha_expiracion);
CREATE INDEX IF NOT EXISTS idx_invitaciones_usuario_correo ON invitaciones_usuario(correo_enviado);

-- ==============================================
-- 📋 TABLA: AUDITORIA_PERMISOS
-- ==============================================
-- Log completo de cambios en permisos y usuarios

CREATE TABLE IF NOT EXISTS auditoria_permisos (
    id SERIAL PRIMARY KEY,
    usuario_afectado_id INTEGER,
    modulo VARCHAR(50),
    accion VARCHAR(100),
    valor_anterior TEXT,
    valor_nuevo TEXT,
    tipo_cambio VARCHAR(50), -- 'CREAR', 'ACTIVAR', 'DESACTIVAR', 'PERMISO', 'ROL'
    realizado_por VARCHAR(100),
    ip_origen VARCHAR(50),
    user_agent TEXT,
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    comentario TEXT,
    datos_adicionales JSONB, -- Para almacenar información extra
    
    -- Constraints
    CONSTRAINT fk_auditoria_permisos_usuario FOREIGN KEY (usuario_afectado_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- Índices para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_auditoria_permisos_usuario_afectado ON auditoria_permisos(usuario_afectado_id);
CREATE INDEX IF NOT EXISTS idx_auditoria_permisos_fecha ON auditoria_permisos(fecha_cambio);
CREATE INDEX IF NOT EXISTS idx_auditoria_permisos_tipo ON auditoria_permisos(tipo_cambio);
CREATE INDEX IF NOT EXISTS idx_auditoria_permisos_realizado_por ON auditoria_permisos(realizado_por);
CREATE INDEX IF NOT EXISTS idx_auditoria_permisos_modulo ON auditoria_permisos(modulo);

-- ==============================================
-- 🎯 DATOS INICIALES: ROLES DEL SISTEMA
-- ==============================================

-- Insertar roles básicos del sistema
INSERT INTO roles_usuario (nombre, descripcion, color, icono, es_sistema, creado_por) VALUES
    ('Administrador', 'Acceso completo a todo el sistema', '#dc2626', 'bi-shield-lock-fill', true, 'sistema'),
    ('Usuario Avanzado', 'Acceso a múltiples módulos con permisos extendidos', '#f59e0b', 'bi-person-gear', true, 'sistema'),
    ('Usuario Básico', 'Acceso limitado a funcionalidades básicas', '#166534', 'bi-person-check', true, 'sistema'),
    ('Contabilidad', 'Acceso específico a módulos contables', '#7c3aed', 'bi-calculator', true, 'sistema'),
    ('Auditor', 'Acceso de solo lectura para auditoría', '#6b7280', 'bi-eye-fill', true, 'sistema')
ON CONFLICT (nombre) DO NOTHING;

-- ==============================================
-- 🔧 FUNCIONES AUXILIARES
-- ==============================================

-- Función para verificar si un usuario tiene un permiso específico
CREATE OR REPLACE FUNCTION verificar_permiso_usuario(
    p_usuario_id INTEGER,
    p_modulo VARCHAR(50),
    p_accion VARCHAR(100)
) RETURNS BOOLEAN AS $$
DECLARE
    permiso_existe BOOLEAN := FALSE;
BEGIN
    SELECT permitido INTO permiso_existe
    FROM permisos_usuario
    WHERE usuario_id = p_usuario_id
      AND modulo = p_modulo
      AND accion = p_accion;
    
    -- Si no encuentra el permiso, retorna FALSE
    RETURN COALESCE(permiso_existe, FALSE);
END;
$$ LANGUAGE plpgsql;

-- Función para obtener todos los permisos de un usuario
CREATE OR REPLACE FUNCTION obtener_permisos_usuario(p_usuario_id INTEGER)
RETURNS TABLE (
    modulo VARCHAR(50),
    accion VARCHAR(100),
    permitido BOOLEAN,
    fecha_asignacion TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.modulo, p.accion, p.permitido, p.fecha_asignacion
    FROM permisos_usuario p
    WHERE p.usuario_id = p_usuario_id
    ORDER BY p.modulo, p.accion;
END;
$$ LANGUAGE plpgsql;

-- Función para asignar un permiso a un usuario
CREATE OR REPLACE FUNCTION asignar_permiso_usuario(
    p_usuario_id INTEGER,
    p_modulo VARCHAR(50),
    p_accion VARCHAR(100),
    p_permitido BOOLEAN,
    p_asignado_por VARCHAR(100) DEFAULT NULL,
    p_comentario TEXT DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    INSERT INTO permisos_usuario (usuario_id, modulo, accion, permitido, asignado_por, comentario)
    VALUES (p_usuario_id, p_modulo, p_accion, p_permitido, p_asignado_por, p_comentario)
    ON CONFLICT (usuario_id, modulo, accion)
    DO UPDATE SET
        permitido = EXCLUDED.permitido,
        asignado_por = EXCLUDED.asignado_por,
        fecha_actualizacion = CURRENT_TIMESTAMP,
        comentario = EXCLUDED.comentario;
    
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Función para crear permisos por defecto para un rol
CREATE OR REPLACE FUNCTION crear_permisos_por_defecto_usuario(
    p_usuario_id INTEGER,
    p_rol VARCHAR(100) DEFAULT 'usuario_basico'
) RETURNS BOOLEAN AS $$
BEGIN
    -- Permisos básicos para todos los usuarios
    PERFORM asignar_permiso_usuario(p_usuario_id, 'admin', 'dashboard', true, 'sistema', 'Permiso por defecto');
    
    -- Permisos según el rol
    CASE p_rol
        WHEN 'administrador' THEN
            -- Administradores tienen acceso completo
            PERFORM asignar_permiso_usuario(p_usuario_id, 'admin', 'gestionar_usuarios', true, 'sistema');
            PERFORM asignar_permiso_usuario(p_usuario_id, 'admin', 'gestionar_permisos', true, 'sistema');
            PERFORM asignar_permiso_usuario(p_usuario_id, 'admin', 'ver_auditoria', true, 'sistema');
            PERFORM asignar_permiso_usuario(p_usuario_id, 'admin', 'gestionar_monitoreo', true, 'sistema');
            
        WHEN 'usuario_avanzado' THEN
            -- Usuarios avanzados tienen acceso a múltiples módulos
            PERFORM asignar_permiso_usuario(p_usuario_id, 'recibir_facturas', 'nueva_factura', true, 'sistema');
            PERFORM asignar_permiso_usuario(p_usuario_id, 'recibir_facturas', 'editar_factura', true, 'sistema');
            PERFORM asignar_permiso_usuario(p_usuario_id, 'relaciones', 'generar_relacion', true, 'sistema');
            PERFORM asignar_permiso_usuario(p_usuario_id, 'relaciones', 'recepcion_digital', true, 'sistema');
            
        WHEN 'usuario_basico' THEN
            -- Usuarios básicos solo pueden ver
            PERFORM asignar_permiso_usuario(p_usuario_id, 'recibir_facturas', 'nueva_factura', true, 'sistema');
            PERFORM asignar_permiso_usuario(p_usuario_id, 'relaciones', 'consultar_relacion', true, 'sistema');
    END CASE;
    
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- ==============================================
-- 🧹 LIMPIEZA Y MANTENIMIENTO
-- ==============================================

-- Función para limpiar invitaciones expiradas (ejecutar periódicamente)
CREATE OR REPLACE FUNCTION limpiar_invitaciones_expiradas()
RETURNS INTEGER AS $$
DECLARE
    registros_eliminados INTEGER := 0;
BEGIN
    DELETE FROM invitaciones_usuario
    WHERE fecha_expiracion < CURRENT_TIMESTAMP
      AND usado = FALSE;
    
    GET DIAGNOSTICS registros_eliminados = ROW_COUNT;
    RETURN registros_eliminados;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener estadísticas del sistema
CREATE OR REPLACE FUNCTION obtener_estadisticas_usuarios()
RETURNS TABLE (
    total_usuarios BIGINT,
    usuarios_activos BIGINT,
    usuarios_inactivos BIGINT,
    invitaciones_pendientes BIGINT,
    permisos_activos BIGINT,
    roles_asignados BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM usuarios) as total_usuarios,
        (SELECT COUNT(*) FROM usuarios WHERE activo = true) as usuarios_activos,
        (SELECT COUNT(*) FROM usuarios WHERE activo = false) as usuarios_inactivos,
        (SELECT COUNT(*) FROM invitaciones_usuario WHERE usado = false AND fecha_expiracion > CURRENT_TIMESTAMP) as invitaciones_pendientes,
        (SELECT COUNT(*) FROM permisos_usuario WHERE permitido = true) as permisos_activos,
        (SELECT COUNT(*) FROM usuario_roles WHERE activo = true) as roles_asignados;
END;
$$ LANGUAGE plpgsql;

-- ==============================================
-- ✅ VERIFICACIÓN DE INSTALACIÓN
-- ==============================================

DO $$
DECLARE
    tabla_count INTEGER;
    funcion_count INTEGER;
BEGIN
    -- Verificar tablas creadas
    SELECT COUNT(*) INTO tabla_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_name IN ('permisos_usuario', 'roles_usuario', 'usuario_roles', 'invitaciones_usuario', 'auditoria_permisos');
    
    -- Verificar funciones creadas
    SELECT COUNT(*) INTO funcion_count
    FROM information_schema.routines
    WHERE routine_schema = 'public'
      AND routine_name IN ('verificar_permiso_usuario', 'obtener_permisos_usuario', 'asignar_permiso_usuario');
    
    -- Log de instalación
    RAISE NOTICE '==============================================';
    RAISE NOTICE '🔐 SISTEMA DE USUARIOS Y PERMISOS INSTALADO';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Tablas creadas: % de 5', tabla_count;
    RAISE NOTICE 'Funciones creadas: % de 3', funcion_count;
    RAISE NOTICE 'Roles del sistema: 5 roles insertados';
    RAISE NOTICE 'Fecha: %', CURRENT_TIMESTAMP;
    RAISE NOTICE '==============================================';
    
    IF tabla_count = 5 AND funcion_count = 3 THEN
        RAISE NOTICE '✅ INSTALACIÓN COMPLETADA EXITOSAMENTE';
    ELSE
        RAISE WARNING '⚠️ INSTALACIÓN INCOMPLETA - Verificar errores';
    END IF;
END $$;

-- ==============================================
-- 📝 COMENTARIOS FINALES
-- ==============================================

COMMENT ON TABLE permisos_usuario IS 'Permisos granulares por usuario, módulo y acción específica';
COMMENT ON TABLE roles_usuario IS 'Plantillas de roles con permisos predefinidos';
COMMENT ON TABLE usuario_roles IS 'Relación many-to-many entre usuarios y roles';
COMMENT ON TABLE invitaciones_usuario IS 'Sistema de invitaciones por correo electrónico';
COMMENT ON TABLE auditoria_permisos IS 'Log completo de cambios en permisos y usuarios';

COMMENT ON FUNCTION verificar_permiso_usuario(INTEGER, VARCHAR, VARCHAR) IS 'Verifica si un usuario tiene un permiso específico';
COMMENT ON FUNCTION obtener_permisos_usuario(INTEGER) IS 'Obtiene todos los permisos de un usuario';
COMMENT ON FUNCTION asignar_permiso_usuario(INTEGER, VARCHAR, VARCHAR, BOOLEAN, VARCHAR, TEXT) IS 'Asigna un permiso a un usuario';
COMMENT ON FUNCTION crear_permisos_por_defecto_usuario(INTEGER, VARCHAR) IS 'Crea permisos por defecto según el rol';
COMMENT ON FUNCTION limpiar_invitaciones_expiradas() IS 'Limpia invitaciones expiradas del sistema';
COMMENT ON FUNCTION obtener_estadisticas_usuarios() IS 'Obtiene estadísticas generales del sistema';

-- Fin del script
-- Autor: GitHub Copilot
-- Sistema: Gestor Login Seguro - Supertiendas Cañaveral
-- Fecha: Octubre 23, 2025