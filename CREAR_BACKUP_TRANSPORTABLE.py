"""
SISTEMA DE BACKUP TRANSPORTABLE - GESTOR DOCUMENTAL
====================================================
Crea una copia completa del proyecto para instalar en otro equipo
Incluye: Código + Base de Datos + Instalador Automático

Fecha: Marzo 4, 2026
"""

import os
import shutil
import subprocess
from datetime import datetime
import zipfile

# ===== CONFIGURACIÓN =====
DESTINO_BACKUP = r"C:\Users\Usuario\Documents\Backup gestor documental"
NOMBRE_BD = "gestor_documental"
USUARIO_BD = "postgres"
PASSWORD_BD = "G3st0radm$2025."

# Ruta de pg_dump (ajustar según instalación de PostgreSQL)
PG_DUMP = r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"
PSQL = r"C:\Program Files\PostgreSQL\18\bin\psql.exe"

class Color:
    """Colores para consola Windows"""
    VERDE = '\033[92m'
    AMARILLO = '\033[93m'
    ROJO = '\033[91m'
    AZUL = '\033[94m'
    RESET = '\033[0m'
    NEGRITA = '\033[1m'

def log(mensaje, color=Color.RESET):
    """Imprime mensaje con timestamp y color"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{color}[{timestamp}] {mensaje}{Color.RESET}")

def verificar_prequisitos():
    """Verifica que existan las herramientas necesarias"""
    log("🔍 Verificando prerequisitos...", Color.AZUL)
    
    errores = []
    
    # Verificar pg_dump
    if not os.path.exists(PG_DUMP):
        errores.append(f"❌ No se encuentra pg_dump en: {PG_DUMP}")
    else:
        log(f"✅ pg_dump encontrado", Color.VERDE)
    
    # Verificar psql
    if not os.path.exists(PSQL):
        errores.append(f"❌ No se encuentra psql en: {PSQL}")
    else:
        log(f"✅ psql encontrado", Color.VERDE)
    
    # Verificar conexión a BD
    try:
        env = os.environ.copy()
        env['PGPASSWORD'] = PASSWORD_BD
        resultado = subprocess.run(
            [PSQL, "-U", USUARIO_BD, "-h", "localhost", "-d", NOMBRE_BD, "-c", "SELECT 1"],
            env=env,
            capture_output=True,
            text=True,
            timeout=10
        )
        if resultado.returncode == 0:
            log(f"✅ Conexión a base de datos OK", Color.VERDE)
        else:
            errores.append(f"❌ No se puede conectar a la BD: {resultado.stderr}")
    except Exception as e:
        errores.append(f"❌ Error verificando BD: {str(e)}")
    
    if errores:
        log("\n⛔ ERRORES ENCONTRADOS:", Color.ROJO)
        for error in errores:
            log(error, Color.ROJO)
        return False
    
    log("✅ Todos los prerequisitos cumplidos\n", Color.VERDE)
    return True

def crear_directorio_backup():
    """Crea el directorio de destino"""
    log("📁 Creando directorio de backup...", Color.AZUL)
    
    try:
        # Crear directorio principal
        os.makedirs(DESTINO_BACKUP, exist_ok=True)
        
        # Crear subdirectorios
        subdirs = [
            "codigo",
            "base_datos",
            "instalador"
        ]
        
        for subdir in subdirs:
            ruta = os.path.join(DESTINO_BACKUP, subdir)
            os.makedirs(ruta, exist_ok=True)
            log(f"  ✅ {subdir}/", Color.VERDE)
        
        log(f"✅ Directorio creado: {DESTINO_BACKUP}\n", Color.VERDE)
        return True
    except Exception as e:
        log(f"❌ Error creando directorio: {str(e)}", Color.ROJO)
        return False

def copiar_codigo_fuente():
    """Copia el código fuente completo"""
    log("📦 Copiando código fuente...", Color.AZUL)
    
    directorio_actual = os.getcwd()
    destino_codigo = os.path.join(DESTINO_BACKUP, "codigo")
    
    # Archivos y carpetas a INCLUIR
    incluir = [
        'app.py',
        'extensions.py',
        'decoradores_permisos.py',
        'utils_fecha.py',
        'utils_licencia.py',
        'config_carpetas.py',
        'requirements.txt',
        '.env.example',  # Incluir ejemplo, NO el .env real por seguridad
        'modules',
        'templates',
        'static',
        'sql',
        'logs',
        'documentos_terceros',
        '.github',
        'README_Estructura.txt',
        'REQUISITOS_INSTALACION.txt',
        '*.md',
        '1_iniciar_gestor.bat',
        '2_iniciar_dian.bat'
    ]
    
    # Carpetas/archivos a EXCLUIR
    excluir = [
        '__pycache__',
        '.venv',
        'venv',
        '.git',
        '.pytest_cache',
        'node_modules',
        '*.pyc',
        '*.pyo',
        '*.log',
        'BACKUP_ORIG',
        'backups'
    ]
    
    archivos_copiados = 0
    
    try:
        for item in os.listdir(directorio_actual):
            # Verificar si está en la lista de exclusión
            if any(excluir_item in item for excluir_item in excluir):
                continue
            
            origen = os.path.join(directorio_actual, item)
            destino = os.path.join(destino_codigo, item)
            
            try:
                if os.path.isdir(origen):
                    # Copiar directorio completo
                    shutil.copytree(origen, destino, 
                                   ignore=shutil.ignore_patterns(*excluir),
                                   dirs_exist_ok=True)
                    log(f"  📁 {item}/ copiado", Color.VERDE)
                elif os.path.isfile(origen):
                    # Copiar archivo
                    shutil.copy2(origen, destino)
                    log(f"  📄 {item} copiado", Color.VERDE)
                
                archivos_copiados += 1
            except Exception as e:
                log(f"  ⚠️  Error copiando {item}: {str(e)}", Color.AMARILLO)
        
        log(f"✅ Código fuente copiado ({archivos_copiados} items)\n", Color.VERDE)
        return True
    except Exception as e:
        log(f"❌ Error copiando código: {str(e)}", Color.ROJO)
        return False

def exportar_base_datos():
    """Exporta la base de datos completa (schema + datos)"""
    log("💾 Exportando base de datos...", Color.AZUL)
    
    destino_bd = os.path.join(DESTINO_BACKUP, "base_datos")
    
    # 1. Backup en formato CUSTOM (comprimido, recomendado)
    archivo_custom = os.path.join(destino_bd, "gestor_documental.backup")
    log("  Exportando en formato CUSTOM (comprimido)...", Color.AZUL)
    
    comando_custom = [
        PG_DUMP,
        "-U", USUARIO_BD,
        "-h", "localhost",
        "-p", "5432",
        "-F", "c",  # Formato custom
        "-b",       # Incluir blobs
        "-v",       # Verbose
        "-f", archivo_custom,
        NOMBRE_BD
    ]
    
    try:
        env = os.environ.copy()
        env['PGPASSWORD'] = PASSWORD_BD
        
        resultado = subprocess.run(comando_custom, env=env, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            tamanio = os.path.getsize(archivo_custom) / (1024 * 1024)
            log(f"  ✅ Backup CUSTOM creado: {tamanio:.2f} MB", Color.VERDE)
        else:
            log(f"  ❌ Error en backup CUSTOM: {resultado.stderr}", Color.ROJO)
            return False
    except Exception as e:
        log(f"  ❌ Error exportando en formato CUSTOM: {str(e)}", Color.ROJO)
        return False
    
    # 2. Backup en formato SQL (texto plano, compatible)
    archivo_sql = os.path.join(destino_bd, "gestor_documental.sql")
    log("  Exportando en formato SQL (texto plano)...", Color.AZUL)
    
    comando_sql = [
        PG_DUMP,
        "-U", USUARIO_BD,
        "-h", "localhost",
        "-p", "5432",
        "-F", "p",  # Formato plain (SQL)
        "-b",       # Incluir blobs
        "--inserts", # Usar INSERT en vez de COPY
        "-f", archivo_sql,
        NOMBRE_BD
    ]
    
    try:
        resultado = subprocess.run(comando_sql, env=env, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            tamanio = os.path.getsize(archivo_sql) / (1024 * 1024)
            log(f"  ✅ Backup SQL creado: {tamanio:.2f} MB", Color.VERDE)
        else:
            log(f"  ⚠️  Advertencia en backup SQL: {resultado.stderr}", Color.AMARILLO)
    except Exception as e:
        log(f"  ⚠️  Error exportando en formato SQL: {str(e)}", Color.AMARILLO)
    
    log(f"✅ Base de datos exportada\n", Color.VERDE)
    return True

def crear_instalador():
    """Crea scripts de instalación automática"""
    log("🔧 Creando instalador automático...", Color.AZUL)
    
    destino_instalador = os.path.join(DESTINO_BACKUP, "instalador")
    
    # ==== SCRIPT 1: INSTALAR.bat (Windows) ====
    script_bat = """@echo off
