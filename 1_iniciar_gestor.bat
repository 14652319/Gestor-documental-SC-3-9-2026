@echo off
echo =====================================
echo   INICIANDO GESTOR DOCUMENTAL
echo   Puerto: 8099
echo   Usando: .venv\Scripts\python.exe
echo =====================================
cd /d "%~dp0"
.venv\Scripts\python.exe app.py
pause
