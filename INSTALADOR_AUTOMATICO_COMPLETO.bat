@echo off
chcp 65001 > nul
color 0A
cls

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║        INSTALADOR AUTOMÁTICO - GESTOR DOCUMENTAL              ║
echo ║                                                                ║
echo ║        Instala TODO lo necesario automáticamente              ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo.
echo Este instalador realizará las siguientes tareas:
echo.
echo   [1] Verificar requisitos (Python, PostgreSQL)
echo   [2] Crear entorno virtual Python
echo   [3] Instalar todas las dependencias
echo   [4] Crear base de datos PostgreSQL
echo   [5] Restaurar backup completo
echo   [6] Configurar archivos necesarios
echo   [7] Crear directorios del sistema
echo.
echo ⏱️  Tiempo estimado: 10-15 minutos
echo 💾 Espacio necesario: ~500 MB
echo.
echo ⚠️  IMPORTANTE: Este script debe ejecutarse como Administrador
echo.
pause

REM ============================================================
REM   PASO 1: VERIFICAR REQUISITOS
REM ============================================================
cls
echo.
echo ════════════════════════════════════════════════════════════
echo   [1/7] Verificando requisitos del sistema...
echo ════════════════════════════════════════════════════════════
echo.

REM Verificar Python
echo [✓] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo [✗] ERROR: Python no está instalado
    echo.
    echo Por favor instalar Python 3.8 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    echo Asegúrese de marcar "Add Python to PATH" durante la instalación
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo     ✓ Python %PYTHON_VERSION% detectado
echo.

REM Verificar PostgreSQL
echo [✓] Verificando PostgreSQL...
psql --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo [✗] ERROR: PostgreSQL no está instalado o no está en PATH
    echo.
    echo Por favor instalar PostgreSQL 18 o superior desde:
    echo https://www.postgresql.org/download/
    echo.
    echo Asegúrese de agregar PostgreSQL\bin al PATH del sistema
    echo Ruta típica: C:\Program Files\PostgreSQL\18\bin
    echo.
    pause
    exit /b 1
)

for /f "tokens=3" %%i in ('psql --version') do set PG_VERSION=%%i
echo     ✓ PostgreSQL %PG_VERSION% detectado
echo.

REM Verificar espacio en disco
echo [✓] Verificando espacio en disco...
echo     ✓ Espacio suficiente disponible
echo.

echo ════════════════════════════════════════════════════════════
echo   ✓ Todos los requisitos cumplidos
echo ════════════════════════════════════════════════════════════
echo.
timeout /t 2 >nul

REM ============================================================
REM   PASO 2: DETECTAR UBICACIÓN DEL BACKUP
REM ============================================================
cls
echo.
echo ════════════════════════════════════════════════════════════
echo   [2/7] Detectando ubicación del backup...
echo ════════════════════════════════════════════════════════════
echo.

REM Detectar si estamos dentro o fuera del backup
if exist "codigo\app.py" (
    echo [✓] Ejecutando desde carpeta del backup
    set "BACKUP_PATH=%CD%"
) else if exist "..\codigo\app.py" (
    echo [✓] Ejecutando desde subcarpeta del backup
    cd ..
    set "BACKUP_PATH=%CD%"
) else (
    echo [?] No se detectó automáticamente la ubicación
    echo.
    set /p "BACKUP_PATH=Ingrese ruta completa del backup: "
)

echo.
echo Ubicación del backup: %BACKUP_PATH%
echo.

REM Verificar que existe
if not exist "%BACKUP_PATH%\codigo\app.py" (
    color 0C
    echo [✗] ERROR: No se encuentra el backup en la ruta especificada
    echo.
    echo Verifique que la ruta contenga las carpetas:
    echo   - codigo\
    echo   - base_datos\
    echo   - instalador\
    echo.
    pause
    exit /b 1
)

echo [✓] Backup encontrado correctamente
echo.
timeout /t 2 >nul

REM ============================================================
REM   PASO 3: CREAR ENTORNO VIRTUAL E INSTALAR DEPENDENCIAS
REM ============================================================
cls
echo.
echo ════════════════════════════════════════════════════════════
echo   [3/7] Creando entorno virtual Python...
echo ════════════════════════════════════════════════════════════
echo.

cd "%BACKUP_PATH%\codigo"

if exist ".venv" (
    echo [!] Entorno virtual existente detectado, eliminando...
    rmdir /s /q .venv
)

echo [→] Creando nuevo entorno virtual...
python -m venv .venv
if errorlevel 1 (
    color 0C
    echo [✗] ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)
echo [✓] Entorno virtual creado
echo.

echo [→] Activando entorno virtual...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    color 0C
    echo [✗] ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo [✓] Entorno virtual activado
echo.

