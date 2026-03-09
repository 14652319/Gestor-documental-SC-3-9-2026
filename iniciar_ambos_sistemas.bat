@echo off
chcp 65001 >nul
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║     🚀 INICIADOR AUTOMÁTICO DE SISTEMAS                       ║
echo ║     Supertiendas Cañaveral - Gestor Documental               ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo 📋 Sistemas a iniciar:
echo    1. Gestor Documental    (Puerto 8099)
echo    2. DIAN vs ERP          (Puerto 8097)
echo.
echo ⏳ Iniciando sistemas...
echo.

REM Verificar si Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está instalado o no está en el PATH
    echo.
    echo 💡 Solución: Instala Python desde https://www.python.org
    pause
    exit /b 1
)

REM Obtener ruta del directorio actual
set "PROJECT_DIR=%~dp0"
set "DIAN_DIR=%PROJECT_DIR%Proyecto Dian Vs ERP v5.20251130"

REM Verificar si la carpeta DIAN vs ERP existe
if not exist "%DIAN_DIR%" (
    echo ❌ ERROR: No se encuentra la carpeta "Proyecto Dian Vs ERP v5.20251130"
    echo.
    echo 📁 Ruta esperada: %DIAN_DIR%
    echo.
    pause
    exit /b 1
)

echo ══════════════════════════════════════════════════════════════
echo.
echo 🟢 [1/2] Iniciando Gestor Documental (Puerto 8099)...
echo.
echo 📁 Directorio: %PROJECT_DIR%
echo 🐍 Activando virtualenv...
echo.

REM Iniciar Gestor Documental en nueva ventana
start "🟢 GESTOR DOCUMENTAL - Puerto 8099" cmd /k "cd /d "%PROJECT_DIR%" && call .venv\Scripts\activate.bat && python app.py"

REM Esperar 5 segundos para que el primer servidor inicie
timeout /t 5 /nobreak >nul

echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo 🔵 [2/2] Iniciando DIAN vs ERP (Puerto 8097)...
echo.
echo 📁 Directorio: %DIAN_DIR%
echo.

REM Iniciar DIAN vs ERP en nueva ventana
start "🔵 DIAN VS ERP - Puerto 8097" cmd /k "cd /d "%DIAN_DIR%" && python app.py"

REM Esperar 3 segundos
timeout /t 3 /nobreak >nul

echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo ✅ SISTEMAS INICIADOS CORRECTAMENTE
echo.
echo 📊 Estado de servidores:
echo    🟢 Gestor Documental:  http://localhost:8099
echo    🔵 DIAN vs ERP:        http://localhost:8097
echo.
echo ⏰ Los servidores están iniciándose en ventanas separadas...
echo    (Pueden tardar 5-10 segundos en estar completamente listos)
echo.
echo 💡 TIP: Deja las ventanas abiertas mientras trabajas
echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo 🌐 Abriendo navegador en 5 segundos...
timeout /t 5 /nobreak >nul

REM Abrir navegador en Gestor Documental
start http://localhost:8099

echo.
echo ✨ ¡Listo! Ya puedes usar los sistemas.
echo.
echo 📌 Para cerrar los servidores: Cierra las ventanas de terminal
echo.
pause
