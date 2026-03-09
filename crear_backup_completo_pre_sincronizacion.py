"""
Script para crear BACKUP COMPLETO antes de implementar sincronización en tiempo real
Crea 2 backups:
1. Backup completo del sistema actual (recuperación)
2. Backup transportable según especificaciones de TIC
"""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
import zipfile

load_dotenv()

# Colores para terminal
class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(texto):
    print(f"\n{Color.CYAN}{Color.BOLD}{'='*80}{Color.END}")
    print(f"{Color.CYAN}{Color.BOLD}{texto.center(80)}{Color.END}")
    print(f"{Color.CYAN}{Color.BOLD}{'='*80}{Color.END}\n")

def print_seccion(texto):
    print(f"\n{Color.YELLOW}{'─'*80}{Color.END}")
    print(f"{Color.YELLOW}{Color.BOLD}{texto}{Color.END}")
    print(f"{Color.YELLOW}{'─'*80}{Color.END}")

def print_exito(texto):
    print(f"{Color.GREEN}✅ {texto}{Color.END}")

def print_error(texto):
    print(f"{Color.RED}❌ {texto}{Color.END}")

def print_info(texto):
    print(f"   {texto}")

def obtener_tamano_legible(bytes):
    """Convierte bytes a formato legible"""
    for unidad in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unidad}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def obtener_tamano_directorio(directorio):
    """Calcula el tamaño total de un directorio"""
    total = 0
    try:
        for entry in os.scandir(directorio):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += obtener_tamano_directorio(entry.path)
    except PermissionError:
        pass
    return total

