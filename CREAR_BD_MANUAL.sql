-- ========================================================
-- SCRIPT DE INSTALACIÓN MANUAL - GESTOR DOCUMENTAL
-- ========================================================
-- Ejecutar este script en pgAdmin 4 o psql como usuario postgres
-- 
-- INSTRUCCIONES:
-- 1. Abrir pgAdmin 4
-- 2. Conectarse a PostgreSQL 18 (puerto 5432)
-- 3. Click derecho en "Databases" -> "Query Tool"
-- 4. Pegar este script y ejecutar (F5)
-- ========================================================

-- Paso 1: Crear la base de datos
CREATE DATABASE gestor_documental
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Spanish_Spain.1252'
    LC_CTYPE = 'Spanish_Spain.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

COMMENT ON DATABASE gestor_documental
    IS 'Base de datos para el sistema Gestor Documental de Supertiendas Cañaveral';

-- Paso 2: Crear el usuario gestor_user (si no existe)
DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'gestor_user') THEN
        CREATE USER gestor_user WITH PASSWORD 'admin2025*';
    END IF;
END
$$;

-- Paso 3: Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE gestor_documental TO gestor_user;

-- ========================================================
-- NOTA IMPORTANTE:
-- ========================================================
-- Después de ejecutar este script:
--
-- 1. Cerrar pgAdmin o esta ventana de Query
--
-- 2. Conectarse a la base de datos "gestor_documental"
--    (Click derecho -> Connect)
--
-- 3. Restaurar el backup usando pgAdmin:
--    a. Click derecho en "gestor_documental" -> Restore
--    b. Seleccionar archivo: backup_gestor_documental.backup
--    c. Click en "Restore"
--
-- O desde línea de comandos (PowerShell):
--    cd "C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
--    $env:PGPASSWORD="admin2025*"
--    & "C:\Program Files\PostgreSQL\18\bin\pg_restore.exe" -U gestor_user -d gestor_documental -v backup_gestor_documental.backup
--
-- 4. Iniciar el servidor Flask:
--    .\.venv\Scripts\activate
--    python app.py
--
-- 5. Abrir navegador en: http://localhost:8099
-- ========================================================