chcp 65001 > nul
echo ================================================================
echo   INSTALADOR AUTOMÁTICO - GESTOR DOCUMENTAL
echo ================================================================
echo.
echo Este script instalará el Gestor Documental en este equipo
echo.
echo REQUISITOS:
echo   - PostgreSQL 18 instalado
echo   - Python 3.8+ instalado
echo   - Usuario 'postgres' con permisos
echo.
pause

REM Verificar Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Instalar Python 3.8+
    pause
    exit /b 1
)

REM Verificar PostgreSQL
psql --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] PostgreSQL no encontrado. Verificar instalación
    pause
    exit /b 1
)

echo.
echo [1/5] Instalando dependencias Python...
cd codigo
python -m venv .venv
call .venv\\Scripts\\activate
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Error instalando dependencias
    pause
    exit /b 1
)

echo.
echo [2/5] Creando base de datos...
psql -U postgres -c "DROP DATABASE IF EXISTS gestor_documental;"
psql -U postgres -c "DROP USER IF EXISTS gestor_user;"
psql -U postgres -c "CREATE USER gestor_user WITH PASSWORD 'abc123';"
psql -U postgres -c "CREATE DATABASE gestor_documental OWNER gestor_user;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE gestor_documental TO gestor_user;"

echo.
echo [3/5] Restaurando base de datos...
echo.
echo Seleccione el formato de restauración:
echo   1. CUSTOM (.backup) - Recomendado, más rápido
echo   2. SQL (.sql) - Alternativo, más lento
echo.
set /p FORMATO="Ingrese opción (1 o 2): "

