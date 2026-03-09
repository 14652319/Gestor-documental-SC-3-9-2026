@echo off
chcp 65001 > nul
echo ================================================================================
echo INSTALACIÓN COMPLETA DEL MÓDULO DIAN VS ERP
echo Sistema de Reconciliación DIAN vs ERP Interno
echo ================================================================================
echo.

echo 📋 PASO 1: Aplicando esquema de base de datos...
echo.
python aplicar_schema_dian_erp.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Error al aplicar esquema. Abortando...
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo 📦 PASO 2: Cargando archivos desde:
echo    D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025
echo ================================================================================
echo.
timeout /t 3 /nobreak > nul

python cargar_archivos_dian_erp.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ⚠️  Error en la carga de archivos
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo ✅ INSTALACIÓN COMPLETADA
echo ================================================================================
echo.
echo Tablas creadas y cargadas:
echo   - dian
echo   - erp_comercial
echo   - erp_financiero
echo   - acuses
echo.
echo Vistas disponibles para consultas:
echo   - v_reconciliacion_dian_comercial
echo   - v_reconciliacion_dian_financiero
echo   - v_dian_con_acuses
echo.
pause
