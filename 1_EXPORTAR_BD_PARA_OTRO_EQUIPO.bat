@echo off
echo =========================================================
echo   PASO 1: EXPORTAR BASE DE DATOS PARA OTRO EQUIPO
echo   Este script crea un backup completo de PostgreSQL
echo =========================================================
echo.

REM Obtener timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%

REM Crear carpeta de exportación
set CARPETA_EXPORT=EXPORT_BD_%TIMESTAMP%
mkdir "%CARPETA_EXPORT%"

echo [1/3] Creando carpeta de exportacion: %CARPETA_EXPORT%
echo.

REM Ejecutar script Python de backup
echo [2/3] Exportando base de datos PostgreSQL...
echo.
.venv\Scripts\python.exe exportar_bd_completa.py "%CARPETA_EXPORT%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =========================================================
    echo   EXPORTACION EXITOSA
    echo =========================================================
    echo.
    echo La base de datos se exporto a: %CARPETA_EXPORT%
    echo.
    echo ARCHIVOS GENERADOS:
    echo   - backup_completo.sql     (Estructura + Datos)
    echo   - info_backup.json        (Metadata)
    echo   - INSTRUCCIONES_IMPORTAR.txt
    echo.
    echo [3/3] SIGUIENTE PASO:
    echo   1. Copia la carpeta '%CARPETA_EXPORT%' al otro equipo
    echo   2. Copia TODA la carpeta del proyecto al otro equipo
    echo   3. En el otro equipo, ejecuta: 2_IMPORTAR_BD_DESDE_BACKUP.bat
    echo.
) else (
    echo.
    echo =========================================================
    echo   ERROR EN LA EXPORTACION
    echo =========================================================
    echo.
    echo Verifica:
    echo   - PostgreSQL esta corriendo
    echo   - Las credenciales en .env son correctas
    echo   - Tienes permisos de lectura en la BD
    echo.
)

echo.
pause
