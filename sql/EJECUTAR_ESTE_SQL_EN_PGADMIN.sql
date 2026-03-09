-- ===============================================
-- SCRIPT SQL PARA EJECUTAR EN pgAdmin o psql
-- Fecha: Octubre 21, 2025
-- ===============================================

-- PASO 1: Cambiar contraseña del usuario (EJECUTAR COMO USUARIO postgres)
-- ===============================================
ALTER USER gestor_user WITH PASSWORD 'ricardo2025';

-- Verificar que se cambió correctamente
\du gestor_user


-- PASO 2: Agregar columna 'tipo' a la tabla consecutivos
-- ===============================================

-- Verificar si la columna ya existe
SELECT column_name 
FROM information_schema.columns 
WHERE table_name='consecutivos' AND column_name='tipo';

-- Si NO existe (resultado vacío), ejecutar los siguientes comandos:

-- 2.1. Agregar columna con valor por defecto temporal
ALTER TABLE consecutivos 
ADD COLUMN tipo VARCHAR(50) DEFAULT 'relaciones';

-- 2.2. Actualizar registros existentes
UPDATE consecutivos 
SET tipo = 'relaciones' 
WHERE tipo IS NULL OR tipo = '';

-- 2.3. Agregar constraint UNIQUE
ALTER TABLE consecutivos 
ADD CONSTRAINT consecutivos_tipo_unique UNIQUE (tipo);

-- 2.4. Remover DEFAULT (ya no necesario)
ALTER TABLE consecutivos 
ALTER COLUMN tipo DROP DEFAULT;

-- 2.5. Hacer columna NOT NULL
ALTER TABLE consecutivos 
ALTER COLUMN tipo SET NOT NULL;


-- PASO 3: Verificar estructura de la tabla
-- ===============================================
SELECT 
    column_name, 
    data_type, 
    character_maximum_length, 
    is_nullable
FROM information_schema.columns 
WHERE table_name='consecutivos'
ORDER BY ordinal_position;


-- PASO 4: Verificar o insertar consecutivo inicial
-- ===============================================

-- Ver consecutivos actuales
SELECT * FROM consecutivos;

-- Si NO existe el registro para 'relaciones', ejecutar:
INSERT INTO consecutivos (tipo, prefijo, ultimo_numero) 
VALUES ('relaciones', 'REL', 11)
ON CONFLICT (tipo) DO NOTHING;

-- Verificar que quedó bien
SELECT * FROM consecutivos WHERE tipo = 'relaciones';


-- ===============================================
-- FIN DEL SCRIPT
-- ===============================================

-- NOTAS IMPORTANTES:
-- 1. Ejecuta PASO 1 primero como usuario postgres
-- 2. Luego ejecuta PASO 2, 3 y 4 en orden
-- 3. Después actualiza el archivo .env con la nueva contraseña
-- 4. Reinicia la aplicación Flask: python app.py
