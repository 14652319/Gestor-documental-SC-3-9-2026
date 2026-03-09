@echo off
echo =====================================================
echo   ABRIR PUERTO 8099 EN FIREWALL DE WINDOWS
echo   Para acceso desde la red WiFi empresarial
echo =====================================================
echo.
echo Este script necesita permisos de ADMINISTRADOR
echo.
pause

REM Crear regla de firewall para puerto 8099
PowerShell -Command "New-NetFirewallRule -DisplayName 'Gestor Documental - Puerto 8099' -Direction Inbound -LocalPort 8099 -Protocol TCP -Action Allow -Profile Any -Enabled True"

echo.
echo =====================================================
if %ERRORLEVEL% EQU 0 (
    echo   EXITO: Puerto 8099 abierto en el firewall
    echo   Tu aplicacion ahora es accesible desde:
    echo   http://192.168.100.121:8099
) else (
    echo   ERROR: No se pudo crear la regla
    echo   Ejecuta este script como ADMINISTRADOR
    echo   Click derecho -^> Ejecutar como administrador
)
echo =====================================================
echo.
pause
