-- =============================================
-- ?? SCHEMA COMPLETO DE MÓDULOS
-- Sistema de Gestión Documental
-- Supertiendas Cañaveral SAS
-- =============================================
-- Fecha de creación: Enero 2025
-- Base de datos: PostgreSQL 12+
-- Tablas: Módulos de Facturas, Relaciones, Archivo Digital, Causaciones, Configuración
-- =============================================

-- -------------------------------------------------
-- ??? LIMPIEZA PREVIA (OPCIONAL - CUIDADO EN PRODUCCIÓN)
-- -------------------------------------------------
-- DROP TABLE IF EXISTS observaciones_documentos CASCADE;
-- DROP TABLE IF EXISTS tokens_correccion_documento CASCADE;
-- DROP TABLE IF EXISTS historial_documentos CASCADE;
-- DROP TABLE IF EXISTS adjuntos_documentos CASCADE;
-- DROP TABLE IF EXISTS documentos_contables CASCADE;
-- DROP TABLE IF EXISTS observaciones_factura CASCADE;
-- DROP TABLE IF EXISTS observaciones_factura_temporal CASCADE;
-- DROP TABLE IF EXISTS facturas_recibidas CASCADE;
-- DROP TABLE IF EXISTS facturas_temporales CASCADE;
-- DROP TABLE IF EXISTS facturas_recibidas_digitales CASCADE;
-- DROP TABLE IF EXISTS recepciones_digitales CASCADE;
-- DROP TABLE IF EXISTS tokens_firma_digital CASCADE;
-- DROP TABLE IF EXISTS relaciones_facturas CASCADE;
-- DROP TABLE IF EXISTS observaciones_causacion CASCADE;
-- DROP TABLE IF EXISTS documentos_causacion CASCADE;
-- DROP TABLE IF EXISTS consecutivos CASCADE;
-- DROP TABLE IF EXISTS centros_operacion CASCADE;
-- DROP TABLE IF EXISTS tipos_documento CASCADE;

-- =================================================
-- MÓDULO: CONFIGURACIÓN (Catálogos Maestros)
-- =================================================

-- -------------------------------------------------
-- ?? TABLA: tipos_documento
-- Catálogo de tipos de documentos contables
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS tipos_documento (
    id SERIAL PRIMARY KEY,
    siglas VARCHAR(10) UNIQUE NOT NULL,  -- NOC, NCM, NTN, LEG, etc.
    nombre VARCHAR(100) NOT NULL,   -- Nota Contable, Nota Crédito, etc.
    descripcion TEXT,
    prefijo VARCHAR(10),-- Prefijo opcional para consecutivos
    requiere_aprobacion BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(50),
    updated_at TIMESTAMP
);

-- Índices para tipos_documento
CREATE INDEX idx_tipos_documento_siglas ON tipos_documento(siglas);
CREATE INDEX idx_tipos_documento_activo ON tipos_documento(activo);

COMMENT ON TABLE tipos_documento IS 'Catálogo maestro de tipos de documentos contables';

-- -------------------------------------------------
-- ?? TABLA: centros_operacion
-- Catálogo de centros de operación (tiendas, bodegas)
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS centros_operacion (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,     -- 001, 002, T001, B001, etc.
    nombre VARCHAR(200) NOT NULL,      -- SC PALMIRA CENTRO, BODEGA CENTRAL
    descripcion TEXT,
    tipo VARCHAR(50) DEFAULT 'tienda',     -- tienda, bodega, administrativo
    ciudad VARCHAR(100),
    direccion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP
);

-- Índices para centros_operacion
CREATE INDEX idx_centros_operacion_codigo ON centros_operacion(codigo);
CREATE INDEX idx_centros_operacion_tipo ON centros_operacion(tipo);
CREATE INDEX idx_centros_operacion_activo ON centros_operacion(activo);

COMMENT ON TABLE centros_operacion IS 'Catálogo maestro de centros de operación (tiendas, bodegas, almacenes)';

-- -------------------------------------------------
-- ?? TABLA: consecutivos
-- Control de numeración automática para documentos
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS consecutivos (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) UNIQUE NOT NULL,          -- relaciones, notas_contables, etc.
    tipo_documento VARCHAR(50) NOT NULL,  -- Para mapeo con tipos_documento