def hacer_backup_postgresql(db_config, archivo_salida):
    """Ejecuta pg_dump para hacer backup de PostgreSQL"""
    print_info(f"Ejecutando pg_dump...")
    
    # Construir comando pg_dump
    comando = [
        'pg_dump',
        '-h', db_config['host'],
        '-p', str(db_config['port']),
        '-U', db_config['user'],
        '-d', db_config['database'],
        '-F', 'c',  # Formato custom (comprimido)
        '-f', archivo_salida,
        '--no-password'
    ]
    
    # Configurar variable de entorno para password
    env = os.environ.copy()
    env['PGPASSWORD'] = db_config['password']
    
    try:
        resultado = subprocess.run(
            comando,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        return True, "Backup de BD exitoso"
    except subprocess.CalledProcessError as e:
        return False, f"Error en pg_dump: {e.stderr}"
    except FileNotFoundError:
        return False, "pg_dump no encontrado. Asegúrate de tener PostgreSQL instalado y en PATH"

def copiar_archivos_sistema(directorio_origen, directorio_destino, excluir=[]):
    """Copia archivos del sistema excluyendo carpetas específicas"""
    archivos_copiados = 0
    tamano_total = 0
    
    for root, dirs, files in os.walk(directorio_origen):
        # Filtrar directorios a excluir
        dirs[:] = [d for d in dirs if d not in excluir and not d.startswith('.')]
        
        # Calcular ruta relativa
        ruta_relativa = os.path.relpath(root, directorio_origen)
        ruta_destino = os.path.join(directorio_destino, ruta_relativa)
        
        # Crear directorio destino
        os.makedirs(ruta_destino, exist_ok=True)
        
        # Copiar archivos
        for archivo in files:
            # Excluir archivos temporales y de sistema
            if archivo.endswith(('.pyc', '.pyo', '.log')) or archivo.startswith('.'):
                continue
            
            origen = os.path.join(root, archivo)
            destino = os.path.join(ruta_destino, archivo)
            
            try:
                shutil.copy2(origen, destino)
                tamano_total += os.path.getsize(origen)
                archivos_copiados += 1
                
                if archivos_copiados % 100 == 0:
                    print(f"\r   📄 Copiados: {archivos_copiados} archivos...", end='', flush=True)
            except Exception as e:
                print(f"\n   ⚠️  Error copiando {archivo}: {e}")
    
    print(f"\r   📄 Copiados: {archivos_copiados} archivos ({obtener_tamano_legible(tamano_total)})")
    return archivos_copiados, tamano_total

def crear_archivo_info_backup(directorio, tipo_backup, info_adicional=None):
    """Crea archivo con información del backup"""
    fecha_actual = datetime.now()
    
    info = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                      INFORMACIÓN DEL BACKUP                                ║
╚════════════════════════════════════════════════════════════════════════════╝

📅 Fecha de creación: {fecha_actual.strftime('%d/%m/%Y %H:%M:%S')}
📦 Tipo de backup: {tipo_backup}
💻 Sistema: Gestor Documental - Supertiendas Cañaveral

══════════════════════════════════════════════════════════════════════════════
CONTENIDO DEL BACKUP
══════════════════════════════════════════════════════════════════════════════

✅ Código fuente completo (Python, SQL, HTML, CSS, JS)
✅ Configuraciones (.env, config files)
✅ Base de datos PostgreSQL (dump completo)
✅ Archivos de documentación
✅ Scripts de utilidades
✅ Templates y recursos estáticos

══════════════════════════════════════════════════════════════════════════════
INSTRUCCIONES DE RESTAURACIÓN
══════════════════════════════════════════════════════════════════════════════

1. RESTAURAR CÓDIGO:
   - Extraer todo el contenido a la ubicación deseada
   - Instalar Python 3.11+
   - Crear entorno virtual: python -m venv .venv
   - Activar: .venv\\Scripts\\activate (Windows) o source .venv/bin/activate (Linux)
   - Instalar dependencias: pip install -r requirements.txt

2. RESTAURAR BASE DE DATOS:
   - Asegurarse de tener PostgreSQL instalado
   - Crear base de datos: createdb gestor_documental
   - Restaurar backup: pg_restore -h localhost -p 5432 -U postgres -d gestor_documental backup_gestor_documental.backup
   - Verificar tablas: psql -d gestor_documental -c "\\dt"

3. CONFIGURAR:
   - Copiar .env.example a .env
   - Configurar DATABASE_URL con tus credenciales
   - Configurar SECRET_KEY
   - Configurar MAIL_* para correos

4. INICIAR APLICACIÓN:
   - python app.py
   - Acceder a: http://localhost:8099

══════════════════════════════════════════════════════════════════════════════
INFORMACIÓN ADICIONAL
══════════════════════════════════════════════════════════════════════════════
"""
    
    if info_adicional:
        info += info_adicional
    
    info += f"""
══════════════════════════════════════════════════════════════════════════════
SOPORTE
══════════════════════════════════════════════════════════════════════════════

📧 Contacto: TIC - Supertiendas Cañaveral
📅 Versión del sistema: {fecha_actual.strftime('%Y%m%d')}

══════════════════════════════════════════════════════════════════════════════
"""
    
    archivo_info = os.path.join(directorio, '📋 LEEME_PRIMERO.txt')
    with open(archivo_info, 'w', encoding='utf-8') as f:
        f.write(info)
    
    print_exito(f"Archivo de información creado: {os.path.basename(archivo_info)}")

def main():
    print_header("BACKUP COMPLETO PRE-SINCRONIZACIÓN")
    print(f"{Color.BOLD}Creando 2 backups de seguridad antes de aplicar cambios{Color.END}\n")
    
    # Obtener configuración de BD
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print_error("DATABASE_URL no encontrado en .env")
        return False
    
    result = urlparse(database_url)
    db_config = {
        'user': result.username,
        'password': result.password,
        'database': result.path[1:],
        'host': result.hostname,
        'port': result.port or 5432
    }
    
    print_info(f"Base de datos: {db_config['database']}")
    print_info(f"Host: {db_config['host']}:{db_config['port']}")
    
    # Directorios
    directorio_actual = os.getcwd()
    directorio_padre = os.path.dirname(directorio_actual)
    
    # Timestamp para nombres únicos
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # ========================================
    # BACKUP 1: RECUPERACIÓN COMPLETA
    # ========================================
    print_seccion("📦 BACKUP 1: SISTEMA COMPLETO (Para recuperación)")
    
    nombre_backup1 = f"BACKUP_PRE_SINCRONIZACION_{timestamp}"
    directorio_backup1 = os.path.join(directorio_padre, nombre_backup1)
    
    print_info(f"Ubicación: {directorio_backup1}")
    
    # Crear directorio
    os.makedirs(directorio_backup1, exist_ok=True)
    print_exito("Directorio creado")
    
    # Crear subdirectorios
    os.makedirs(os.path.join(directorio_backup1, 'codigo'), exist_ok=True)
    os.makedirs(os.path.join(directorio_backup1, 'base_datos'), exist_ok=True)
    
    # Copiar código
    print_info("Copiando código fuente...")
    archivos1, tamano1 = copiar_archivos_sistema(
        directorio_actual,
        os.path.join(directorio_backup1, 'codigo'),
        excluir=['__pycache__', '.venv', 'venv', 'node_modules', 'BACKUP_COMPLETO_26DIC2025']
    )
    
    # Backup de BD
    print_info("Creando backup de PostgreSQL...")
    archivo_bd1 = os.path.join(directorio_backup1, 'base_datos', 'backup_gestor_documental.backup')
    exito_bd1, msg_bd1 = hacer_backup_postgresql(db_config, archivo_bd1)
    
    if exito_bd1:
        tamano_bd1 = os.path.getsize(archivo_bd1)
        print_exito(f"BD respaldada: {obtener_tamano_legible(tamano_bd1)}")
    else:
        print_error(msg_bd1)
    
    # Crear archivo de información
    crear_archivo_info_backup(
        directorio_backup1,
        "RECUPERACIÓN COMPLETA",
        f"""
🎯 Propósito: Backup de seguridad antes de implementar sincronización en tiempo real
📊 Archivos incluidos: {archivos1:,}
💾 Tamaño total: {obtener_tamano_legible(tamano1 + (tamano_bd1 if exito_bd1 else 0))}
🔧 Estado: Sistema funcional completo
"""
    )
    
    tamano_total_backup1 = obtener_tamano_directorio(directorio_backup1)
    print_exito(f"BACKUP 1 completado: {obtener_tamano_legible(tamano_total_backup1)}")
    
    # ========================================
    # BACKUP 2: TRANSPORTABLE (Especificaciones TIC)
    # ========================================
    print_seccion("📦 BACKUP 2: PAQUETE TRANSPORTABLE (Especificaciones TIC)")
    
    nombre_backup2 = f"GESTOR_DOCUMENTAL_TRANSPORTABLE_{timestamp}"
    directorio_backup2 = os.path.join(directorio_padre, nombre_backup2)
    
    print_info(f"Ubicación: {directorio_backup2}")
    
    # Crear directorio
    os.makedirs(directorio_backup2, exist_ok=True)
    print_exito("Directorio creado")
    
    # Copiar código (más limpio, sin temporales)
    print_info("Copiando código fuente optimizado...")
    archivos2, tamano2 = copiar_archivos_sistema(
        directorio_actual,
        directorio_backup2,
        excluir=[
            '__pycache__', '.venv', 'venv', 'node_modules', 
            'BACKUP_COMPLETO_26DIC2025', 'logs', 'documentos_terceros',
            'uploads'
        ]
    )
    
    # Crear estructura de directorios necesarios (vacíos)
    print_info("Creando estructura de directorios...")
    directorios_necesarios = [
        'logs',
        'documentos_terceros',
        'uploads/dian',
        'uploads/erp_fn',
        'uploads/erp_cm',
        'uploads/acuses',
        'uploads/rg_erp_er',
        'modules/dian_vs_erp/uploads'
    ]
    
    for dir_necesario in directorios_necesarios:
        ruta_completa = os.path.join(directorio_backup2, dir_necesario)
        os.makedirs(ruta_completa, exist_ok=True)
        # Crear archivo .gitkeep para mantener la carpeta en git
        with open(os.path.join(ruta_completa, '.gitkeep'), 'w') as f:
            f.write('')
    
    print_exito(f"{len(directorios_necesarios)} directorios de trabajo creados")
    
    # Backup de BD
    print_info("Creando backup de PostgreSQL...")
    archivo_bd2 = os.path.join(directorio_backup2, 'backup_gestor_documental.backup')
    exito_bd2, msg_bd2 = hacer_backup_postgresql(db_config, archivo_bd2)
    
    if exito_bd2:
        tamano_bd2 = os.path.getsize(archivo_bd2)
        print_exito(f"BD respaldada: {obtener_tamano_legible(tamano_bd2)}")
    else:
        print_error(msg_bd2)
    
    # Crear script de instalación Windows
    print_info("Creando scripts de instalación...")
    
    script_instalacion_windows = os.path.join(directorio_backup2, '1_INSTALAR_WINDOWS.bat')
    with open(script_instalacion_windows, 'w', encoding='utf-8') as f:
        f.write("""@echo off
echo ========================================
echo INSTALACION GESTOR DOCUMENTAL
echo Supertiendas Canaveral
echo ========================================
echo.

echo [1/5] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado. Instala Python 3.11+ primero.
    pause
    exit /b 1
)

