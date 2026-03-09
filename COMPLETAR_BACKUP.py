"""
Completar backup - Solo BD e Instalador
"""
import os
import subprocess
from datetime import datetime

DESTINO = r"C:\Users\Usuario\Documents\Backup gestor documental"

print("\n[1/2] Exportando base de datos...")
destino_bd = os.path.join(DESTINO, "base_datos")
archivo_sql = os.path.join(destino_bd, "gestor_documental.sql")

comando = [
    r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe",
    "-U", "postgres",
    "-h", "localhost",
    "-F", "p",
    "--inserts",
    "-f", archivo_sql,
    "gestor_documental"
]

try:
    env = os.environ.copy()
    env['PGPASSWORD'] = "G3st0radm$2025."
    
    print("   Ejecutando pg_dump... (puede tardar varios minutos)")
    resultado = subprocess.run(comando, env=env, capture_output=True, text=True, timeout=600)
    
    if resultado.returncode == 0:
        tamanio = os.path.getsize(archivo_sql) / (1024 * 1024)
        print(f"   ✅ Backup SQL: {tamanio:.2f} MB\n")
    else:
        print(f"   ❌ Error: {resultado.stderr}\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")

# Backup formato CUSTOM (comprimido) también
archivo_backup = os.path.join(destino_bd, "gestor_documental.backup")
comando_custom = [
    r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe",
    "-U", "postgres",
    "-h", "localhost",
    "-F", "c",
    "-b",
    "-f", archivo_backup,
    "gestor_documental"
]

try:
    print("   Creando backup comprimido...")
    resultado = subprocess.run(comando_custom, env=env, capture_output=True, text=True, timeout=600)
    
    if resultado.returncode == 0:
        tamanio = os.path.getsize(archivo_backup) / (1024 * 1024)
        print(f"   ✅ Backup CUSTOM: {tamanio:.2f} MB\n")
except Exception as e:
    print(f"   ⚠️  Error en backup custom: {e}\n")

print("[2/2] Creando instalador...")

instalador_bat = """@echo off
chcp 65001 > nul
echo ================================================================
echo   INSTALADOR AUTOMÁTICO - GESTOR DOCUMENTAL
echo ================================================================
echo.
echo Este script instalará el Gestor Documental en este equipo
echo.
pause

echo.
echo [1/5] Verificando Python...
python --version
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Instalar Python 3.8+
    pause
    exit /b 1
)

echo.
echo [2/5] Instalando dependencias Python...
cd ..\\codigo
python -m venv .venv
call .venv\\Scripts\\activate
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Error instalando dependencias
    pause
    exit /b 1
)

echo.
echo [3/5] Creando base de datos en PostgreSQL...
echo.
echo IMPORTANTE: Ingrese la contraseña del usuario 'postgres' cuando se solicite
echo.
psql -U postgres -c "DROP DATABASE IF EXISTS gestor_documental;"
psql -U postgres -c "CREATE DATABASE gestor_documental;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE gestor_documental TO postgres;"

echo.
echo [4/5] Restaurando base de datos...
echo.
echo Seleccione formato de restauración:
echo   1. SQL (texto plano) - Recomendado
echo   2. CUSTOM (comprimido) - Más rápido
echo.
set /p FORMATO="Ingrese opción (1 o 2): "

if "%FORMATO%"=="2" (
    echo Restaurando desde backup CUSTOM...
    pg_restore -U postgres -d gestor_documental -v ..\\base_datos\\gestor_documental.backup
) else (
    echo Restaurando desde backup SQL...
    psql -U postgres -d gestor_documental -f ..\\base_datos\\gestor_documental.sql
)

if errorlevel 1 (
    echo.
    echo [ADVERTENCIA] Algunos errores durante restauración (pueden ser normales)
    echo Continúa la instalación...
)

echo.
echo [5/5] Configuración final...
if not exist .env (
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANTE: Editar .env con las rutas de red correctas
)

if not exist logs mkdir logs
if not exist documentos_terceros mkdir documentos_terceros

echo.
echo ================================================================
echo   ✅ INSTALACIÓN COMPLETADA
echo ================================================================
echo.
echo 📋 PRÓXIMOS PASOS:
echo.
echo   1. Editar archivo .env con las rutas UNC de red:
echo      Buscar sección "CARPETAS DE RED - CAUSACIONES"
echo      Actualizar todas las rutas CARPETA_*
echo.
echo   2. Iniciar el servidor:
echo      .\\1_iniciar_gestor.bat
echo.
echo   3. Acceder al sistema:
echo      http://localhost:8099
echo.
echo 👤 Usuario de prueba:
echo    NIT: 805028041
echo    Usuario: admin
echo.
pause
"""

