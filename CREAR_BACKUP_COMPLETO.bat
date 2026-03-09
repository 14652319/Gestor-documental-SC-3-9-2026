@echo off
chcp 65001 > nul
cls
echo ================================================================
echo   📦 CREAR BACKUP TRANSPORTABLE COMPLETO
echo ================================================================
echo.
echo Este script creará una copia completa del Gestor Documental
echo.
echo Ubicación: C:\Users\Usuario\Documents\Backup gestor documental
echo.
echo Incluye:
echo   ✅ Código fuente completo
echo   ✅ Base de datos PostgreSQL (SQL + CUSTOM)
echo   ✅ Instalador automático
echo   ✅ Documentación completa
echo.
echo ⏱️  Tiempo estimado: 5-10 minutos
echo.
pause

echo.
echo ================================================================
echo   Paso 1/2: Copiando código fuente...
echo ================================================================
python BACKUP_SIMPLE.py
if errorlevel 1 (
    echo.
    echo ❌ Error en copia de código
    pause
    exit /b 1
)

echo.
echo ================================================================
echo   Paso 2/2: Exportando BD y creando instalador...
echo ================================================================
python COMPLETAR_BACKUP.py
if errorlevel 1 (
    echo.
    echo ❌ Error en exportación de BD
    pause
    exit /b 1
)

echo.
echo ================================================================
echo   ✅ BACKUP COMPLETADO EXITOSAMENTE
echo ================================================================
echo.
echo 📦 Ubicación: C:\Users\Usuario\Documents\Backup gestor documental
echo.
echo 📋 Contenido:
echo    ├── codigo/                 (aplicación completa)
echo    ├── base_datos/             (backups PostgreSQL)
echo    ├── instalador/             (INSTALAR.bat)
echo    └── README_INSTALACION.txt  (instrucciones)
echo.
echo 💡 Próximos pasos:
echo    1. Copiar la carpeta completa a USB o red
echo    2. Llevar al equipo destino
echo    3. Ejecutar: instalador\INSTALAR.bat
echo.
echo Ver README_INSTALACION.txt para más detalles
echo.
pause
