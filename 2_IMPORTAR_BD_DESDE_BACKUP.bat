@echo off
echo =========================================================
echo   PASO 2: IMPORTAR BASE DE DATOS EN ESTE EQUIPO
echo   Este script importa el backup de PostgreSQL
echo =========================================================
echo.

REM Buscar carpetas de exportación
echo Buscando carpetas de backup...
echo.

for /d %%D in (EXPORT_BD_*) do (
    echo Encontrada: %%D
    set CARPETA_BACKUP=%%D
)

if not defined CARPETA_BACKUP (
    echo ❌ ERROR: No se encontro ninguna carpeta EXPORT_BD_*
    echo.
    echo Asegurate de:
    echo   1. Haber ejecutado 1_EXPORTAR_BD_PARA_OTRO_EQUIPO.bat en el otro equipo
    echo   2. Copiar la carpeta EXPORT_BD_* a este proyecto
    echo.
    pause
    exit /b 1
)

echo.
echo Usando backup: %CARPETA_BACKUP%
echo.

REM Verificar que existe el archivo SQL
if not exist "%CARPETA_BACKUP%\backup_completo.sql" (
    echo ❌ ERROR: No se encontro backup_completo.sql en %CARPETA_BACKUP%
    echo.
    pause
    exit /b 1
)

echo =========================================================
echo   CONFIGURACION REQUERIDA
echo =========================================================
echo.
echo Antes de continuar, asegurate de:
echo   [✓] PostgreSQL esta instalado en este equipo
echo   [✓] Conoces la contraseña del usuario 'postgres'
echo   [✓] El archivo .env tiene la configuracion correcta
echo.
set /p CONTINUAR="¿Continuar con la importacion? (S/N): "
if /i not "%CONTINUAR%"=="S" (
    echo.
    echo Importacion cancelada.
    pause
    exit /b 0
)

echo.
echo =========================================================
echo   IMPORTANDO BASE DE DATOS
echo =========================================================
echo.

REM Pedir contraseña de PostgreSQL
set /p PGPASSWORD="Ingresa la contraseña de PostgreSQL (usuario postgres): "
echo.

REM Exportar contraseña como variable de entorno
set PGPASSWORD=%PGPASSWORD%

REM Extraer nombre de base de datos del .env
for /f "tokens=2 delims=/" %%A in ('findstr "DATABASE_URL" .env') do (
    for /f "tokens=1" %%B in ("%%A") do set DBNAME=%%B
)

echo [1/3] Creando base de datos: %DBNAME%
psql -U postgres -c "CREATE DATABASE %DBNAME%;" 2>nul

echo [2/3] Importando estructura y datos...
echo       (Esto puede tardar varios minutos)
echo.

psql -U postgres -d %DBNAME% -f "%CARPETA_BACKUP%\backup_completo.sql"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [3/3] Verificando importacion...
    psql -U postgres -d %DBNAME% -c "\dt"
    
    echo.
    echo =========================================================
    echo   IMPORTACION EXITOSA
    echo =========================================================
    echo.
    echo La base de datos se importo correctamente.
    echo.
    echo PROXIMOS PASOS:
    echo   1. Verifica el archivo .env tenga la configuracion correcta
    echo   2. Instala las dependencias: pip install -r requirements.txt
    echo   3. Inicia la aplicacion: 1_iniciar_gestor.bat
    echo.
) else (
    echo.
    echo =========================================================
    echo   ERROR EN LA IMPORTACION
    echo =========================================================
    echo.
    echo Verifica:
    echo   - La contraseña de PostgreSQL es correcta
    echo   - PostgreSQL esta corriendo
    echo   - Tienes permisos de escritura
    echo   - El archivo .env tiene DATABASE_URL correcto
    echo.
)

REM Limpiar contraseña
set PGPASSWORD=

echo.
pause
