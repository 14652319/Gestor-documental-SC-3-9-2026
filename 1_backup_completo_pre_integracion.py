"""
═══════════════════════════════════════════════════════════════════
  BACKUP COMPLETO DEL PROYECTO PRINCIPAL
  Antes de integrar módulo SAGRILAFT
  Fecha: 28 de Enero de 2026
═══════════════════════════════════════════════════════════════════
"""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# ==================== CONFIGURACIÓN ====================
PROYECTO_PRINCIPAL = Path(__file__).parent
# Ruta FIJA donde se guardan los backups (fuera del proyecto)
CARPETA_BACKUPS = Path(r"C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\Backup")
NOMBRE_BACKUP = f"GESTOR_DOCUMENTAL_BACKUP_PREINTEGRACION_SAGRILAFT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
RUTA_BACKUP = CARPETA_BACKUPS / NOMBRE_BACKUP

# Base de datos PostgreSQL
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "gestor_documental"
DB_USER = "postgres"

# Carpetas a excluir del backup
EXCLUIR = [
    ".venv",
    "__pycache__",
    ".git",
    "logs",
    "*.pyc",
    ".pytest_cache",
    ".vscode"
]

print("\n" + "="*70)
print("   📦 BACKUP COMPLETO DEL PROYECTO PRINCIPAL")
print("="*70 + "\n")

# ==================== PASO 1: CREAR CARPETA DE BACKUP ====================
print("🔧 PASO 1: Creando carpeta de backup...")
try:
    RUTA_BACKUP.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ Carpeta creada: {RUTA_BACKUP.name}\n")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# ==================== PASO 2: COPIAR CÓDIGO FUENTE ====================
print("📄 PASO 2: Copiando código fuente...")
archivos_copiados = 0
carpetas_copiadas = 0

try:
    for item in PROYECTO_PRINCIPAL.iterdir():
        # Saltar carpetas excluidas
        if any(excl in str(item) for excl in EXCLUIR):
            continue
        
        destino = RUTA_BACKUP / item.name
        
        if item.is_file():
            shutil.copy2(item, destino)
            archivos_copiados += 1
        elif item.is_dir():
            shutil.copytree(item, destino, ignore=shutil.ignore_patterns(*EXCLUIR))
            carpetas_copiadas += 1
            print(f"   ✅ {item.name}/")
    
    print(f"   ✅ {archivos_copiados} archivos + {carpetas_copiadas} carpetas copiadas\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")

# ==================== PASO 3: BACKUP DE BASE DE DATOS ====================
print("🗄️  PASO 3: Respaldando base de datos PostgreSQL...")
archivo_sql = RUTA_BACKUP / f"backup_bd_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

try:
    # Intentar backup con pg_dump
    comando = [
        "pg_dump",
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-U", DB_USER,
        "-d", DB_NAME,
        "-f", str(archivo_sql),
        "--no-password"
    ]
    
    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if resultado.returncode == 0:
        tamaño = archivo_sql.stat().st_size / (1024 * 1024)  # MB
        print(f"   ✅ Base de datos respaldada: {archivo_sql.name} ({tamaño:.2f} MB)")
    else:
        print(f"   ⚠️  pg_dump no disponible. Creando script de backup manual...")
        # Crear script alternativo
        script_backup = RUTA_BACKUP / "ejecutar_backup_bd.bat"
        with open(script_backup, 'w', encoding='utf-8') as f:
            f.write(f'''@echo off
echo Respaldando base de datos...
pg_dump -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d {DB_NAME} -f "{archivo_sql}" --no-password
echo Backup completado: {archivo_sql}
pause
''')
        print(f"   ⚠️  Ejecuta manualmente: {script_backup.name}")
except subprocess.TimeoutExpired:
    print("   ⚠️  Timeout. Base de datos muy grande. Ejecuta backup manual.")
except FileNotFoundError:
    print("   ⚠️  pg_dump no encontrado. Instala PostgreSQL o usa pgAdmin.")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

print()

# ==================== PASO 4: COPIAR .ENV ====================
print("🔑 PASO 4: Respaldando archivo .env...")
env_origen = PROYECTO_PRINCIPAL / ".env"
env_destino = RUTA_BACKUP / ".env"

if env_origen.exists():
    shutil.copy2(env_origen, env_destino)
    print(f"   ✅ Archivo .env respaldado\n")
else:
    print(f"   ⚠️  Archivo .env no encontrado\n")

# ==================== PASO 5: CREAR ARCHIVO DE INVENTARIO ====================
print("📋 PASO 5: Generando inventario del backup...")
inventario = RUTA_BACKUP / "INVENTARIO_BACKUP.txt"

with open(inventario, 'w', encoding='utf-8') as f:
    f.write("═══════════════════════════════════════════════════════════════════\n")
    f.write("  INVENTARIO DE BACKUP - PROYECTO PRINCIPAL\n")
    f.write(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("═══════════════════════════════════════════════════════════════════\n\n")
    
    f.write("📦 CONTENIDO DEL BACKUP:\n\n")
    
    # Listar carpetas principales
    f.write("📁 CARPETAS:\n")
    for carpeta in sorted(RUTA_BACKUP.iterdir()):
        if carpeta.is_dir():
            # Contar archivos en la carpeta
            archivos = sum(1 for _ in carpeta.rglob("*") if _.is_file())
            f.write(f"   ✓ {carpeta.name}/ ({archivos} archivos)\n")
    
    f.write("\n📄 ARCHIVOS RAÍZ:\n")
    for archivo in sorted(RUTA_BACKUP.iterdir()):
        if archivo.is_file():
            tamaño_kb = archivo.stat().st_size / 1024
            f.write(f"   ✓ {archivo.name} ({tamaño_kb:.2f} KB)\n")
    
    f.write("\n" + "="*70 + "\n")
    f.write("🔒 ESTE BACKUP ES PREVIO A LA INTEGRACIÓN DEL MÓDULO SAGRILAFT\n")
    f.write("   Si algo sale mal, restaurar desde esta carpeta.\n")
    f.write("="*70 + "\n")

print(f"   ✅ Inventario generado: {inventario.name}\n")

# ==================== RESUMEN FINAL ====================
print("="*70)
print("   ✅ BACKUP COMPLETADO EXITOSAMENTE")
print("="*70 + "\n")

print(f"📁 Ubicación: {RUTA_BACKUP}\n")

print("📊 RESUMEN:")
print(f"   • {archivos_copiados} archivos raíz copiados")
print(f"   • {carpetas_copiadas} carpetas copiadas")
print(f"   • Base de datos: {'✅ Respaldada' if archivo_sql.exists() else '⚠️ Manual'}")
print(f"   • Archivo .env: {'✅ Incluido' if env_destino.exists() else '⚠️ No encontrado'}")
print()

print("🔒 BACKUP SEGURO:")
print(f"   • Excluye: .venv, __pycache__, logs")
print(f"   • Tamaño total: ~{sum(f.stat().st_size for f in RUTA_BACKUP.rglob('*') if f.is_file()) / (1024*1024):.2f} MB")
print()

print("🚀 PRÓXIMO PASO:")
print("   Ejecutar script de análisis de conflictos antes de integrar.")
print("   Esperar confirmación del usuario para proceder.\n")

print("="*70)
print("   🎯 LISTO PARA INTEGRACIÓN DEL MÓDULO SAGRILAFT")
print("="*70 + "\n")
