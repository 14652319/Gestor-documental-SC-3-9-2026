@echo off
REM ================================================================================
REM CONFIGURADOR DEL MONITOREO AUTOMÁTICO DE ALERTAS SAGRILAFT
REM ================================================================================
REM Este script configura Windows Task Scheduler para ejecutar el monitoreo
REM de vencimientos SAGRILAFT automáticamente todos los días a las 8:00 AM
REM ================================================================================

echo.
echo ========================================================================
echo   CONFIGURADOR DE MONITOREO AUTOMATICO - SAGRILAFT
echo ========================================================================
echo.

REM Obtener la ruta del proyecto actual
set PROJECT_DIR=%~dp0
echo   Ruta del proyecto: %PROJECT_DIR%
echo.

REM Validar que existan los archivos necesarios
if not exist "%PROJECT_DIR%ejecutar_monitoreo_sagrilaft.py" (
    echo ❌ ERROR: No se encuentra el archivo ejecutar_monitoreo_sagrilaft.py
    pause
    exit /b 1
)

if not exist "%PROJECT_DIR%.venv\Scripts\python.exe" (
    echo ❌ ERROR: No se encuentra el entorno virtual .venv
    pause
    exit /b 1
)

echo ✅ Archivos validados correctamente
echo.

REM Crear la tarea programada
echo   Creando tarea programada en Windows Task Scheduler...
echo.

schtasks /create ^
    /tn "Gestor Documental - Monitoreo SAGRILAFT" ^
    /tr "\"%PROJECT_DIR%.venv\Scripts\python.exe\" \"%PROJECT_DIR%ejecutar_monitoreo_sagrilaft.py\"" ^
    /sc daily ^
    /st 08:00 ^
    /rl highest ^
    /f

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ ERROR al crear la tarea programada
    echo    Verifica que tengas permisos de administrador
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo   ✅ CONFIGURACIÓN COMPLETADA
echo ========================================================================
echo.
echo   Tarea programada creada exitosamente:
echo     📅 Nombre: Gestor Documental - Monitoreo SAGRILAFT
echo     ⏰ Ejecución: Todos los días a las 8:00 AM
echo     📂 Script: ejecutar_monitoreo_sagrilaft.py
echo     📄 Logs: logs/sagrilaft_monitor.log
echo.
echo   Para ver la tarea configurada:
echo     1. Abre "Programador de tareas"
echo     2. Busca "Gestor Documental - Monitoreo SAGRILAFT"
echo.
echo   Para ejecutar una prueba manual AHORA:
echo     python ejecutar_monitoreo_sagrilaft.py
echo.
echo   Para ver los logs en tiempo real:
echo     Get-Content logs\sagrilaft_monitor.log -Tail 50 -Wait
echo.
echo ========================================================================
echo.
pause
