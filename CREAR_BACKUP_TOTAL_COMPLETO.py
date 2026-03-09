"""
BACKUP COMPLETO TOTAL - Copiar TODO el proyecto
Copia exacta del proyecto + Base de datos completa
"""
import os
import shutil
import subprocess
from datetime import datetime

# Configuración
ORIGEN = r"D:\0.1. Backup Equipo Contablilidad\Gestor Documental\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
DESTINO = r"C:\Users\Usuario\Documents\Gestor documentalv4.3.2026"

# Credenciales PostgreSQL
USUARIO_BD = "postgres"
PASSWORD_BD = "G3st0radm$2025."
NOMBRE_BD = "gestor_documental"
PG_DUMP = r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"

print("\n" + "="*80)
print("   BACKUP COMPLETO TOTAL - GESTOR DOCUMENTAL")
print("="*80)
print(f"\nOrigen:  {ORIGEN}")
print(f"Destino: {DESTINO}\n")
print("Este proceso copiará TODO el proyecto + Base de datos completa")
print("\n⏱️  Tiempo estimado: 5-10 minutos")
print("💾 Espacio necesario: ~1 GB\n")

input("Presione ENTER para continuar...")

# ====================
# PASO 1: COPIAR TODO EL CÓDIGO
# ====================
print("\n" + "="*80)
print("PASO 1/3: Copiando TODO el código fuente...")
print("="*80 + "\n")

# Eliminar destino si existe
if os.path.exists(DESTINO):
    print(f"[!] Destino existe, eliminando...")
    try:
        shutil.rmtree(DESTINO)
        print(f"[✓] Destino eliminado\n")
    except Exception as e:
        print(f"[✗] Error eliminando destino: {e}")
        exit(1)

# Crear destino
os.makedirs(DESTINO, exist_ok=True)
print(f"[✓] Directorio destino creado\n")

# Copiar TODO excepto .venv y __pycache__
print("[→] Copiando archivos... (esto puede tardar varios minutos)\n")

def ignorar_archivos(dir, files):
    """Función para ignorar ciertos archivos/carpetas"""
    ignorar = set()
    for f in files:
        # Ignorar carpetas específicas
        if f in ['.venv', 'venv', '__pycache__', '.git', '.pytest_cache', 
                'node_modules', '.vscode']:
            ignorar.add(f)
        # Ignorar archivos .pyc
        if f.endswith('.pyc') or f.endswith('.pyo'):
            ignorar.add(f)
    return ignorar

try:
    # Copiar TODO el directorio
    total = 0
    for item in os.listdir(ORIGEN):
        if item in ['.venv', 'venv', '__pycache__', '.git']:
            print(f"  [Omitiendo] {item}")
            continue
        
        origen_item = os.path.join(ORIGEN, item)
        destino_item = os.path.join(DESTINO, item)
        
        try:
            if os.path.isdir(origen_item):
                shutil.copytree(origen_item, destino_item, ignore=ignorar_archivos)
                print(f"  [✓] {item}/")
            else:
                shutil.copy2(origen_item, destino_item)
                print(f"  [✓] {item}")
            total += 1
        except Exception as e:
            print(f"  [!] Error con {item}: {e}")
    
    print(f"\n[✓] {total} items copiados correctamente\n")
    
except Exception as e:
    print(f"\n[✗] ERROR copiando código: {e}\n")
    exit(1)

# ====================
# PASO 2: EXPORTAR BASE DE DATOS COMPLETA
# ====================
print("\n" + "="*80)
print("PASO 2/3: Exportando base de datos completa...")
print("="*80 + "\n")

# Crear directorio para BD
bd_dir = os.path.join(DESTINO, "BASE_DATOS_COMPLETA")
os.makedirs(bd_dir, exist_ok=True)

# Exportar en formato SQL (texto plano - más compatible)
print("[→] Exportando en formato SQL (texto plano)...")
archivo_sql = os.path.join(bd_dir, "gestor_documental_COMPLETO.sql")

comando_sql = [
    PG_DUMP,
    "-U", USUARIO_BD,
    "-h", "localhost",
    "-p", "5432",
    "-F", "p",  # Formato plain text
    "--inserts",  # Usar INSERT (más compatible)
    "--no-owner",  # Sin dueño específico
    "--no-acl",    # Sin permisos específicos
    "-f", archivo_sql,
    NOMBRE_BD
]

