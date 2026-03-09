@echo off
REM ========================================================
REM INSTALACION SIMPLIFICADA - GESTOR DOCUMENTAL
REM ========================================================
echo.
echo ========================================================
echo   INSTALACION - GESTOR DOCUMENTAL
echo ========================================================
echo.

set POSTGRES_PATH=C:\Program Files\PostgreSQL\18\bin
set DB_NAME=gestor_documental

echo [PASO 1/5] Creando base de datos...
echo.
echo Se te pedira la contrasena de PostgreSQL (usuario: postgres)
"%POSTGRES_PATH%\createdb.exe" -U postgres %DB_NAME%
if errorlevel 1 (
    echo.
    echo NOTA: Si la base de datos ya existe, continuaremos con la restauracion.
    echo.
)

echo.
echo [PASO 2/5] Restaurando backup de datos...
echo.
"%POSTGRES_PATH%\pg_restore.exe" -U postgres -d %DB_NAME% -v backup_gestor_documental.backup
if errorlevel 1 (
    echo.
    echo ADVERTENCIA: Hubo algunos errores al restaurar el backup.
    echo Esto puede ser normal si algunas tablas ya existen.
    echo.
)

echo.
echo [PASO 3/5] Actualizando archivo .env...
if not exist .env (
    copy .env.example .env
    echo Archivo .env creado desde .env.example
) else (
    echo Archivo .env ya existe, no se modificara
)

echo.
echo [PASO 4/5] Verificando instalacion...
echo Tablas en la base de datos:
"%POSTGRES_PATH%\psql.exe" -U postgres -d %DB_NAME% -c "\dt"

echo.
echo [PASO 5/5] Actualizando esquema con Python...
call .venv\Scripts\activate.bat
python update_tables.py

echo.
echo ========================================================
echo   INSTALACION COMPLETADA
echo ========================================================
echo.
echo PROXIMOS PASOS:
echo 1. Editar el archivo .env con tus configuraciones
echo    (especialmente DATABASE_URL con tu contrasena de PostgreSQL)
echo.
echo 2. Iniciar el servidor:
echo    iniciar_servidor.bat
echo.
echo 3. Abrir en navegador:
echo    http://localhost:8099
echo.
echo 4. Verificar usuarios:
echo    python check_user_status.py
echo.
pause