if "%FORMATO%"=="1" (
    echo Restaurando desde formato CUSTOM...
    pg_restore -U gestor_user -h localhost -d gestor_documental -v ..\\base_datos\\gestor_documental.backup
) else (
    echo Restaurando desde formato SQL...
    psql -U gestor_user -h localhost -d gestor_documental -f ..\\base_datos\\gestor_documental.sql
)

if errorlevel 1 (
    echo [ADVERTENCIA] Algunos errores durante la restauración (pueden ser normales)
)

echo.
echo [4/5] Configurando .env...
if not exist .env (
    copy .env.example .env
    echo [IMPORTANTE] Editar el archivo .env con las rutas correctas de red
)

echo.
echo [5/5] Creando directorios...
if not exist logs mkdir logs
if not exist documentos_terceros mkdir documentos_terceros
if not exist "Proyecto Dian Vs ERP v5.20251130" mkdir "Proyecto Dian Vs ERP v5.20251130"

echo.
echo ================================================================
echo   ✅ INSTALACIÓN COMPLETADA
echo ================================================================
echo.
echo PRÓXIMOS PASOS:
echo   1. Editar .env con las rutas de red correctas
echo   2. Ejecutar: 1_iniciar_gestor.bat
echo   3. Acceder a: http://localhost:8099
echo.
echo Usuario de prueba:
echo   NIT: 805028041
echo   Usuario: admin
echo   Contraseña: (según configuración)
echo.
pause
"""

    ruta_bat = os.path.join(destino_instalador, "INSTALAR.bat")
    with open(ruta_bat, 'w', encoding='utf-8') as f:
        f.write(script_bat)
    log("  ✅ INSTALAR.bat creado", Color.VERDE)
    
    # ==== SCRIPT 2: RESTAURAR_BD.py (Python) ====
    script_py = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script de restauración de base de datos
Alternativa a INSTALAR.bat para control más preciso
'''

import os
import subprocess
import sys

# Configuración
USUARIO_BD = "gestor_user"
PASSWORD_BD = "abc123"
NOMBRE_BD = "gestor_documental"

def ejecutar_comando(comando, env=None):
    '''Ejecuta comando y retorna resultado'''
    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        env=env or os.environ.copy()
    )
    return resultado

def crear_base_datos():
    '''Crea la base de datos y usuario'''
    print("\\n[1/3] Creando base de datos...")
    
    comandos = [
        f"DROP DATABASE IF EXISTS {NOMBRE_BD};",
        f"DROP USER IF EXISTS {USUARIO_BD};",
        f"CREATE USER {USUARIO_BD} WITH PASSWORD '{PASSWORD_BD}';",
        f"CREATE DATABASE {NOMBRE_BD} OWNER {USUARIO_BD};",
        f"GRANT ALL PRIVILEGES ON DATABASE {NOMBRE_BD} TO {USUARIO_BD};"
    ]
    
    for comando in comandos:
        resultado = ejecutar_comando(
            ["psql", "-U", "postgres", "-c", comando]
        )
        if resultado.returncode != 0:
            print(f"⚠️  Advertencia: {resultado.stderr}")
    
    print("✅ Base de datos creada")

def restaurar_bd():
    '''Restaura el backup de la base de datos'''
    print("\\n[2/3] Restaurando base de datos...")
    
    # Buscar archivos de backup
    bd_dir = os.path.join(os.path.dirname(__file__), "..", "base_datos")
    archivo_custom = os.path.join(bd_dir, "gestor_documental.backup")
    archivo_sql = os.path.join(bd_dir, "gestor_documental.sql")
    
    env = os.environ.copy()
    env['PGPASSWORD'] = PASSWORD_BD
    
    # Intentar con formato CUSTOM
    if os.path.exists(archivo_custom):
        print(f"Restaurando desde: {archivo_custom}")
        resultado = ejecutar_comando(
            ["pg_restore", "-U", USUARIO_BD, "-h", "localhost", 
             "-d", NOMBRE_BD, "-v", archivo_custom],
            env=env
        )
        if resultado.returncode == 0:
            print("✅ Restauración completada")
            return True
    
    # Intentar con formato SQL
    if os.path.exists(archivo_sql):
        print(f"Restaurando desde: {archivo_sql}")
        resultado = ejecutar_comando(
            ["psql", "-U", USUARIO_BD, "-h", "localhost", 
             "-d", NOMBRE_BD, "-f", archivo_sql],
            env=env
        )
        print("✅ Restauración completada")
        return True
    
    print("❌ No se encontraron archivos de backup")
    return False

def verificar_instalacion():
    '''Verifica que la instalación sea correcta'''
    print("\\n[3/3] Verificando instalación...")
    
    env = os.environ.copy()
    env['PGPASSWORD'] = PASSWORD_BD
    
    resultado = ejecutar_comando(
        ["psql", "-U", USUARIO_BD, "-h", "localhost", "-d", NOMBRE_BD,
         "-c", "SELECT COUNT(*) FROM usuarios;"],
        env=env
    )
    
    if resultado.returncode == 0:
        print("✅ Verificación exitosa")
        print(resultado.stdout)
        return True
    else:
        print("❌ Error en verificación")
        print(resultado.stderr)
        return False

if __name__ == "__main__":
    print("="*60)
    print("  RESTAURAR BASE DE DATOS - GESTOR DOCUMENTAL")
    print("="*60)
    
    try:
        crear_base_datos()
        restaurar_bd()
        verificar_instalacion()
        
        print("\\n" + "="*60)
        print("  ✅ PROCESO COMPLETADO")
        print("="*60)
    except KeyboardInterrupt:
        print("\\n\\n⚠️  Proceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ ERROR: {str(e)}")
        sys.exit(1)
"""

    ruta_py = os.path.join(destino_instalador, "RESTAURAR_BD.py")
    with open(ruta_py, 'w', encoding='utf-8') as f:
        f.write(script_py)
    log("  ✅ RESTAURAR_BD.py creado", Color.VERDE)
    
    # ==== SCRIPT 3: LEEME.txt ====
    leeme = """
=================================================================
   INSTALACIÓN DEL GESTOR DOCUMENTAL - GUÍA RÁPIDA
=================================================================

📦 CONTENIDO DEL BACKUP:

  1. codigo/             → Código fuente completo
  2. base_datos/         → Backup de PostgreSQL
  3. instalador/         → Scripts de instalación
     - INSTALAR.bat      → Instalador automático Windows
     - RESTAURAR_BD.py   → Script Python alternativo
     - LEEME.txt         → Este archivo

=================================================================
   REQUISITOS PREVIOS
=================================================================

✅ PostgreSQL 18 instalado
✅ Python 3.8 o superior instalado
✅ Usuario 'postgres' con permisos administrativos
✅ Conexión de red a las carpetas compartidas

=================================================================
   INSTALACIÓN RÁPIDA (Windows)
=================================================================

1. Abrir PowerShell o CMD como Administrador

2. Ir al directorio del instalador:
   cd "C:\\Users\\Usuario\\Documents\\Backup gestor documental\\instalador"

3. Ejecutar el instalador:
   .\\INSTALAR.bat

4. Seguir las instrucciones en pantalla

5. Editar el archivo .env con las rutas de red correctas

6. Iniciar el servidor:
   cd ..\\codigo
   .\\1_iniciar_gestor.bat

7. Acceder a: http://localhost:8099

=================================================================
   INSTALACIÓN MANUAL
=================================================================

Si el instalador automático falla, seguir estos pasos:

1. CREAR ENTORNO VIRTUAL:
   cd codigo
   python -m venv .venv
   .venv\\Scripts\\activate

2. INSTALAR DEPENDENCIAS:
   pip install -r requirements.txt

3. CREAR BASE DE DATOS (en psql):
   CREATE USER gestor_user WITH PASSWORD 'abc123';
   CREATE DATABASE gestor_documental OWNER gestor_user;
   GRANT ALL PRIVILEGES ON DATABASE gestor_documental TO gestor_user;

4. RESTAURAR BACKUP:
   Opción A (recomendado):
     pg_restore -U gestor_user -d gestor_documental gestor_documental.backup
   
   Opción B (alternativo):
     psql -U gestor_user -d gestor_documental -f gestor_documental.sql

5. CONFIGURAR .env:
   Copiar .env.example a .env
   Editar las rutas de red

6. INICIAR SERVIDOR:
   python app.py

=================================================================
   CONFIGURACIÓN DE RUTAS DE RED
=================================================================

Editar el archivo: codigo\\.env

Buscar la sección "CARPETAS DE RED - CAUSACIONES"

Actualizar las rutas UNC según su infraestructura:

  CARPETA_CYS=\\\\192.168.11.227\\acreedores_digitales\\...
  CARPETA_DOM=\\\\192.168.11.227\\acreedores_digitales\\...
  ...etc

⚠️  IMPORTANTE: Usar rutas UNC (\\\\servidor\\...) 
   NO usar letras de unidad (V:, W:, X:)

=================================================================
   USUARIOS DE PRUEBA
=================================================================

Usuario Administrador Interno:
  NIT: 805028041
  Usuario: admin
  Contraseña: (según configuración en BD)

Usuario Administrador Interno 2:
  NIT: 805013653
  Usuario: (verificar en BD)
  Contraseña: (según configuración en BD)

=================================================================
   SOLUCIÓN DE PROBLEMAS
=================================================================

❌ "pg_restore: command not found"
   → Agregar PostgreSQL al PATH del sistema
   → Ruta típica: C:\\Program Files\\PostgreSQL\\18\\bin

❌ "No se puede conectar a la base de datos"
   → Verificar que PostgreSQL esté corriendo
   → Verificar usuario/contraseña en .env
   → Verificar puerto 5432 disponible

❌ "Error importando módulos Python"
   → Verificar que el entorno virtual esté activado
   → Reinstalar requirements: pip install -r requirements.txt

❌ "No lee las carpetas de red"
   → Verificar rutas UNC en .env
   → Verificar permisos de red
   → Ejecutar: python verificar_carpetas_red.py

=================================================================
   SOPORTE Y DOCUMENTACIÓN
=================================================================

📖 Documentación completa en:
   codigo\\.github\\copilot-instructions.md

📝 Logs del sistema en:
   codigo\\logs\\security.log
   codigo\\logs\\app.log

🔧 Scripts de utilidad en:
   codigo\\*.py (archivos de administración)

=================================================================

Fecha de backup: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
Versión: Gestor Documental v2.0 (Marzo 2026)

=================================================================
"""

    ruta_leeme = os.path.join(destino_instalador, "LEEME.txt")
    with open(ruta_leeme, 'w', encoding='utf-8') as f:
        f.write(leeme)
    log("  ✅ LEEME.txt creado", Color.VERDE)
    
    log(f"✅ Instalador creado\n", Color.VERDE)
    return True