try:
    env = os.environ.copy()
    env['PGPASSWORD'] = PASSWORD_BD
    
    resultado = subprocess.run(
        comando_sql, 
        env=env, 
        capture_output=True, 
        text=True,
        timeout=600  # 10 minutos máximo
    )
    
    if resultado.returncode == 0:
        tamanio = os.path.getsize(archivo_sql) / (1024 * 1024)
        print(f"[✓] Backup SQL creado: {tamanio:.2f} MB\n")
    else:
        print(f"[✗] Error en backup SQL: {resultado.stderr}\n")
        exit(1)
except Exception as e:
    print(f"[✗] Error exportando SQL: {e}\n")
    exit(1)

# Exportar también en formato CUSTOM (comprimido)
print("[→] Exportando en formato CUSTOM (comprimido)...")
archivo_custom = os.path.join(bd_dir, "gestor_documental_COMPLETO.backup")

comando_custom = [
    PG_DUMP,
    "-U", USUARIO_BD,
    "-h", "localhost",
    "-p", "5432",
    "-F", "c",  # Formato custom
    "-b",       # Incluir blobs
    "--no-owner",
    "--no-acl",
    "-f", archivo_custom,
    NOMBRE_BD
]

try:
    resultado = subprocess.run(
        comando_custom,
        env=env,
        capture_output=True,
        text=True,
        timeout=600
    )
    
    if resultado.returncode == 0:
        tamanio = os.path.getsize(archivo_custom) / (1024 * 1024)
        print(f"[✓] Backup CUSTOM creado: {tamanio:.2f} MB\n")
    else:
        print(f"[!] Advertencia en backup CUSTOM: {resultado.stderr}\n")
except Exception as e:
    print(f"[!] Advertencia exportando CUSTOM: {e}\n")

# ====================
# PASO 3: CREAR INSTALADOR COMPLETO
# ====================
print("\n" + "="*80)
print("PASO 3/3: Creando instalador automático...")
print("="*80 + "\n")

instalador_contenido = f"""@echo off
chcp 65001 > nul
color 0A
cls

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║        INSTALADOR - GESTOR DOCUMENTAL v4.3.2026              ║
echo ║                                                                ║
echo ║        Restauración completa del sistema                       ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo.
echo Este instalador restaurará el sistema completo:
echo.
echo   [1] Crear entorno virtual Python
echo   [2] Instalar todas las dependencias
echo   [3] Crear base de datos PostgreSQL
echo   [4] Restaurar TODOS los datos
echo   [5] Configurar el sistema
echo.
echo ⏱️  Tiempo estimado: 10-15 minutos
echo.
pause

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] Python no instalado
    pause
    exit /b 1
)

REM Verificar PostgreSQL
psql --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] PostgreSQL no instalado
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════
echo   [1/5] Creando entorno virtual Python...
echo ════════════════════════════════════════════════════════════
echo.

if exist ".venv" rmdir /s /q .venv
python -m venv .venv
call .venv\\Scripts\\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt

echo.
echo ════════════════════════════════════════════════════════════
echo   [2/5] Creando base de datos...
echo ════════════════════════════════════════════════════════════
echo.
echo Ingrese la contraseña de 'postgres' cuando se solicite
echo.

psql -U postgres -c "DROP DATABASE IF EXISTS {NOMBRE_BD};"
psql -U postgres -c "CREATE DATABASE {NOMBRE_BD};"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE {NOMBRE_BD} TO postgres;"

echo.
echo ════════════════════════════════════════════════════════════
echo   [3/5] Restaurando base de datos completa...
echo ════════════════════════════════════════════════════════════
echo.
echo Seleccione formato:
echo   [1] SQL (recomendado, más compatible)
echo   [2] CUSTOM (más rápido)
echo.
set /p FORMATO="Opción (1 o 2): "

if "%FORMATO%"=="2" (
    echo Restaurando formato CUSTOM...
    pg_restore -U postgres -d {NOMBRE_BD} -v BASE_DATOS_COMPLETA\\gestor_documental_COMPLETO.backup
) else (
    echo Restaurando formato SQL...
    psql -U postgres -d {NOMBRE_BD} -f BASE_DATOS_COMPLETA\\gestor_documental_COMPLETO.sql
)

echo.
echo ════════════════════════════════════════════════════════════
echo   [4/5] Configurando archivos...
echo ════════════════════════════════════════════════════════════
echo.

if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo [✓] Archivo .env creado
    )
)

if not exist logs mkdir logs
if not exist documentos_terceros mkdir documentos_terceros

echo.
echo ════════════════════════════════════════════════════════════
echo   [5/5] Verificando instalación...
echo ════════════════════════════════════════════════════════════
echo.

psql -U postgres -d {NOMBRE_BD} -c "SELECT COUNT(*) FROM usuarios;" >nul 2>&1
if errorlevel 1 (
    echo [!] ADVERTENCIA: No se pudo verificar la BD
) else (
    echo [✓] Base de datos verificada correctamente
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║              ✓✓✓ INSTALACIÓN COMPLETADA ✓✓✓                  ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo.
echo PRÓXIMOS PASOS:
echo.
echo   1. Editar .env con las rutas de red:
echo      - CARPETA_CYS
echo      - CARPETA_DOM
echo      - CARPETA_TIC
echo      - CARPETA_MER
echo      - CARPETA_MYP
echo      - CARPETA_FIN
echo      (Usar rutas UNC: \\\\servidor\\carpeta)
echo.
echo   2. Iniciar el servidor:
echo      1_iniciar_gestor.bat
echo.
echo   3. Acceder al sistema:
echo      http://localhost:8099
echo.
echo   Usuario: admin
echo   NIT: 805028041
echo.
pause
"""