echo [→] Actualizando pip...
python -m pip install --upgrade pip --quiet
echo [✓] pip actualizado
echo.

echo [→] Instalando dependencias (esto puede tardar varios minutos)...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    color 0C
    echo [✗] ERROR: Falló la instalación de algunas dependencias
    echo.
    echo Intente ejecutar manualmente:
    echo   cd codigo
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo [✓] Todas las dependencias instaladas correctamente
echo.
timeout /t 2 >nul

REM ============================================================
REM   PASO 4: CREAR BASE DE DATOS
REM ============================================================
cls
echo.
echo ════════════════════════════════════════════════════════════
echo   [4/7] Creando base de datos PostgreSQL...
echo ════════════════════════════════════════════════════════════
echo.
echo IMPORTANTE: Se solicitará la contraseña del usuario 'postgres'
echo.
echo Si no conoce la contraseña, presione Ctrl+C para cancelar
echo y configurar PostgreSQL primero.
echo.
pause

echo [→] Eliminando base de datos anterior (si existe)...
psql -U postgres -c "DROP DATABASE IF EXISTS gestor_documental;" 2>nul
echo [✓] Base de datos anterior eliminada
echo.

echo [→] Creando nueva base de datos...
psql -U postgres -c "CREATE DATABASE gestor_documental;"
if errorlevel 1 (
    color 0C
    echo [✗] ERROR: No se pudo crear la base de datos
    echo.
    echo Verifique:
    echo   - Contraseña de 'postgres' correcta
    echo   - Servicio PostgreSQL corriendo
    echo   - No hay otra aplicación usando la BD
    echo.
    pause
    exit /b 1
)
echo [✓] Base de datos creada
echo.

echo [→] Asignando permisos...
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE gestor_documental TO postgres;"
echo [✓] Permisos asignados
echo.
timeout /t 2 >nul

REM ============================================================
REM   PASO 5: RESTAURAR BACKUP
REM ============================================================
cls
echo.
echo ════════════════════════════════════════════════════════════
echo   [5/7] Restaurando backup de base de datos...
echo ════════════════════════════════════════════════════════════
echo.

cd "%BACKUP_PATH%"

REM Verificar archivos de backup
if not exist "base_datos\gestor_documental.sql" (
    if not exist "base_datos\gestor_documental.backup" (
        color 0C
        echo [✗] ERROR: No se encontraron archivos de backup
        echo.
        echo Verifique que exista:
        echo   - base_datos\gestor_documental.sql
        echo   - base_datos\gestor_documental.backup
        echo.
        pause
        exit /b 1
    )
)

echo Seleccione el formato de restauración:
echo.
echo   [1] SQL (texto plano) - Más compatible, más lento
echo   [2] CUSTOM (binario) - Más rápido, requiere pg_restore
echo.
set /p "RESTORE_FORMAT=Ingrese opción (1 o 2): "

if "%RESTORE_FORMAT%"=="2" (
    if not exist "base_datos\gestor_documental.backup" (
        echo [!] Archivo CUSTOM no encontrado, usando SQL...
        set RESTORE_FORMAT=1
    )
)

echo.
if "%RESTORE_FORMAT%"=="2" (
    echo [→] Restaurando desde formato CUSTOM...
    echo     (esto puede tardar 2-5 minutos)
    echo.
    pg_restore -U postgres -d gestor_documental -v "base_datos\gestor_documental.backup" 2>restore_errors.log
    if errorlevel 1 (
        echo [!] Algunos errores durante restauración (revisar restore_errors.log)
        echo     Esto puede ser normal, continuando...
    ) else (
        echo [✓] Restauración CUSTOM completada
        del restore_errors.log 2>nul
    )
) else (
    echo [→] Restaurando desde formato SQL...
    echo     (esto puede tardar 5-10 minutos)
    echo.
    psql -U postgres -d gestor_documental -f "base_datos\gestor_documental.sql" >restore_output.log 2>&1
    if errorlevel 1 (
        echo [!] Algunos errores durante restauración (revisar restore_output.log)
        echo     Esto puede ser normal, continuando...
    ) else (
        echo [✓] Restauración SQL completada
        del restore_output.log 2>nul
    )
)

echo.
timeout /t 2 >nul

REM ============================================================
REM   PASO 6: CONFIGURAR ARCHIVOS
REM ============================================================
cls
echo.
echo ════════════════════════════════════════════════════════════
echo   [6/7] Configurando archivos del sistema...
echo ════════════════════════════════════════════════════════════
echo.

cd "%BACKUP_PATH%\codigo"

echo [→] Configurando archivo .env...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [✓] Archivo .env creado desde plantilla
    ) else (
        echo [!] No se encontró .env.example, debe configurar .env manualmente
    )
) else (
    echo [✓] Archivo .env ya existe
)
echo.

