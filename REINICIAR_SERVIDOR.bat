@echo off
echo ========================================
echo   REINICIANDO SERVIDOR FLASK
echo ========================================
echo.

:: Detener todos los procesos Python del gestor
echo [1/3] Deteniendo servidor actual...
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *GESTOR_DOCUMENTAL*" 2>nul
timeout /t 2 /nobreak >nul

:: Limpiar cache de Python
echo [2/3] Limpiando cache de Python...
del /s /q __pycache__ 2>nul
del /s /q *.pyc 2>nul

:: Reiniciar servidor
echo [3/3] Iniciando servidor con cambios aplicados...
echo.
echo ========================================
echo   SERVIDOR INICIANDO EN PUERTO 8099
echo ========================================
echo.
call .\.venv\Scripts\activate.bat
python app.py

pause