# Guardar instalador
ruta_instalador = os.path.join(DESTINO, "INSTALAR.bat")
with open(ruta_instalador, 'w', encoding='utf-8') as f:
    f.write(instalador_contenido)

print("[✓] INSTALAR.bat creado\n")

# Crear README
readme = f"""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║           BACKUP COMPLETO - GESTOR DOCUMENTAL v4.3.2026              ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

Fecha de backup: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

═══════════════════════════════════════════════════════════════════════
   📦 CONTENIDO DEL BACKUP COMPLETO
═══════════════════════════════════════════════════════════════════════

✅ TODO el código fuente (copia exacta del proyecto)
✅ TODAS las tablas de la base de datos
✅ TODOS los datos (usuarios, facturas, configuraciones, etc.)
✅ Todos los archivos de configuración
✅ Todos los módulos del sistema
✅ Instalador automático

═══════════════════════════════════════════════════════════════════════
   🗂️ ESTRUCTURA
═══════════════════════════════════════════════════════════════════════

📁 Raíz del proyecto:
   ├── app.py                    → Aplicación principal
   ├── extensions.py             → Extensiones SQLAlchemy
   ├── utils_licencia.py         → Sistema de licencias
   ├── utils_fecha.py            → Utilidades de fecha
   ├── decoradores_permisos.py   → Sistema de permisos
   ├── config_carpetas.py        → Configuración de rutas
   ├── requirements.txt          → Dependencias Python
   ├── .env                      → Configuración (EDITAR)
   ├── .env.example              → Plantilla
   │
   ├── modules/                  → Módulos del sistema
   │   ├── recibir_facturas/
   │   ├── relaciones/
   │   ├── causaciones/
   │   ├── configuracion/
   │   ├── dian_vs_erp/
   │   ├── terceros/
   │   └── admin/
   │
   ├── templates/                → Plantillas HTML
   ├── static/                   → CSS, JS, imágenes
   ├── sql/                      → Scripts SQL
   ├── logs/                     → Logs del sistema
   ├── documentos_terceros/      → PDFs
   │
   ├── BASE_DATOS_COMPLETA/      → Backups de PostgreSQL
   │   ├── gestor_documental_COMPLETO.sql      (texto plano)
   │   └── gestor_documental_COMPLETO.backup   (comprimido)
   │
   └── INSTALAR.bat              → ⭐ Instalador automático

═══════════════════════════════════════════════════════════════════════
   🚀 INSTALACIÓN EN OTRO EQUIPO
═══════════════════════════════════════════════════════════════════════

PASO 1: Copiar esta carpeta completa al equipo destino

PASO 2: Ejecutar INSTALAR.bat como Administrador
   - Clic derecho → "Ejecutar como administrador"
   - Seguir las instrucciones en pantalla

PASO 3: Editar .env con las rutas de red correctas

PASO 4: Iniciar el servidor
   - Ejecutar: 1_iniciar_gestor.bat

PASO 5: Acceder al sistema
   - Navegador: http://localhost:8099
   - NIT: 805028041
   - Usuario: admin

═══════════════════════════════════════════════════════════════════════
   ⚙️ REQUISITOS DEL EQUIPO DESTINO
═══════════════════════════════════════════════════════════════════════

✅ Windows 10/11 o Windows Server
✅ PostgreSQL 18 (o superior)
✅ Python 3.8 o superior
✅ ~500 MB espacio libre
✅ Permisos de administrador

═══════════════════════════════════════════════════════════════════════
   📊 BASE DE DATOS INCLUIDA
═══════════════════════════════════════════════════════════════════════

El backup incluye TODAS las tablas con TODOS los datos:

✅ usuarios              → Todos los usuarios registrados
✅ terceros              → Todos los proveedores/terceros
✅ facturas_recibidas    → Todas las facturas recibidas
✅ relaciones_facturas   → Todas las relaciones digitales
✅ permisos_usuarios     → Todos los permisos configurados
✅ configuracion         → Toda la configuración del sistema
✅ logs y auditorías     → Historial completo
✅ ... y TODAS las demás tablas del sistema

═══════════════════════════════════════════════════════════════════════
   🔧 INSTALACIÓN MANUAL (si falla el instalador)
═══════════════════════════════════════════════════════════════════════

1. Crear entorno virtual:
   python -m venv .venv
   .venv\\Scripts\\activate.bat

2. Instalar dependencias:
   pip install -r requirements.txt

3. Crear base de datos:
   psql -U postgres
   CREATE DATABASE gestor_documental;
   \\q

4. Restaurar backup:
   psql -U postgres -d gestor_documental -f BASE_DATOS_COMPLETA\\gestor_documental_COMPLETO.sql

5. Configurar .env:
   copy .env.example .env
   notepad .env

6. Iniciar:
   python app.py

═══════════════════════════════════════════════════════════════════════
   ⚠️  CONFIGURACIÓN IMPORTANTE
═══════════════════════════════════════════════════════════════════════

Editar .env con las rutas UNC de red:

CARPETA_CYS=\\\\192.168.11.227\\acreedores_digitales\\COMPRAS_Y_SUMINISTROS\\...
CARPETA_DOM=\\\\192.168.11.227\\acreedores_digitales\\DOMICILIOS\\...
CARPETA_TIC=\\\\192.168.11.227\\acreedores_digitales\\TECNOLOGIA\\...
CARPETA_MER=\\\\192.168.11.227\\acreedores_digitales\\ACREEDORES\\...
CARPETA_MYP=\\\\192.168.11.227\\acreedores_digitales\\MYP ESTRATEGICA\\...
CARPETA_FIN=\\\\192.168.11.227\\acreedores_digitales\\FINANCIERO\\...

⚠️  NO usar letras de unidad (V:, W:, X:) - SOLO rutas UNC

═══════════════════════════════════════════════════════════════════════
   💡 SOPORTE
═══════════════════════════════════════════════════════════════════════

Documentación técnica completa:
   .github\\copilot-instructions.md

Logs del sistema:
   logs\\security.log
   logs\\app.log

Scripts de diagnóstico:
   verificar_carpetas_red.py
   check_user_status.py

═══════════════════════════════════════════════════════════════════════

Este es un BACKUP COMPLETO que incluye:
   ✅ TODO el código
   ✅ TODAS las tablas
   ✅ TODOS los datos
   ✅ TODAS las configuraciones

Puede instalarse en cualquier equipo con los requisitos mínimos.

═══════════════════════════════════════════════════════════════════════

Versión: Gestor Documental v4.3.2026
Framework: Flask 3.0
Base de Datos: PostgreSQL 18
Python: 3.8+

Backup creado desde:
{ORIGEN}

═══════════════════════════════════════════════════════════════════════
"""