echo [2/5] Creando entorno virtual...
python -m venv .venv

echo [3/5] Activando entorno virtual...
call .venv\\Scripts\\activate.bat

echo [4/5] Instalando dependencias...
pip install -r requirements.txt

echo [5/5] Configurando...
if not exist .env (
    copy .env.example .env
    echo ATENCION: Configura el archivo .env con tus credenciales
)

echo.
echo ========================================
echo INSTALACION COMPLETADA
echo ========================================
echo.
echo Proximos pasos:
echo 1. Edita .env con tus configuraciones
echo 2. Restaura la base de datos con 2_RESTAURAR_BD_WINDOWS.bat
echo 3. Inicia la aplicacion con 3_INICIAR_APLICACION.bat
echo.
pause
""")
    
    script_restaurar_bd = os.path.join(directorio_backup2, '2_RESTAURAR_BD_WINDOWS.bat')
    with open(script_restaurar_bd, 'w', encoding='utf-8') as f:
        f.write("""@echo off
echo ========================================
echo RESTAURAR BASE DE DATOS
echo ========================================
echo.

set /p PGHOST="Host PostgreSQL (default: localhost): " || set PGHOST=localhost
set /p PGPORT="Puerto (default: 5432): " || set PGPORT=5432
set /p PGUSER="Usuario (default: postgres): " || set PGUSER=postgres
set /p PGDATABASE="Base de datos (default: gestor_documental): " || set PGDATABASE=gestor_documental