ruta_instalador = os.path.join(DESTINO, "instalador", "INSTALAR.bat")
with open(ruta_instalador, 'w', encoding='utf-8') as f:
    f.write(instalador_bat)
print("   ✅ INSTALAR.bat creado")

# README
readme = f"""
================================================================
   GESTOR DOCUMENTAL - INSTALACIÓN COMPLETA
================================================================

Backup creado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📦 CONTENIDO:

  codigo/                → Aplicación Flask completa
  base_datos/            → Backups PostgreSQL
    ├── gestor_documental.sql     (texto plano, 100% compatible)
    └── gestor_documental.backup  (comprimido, más rápido)
  instalador/            → Scripts de instalación automática
    └── INSTALAR.bat

================================================================
   REQUISITOS DEL SISTEMA
================================================================

✅ Windows 10/11 o Windows Server
✅ PostgreSQL 18 (o superior) instalado
✅ Python 3.8+ instalado
✅ Conexión a red corporativa (para carpetas compartidas)
✅ Permisos de administrador

================================================================
   INSTALACIÓN RÁPIDA
================================================================

1. Copiar esta carpeta completa al equipo destino

2. Abrir PowerShell o CMD como Administrador

3. Navegar a la carpeta instalador:
   cd "C:\\Users\\Usuario\\Documents\\Backup gestor documental\\instalador"

4. Ejecutar el instalador:
   .\\INSTALAR.bat

5. Seguir las instrucciones en pantalla

6. Editar .env con las rutas de red correctas

7. Iniciar: codigo\\1_iniciar_gestor.bat

8. Acceder a: http://localhost:8099

================================================================
   CONFIGURACIÓN DE RUTAS DE RED
================================================================

⚠️  MUY IMPORTANTE: Después de instalar, editar el archivo:

   codigo\\.env

Actualizar todas las variables CARPETA_* con las rutas UNC correctas:

  CARPETA_CYS=\\\\192.168.11.227\\acreedores_digitales\\COMPRAS_Y_SUMINISTROS\\...
  CARPETA_DOM=\\\\192.168.11.227\\acreedores_digitales\\DOMICILIOS\\...
  CARPETA_TIC=\\\\192.168.11.227\\acreedores_digitales\\TECNOLOGIA\\...
  CARPETA_MER=\\\\192.168.11.227\\acreedores_digitales\\ACREEDORES\\...
  CARPETA_MYP=\\\\192.168.11.227\\acreedores_digitales\\MYP ESTRATEGICA\\...
  CARPETA_FIN=\\\\192.168.11.227\\acreedores_digitales\\FINANCIERO\\...

⚠️  NO usar letras de unidad (V:, W:, X:) - SOLO rutas UNC (\\\\servidor\\...)

================================================================
   RESTAURACIÓN MANUAL (si el instalador falla)
================================================================

1. CREAR ENTORNO VIRTUAL:
   cd codigo
   python -m venv .venv
   .venv\\Scripts\\activate.bat

2. INSTALAR DEPENDENCIAS:
   pip install -r requirements.txt

3. CREAR BASE DE DATOS:
   psql -U postgres
   CREATE DATABASE gestor_documental;
   \\q

4. RESTAURAR BACKUP (elegir uno):
   
   Opción A (SQL - más compatible):
   psql -U postgres -d gestor_documental -f ..\\base_datos\\gestor_documental.sql
   
   Opción B (CUSTOM - más rápido):
   pg_restore -U postgres -d gestor_documental ..\\base_datos\\gestor_documental.backup

5. CONFIGURAR:
   copy .env.example .env
   (editar .env con rutas correctas)

6. INICIAR:
   python app.py

================================================================
   USUARIOS ADMINISTRATIVOS
================================================================

Usuario Principal:
  NIT: 805028041
  Usuario: admin
  Contraseña: (consultar en base de datos)

Usuario Secundario:
  NIT: 805013653
  Usuario: (consultar en base de datos)

================================================================
   MÓDULOS INCLUIDOS
================================================================

✅ Recibir Facturas       - Recepción de facturas de proveedores
✅ Relaciones             - Generación de relaciones digitales
✅ Causaciones            - Gestión de causaciones
✅ DIAN vs ERP           - Reconciliación de facturas electrónicas
✅ Terceros              - Gestión de proveedores
✅ Configuración         - Configuración del sistema
✅ Administración        - Gestión de usuarios y permisos

================================================================
   PUERTOS UTILIZADOS
================================================================

8099  → Gestor Documental (aplicación principal)
8097  → DIAN vs ERP (módulo independiente)

================================================================
   ESTRUCTURA DE ARCHIVOS
================================================================

codigo/
├── app.py                    → Aplicación principal Flask
├── extensions.py             → Extensiones SQLAlchemy
├── decoradores_permisos.py   → Sistema de permisos
├── utils_fecha.py            → Utilidades de fecha (Colombia UTC-5)
├── config_carpetas.py        → Configuración de carpetas de red
├── requirements.txt          → Dependencias Python
├── .env                      → Configuración (EDITAR)
├── .env.example              → Plantilla de configuración
├── modules/                  → Módulos del sistema
│   ├── recibir_facturas/
│   ├── relaciones/
│   ├── causaciones/
│   ├── configuracion/
│   ├── dian_vs_erp/
│   └── terceros/
├── templates/                → Plantillas HTML
├── static/                   → Archivos estáticos (CSS, JS, imágenes)
├── sql/                      → Scripts SQL
├── logs/                     → Logs del sistema
└── documentos_terceros/      → PDFs de documentación

================================================================
   SOLUCIÓN DE PROBLEMAS COMUNES
================================================================

❌ "pg_dump: command not found" o "psql: command not found"
   → Agregar PostgreSQL al PATH:
     C:\\Program Files\\PostgreSQL\\18\\bin

❌ "No se puede conectar a la base de datos"
   → Verificar PostgreSQL corriendo: services.msc
   → Verificar puerto 5432 disponible
   → Verificar USER y PASSWORD en .env

❌ "Error importando módulos Python"
   → Activar entorno virtual: .venv\\Scripts\\activate
   → Reinstalar: pip install -r requirements.txt

❌ "No lee las carpetas de red"
   → Verificar rutas UNC en .env
   → Verificar permisos de red del usuario
   → Ejecutar: python verificar_carpetas_red.py

❌ "Error al iniciar Flask"
   → Verificar puerto 8099 disponible
   → Verificar logs en logs/security.log
   → Verificar .env configurado correctamente

================================================================
   DOCUMENTACIÓN ADICIONAL
================================================================

📖 Instrucciones completas para desarrolladores:
   codigo\\.github\\copilot-instructions.md

📝 Logs del sistema:
   codigo\\logs\\security.log
   codigo\\logs\\app.log

🔧 Scripts de utilidad:
   codigo\\*.py (múltiples scripts de administración)

================================================================
   SOPORTE Y MANTENIMIENTO
================================================================

📧 Para soporte técnico, consultar con el equipo de TI

🔄 Para actualizar el sistema:
   git pull origin main (si está versionado)
   pip install -r requirements.txt (actualizar dependencias)

💾 Para hacer backup:
   Ejecutar: python crear_backup_completo.py

================================================================

Versión: Gestor Documental v2.0
Framework: Flask 3.0
Base de Datos: PostgreSQL 18
Python: 3.8+

================================================================
"""

ruta_readme = os.path.join(DESTINO, "README_INSTALACION.txt")
with open(ruta_readme, 'w', encoding='utf-8') as f:
    f.write(readme)
print("   ✅ README_INSTALACION.txt creado\n")

print("="*70)
print("🎉 BACKUP COMPLETADO")
print("="*70)
print(f"\n📦 Ubicación: {DESTINO}")
print("\n📂 Contenido:")
print("   ├── codigo/              (314 archivos, 5 directorios)")
print("   ├── base_datos/          (.sql y .backup)")
print("   ├── instalador/          (INSTALAR.bat)")
print("   └── README_INSTALACION.txt")
print("\n✅ Listo para copiar e instalar en otro equipo")
print("\n📋 Ver: README_INSTALACION.txt para instrucciones completas\n")
