-- ====================================================
-- SISTEMA DE CARGA AUTOMÁTICA DE ARCHIVOS
-- Fecha: 30 de Diciembre de 2025
-- Propósito: Registrar archivos procesados y configurar rutas
-- ====================================================

-- TABLA 1: Registro de archivos procesados
CREATE TABLE IF NOT EXISTS archivos_procesados (
    id SERIAL PRIMARY KEY,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_completa TEXT NOT NULL,
    carpeta_origen VARCHAR(100) NOT NULL,  -- 'DIAN', 'ERP_FINANCIERO', 'ERP_COMERCIAL', 'ACUSES', 'ERRORES_ERP'
    hash_md5 VARCHAR(32) NOT NULL UNIQUE,  -- Para detectar duplicados
    fecha_procesamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    registros_insertados INTEGER DEFAULT 0,
    registros_duplicados INTEGER DEFAULT 0,
    tiempo_proceso_segundos NUMERIC(10, 2),
    usuario_proceso VARCHAR(100),
    nit_empresa VARCHAR(20),
    estado VARCHAR(50) DEFAULT 'COMPLETADO',  -- 'COMPLETADO', 'ERROR', 'PARCIAL'
    mensaje_error TEXT,
    CONSTRAINT uq_hash_archivo UNIQUE (hash_md5)
);

-- TABLA 2: Configuración de rutas de carga
CREATE TABLE IF NOT EXISTS configuracion_rutas_carga (
    id SERIAL PRIMARY KEY,
    nombre_carpeta VARCHAR(100) NOT NULL UNIQUE,  -- 'DIAN', 'ERP_FINANCIERO', etc.
    ruta_pendientes TEXT NOT NULL,
    ruta_procesados TEXT,  -- Opcional: carpeta donde mover archivos procesados
    activa BOOLEAN DEFAULT TRUE,
    tipo_archivo VARCHAR(50) NOT NULL,  -- 'dian', 'erp_financiero', 'erp_comercial', 'acuses', 'errores_erp'
    extensiones_permitidas VARCHAR(100) DEFAULT '.xlsx,.xlsm,.csv,.ods',  -- Sin .xls por archivos corruptos
    orden_procesamiento INTEGER DEFAULT 999,  -- Para ordenar el procesamiento
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(100),
    nit_empresa VARCHAR(20)
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_archivos_hash ON archivos_procesados(hash_md5);
CREATE INDEX IF NOT EXISTS idx_archivos_carpeta ON archivos_procesados(carpeta_origen);
CREATE INDEX IF NOT EXISTS idx_archivos_fecha ON archivos_procesados(fecha_procesamiento);
CREATE INDEX IF NOT EXISTS idx_archivos_estado ON archivos_procesados(estado);
CREATE INDEX IF NOT EXISTS idx_rutas_activa ON configuracion_rutas_carga(activa);
CREATE INDEX IF NOT EXISTS idx_rutas_tipo ON configuracion_rutas_carga(tipo_archivo);

-- Insertar configuraciones por defecto
INSERT INTO configuracion_rutas_carga 
    (nombre_carpeta, ruta_pendientes, ruta_procesados, tipo_archivo, orden_procesamiento, descripcion, usuario_creacion, nit_empresa)
VALUES 
    ('DIAN', 
     'D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\Dian',
     'D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\Dian\Procesados',
     'dian', 
     1, 
     'Facturas electrónicas de DIAN - Se procesa primero',
     'SISTEMA',
     NULL),
     
    ('ERP_FINANCIERO',
     'D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\ERP Financiero',
     'D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\ERP Financiero\Procesados',
     'erp_financiero',
     2,
     'Datos del módulo financiero del ERP',
     'SISTEMA',
     NULL),
     
    ('ERP_COMERCIAL',
     'D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\ERP Comercial',
     'D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\ERP Comercial\Procesados',
     'erp_comercial',
     3,
     'Datos del módulo comercial del ERP',
     'SISTEMA',
     NULL),
     
    ('ACUSES',
     'D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\Acuses',
     'D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\Acuses\Procesados',
     'acuses',
     4,
     'Acuses de recibo de facturas electrónicas',
     'SISTEMA',
     NULL),
     
    ('ERRORES_ERP',
     'D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\RG_ERP_Errores',
     'D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\RG_ERP_Errores\Procesados',
     'errores_erp',
     5,
     'Registros de errores del ERP',
     'SISTEMA',
     NULL)
ON CONFLICT (nombre_carpeta) DO NOTHING;

-- Comentarios
COMMENT ON TABLE archivos_procesados IS 'Registro histórico de todos los archivos procesados en el sistema DIAN vs ERP';
COMMENT ON TABLE configuracion_rutas_carga IS 'Configuración de carpetas donde el sistema busca archivos para cargar automáticamente';

COMMENT ON COLUMN archivos_procesados.hash_md5 IS 'Hash MD5 del contenido del archivo para detectar duplicados';
COMMENT ON COLUMN archivos_procesados.carpeta_origen IS 'Tipo de carpeta: DIAN, ERP_FINANCIERO, ERP_COMERCIAL, ACUSES, ERRORES_ERP';
COMMENT ON COLUMN archivos_procesados.estado IS 'COMPLETADO: sin errores, ERROR: falló completamente, PARCIAL: cargó con warnings';
COMMENT ON COLUMN configuracion_rutas_carga.activa IS 'Si FALSE, no se procesarán archivos de esta carpeta';
COMMENT ON COLUMN configuracion_rutas_carga.orden_procesamiento IS 'Orden en que se procesan las carpetas (1=primero)';