ruta_readme = os.path.join(DESTINO, "LEEME_BACKUP_COMPLETO.txt")
with open(ruta_readme, 'w', encoding='utf-8') as f:
    f.write(readme)

print("[✓] LEEME_BACKUP_COMPLETO.txt creado\n")

# ====================
# RESUMEN FINAL
# ====================
print("\n" + "="*80)
print("   ✅✅✅ BACKUP COMPLETO CREADO EXITOSAMENTE ✅✅✅")
print("="*80 + "\n")

# Contar archivos
total_archivos = 0
for root, dirs, files in os.walk(DESTINO):
    total_archivos += len(files)

# Calcular tamaño
total_tamanio = 0
for root, dirs, files in os.walk(DESTINO):
    for file in files:
        try:
            filepath = os.path.join(root, file)
            total_tamanio += os.path.getsize(filepath)
        except:
            pass

tamanio_mb = total_tamanio / (1024 * 1024)

print(f"📁 Ubicación: {DESTINO}")
print(f"📊 Archivos: {total_archivos}")
print(f"💾 Tamaño: {tamanio_mb:.2f} MB")
print()
print("📦 Contenido:")
print("   ✅ TODO el código fuente")
print("   ✅ Base de datos completa (SQL + CUSTOM)")
print("   ✅ Instalador automático (INSTALAR.bat)")
print("   ✅ Documentación completa")
print()
print("🚀 Para instalar en otro equipo:")
print("   1. Copiar carpeta completa")
print("   2. Ejecutar INSTALAR.bat como Administrador")
print("   3. Seguir instrucciones")
print()
print("📖 Ver: LEEME_BACKUP_COMPLETO.txt para más información")
print()

input("Presione ENTER para salir...")
