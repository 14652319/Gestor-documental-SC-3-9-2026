@echo off
chcp 65001 > nul
echo ================================================================
echo   CREAR BACKUP TRANSPORTABLE - AUTOMÁTICO
echo ================================================================
echo.
echo Creando backup completo en:
echo C:\Users\Usuario\Documents\Backup gestor documental
echo.
echo Este proceso puede tardar varios minutos...
echo.

REM Ejecutar script sin confirmación
echo. | python CREAR_BACKUP_TRANSPORTABLE.py

echo.
echo ================================================================
echo Proceso completado. Verificar mensajes arriba.
echo ================================================================
pause