def crear_resumen():
    """Crea archivo de resumen del backup"""
    log("📊 Creando resumen del backup...", Color.AZUL)
    
    resumen = f"""
=================================================================
   RESUMEN DEL BACKUP - GESTOR DOCUMENTAL
=================================================================

📅 Fecha de backup: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📁 Ubicación: {DESTINO_BACKUP}

=================================================================
   CONTENIDO
=================================================================

1. CÓDIGO FUENTE (codigo/):
   ✅ Archivos Python (.py)
   ✅ Templates HTML
   ✅ Archivos estáticos (CSS, JS, imágenes)
   ✅ Módulos (recibir_facturas, relaciones, causaciones, etc.)
   ✅ Configuraciones
   ✅ Scripts de inicio

2. BASE DE DATOS (base_datos/):
   ✅ gestor_documental.backup (formato CUSTOM)
   ✅ gestor_documental.sql (formato SQL)
   
3. INSTALADOR (instalador/):
   ✅ INSTALAR.bat (Windows automático)
   ✅ RESTAURAR_BD.py (script Python)
   ✅ LEEME.txt (documentación)

=================================================================
   INSTRUCCIONES RÁPIDAS
=================================================================

Para instalar en otro equipo:

1. Copiar la carpeta completa al equipo destino
2. Ir a: instalador/
3. Ejecutar: INSTALAR.bat
4. Seguir las instrucciones

Para más detalles, ver: instalador/LEEME.txt

=================================================================
   INFORMACIÓN TÉCNICA
=================================================================

Base de datos: PostgreSQL
Usuario BD: {USUARIO_BD}
Nombre BD: {NOMBRE_BD}
Framework: Flask 3.0
Python: 3.8+

Módulos incluidos:
  - Recibir Facturas
  - Relaciones
  - Causaciones
  - DIAN vs ERP
  - Terceros
  - Configuración
  - Administración

=================================================================
"""

    ruta_resumen = os.path.join(DESTINO_BACKUP, "RESUMEN_BACKUP.txt")
    with open(ruta_resumen, 'w', encoding='utf-8') as f:
        f.write(resumen)
    
    log(f"✅ Resumen creado\n", Color.VERDE)
    return True

