-- =====================================================
-- SCHEMA: USUARIOS INTERNOS Y PERMISOS POR MÓDULO
-- Fecha: 18 de Octubre 2025
-- =====================================================

-- Tabla: Usuarios Internos (empleados de SC y Legran)
CREATE TABLE IF NOT EXISTS usuarios_internos (
    id SERIAL PRIMARY KEY,
    numero_identificacion VARCHAR(20) UNIQUE NOT NULL,
    primer_nombre VARCHAR(50) NOT NULL,
    segundo_nombre VARCHAR(50),
    primer_apellido VARCHAR(50) NOT NULL,
    segundo_apellido VARCHAR(50),
    correo_electronico VARCHAR(255) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    centro_operacion_id INTEGER REFERENCES centros_operacion(id),
    usuario VARCHAR(50) UNIQUE NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('ADMINISTRADOR', 'USUARIO1', 'USUARIO2', 'USUARIO3')),
    empresa VARCHAR(5) NOT NULL CHECK (empresa IN ('SC', 'LG')),
    activo BOOLEAN DEFAULT FALSE,
    invitacion_enviada BOOLEAN DEFAULT FALSE,
    fecha_invitacion TIMESTAMP,
    token_activacion VARCHAR(100) UNIQUE,
    fecha_expiracion_token TIMESTAMP,
    password_hash VARCHAR(255),
    ultimo_acceso TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creado_por VARCHAR(50),
    actualizado_por VARCHAR(50)
);

-- Tabla: Permisos por Módulo
CREATE TABLE IF NOT EXISTS permisos_modulos (
    id SERIAL PRIMARY KEY,
    usuario_interno_id INTEGER REFERENCES usuarios_internos(id) ON DELETE CASCADE,
    modulo VARCHAR(50) NOT NULL,
    permiso VARCHAR(100) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(usuario_interno_id, modulo, permiso)
);

