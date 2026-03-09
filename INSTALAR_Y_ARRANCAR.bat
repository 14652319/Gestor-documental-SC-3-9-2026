@echo off
echo =====================================
echo   INSTALACION Y ARRANQUE COMPLETO
echo =====================================

cd /d "%~dp0"

echo.
echo [1/4] Matando procesos Python existentes...
taskkill /F /IM python.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/4] Actualizando pip en venv...
.venv\Scripts\python.exe -m pip install --upgrade pip --quiet

echo [3/4] Instalando pyarrow en venv (sin compilar)...
.venv\Scripts\python.exe -m pip install --only-binary=:all: pyarrow==23.0.1 --quiet

echo [4/4] Verificando instalacion...
.venv\Scripts\python.exe -c "import pyarrow; print('✅ pyarrow version:', pyarrow.__version__)"

echo.
echo =====================================
echo   INICIANDO SERVIDOR...
echo   Puerto: 8099
echo =====================================
.venv\Scripts\python.exe app.py

pause
