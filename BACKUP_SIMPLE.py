"""
Backup Simplificado - Solo Copia Directa
Crea copia completa del proyecto sin verificaciones complejas
"""
import os
import shutil
from datetime import datetime
import subprocess

DESTINO = r"C:\Users\Usuario\Documents\Backup gestor documental"
ORIGEN = os.getcwd()

print("\n" + "="*70)
print("   BACKUP SIMPLIFICADO - GESTOR DOCUMENTAL")
print("="*70)
print(f"\nOrigen: {ORIGEN}")
print(f"Destino: {DESTINO}\n")

# Crear directorio destino
print("[1/4] Creando directorios...")
os.makedirs(os.path.join(DESTINO, "codigo"), exist_ok=True)
os.makedirs(os.path.join(DESTINO, "base_datos"), exist_ok=True)
os.makedirs(os.path.join(DESTINO, "instalador"), exist_ok=True)
print("✅ Directorios creados\n")

# Copiar código
print("[2/4] Copiando código fuente...(esto puede tardar varios minutos)")
destino_codigo = os.path.join(DESTINO, "codigo")

excluir = {
    '__pycache__', '.venv', 'venv', '.git', '.pytest_cache',
    'node_modules', 'BACKUP_ORIG', 'backups'
}

archivos_copiados = 0
for item in os.listdir(ORIGEN):
    if item in excluir:
        print(f"   Omitiendo: {item}")
        continue
    
    origen_item = os.path.join(ORIGEN, item)
    destino_item = os.path.join(destino_codigo, item)
    
    try:
        if os.path.isdir(origen_item):
            shutil.copytree(origen_item, destino_item, 
                           ignore=shutil.ignore_patterns('__pycache__', '*.pyc'),
                           dirs_exist_ok=True)
            print(f"   ✅ {item}/")
        else:
            shutil.copy2(origen_item, destino_item)
            print(f"   ✅ {item}")
        archivos_copiados += 1
    except Exception as e:
        print(f"   ⚠️  Error con {item}: {e}")

print(f"✅ {archivos_copiados} items copiados\n")

# Exportar BD
print("[3/4] Exportando base de datos...")
destino_bd = os.path.join(DESTINO, "base_datos")

# Backup formato SQL
archivo_sql = os.path.join(destino_bd, "gestor_documental.sql")
comando = [
    r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe",
    "-U", "postgres",
    "-h", "localhost",
    "-F", "p",  # Formato texto
    "--inserts",
    "-f", archivo_sql,
    "gestor_documental"
]

try:
    env = os.environ.copy()
    env['PGPASSWORD'] = "G3st0radm$2025."
    
    print("   Ejecutando pg_dump...")
    resultado = subprocess.run(comando, env=env, capture_output=True, text=True, timeout=300)
    
    if resultado.returncode == 0:
        tamanio = os.path.getsize(archivo_sql) / (1024 * 1024)
        print(f"   ✅ Backup SQL creado: {tamanio:.2f} MB")
    else:
        print(f"   ❌ Error: {resultado.stderr}")
except Exception as e:
    print(f"   ❌ Error exportando BD: {e}")

print("\n[4/4] Creando instalador...")

# Script de instalación
instalador_script = """@echo off
chcp 65001 > nul
echo ================================================================
echo   INSTALADOR - GESTOR DOCUMENTAL
echo ================================================================
echo.
echo [1/4] Instalando dependencias Python...
cd codigo
python -m venv .venv
call .venv\\Scripts\\activate
pip install -r requirements.txt

echo.
echo [2/4] Creando base de datos...
psql -U postgres -c "DROP DATABASE IF EXISTS gestor_documental;"
psql -U postgres -c "CREATE DATABASE gestor_documental;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE gestor_documental TO postgres;"

echo.
echo [3/4] Restaurando base de datos...
set PGPASSWORD=G3st0radm$2025.
psql -U postgres -d gestor_documental -f ..\\base_datos\\gestor_documental.sql

echo.
echo [4/4] Configurando...
if not exist .env copy .env.example .env
if not exist logs mkdir logs
if not exist documentos_terceros mkdir documentos_terceros

echo.
echo ================================================================
echo   ✅ INSTALACIÓN COMPLETADA
echo ================================================================
echo.
echo Editar .env con las rutas de red correctas
echo Luego ejecutar: 1_iniciar_gestor.bat
echo Acceder a: http://localhost:8099
echo.
pause
"""

ruta_instalador = os.path.join(DESTINO, "instalador", "INSTALAR.bat")
with open(ruta_instalador, 'w', encoding='utf-8') as f:
    f.write(instalador_script)

# README
readme = f"""
================================================================
   BACKUP GESTOR DOCUMENTAL - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================

📂 CONTENIDO:

  codigo/                → Código fuente completo
  base_datos/           → Backup PostgreSQL (.sql)
  instalador/           → INSTALAR.bat

================================================================
   INSTALACIÓN
================================================================

1. Copiar toda la carpeta al equipo destino

2. Abrir PowerShell como Administrador

3. Ir a: instalador/

4. Ejecutar: .\\INSTALAR.bat

5. Seguir instrucciones

================================================================
   REQUISITOS
================================================================

✅ PostgreSQL 18 instalado
✅ Python 3.8+ instalado
✅ Conexión a carpetas de red corporativa

================================================================
   CONFIGURACIÓN IMPORTANTE
================================================================

Después de instalar, editar:

  codigo\\.env

Actualizar las rutas UNC de las carpetas de red:

  CARPETA_CYS=\\\\192.168.11.227\\acreedores_digitales\\...
  CARPETA_DOM=\\\\192.168.11.227\\acreedores_digitales\\...
  etc...

================================================================

Usuario administrador:
  NIT: 805028041
  Usuario: admin

================================================================
"""

ruta_readme = os.path.join(DESTINO, "README_INSTALACION.txt")
with open(ruta_readme, 'w', encoding='utf-8') as f:
    f.write(readme)

print("✅ Instalador creado\n")

print("="*70)
print("🎉 BACKUP COMPLETADO")
print("="*70)
print(f"\n📦 Ubicación: {DESTINO}")
print("\n📂 Estructura:")
print("   ├── codigo/")
print("   ├── base_datos/")
print("   ├── instalador/")
print("   └── README_INSTALACION.txt")
print("\n✅ Listo para copiar a otro equipo\n")