echo.
echo Restaurando backup...
pg_restore -h %PGHOST% -p %PGPORT% -U %PGUSER% -d %PGDATABASE% -c backup_gestor_documental.backup

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo BASE DE DATOS RESTAURADA EXITOSAMENTE
    echo ========================================
) else (
    echo.
    echo ERROR: Fallo la restauracion
    echo Verifica que PostgreSQL este instalado y las credenciales sean correctas
)

echo.
pause
""")
    
    script_iniciar = os.path.join(directorio_backup2, '3_INICIAR_APLICACION.bat')
    with open(script_iniciar, 'w', encoding='utf-8') as f:
        f.write("""@echo off
echo ========================================
echo GESTOR DOCUMENTAL
echo Supertiendas Canaveral
echo ========================================
echo.
echo Iniciando aplicacion...
echo Accede a: http://localhost:8099
echo.
echo Presiona Ctrl+C para detener
echo.

call .venv\\Scripts\\activate.bat
python app.py
""")
    
    print_exito("Scripts de instalación creados")
    
    # Crear archivo de información
    crear_archivo_info_backup(
        directorio_backup2,
        "PAQUETE TRANSPORTABLE (Especificaciones TIC)",
        f"""
🎯 Propósito: Instalación en nuevos servidores o entornos
📊 Archivos incluidos: {archivos2:,}
💾 Tamaño total: {obtener_tamano_legible(tamano2 + (tamano_bd2 if exito_bd2 else 0))}
🔧 Estado: Listo para instalar
📜 Incluye: Scripts de instalación automatizada

SCRIPTS INCLUIDOS:
✅ 1_INSTALAR_WINDOWS.bat - Configuración automática
✅ 2_RESTAURAR_BD_WINDOWS.bat - Restauración de base de datos
✅ 3_INICIAR_APLICACION.bat - Inicio de aplicación
"""
    )
    
    tamano_total_backup2 = obtener_tamano_directorio(directorio_backup2)
    print_exito(f"BACKUP 2 completado: {obtener_tamano_legible(tamano_total_backup2)}")
    
    # ========================================
    # RESUMEN FINAL
    # ========================================
    print_header("RESUMEN DE BACKUPS CREADOS")
    
    print(f"{Color.BOLD}📦 BACKUP 1 - RECUPERACIÓN COMPLETA:{Color.END}")
    print_info(f"📁 Ubicación: {nombre_backup1}\\")
    print_info(f"💾 Tamaño: {obtener_tamano_legible(tamano_total_backup1)}")
    print_info(f"📄 Archivos: {archivos1:,}")
    print_info(f"✅ Base de datos: {'Incluida' if exito_bd1 else 'Error'}")
    
    print(f"\n{Color.BOLD}📦 BACKUP 2 - TRANSPORTABLE TIC:{Color.END}")
    print_info(f"📁 Ubicación: {nombre_backup2}\\")
    print_info(f"💾 Tamaño: {obtener_tamano_legible(tamano_total_backup2)}")
    print_info(f"📄 Archivos: {archivos2:,}")
    print_info(f"✅ Base de datos: {'Incluida' if exito_bd2 else 'Error'}")
    print_info(f"✅ Scripts instalación: 3 archivos .bat")
    
    print(f"\n{Color.GREEN}{Color.BOLD}🎉 BACKUPS COMPLETADOS EXITOSAMENTE{Color.END}")
    print(f"\n{Color.CYAN}Ahora puedes proceder con la implementación de sincronización en tiempo real.{Color.END}")
    print(f"{Color.CYAN}Si algo falla, puedes restaurar desde cualquiera de los 2 backups.{Color.END}\n")
    
    return True

if __name__ == '__main__':
    try:
        exito = main()
        if not exito:
            exit(1)
    except KeyboardInterrupt:
        print(f"\n\n{Color.YELLOW}⚠️  Backup interrumpido por el usuario{Color.END}")
        exit(1)
    except Exception as e:
        print(f"\n{Color.RED}❌ ERROR INESPERADO: {e}{Color.END}")
        import traceback
        traceback.print_exc()
        exit(1)