def main():
    """Función principal"""
    import sys
    
    print("\n" + "="*70)
    print(f"{Color.NEGRITA}{Color.AZUL}   CREAR BACKUP TRANSPORTABLE - GESTOR DOCUMENTAL{Color.RESET}")
    print("="*70 + "\n")
    
    print(f"{Color.AMARILLO}Este script creará una copia completa del proyecto en:{Color.RESET}")
    print(f"{Color.NEGRITA}{DESTINO_BACKUP}{Color.RESET}\n")
    
    # Modo automático si se pasa --auto
    if "--auto" not in sys.argv:
        input("Presione ENTER para continuar o Ctrl+C para cancelar...")
    else:
        log("Modo automático activado, iniciando backup...", Color.VERDE)
    print()
    
    # Paso 1: Verificar prerequisitos
    if not verificar_prequisitos():
        log("\n⛔ No se puede continuar. Resolver los errores primero.", Color.ROJO)
        return False
    
    # Paso 2: Crear directorio
    if not crear_directorio_backup():
        return False
    
    # Paso 3: Copiar código
    if not copiar_codigo_fuente():
        return False
    
    # Paso 4: Exportar BD
    if not exportar_base_datos():
        return False
    
    # Paso 5: Crear instalador
    if not crear_instalador():
        return False
    
    # Paso 6: Crear resumen
    if not crear_resumen():
        return False
    
    # ===== FINALIZACIÓN =====
    print("\n" + "="*70)
    log(f"🎉 BACKUP COMPLETADO EXITOSAMENTE", Color.VERDE + Color.NEGRITA)
    print("="*70 + "\n")
    
    print(f"{Color.AZUL}📦 Ubicación del backup:{Color.RESET}")
    print(f"   {DESTINO_BACKUP}\n")
    
    print(f"{Color.AZUL}📂 Estructura creada:{Color.RESET}")
    print(f"   ├── codigo/              (código fuente completo)")
    print(f"   ├── base_datos/          (backup PostgreSQL)")
    print(f"   ├── instalador/          (scripts de instalación)")
    print(f"   └── RESUMEN_BACKUP.txt   (este resumen)\n")
    
    print(f"{Color.AZUL}📋 Próximos pasos:{Color.RESET}")
    print(f"   1. Copiar la carpeta al equipo destino")
    print(f"   2. Ejecutar: instalador\\INSTALAR.bat")
    print(f"   3. Seguir las instrucciones en pantalla\n")
    
    print(f"{Color.AMARILLO}⚠️  Recordar:{Color.RESET}")
    print(f"   - Configurar el archivo .env con las rutas de red correctas")
    print(f"   - Verificar que PostgreSQL esté instalado en el equipo destino")
    print(f"   - Verificar que Python 3.8+ esté instalado\n")
    
    return True

if __name__ == "__main__":
    try:
        exito = main()
        if exito:
            input("\nPresione ENTER para salir...")
        else:
            log("\n❌ El proceso no se completó correctamente", Color.ROJO)
            input("\nPresione ENTER para salir...")
    except KeyboardInterrupt:
        log("\n\n⚠️  Proceso cancelado por el usuario", Color.AMARILLO)
    except Exception as e:
        log(f"\n❌ ERROR INESPERADO: {str(e)}", Color.ROJO)
        import traceback
        traceback.print_exc()
        input("\nPresione ENTER para salir...")
