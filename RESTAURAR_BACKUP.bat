@echo off
REM Script de Restauración - Backup Completo Gestor Documental
REM Generado: 26/12/2025 22:04:49

echo ============================================
echo RESTAURACION DE BACKUP - GESTOR DOCUMENTAL
echo ============================================
echo.

REM 1. Extraer archivo ZIP
echo [1/3] Extrayendo archivos...
powershell -Command "Expand-Archive -Path 'BACKUP_COMPLETO_20251226_220449.zip' -DestinationPath 'restauracion_temp' -Force"
if errorlevel 1 (
    echo ERROR: No se pudo extraer el archivo ZIP
    pause
    exit /b 1
)
echo OK: Archivos extraidos

REM 2. Buscar archivo .backup de PostgreSQL
echo.
echo [2/3] Buscando backup de base de datos...
for %%f in (restauracion_temp\*.backup) do set BACKUP_FILE=%%f
if not defined BACKUP_FILE (
    echo ERROR: No se encontro archivo .backup
    pause
    exit /b 1
)
echo OK: Backup encontrado: %BACKUP_FILE%

REM 3. Restaurar base de datos
echo.
echo [3/3] Restaurando base de datos PostgreSQL...
echo IMPORTANTE: Esto sobreescribira la base de datos actual
set /p confirmar="¿Desea continuar? (S/N): "
if /i not "%confirmar%"=="S" (
    echo Restauracion cancelada por el usuario
    pause
    exit /b 0
)

REM Crear nueva BD si no existe
psql -U postgres -c "DROP DATABASE IF EXISTS gestor_documental;"
psql -U postgres -c "CREATE DATABASE gestor_documental OWNER gestor_user;"

REM Restaurar backup
pg_restore -U gestor_user -d gestor_documental -v "%BACKUP_FILE%"
if errorlevel 1 (
    echo ERROR: Fallo la restauracion de la base de datos
    pause
    exit /b 1
)

echo.
echo ============================================
echo RESTAURACION COMPLETADA EXITOSAMENTE
echo ============================================
echo.
echo Archivos restaurados en: restauracion_temp\
echo Base de datos restaurada: gestor_documental
echo.
echo Proximos pasos:
echo 1. Copiar archivos de restauracion_temp\ a tu directorio de trabajo
echo 2. Instalar dependencias: pip install -r requirements.txt
echo 3. Verificar archivo .env con configuraciones
echo 4. Iniciar servidor: python app.py
echo.
pause