prefijo VARCHAR(10),     -- REL-, NOC-, NCM-
    ultimo_consecutivo INTEGER DEFAULT 0 NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para consecutivos
CREATE INDEX idx_consecutivos_tipo ON consecutivos(tipo);

COMMENT ON TABLE consecutivos IS 'Control de numeración secuencial para diferentes tipos de documentos';

-- =================================================
-- MÓDULO: RECIBIR FACTURAS
-- =================================================

-- -------------------------------------------------
-- ?? TABLA: facturas_temporales
-- Facturas en proceso de edición (no guardadas definitivamente)
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS facturas_temporales (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    nit_tercero VARCHAR(20) NOT NULL,
    razon_social VARCHAR(255),
    prefijo VARCHAR(10),
    folio VARCHAR(50),
    fecha_factura DATE,
    valor_factura NUMERIC(15, 2),
    centro_operacion_id INTEGER REFERENCES centros_operacion(id) ON DELETE SET NULL,
    centro_operacion VARCHAR(200),          -- Nombre del centro (desnormalizado)
    comprador VARCHAR(200),
    usuario_solicita VARCHAR(200),
    quien_recibe VARCHAR(200),
    fecha_radicacion DATE DEFAULT CURRENT_DATE,
    estado VARCHAR(20) DEFAULT 'temporal' CHECK (estado IN ('temporal', 'guardada')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP
);

-- Índices para facturas_temporales
CREATE INDEX idx_facturas_temporales_usuario ON facturas_temporales(usuario_id);
CREATE INDEX idx_facturas_temporales_nit ON facturas_temporales(nit_tercero);
CREATE INDEX idx_facturas_temporales_estado ON facturas_temporales(estado);
CREATE INDEX idx_facturas_temporales_fecha ON facturas_temporales(fecha_factura);

COMMENT ON TABLE facturas_temporales IS 'Facturas en edición temporal (no guardadas definitivamente)';

-- -------------------------------------------------
-- ?? TABLA: facturas_recibidas
-- Facturas guardadas permanentemente
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS facturas_recibidas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    nit_tercero VARCHAR(20) NOT NULL,
    razon_social VARCHAR(255),
  prefijo VARCHAR(10),
    folio VARCHAR(50),
  fecha_factura DATE,
    valor_factura NUMERIC(15, 2),
    centro_operacion_id INTEGER REFERENCES centros_operacion(id) ON DELETE SET NULL,
    centro_operacion VARCHAR(200),
    comprador VARCHAR(200),
    usuario_solicita VARCHAR(200),
    quien_recibe VARCHAR(200),
    fecha_radicacion DATE DEFAULT CURRENT_DATE,
    estado VARCHAR(20) DEFAULT 'recibida' CHECK (estado IN ('recibida', 'anulada', 'relacionada')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_guardado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP
);

-- Índices para facturas_recibidas
CREATE INDEX idx_facturas_recibidas_usuario ON facturas_recibidas(usuario_id);
CREATE INDEX idx_facturas_recibidas_nit ON facturas_recibidas(nit_tercero);
CREATE INDEX idx_facturas_recibidas_estado ON facturas_recibidas(estado);
CREATE INDEX idx_facturas_recibidas_fecha ON facturas_recibidas(fecha_factura);
CREATE INDEX idx_facturas_recibidas_prefijo_folio ON facturas_recibidas(prefijo, folio);

COMMENT ON TABLE facturas_recibidas IS 'Facturas guardadas permanentemente en el sistema';

-- -------------------------------------------------
-- ?? TABLA: observaciones_factura_temporal
-- Observaciones editables para facturas temporales
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS observaciones_factura_temporal (
    id SERIAL PRIMARY KEY,
    factura_temporal_id INTEGER NOT NULL REFERENCES facturas_temporales(id) ON DELETE CASCADE,
    observacion TEXT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para observaciones_factura_temporal
CREATE INDEX idx_obs_factura_temporal_factura ON observaciones_factura_temporal(factura_temporal_id);

COMMENT ON TABLE observaciones_factura_temporal IS 'Observaciones asociadas a facturas temporales (editables)';

-- -------------------------------------------------
-- ?? TABLA: observaciones_factura
-- Observaciones permanentes para facturas recibidas
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS observaciones_factura (
    id SERIAL PRIMARY KEY,
    factura_recibida_id INTEGER NOT NULL REFERENCES facturas_recibidas(id) ON DELETE CASCADE,
    observacion TEXT NOT NULL,
    usuario_creador VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para observaciones_factura
CREATE INDEX idx_obs_factura_factura ON observaciones_factura(factura_recibida_id);

COMMENT ON TABLE observaciones_factura IS 'Observaciones permanentes asociadas a facturas recibidas (auditoría)';

-- =================================================
-- MÓDULO: RELACIONES DE FACTURAS
-- =================================================

-- -------------------------------------------------
-- ?? TABLA: relaciones_facturas
-- Relaciones de facturas generadas
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS relaciones_facturas (
  id SERIAL PRIMARY KEY,
    numero_relacion VARCHAR(20) NOT NULL UNIQUE,        -- REL-001, REL-002, etc.
    fecha_generacion DATE NOT NULL DEFAULT CURRENT_DATE,
    para VARCHAR(50) NOT NULL CHECK (para IN ('CONTABILIDAD', 'PAGOS', 'SUMINISTROS', 'OTRO')),
    usuario VARCHAR(100) NOT NULL,
    
 -- Datos de la factura relacionada
    nit VARCHAR(20) NOT NULL,
 razon_social VARCHAR(255),
 prefijo VARCHAR(10) NOT NULL,
    folio VARCHAR(50) NOT NULL,
    co VARCHAR(10),  -- Centro de operación
    valor_total NUMERIC(15, 2),
    fecha_factura DATE, -- Fecha de radicación
    fecha_expedicion DATE,    -- Fecha de expedición
    
    -- Estado de recepción digital
    recibida BOOLEAN DEFAULT FALSE,
    usuario_check VARCHAR(100),
    fecha_check TIMESTAMP,
 
    -- Auditoría
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para relaciones_facturas
CREATE INDEX idx_relaciones_facturas_numero ON relaciones_facturas(numero_relacion);
CREATE INDEX idx_relaciones_facturas_nit ON relaciones_facturas(nit);
CREATE INDEX idx_relaciones_facturas_usuario ON relaciones_facturas(usuario);
CREATE INDEX idx_relaciones_facturas_prefijo_folio ON relaciones_facturas(prefijo, folio);
CREATE INDEX idx_relaciones_facturas_recibida ON relaciones_facturas(recibida);

COMMENT ON TABLE relaciones_facturas IS 'Histórico de relaciones de facturas generadas';

-- -------------------------------------------------
-- ?? TABLA: tokens_firma_digital
-- Tokens para validación de recepciones digitales
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS tokens_firma_digital (
    id SERIAL PRIMARY KEY,
    token VARCHAR(6) NOT NULL,    -- PIN de 6 dígitos
    usuario VARCHAR(100) NOT NULL,
    numero_relacion VARCHAR(20) NOT NULL,
    correo_destino VARCHAR(255),
  
    -- Validez del token
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
fecha_expiracion TIMESTAMP NOT NULL,           -- Validez 24 horas
    usado BOOLEAN DEFAULT FALSE,
    intentos_validacion INTEGER DEFAULT 0,
 fecha_uso TIMESTAMP,
    
    -- Auditoría
    ip_creacion VARCHAR(50),
 ip_uso VARCHAR(50)
);

-- Índices para tokens_firma_digital
CREATE INDEX idx_tokens_firma_token ON tokens_firma_digital(token);
CREATE INDEX idx_tokens_firma_usuario ON tokens_firma_digital(usuario);
CREATE INDEX idx_tokens_firma_relacion ON tokens_firma_digital(numero_relacion);

COMMENT ON TABLE tokens_firma_digital IS 'Tokens de validación para firmas digitales de recepciones';

-- -------------------------------------------------
-- ? TABLA: recepciones_digitales
-- Auditoría de recepciones digitales de relaciones
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS recepciones_digitales (
  id SERIAL PRIMARY KEY,
    numero_relacion VARCHAR(20) NOT NULL,
    
    -- Datos del receptor
    usuario_receptor VARCHAR(100) NOT NULL,
    nombre_receptor VARCHAR(255),
    
    -- Datos de la recepción
    fecha_recepcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_recepcion VARCHAR(50),
    user_agent TEXT,
    
    -- Estado de recepción
    facturas_recibidas INTEGER DEFAULT 0,
    facturas_totales INTEGER DEFAULT 0,
    completa BOOLEAN DEFAULT FALSE,
    
    -- Firma digital
    firma_digital VARCHAR(255),   -- Hash SHA256
    
    -- Auditoría
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para recepciones_digitales
CREATE INDEX idx_recepciones_digitales_relacion ON recepciones_digitales(numero_relacion);
CREATE INDEX idx_recepciones_digitales_usuario ON recepciones_digitales(usuario_receptor);
CREATE INDEX idx_recepciones_digitales_fecha ON recepciones_digitales(fecha_recepcion);

COMMENT ON TABLE recepciones_digitales IS 'Auditoría completa de recepciones digitales de relaciones';

-- -------------------------------------------------
-- ?? TABLA: facturas_recibidas_digitales
-- Detalle de facturas recibidas digitalmente
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS facturas_recibidas_digitales (
    id SERIAL PRIMARY KEY,
    recepcion_id INTEGER REFERENCES recepciones_digitales(id) ON DELETE CASCADE,
    numero_relacion VARCHAR(20) NOT NULL,
    
    -- Datos de la factura
    nit VARCHAR(20) NOT NULL,
    razon_social VARCHAR(255),
    prefijo VARCHAR(10) NOT NULL,
    folio VARCHAR(50) NOT NULL,
    co VARCHAR(10),
    valor_total NUMERIC(15, 2),
    fecha_factura DATE,
    
    -- Datos de recepción
  recibida BOOLEAN DEFAULT FALSE,
    fecha_check TIMESTAMP,
  usuario_check VARCHAR(100),
    observaciones TEXT,
    
    -- Auditoría
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para facturas_recibidas_digitales
CREATE INDEX idx_facturas_digitales_recepcion ON facturas_recibidas_digitales(recepcion_id);
CREATE INDEX idx_facturas_digitales_relacion ON facturas_recibidas_digitales(numero_relacion);
CREATE INDEX idx_facturas_digitales_nit ON facturas_recibidas_digitales(nit);

COMMENT ON TABLE facturas_recibidas_digitales IS 'Detalle de cada factura recibida en recepciones digitales';

-- =================================================
-- MÓDULO: ARCHIVO DIGITAL / NOTAS CONTABLES
-- =================================================

-- -------------------------------------------------
-- ?? TABLA: documentos_contables
-- Registro principal de documentos contables
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS documentos_contables (
    id SERIAL PRIMARY KEY,
  tipo_documento_id INTEGER NOT NULL REFERENCES tipos_documento(id),
    centro_operacion_id INTEGER NOT NULL REFERENCES centros_operacion(id),
    consecutivo VARCHAR(20) NOT NULL,  -- 00000001, 00000002, etc.
    fecha_documento DATE NOT NULL,
    empresa VARCHAR(10) NOT NULL CHECK (empresa IN ('SC', 'LG')),  -- Supertiendas o Legran
    nombre_archivo VARCHAR(255) NOT NULL,        -- CO-TIPO-CONSEC.pdf
    ruta_archivo VARCHAR(500) NOT NULL,
    observaciones TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo' CHECK (estado IN ('activo', 'anulado', 'eliminado')),
    
    -- Auditoría
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(50),
    updated_at TIMESTAMP,
    
    -- Constraint único: un solo documento por tipo+centro+consecutivo
    CONSTRAINT uq_tipo_centro_consecutivo UNIQUE (tipo_documento_id, centro_operacion_id, consecutivo)
);

-- Índices para documentos_contables
CREATE INDEX idx_documentos_contables_tipo ON documentos_contables(tipo_documento_id);
CREATE INDEX idx_documentos_contables_centro ON documentos_contables(centro_operacion_id);
CREATE INDEX idx_documentos_contables_fecha ON documentos_contables(fecha_documento);
CREATE INDEX idx_documentos_contables_estado ON documentos_contables(estado);
CREATE INDEX idx_documentos_contables_empresa ON documentos_contables(empresa);
CREATE INDEX idx_documentos_contables_created_by ON documentos_contables(created_by);

COMMENT ON TABLE documentos_contables IS 'Registro principal de documentos contables cargados en el sistema';

-- -------------------------------------------------
-- ?? TABLA: adjuntos_documentos
-- Archivos adicionales asociados a documentos contables
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS adjuntos_documentos (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documentos_contables(id) ON DELETE CASCADE,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    tipo_archivo VARCHAR(50),     -- xlsx, jpg, png, etc.
 tamano_bytes INTEGER,
    descripcion VARCHAR(255),
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para adjuntos_documentos
CREATE INDEX idx_adjuntos_documentos_documento ON adjuntos_documentos(documento_id);

COMMENT ON TABLE adjuntos_documentos IS 'Archivos adicionales (Excel, imágenes) asociados a documentos contables';

-- -------------------------------------------------
-- ?? TABLA: historial_documentos
-- Auditoría completa de cambios en documentos
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS historial_documentos (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documentos_contables(id) ON DELETE CASCADE,
accion VARCHAR(50) NOT NULL CHECK (accion IN ('CREADO', 'EDITADO', 'ANULADO', 'ELIMINADO', 'VISUALIZADO')),
    campo_modificado VARCHAR(100),
    valor_anterior TEXT,
    valor_nuevo TEXT,
    motivo TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para historial_documentos
CREATE INDEX idx_historial_documentos_documento ON historial_documentos(documento_id);
CREATE INDEX idx_historial_documentos_accion ON historial_documentos(accion);
CREATE INDEX idx_historial_documentos_fecha ON historial_documentos(created_at);

COMMENT ON TABLE historial_documentos IS 'Auditoría completa de todos los cambios realizados a documentos contables';

-- -------------------------------------------------
-- ?? TABLA: observaciones_documentos
-- Observaciones con auditoría para documentos contables
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS observaciones_documentos (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documentos_contables(id) ON DELETE CASCADE,
    observacion TEXT NOT NULL,
    momento VARCHAR(20) NOT NULL CHECK (momento IN ('CARGA', 'EDICION')),
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para observaciones_documentos
CREATE INDEX idx_observaciones_documentos_documento ON observaciones_documentos(documento_id);

COMMENT ON TABLE observaciones_documentos IS 'Observaciones con auditoría completa para documentos contables';

-- -------------------------------------------------
-- ?? TABLA: tokens_correccion_documento
-- Tokens de validación para correcciones críticas
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS tokens_correccion_documento (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documentos_contables(id) ON DELETE CASCADE,
    token VARCHAR(6) NOT NULL,        -- Código de 6 dígitos
    
    -- Campos que se van a cambiar
    empresa_anterior VARCHAR(10),
    empresa_nueva VARCHAR(10),
    tipo_documento_anterior_id INTEGER,
    tipo_documento_nuevo_id INTEGER,
    centro_operacion_anterior_id INTEGER,
    centro_operacion_nuevo_id INTEGER,
    consecutivo_anterior VARCHAR(20),
    consecutivo_nuevo VARCHAR(20),
    fecha_documento_anterior DATE,
    fecha_documento_nueva DATE,
  
    -- Justificación
    justificacion TEXT NOT NULL,
    
    -- Control de validación
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL,       -- +10 minutos
    intentos_validacion INTEGER DEFAULT 0,
    usado BOOLEAN DEFAULT FALSE,
    fecha_uso TIMESTAMP,
  
    -- Auditoría
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_by VARCHAR(50) NOT NULL,
    validado_por VARCHAR(50)
);

-- Índices para tokens_correccion_documento
CREATE INDEX idx_tokens_correccion_documento_doc ON tokens_correccion_documento(documento_id);
CREATE INDEX idx_tokens_correccion_documento_token ON tokens_correccion_documento(token);

COMMENT ON TABLE tokens_correccion_documento IS 'Tokens de validación para correcciones de campos críticos en documentos';

-- =================================================
-- MÓDULO: CAUSACIONES
-- =================================================

-- -------------------------------------------------
-- ?? TABLA: documentos_causacion
-- Documentos de causación contable
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS documentos_causacion (
    id SERIAL PRIMARY KEY,
    tipo_documento VARCHAR(50) NOT NULL,         -- CAUSACION, COMPROBANTE, etc.
  numero_documento VARCHAR(50) NOT NULL,
    fecha_causacion DATE NOT NULL,
    tercero_nit VARCHAR(20),
    tercero_razon_social VARCHAR(255),
    valor_total NUMERIC(15, 2),
    centro_operacion_id INTEGER REFERENCES centros_operacion(id) ON DELETE SET NULL,
    estado VARCHAR(20) DEFAULT 'activa' CHECK (estado IN ('activa', 'anulada', 'contabilizada')),
    
    -- Archivos asociados
    ruta_pdf VARCHAR(500),
 ruta_adjuntos TEXT,         -- JSON con rutas de adjuntos
    
    -- Auditoría
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(50),
    updated_at TIMESTAMP
);

-- Índices para documentos_causacion
CREATE INDEX idx_documentos_causacion_numero ON documentos_causacion(numero_documento);
CREATE INDEX idx_documentos_causacion_fecha ON documentos_causacion(fecha_causacion);
CREATE INDEX idx_documentos_causacion_tercero ON documentos_causacion(tercero_nit);
CREATE INDEX idx_documentos_causacion_estado ON documentos_causacion(estado);

COMMENT ON TABLE documentos_causacion IS 'Documentos de causación contable';

-- -------------------------------------------------
-- ?? TABLA: observaciones_causacion
-- Observaciones para documentos de causación
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS observaciones_causacion (
    id SERIAL PRIMARY KEY,
    documento_causacion_id INTEGER NOT NULL REFERENCES documentos_causacion(id) ON DELETE CASCADE,
 observacion TEXT NOT NULL,
 created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para observaciones_causacion
CREATE INDEX idx_observaciones_causacion_documento ON observaciones_causacion(documento_causacion_id);

COMMENT ON TABLE observaciones_causacion IS 'Observaciones asociadas a documentos de causación';

-- =================================================
-- FUNCIONES Y TRIGGERS
-- =================================================

-- Función para actualizar timestamps automáticamente
CREATE OR REPLACE FUNCTION actualizar_timestamp_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para actualización de timestamps
DROP TRIGGER IF EXISTS trigger_update_facturas_temporales ON facturas_temporales;
CREATE TRIGGER trigger_update_facturas_temporales
 BEFORE UPDATE ON facturas_temporales
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_timestamp_modificacion();

DROP TRIGGER IF EXISTS trigger_update_facturas_recibidas ON facturas_recibidas;
CREATE TRIGGER trigger_update_facturas_recibidas
    BEFORE UPDATE ON facturas_recibidas
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_timestamp_modificacion();

DROP TRIGGER IF EXISTS trigger_update_documentos_contables ON documentos_contables;
CREATE TRIGGER trigger_update_documentos_contables
    BEFORE UPDATE ON documentos_contables
    FOR EACH ROW
 EXECUTE FUNCTION actualizar_timestamp_modificacion();

-- =================================================
-- DATOS INICIALES (SEEDS)
-- =================================================

-- Insertar tipos de documento por defecto
INSERT INTO tipos_documento (siglas, nombre, descripcion, prefijo, activo) VALUES
('NOC', 'Nota Contable', 'Notas contables generales', 'NOC-', TRUE),
('NCM', 'Nota Crédito Mercancía', 'Notas de crédito por devolución de mercancía', 'NCM-', TRUE),
('NTN', 'Nota Nomina', 'Notas de nómina', 'NTN-', TRUE),
('LEG', 'Legalizaciones', 'Documentos de legalización de gastos', 'LEG-', TRUE),
('CMP', 'Comprobante de Egreso', 'Comprobantes de egreso', 'CMP-', TRUE)
ON CONFLICT (siglas) DO NOTHING;

-- Insertar centros de operación por defecto
INSERT INTO centros_operacion (codigo, nombre, tipo, ciudad, activo) VALUES
('001', 'SC PALMIRA CENTRO', 'tienda', 'PALMIRA', TRUE),
('002', 'SC GUACARÍ', 'tienda', 'GUACARÍ', TRUE),
('003', 'SC MIRANDA', 'tienda', 'MIRANDA', TRUE),
('B001', 'BODEGA CENTRAL', 'bodega', 'PALMIRA', TRUE),
('A001', 'ADMINISTRATIVO', 'administrativo', 'PALMIRA', TRUE)
ON CONFLICT (codigo) DO NOTHING;

-- Insertar consecutivos iniciales
INSERT INTO consecutivos (tipo, tipo_documento, prefijo, ultimo_consecutivo) VALUES
('relaciones', 'RELACION', 'REL-', 0),
('notas_contables', 'NOTA_CONTABLE', 'NOC-', 0),
('causaciones', 'CAUSACION', 'CAU-', 0)
ON CONFLICT (tipo) DO NOTHING;

-- =================================================
-- PERMISOS DE USUARIO
-- =================================================

-- Dar permisos completos al usuario gestor_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gestor_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gestor_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO gestor_user;

-- =================================================
-- VERIFICACIÓN FINAL
-- =================================================

-- Listar todas las tablas creadas
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename NOT IN ('terceros', 'usuarios', 'accesos', 'ips_sospechosas', 'ips_negras', 'ips_blancas', 
 'solicitudes_registro', 'documentos_tercero', 'tokens_recuperacion', 'contrasenas_usadas')
ORDER BY tablename;

-- Mostrar estadísticas
SELECT 
    'Tipos Documento' as tabla, COUNT(*) as registros FROM tipos_documento
UNION ALL
SELECT 'Centros Operación', COUNT(*) FROM centros_operacion
UNION ALL
SELECT 'Consecutivos', COUNT(*) FROM consecutivos
UNION ALL
SELECT 'Facturas Temporales', COUNT(*) FROM facturas_temporales
UNION ALL
SELECT 'Facturas Recibidas', COUNT(*) FROM facturas_recibidas
UNION ALL
SELECT 'Relaciones Facturas', COUNT(*) FROM relaciones_facturas
UNION ALL
SELECT 'Documentos Contables', COUNT(*) FROM documentos_contables
UNION ALL
SELECT 'Documentos Causación', COUNT(*) FROM documentos_causacion;

-- =================================================
-- ?? NOTAS IMPORTANTES
-- =================================================
/*
1. ORDEN DE EJECUCIÓN:
   - Ejecutar primero: schema_completo.sql (tablas core)
   - Luego ejecutar: schema_modulos_completo.sql (este archivo)

2. MÓDULOS INCLUIDOS:
   ? Configuración (tipos_documento, centros_operacion, consecutivos)
   ? Recibir Facturas (facturas_temporales, facturas_recibidas, observaciones)
   ? Relaciones (relaciones_facturas, recepciones_digitales, tokens_firma)
   ? Archivo Digital (documentos_contables, adjuntos, historial)
   ? Causaciones (documentos_causacion, observaciones_causacion)

3. TOTAL DE TABLAS EN ESTE SCRIPT: 21 tablas

4. RELACIONES:
   - tipos_documento ? documentos_contables
   - centros_operacion ? facturas_recibidas, documentos_contables, documentos_causacion
   - usuarios (tabla core) ? facturas_temporales, facturas_recibidas

5. AUDITORÍA:
   - Todas las tablas incluyen timestamps de creación/modificación
   - Historial completo de cambios en documentos
   - Registro de IP y user agent en operaciones críticas

6. MANTENIMIENTO:
   - Limpiar tokens expirados periódicamente:
     DELETE FROM tokens_firma_digital WHERE fecha_expiracion < CURRENT_TIMESTAMP AND usado = TRUE;
  DELETE FROM tokens_correccion_documento WHERE fecha_expiracion < CURRENT_TIMESTAMP AND usado = TRUE;
   
   - Archivar facturas temporales antiguas (más de 30 días):
     DELETE FROM facturas_temporales WHERE fecha_creacion < CURRENT_TIMESTAMP - INTERVAL '30 days';

7. BACKUP:
   - Realizar backups diarios incluyendo estas tablas
   - Comando: pg_dump -U gestor_user gestor_documental --table=facturas_recibidas --table=documentos_contables > backup_modulos.sql
*/
