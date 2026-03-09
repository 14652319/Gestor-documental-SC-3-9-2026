"""
Completar backup - Solo base de datos PostgreSQL
"""

import os
import subprocess

DESTINO = r"D:\0.1. Backup Equipo Contablilidad\Gestor Documental\Backups\GESTOR_DOCUMENTAL_BACKUP_20260226_103600"
BD_DIR = os.path.join(DESTINO, "base_datos")
DB_NAME = "gestor_documental"
DB_USER = "postgres"
DB_PASSWORD = "G3st0radm$2025."
PG_DUMP = r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"

DB_FILE = os.path.join(BD_DIR, "gestor_documental_26feb2026.sql")
DB_CUSTOM_FILE = os.path.join(BD_DIR, "gestor_documental_26feb2026.backup")

# Configurar variable de entorno para password
env = os.environ.copy()
env['PGPASSWORD'] = DB_PASSWORD

print("=" * 80)
print("COMPLETANDO BACKUP - EXPORTANDO BASE DE DATOS")
print("=" * 80)
print(f"\nBase de datos: {DB_NAME}")
print(f"Destino: {BD_DIR}\n")

# Usar pg_dump con formato SQL plano
comando_sql = [
    PG_DUMP,
    "-h", "localhost",
    "-p", "5432",
    "-U", DB_USER,
    "-d", DB_NAME,
    "-f", DB_FILE,
    "--no-owner",
    "--no-acl",
    "--encoding=UTF8"
]

# Usar pg_dump con formato custom (comprimido)
comando_custom = [
    PG_DUMP,
    "-h", "localhost",
    "-p", "5432",
    "-U", DB_USER,
    "-d", DB_NAME,
    "-f", DB_CUSTOM_FILE,
    "-F", "c",
    "--no-owner",
    "--no-acl"
]

try:
    # Exportar en formato SQL
    print("[1/2] Exportando en formato SQL plano...")
    resultado = subprocess.run(comando_sql, env=env, check=True, capture_output=True, text=True)
    if os.path.exists(DB_FILE):
        tamano_sql = os.path.getsize(DB_FILE) / (1024 * 1024)
        print(f"   [OK] Archivo SQL creado: {tamano_sql:.2f} MB")
    else:
        print("   [ERROR] Archivo SQL no se creo")
    
    # Exportar en formato custom (comprimido)
    print("\n[2/2] Exportando en formato custom (comprimido)...")
    resultado = subprocess.run(comando_custom, env=env, check=True, capture_output=True, text=True)
    if os.path.exists(DB_CUSTOM_FILE):
        tamano_custom = os.path.getsize(DB_CUSTOM_FILE) / (1024 * 1024)
        print(f"   [OK] Archivo custom creado: {tamano_custom:.2f} MB")
    else:
        print("   [ERROR] Archivo custom no se creo")
    
    print("\n" + "=" * 80)
    print("EXPORTACION COMPLETADA EXITOSAMENTE")
    print("=" * 80)
    
except subprocess.CalledProcessError as e:
    print(f"\n[ERROR] Error ejecutando pg_dump:")
    print(f"   Comando: {' '.join(e.cmd)}")
    print(f"   Codigo de salida: {e.returncode}")
    if e.stderr:
        print(f"   Stderr: {e.stderr}")
    if e.stdout:
        print(f"   Stdout: {e.stdout}")
except Exception as e:
    print(f"\n[ERROR] Error inesperado: {e}")

# Verificar archivos creados
print("\n[VERIFICACION] Archivos en carpeta base_datos:")
if os.path.exists(BD_DIR):
    archivos = os.listdir(BD_DIR)
    if archivos:
        for archivo in archivos:
            ruta = os.path.join(BD_DIR, archivo)
            tamano = os.path.getsize(ruta) / (1024 * 1024)
            print(f"   - {archivo}: {tamano:.2f} MB")
    else:
        print("   (vacia)")
else:
    print("   [ERROR] Carpeta no existe")