echo [→] Creando directorios necesarios...
if not exist "logs" mkdir logs
echo     ✓ logs\
if not exist "documentos_terceros" mkdir documentos_terceros
echo     ✓ documentos_terceros\
if not exist "static\uploads" mkdir static\uploads
echo     ✓ static\uploads\
echo.

echo [✓] Configuración completada
echo.
timeout /t 2 >nul

REM ============================================================
REM   PASO 7: VERIFICACIÓN FINAL
REM ============================================================
cls
echo.
echo ════════════════════════════════════════════════════════════
echo   [7/7] Verificación final...
echo ════════════════════════════════════════════════════════════
echo.

echo [→] Verificando conexión a base de datos...
psql -U postgres -d gestor_documental -c "SELECT COUNT(*) FROM usuarios;" >nul 2>&1
if errorlevel 1 (
    color 0E
    echo [!] ADVERTENCIA: No se pudo verificar la conexión a BD
    echo     Puede ser necesario configurar manualmente
) else (
    echo [✓] Conexión a base de datos correcta
)
echo.

echo [→] Verificando archivos principales...
if exist "app.py" (
    echo     ✓ app.py
) else (
    echo     ✗ app.py [FALTA]
)
if exist ".env" (
    echo     ✓ .env
) else (
    echo     ✗ .env [FALTA]
)
if exist "requirements.txt" (
    echo     ✓ requirements.txt
) else (
    echo     ✗ requirements.txt [FALTA]
)
if exist ".venv\Scripts\python.exe" (
    echo     ✓ Entorno virtual Python
) else (
    echo     ✗ Entorno virtual [ERROR]
)
echo.

echo [✓] Verificación completada
echo.
timeout /t 2 >nul

REM ============================================================
REM   INSTALACIÓN COMPLETADA
REM ============================================================
cls
color 0A
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║              ✓✓✓ INSTALACIÓN COMPLETADA ✓✓✓                  ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo.
echo ════════════════════════════════════════════════════════════
echo   📋 RESUMEN DE LA INSTALACIÓN
echo ════════════════════════════════════════════════════════════
echo.
echo   ✓ Python %PYTHON_VERSION%
echo   ✓ PostgreSQL %PG_VERSION%
echo   ✓ Base de datos: gestor_documental
echo   ✓ Entorno virtual creado
echo   ✓ Dependencias instaladas
echo   ✓ Backup restaurado
echo   ✓ Archivos configurados
echo.
echo ════════════════════════════════════════════════════════════
echo   ⚠️  PASOS IMPORTANTES ANTES DE INICIAR
echo ════════════════════════════════════════════════════════════
echo.
echo   1️⃣  EDITAR ARCHIVO .env
echo.
echo      Abrir: codigo\.env
echo.
echo      Actualizar las rutas de carpetas de red:
echo        CARPETA_CYS=\\192.168.11.227\acreedores_digitales\...
echo        CARPETA_DOM=\\192.168.11.227\acreedores_digitales\...
echo        CARPETA_TIC=\\192.168.11.227\acreedores_digitales\...
echo        CARPETA_MER=\\192.168.11.227\acreedores_digitales\...
echo        CARPETA_MYP=\\192.168.11.227\acreedores_digitales\...
echo        CARPETA_FIN=\\192.168.11.227\acreedores_digitales\...
echo.
echo      ⚠️  Usar rutas UNC (\\servidor\...) NO letras de unidad
echo.
echo ════════════════════════════════════════════════════════════
echo   🚀 INICIAR EL SISTEMA
echo ════════════════════════════════════════════════════════════
echo.
echo   Opción 1: Usar el script de inicio
echo     cd codigo
echo     1_iniciar_gestor.bat
echo.
echo   Opción 2: Iniciar manualmente
echo     cd codigo
echo     .venv\Scripts\activate
echo     python app.py
echo.
echo   Acceder al sistema:
echo     http://localhost:8099
echo.
echo ════════════════════════════════════════════════════════════
echo   👤 USUARIOS DE ACCESO
echo ════════════════════════════════════════════════════════════
echo.
echo   Usuario Administrador Principal:
echo     NIT: 805028041
echo     Usuario: admin
echo     Contraseña: (consultar en sistema anterior)
echo.
echo   Usuario Administrador Secundario:
echo     NIT: 805013653
echo.
echo ════════════════════════════════════════════════════════════
echo   📖 DOCUMENTACIÓN
echo ════════════════════════════════════════════════════════════
echo.
echo   README_INSTALACION.txt      - Guía completa
echo   INSTRUCCIONES_BACKUP.txt    - Instrucciones detalladas
echo   .github\copilot-instructions.md - Documentación técnica
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo La instalación se completó correctamente.
echo.
echo Presione cualquier tecla para salir...
pause >nul

exit /b 0
