@echo off
REM =============================================
REM INICIAR SERVIDOR FLASK - GESTOR DOCUMENTAL
REM =============================================

echo.
echo ============================================
echo  GESTOR DOCUMENTAL - SUPERTIENDAS CANAVERAL
echo  Iniciando servidor Flask...
echo ============================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "app.py" (
    echo ERROR: No se encuentra app.py
    echo Asegurate de estar en el directorio correcto
    pause
    exit /b 1
)

REM Activar virtualenv si existe
if exist ".venv\Scripts\activate.bat" (
    echo Activando virtualenv...
    call .venv\Scripts\activate.bat
    echo.
)

REM Verificar que Python esta disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    pause
    exit /b 1
)

echo Python encontrado:
python --version
echo.

REM Verificar archivo .env
if not exist ".env" (
    echo ADVERTENCIA: No se encuentra archivo .env
    echo El servidor podria no funcionar correctamente
    echo.
)

REM Mostrar informacion
echo ============================================
echo  INFORMACION DEL SERVIDOR
echo ============================================
echo.
echo  URL Local:    http://127.0.0.1:5000
echo  URL Red:      http://192.168.101.72:5000
echo  Debug Mode:   ON
echo.
echo  Para detener el servidor: Ctrl + C
echo.
echo ============================================
echo  INICIANDO SERVIDOR...
echo ============================================
echo.

REM Iniciar servidor
python app.py

REM Si el servidor se detiene
echo.
echo ============================================
echo  SERVIDOR DETENIDO
echo ============================================
echo.
pause
