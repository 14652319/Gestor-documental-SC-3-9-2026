@echo off
REM ========================================
REM BACKUP MANUAL DE BASE DE DATOS POSTGRESQL
REM Gestor Documental - 26 Diciembre 2025
REM ========================================

echo ============================================
echo BACKUP BASE DE DATOS - GESTOR DOCUMENTAL
echo ============================================
echo.

REM Configurar PATH de PostgreSQL (ajustar según instalación)
set PGPATH=C:\Program Files\PostgreSQL\18\bin
if exist "%PGPATH%\pg_dump.exe" (
    set PATH=%PATH%;%PGPATH%
    echo [OK] PostgreSQL encontrado en: %PGPATH%
) else (
    echo [WARNING] PostgreSQL no encontrado en la ubicación por defecto
    echo Por favor, agrega pg_dump.exe al PATH o ajusta la variable PGPATH en este script
    echo.
    echo Rutas comunes de PostgreSQL:
    echo - C:\Program Files\PostgreSQL\14\bin
    echo - C:\Program Files\PostgreSQL\15\bin
    echo - C:\Program Files\PostgreSQL\16\bin
    echo - C:\Program Files\PostgreSQL\18\bin
    echo - C:\PostgreSQL\18\bin
    echo.
    pause
    exit /b 1
)

REM Carpeta de destino FIJA para backups
set BACKUP_DIR=C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\Backup
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Generar nombre de archivo con fecha/hora
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set BACKUP_FILE=%BACKUP_DIR%\backup_gestor_documental_%mydate%_%mytime%.backup

echo.
echo Creando backup de la base de datos...
echo Carpeta: %BACKUP_DIR%
echo Archivo: backup_gestor_documental_%mydate%_%mytime%.backup
echo.

REM Ejecutar pg_dump
set PGPASSWORD=abc123
pg_dump -U gestor_user -h localhost -p 5432 -F c -b -v -f %BACKUP_FILE% gestor_documental

if errorlevel 1 (
    echo.
    echo [ERROR] Fallo al crear backup de la base de datos
    echo.
    echo Posibles causas:
    echo 1. PostgreSQL no está corriendo
    echo 2. Usuario o password incorrectos
    echo 3. Base de datos no existe
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo BACKUP COMPLETADO EXITOSAMENTE
echo ============================================
echo.
echo Archivo generado: %BACKUP_FILE%

REM Mostrar tamaño del archivo
for %%A in (%BACKUP_FILE%) do (
    set size=%%~zA
)
set /a size_mb=%size% / 1048576
echo Tamaño: %size_mb% MB
echo.

echo El archivo de backup contiene:
echo - Todas las tablas con datos
echo - Indices y constraints
echo - Secuencias y triggers
echo - Esquema completo
echo.

echo Para restaurar este backup:
echo 1. Ejecutar: pg_restore -U gestor_user -d gestor_documental -v %BACKUP_FILE%
echo.

echo IMPORTANTE: Guarda este archivo en un lugar seguro
pause