-- Tabla: Historial de cambios de usuarios internos
CREATE TABLE IF NOT EXISTS historial_usuarios_internos (
    id SERIAL PRIMARY KEY,
    usuario_interno_id INTEGER REFERENCES usuarios_internos(id) ON DELETE CASCADE,
    accion VARCHAR(50) NOT NULL,
    campo_modificado VARCHAR(100),
    valor_anterior TEXT,
    valor_nuevo TEXT,
    motivo TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    realizado_por VARCHAR(50),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_usuarios_internos_nit ON usuarios_internos(numero_identificacion);
CREATE INDEX IF NOT EXISTS idx_usuarios_internos_usuario ON usuarios_internos(usuario);
CREATE INDEX IF NOT EXISTS idx_usuarios_internos_correo ON usuarios_internos(correo_electronico);
CREATE INDEX IF NOT EXISTS idx_usuarios_internos_empresa ON usuarios_internos(empresa);
CREATE INDEX IF NOT EXISTS idx_usuarios_internos_rol ON usuarios_internos(rol);
CREATE INDEX IF NOT EXISTS idx_usuarios_internos_activo ON usuarios_internos(activo);
CREATE INDEX IF NOT EXISTS idx_permisos_modulos_usuario ON permisos_modulos(usuario_interno_id);
CREATE INDEX IF NOT EXISTS idx_permisos_modulos_modulo ON permisos_modulos(modulo);

-- Comentarios de documentación
COMMENT ON TABLE usuarios_internos IS 'Usuarios empleados de Supertiendas Cañaveral y Legran';
COMMENT ON TABLE permisos_modulos IS 'Permisos granulares por módulo para cada usuario';
COMMENT ON TABLE historial_usuarios_internos IS 'Auditoría completa de cambios en usuarios internos';

COMMENT ON COLUMN usuarios_internos.rol IS 'ADMINISTRADOR: Acceso completo | USUARIO1-3: Niveles de acceso progresivos';
COMMENT ON COLUMN usuarios_internos.empresa IS 'SC: Supertiendas Cañaveral SAS | LG: La Galería y Cía SAS (Legran)';
COMMENT ON COLUMN usuarios_internos.activo IS 'FALSE hasta que el usuario active su cuenta mediante token';
COMMENT ON COLUMN usuarios_internos.token_activacion IS 'Token único para activación de cuenta vía email';

-- Datos iniciales: Lista de usuarios internos para pre-registro
INSERT INTO usuarios_internos (
    numero_identificacion,
    primer_nombre,
    segundo_nombre,
    primer_apellido,
    segundo_apellido,
    correo_electronico,
    telefono,
    centro_operacion_id,
    usuario,
    rol,
    empresa,
    activo,
    creado_por
) VALUES
    ('TEMP001', 'DIANA', 'MARCELA', 'SANCHEZ', '', 'dmsanchez@supertiendascanaveral.com', '3001234567', 1, 'dmsanchez', 'USUARIO1', 'SC', FALSE, 'SISTEMA'),
    ('TEMP002', 'JHON', 'JAIRO', 'TENORIO', '', 'jjtenorio@supertiendascanaveral.com', '3001234567', 1, 'jjtenorio', 'USUARIO1', 'SC', FALSE, 'SISTEMA'),
    ('TEMP003', 'LAURA', 'MARCELA', 'RESTREPO', 'VALLEJO', 'laura.restrepo@supertiendascanaveral.com', '3001234567', 1, 'lrestrepo', 'USUARIO1', 'SC', FALSE, 'SISTEMA'),
    ('TEMP004', 'MAGALI', '', 'DIAZ', '', 'mdiaz@supertiendascanaveral.com', '3001234567', 1, 'mdiaz', 'USUARIO1', 'SC', FALSE, 'SISTEMA'),
    ('TEMP005', 'ALEJANDRA', '', 'RUA', '', 'arua@supertiendascanaveral.com', '3001234567', 1, 'arua', 'USUARIO1', 'SC', FALSE, 'SISTEMA'),
    ('TEMP006', 'BRAYAN', 'DAVID', 'AYALA', 'BETANCUR', 'brayan.ayala@supertiendascanaveral.com', '3001234567', 1, 'bayala', 'USUARIO1', 'SC', FALSE, 'SISTEMA'),
    ('TEMP007', 'CINDY', 'KATHERINE', 'CABRERA', 'CARMONA', 'katherine.cabrera@supertiendascanaveral.com', '3001234567', 1, 'kcabrera', 'USUARIO1', 'SC', FALSE, 'SISTEMA'),
    ('TEMP008', 'AUX', 'CONTA', 'UNO', '', 'auxconta01@supertiendascanaveral.com', '3001234567', 1, 'auxconta01', 'USUARIO1', 'SC', FALSE, 'SISTEMA'),
    ('TEMP009', 'JUAN', 'CARLOS', 'BOTINA', '', 'jcbotina@supertiendascanaveral.com', '3001234567', 1, 'jcbotina', 'USUARIO2', 'SC', FALSE, 'SISTEMA'),
    ('TEMP010', 'M', '', 'AGUDELO', '', 'magudelo@supertiendascanaveral.com', '3001234567', 1, 'magudelo', 'USUARIO2', 'SC', FALSE, 'SISTEMA'),
    ('14652319', 'RICARDO', '', 'RIASCOS', '', 'rriascos@supertiendascanaveral.com', '3128676047', 1, 'rriascos', 'ADMINISTRADOR', 'SC', TRUE, 'SISTEMA')
ON CONFLICT (numero_identificacion) DO NOTHING;

-- Permisos por defecto para ADMINISTRADOR (acceso completo)
INSERT INTO permisos_modulos (usuario_interno_id, modulo, permiso, activo)
SELECT 
    id,
    modulo,
    permiso,
    TRUE
FROM usuarios_internos,
    (VALUES 
        ('CAUSACIONES', 'VER_PDF'),
        ('CAUSACIONES', 'RENOMBRAR_PDF'),
        ('CAUSACIONES', 'BORRAR_PDF'),
        ('CAUSACIONES', 'MOVER_PDF'),
        ('CAUSACIONES', 'GENERAR_LISTADOS'),
        ('CAUSACIONES', 'DESCARGAR'),
        
        ('NOTAS_CONTABILIDAD', 'VER_NOTAS'),
        ('NOTAS_CONTABILIDAD', 'SELECCIONAR'),
        ('NOTAS_CONTABILIDAD', 'CARGAR_DOCUMENTO'),
        ('NOTAS_CONTABILIDAD', 'EDITAR_DOCUMENTO'),
        ('NOTAS_CONTABILIDAD', 'GUARDAR_DOCUMENTOS'),
        
        ('RECIBIR_FACTURAS', 'ADICIONAR'),
        ('RECIBIR_FACTURAS', 'BORRAR'),
        ('RECIBIR_FACTURAS', 'GUARDAR'),
        ('RECIBIR_FACTURAS', 'EDITAR'),
        
        ('GENERAR_RELACIONES', 'SELECCIONAR'),
        ('GENERAR_RELACIONES', 'GENERAR_RELACION'),
        
        ('DIAN_VS_ERP', 'CARGAR_DOCUMENTOS'),
        ('DIAN_VS_ERP', 'PROCESAR_DOCUMENTOS'),
        ('DIAN_VS_ERP', 'DESCARGAR_EXCEL'),
        
        ('SEGURIDAD_SOCIAL', 'VER_PDF'),
        ('SEGURIDAD_SOCIAL', 'EDITAR'),
        ('SEGURIDAD_SOCIAL', 'CARGAR_PDF'),
        ('SEGURIDAD_SOCIAL', 'DESCARGAR'),
        
        ('TERCEROS', 'CREAR_TERCERO'),
        ('TERCEROS', 'ACTIVAR_TERCERO'),
        ('TERCEROS', 'DESACTIVAR_TERCERO'),
        ('TERCEROS', 'CARGAR_DOCUMENTOS'),
        ('TERCEROS', 'DESCARGAR_DOCUMENTOS'),
        ('TERCEROS', 'VER_DOCUMENTOS'),
        ('TERCEROS', 'APROBAR_DOCUMENTOS'),
        ('TERCEROS', 'RECHAZAR_DOCUMENTOS'),
        ('TERCEROS', 'SELECCIONAR'),
        ('TERCEROS', 'VER_ARCHIVOS'),
        ('TERCEROS', 'ESCRIBIR_OBSERVACIONES'),
        ('TERCEROS', 'GUARDAR_CAMBIOS')
    ) AS permisos(modulo, permiso)
WHERE rol = 'ADMINISTRADOR'
ON CONFLICT (usuario_interno_id, modulo, permiso) DO NOTHING;

-- Trigger para actualizar fecha_actualizacion
CREATE OR REPLACE FUNCTION actualizar_fecha_actualizacion_usuario_interno()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_usuario_interno
    BEFORE UPDATE ON usuarios_internos
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_actualizacion_usuario_interno();

-- Vista para consultas rápidas de usuarios con permisos
CREATE OR REPLACE VIEW v_usuarios_con_permisos AS
SELECT 
    ui.id,
    ui.numero_identificacion,
    CONCAT(ui.primer_nombre, ' ', COALESCE(ui.segundo_nombre || ' ', ''), ui.primer_apellido, ' ', COALESCE(ui.segundo_apellido, '')) AS nombre_completo,
    ui.correo_electronico,
    ui.telefono,
    co.codigo AS codigo_co,
    co.nombre AS nombre_co,
    ui.usuario,
    ui.rol,
    ui.empresa,
    ui.activo,
    ui.invitacion_enviada,
    ui.ultimo_acceso,
    COUNT(pm.id) AS total_permisos,
    COUNT(CASE WHEN pm.activo = TRUE THEN 1 END) AS permisos_activos
FROM usuarios_internos ui
LEFT JOIN centros_operacion co ON ui.centro_operacion_id = co.id
LEFT JOIN permisos_modulos pm ON ui.id = pm.usuario_interno_id
GROUP BY ui.id, co.codigo, co.nombre;

COMMENT ON VIEW v_usuarios_con_permisos IS 'Vista consolidada de usuarios internos con conteo de permisos';
