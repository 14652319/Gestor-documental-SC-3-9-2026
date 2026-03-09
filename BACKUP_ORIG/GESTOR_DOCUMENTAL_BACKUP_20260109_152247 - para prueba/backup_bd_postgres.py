"""
Script para hacer backup de PostgreSQL usando pg_dump
Busca pg_dump automáticamente y hace backup en ambos directorios
"""
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
from datetime import datetime

load_dotenv()

# Colores
class Color:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def encontrar_pg_dump():
    """Busca pg_dump en ubicaciones comunes de Windows"""
    print(f"{Color.CYAN}🔍 Buscando pg_dump en el sistema...{Color.END}")
    
    # Ubicaciones comunes de PostgreSQL en Windows
    ubicaciones_comunes = [
        r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\14\bin\pg_dump.exe",
        r"C:\Program Files (x86)\PostgreSQL\18\bin\pg_dump.exe",
        r"C:\Program Files (x86)\PostgreSQL\17\bin\pg_dump.exe",
        r"C:\Program Files (x86)\PostgreSQL\16\bin\pg_dump.exe",
        r"C:\PostgreSQL\18\bin\pg_dump.exe",
        r"C:\PostgreSQL\17\bin\pg_dump.exe",
        r"C:\PostgreSQL\16\bin\pg_dump.exe",
    ]
    
    # Buscar en ubicaciones comunes
    for ubicacion in ubicaciones_comunes:
        if os.path.exists(ubicacion):
            print(f"{Color.GREEN}✅ pg_dump encontrado: {ubicacion}{Color.END}")
            return ubicacion
    
    # Intentar buscar en PATH
    try:
        resultado = subprocess.run(['where', 'pg_dump'], capture_output=True, text=True, shell=True)
        if resultado.returncode == 0:
            ruta = resultado.stdout.strip().split('\n')[0]
            print(f"{Color.GREEN}✅ pg_dump encontrado en PATH: {ruta}{Color.END}")
            return ruta
    except:
        pass
    
    # Buscar recursivamente en Program Files (más lento)
    print(f"{Color.YELLOW}⏳ Buscando en Program Files (puede tardar)...{Color.END}")
    for drive in ['C:\\']:
        for root in [r'Program Files\PostgreSQL', r'Program Files (x86)\PostgreSQL', 'PostgreSQL']:
            base_path = os.path.join(drive, root)
            if os.path.exists(base_path):
                for dirpath, dirnames, filenames in os.walk(base_path):
                    if 'pg_dump.exe' in filenames:
                        ruta = os.path.join(dirpath, 'pg_dump.exe')
                        print(f"{Color.GREEN}✅ pg_dump encontrado: {ruta}{Color.END}")
                        return ruta
    
    return None

def hacer_backup_bd(pg_dump_path, db_config, archivo_salida):
    """Ejecuta pg_dump para hacer backup"""
    print(f"\n{Color.CYAN}📦 Creando backup de BD...{Color.END}")
    print(f"   Base de datos: {db_config['database']}")
    print(f"   Host: {db_config['host']}:{db_config['port']}")
    print(f"   Archivo: {os.path.basename(archivo_salida)}")
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)
    
    # Comando pg_dump
    comando = [
        pg_dump_path,
        '-h', db_config['host'],
        '-p', str(db_config['port']),
        '-U', db_config['user'],
        '-d', db_config['database'],
        '-F', 'c',  # Formato custom comprimido
        '-f', archivo_salida,
        '--no-password'
    ]
    
    # Configurar password en variable de entorno
    env = os.environ.copy()
    env['PGPASSWORD'] = db_config['password']
    
    try:
        print(f"{Color.YELLOW}   Ejecutando pg_dump...{Color.END}", end='', flush=True)
        
        resultado = subprocess.run(
            comando,
            env=env,
            capture_output=True,
            text=True,
            check=True,
            timeout=300  # 5 minutos máximo
        )
        
        # Verificar que el archivo se creó
        if os.path.exists(archivo_salida):
            tamano = os.path.getsize(archivo_salida)
            tamano_mb = tamano / (1024 * 1024)
            print(f"\r{Color.GREEN}✅ Backup completado: {tamano_mb:.2f} MB{Color.END}")
            return True, tamano
        else:
            print(f"\r{Color.RED}❌ Error: Archivo no creado{Color.END}")
            return False, 0
    
    except subprocess.TimeoutExpired:
        print(f"\r{Color.RED}❌ Error: Timeout (5 minutos){Color.END}")
        return False, 0
    except subprocess.CalledProcessError as e:
        print(f"\r{Color.RED}❌ Error en pg_dump:{Color.END}")
        print(f"{Color.RED}   {e.stderr}{Color.END}")
        return False, 0
    except Exception as e:
        print(f"\r{Color.RED}❌ Error inesperado: {e}{Color.END}")
        return False, 0

def main():
    print(f"\n{Color.BOLD}{'='*80}{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}BACKUP DE BASE DE DATOS POSTGRESQL{Color.END}")
    print(f"{Color.BOLD}{'='*80}{Color.END}\n")
    
    # Obtener configuración de .env
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print(f"{Color.RED}❌ ERROR: DATABASE_URL no encontrado en .env{Color.END}")
        return False
    
    result = urlparse(database_url)
    db_config = {
        'user': result.username,
        'password': result.password,
        'database': result.path[1:],
        'host': result.hostname,
        'port': result.port or 5432
    }
    
    # Buscar pg_dump
    pg_dump_path = encontrar_pg_dump()
    
    if not pg_dump_path:
        print(f"\n{Color.RED}❌ ERROR: No se encontró pg_dump{Color.END}")
        print(f"\n{Color.YELLOW}Posibles soluciones:{Color.END}")
        print(f"   1. Instalar PostgreSQL desde: https://www.postgresql.org/download/windows/")
        print(f"   2. Agregar PostgreSQL al PATH del sistema")
        print(f"   3. Especificar ruta manualmente en este script")
        return False
    
    # Encontrar los backups creados hoy
    directorio_padre = os.path.dirname(os.getcwd())
    timestamp_base = datetime.now().strftime('%Y%m%d')
    
    backups_encontrados = []
    for item in os.listdir(directorio_padre):
        if timestamp_base in item and os.path.isdir(os.path.join(directorio_padre, item)):
            backups_encontrados.append(item)
    
    if not backups_encontrados:
        print(f"\n{Color.YELLOW}⚠️  No se encontraron backups de hoy. Buscando el más reciente...{Color.END}")
        # Buscar backups con cualquier fecha
        for item in os.listdir(directorio_padre):
            if ('BACKUP_PRE_SINCRONIZACION' in item or 'GESTOR_DOCUMENTAL_TRANSPORTABLE' in item) and os.path.isdir(os.path.join(directorio_padre, item)):
                backups_encontrados.append(item)
    
    if not backups_encontrados:
        print(f"{Color.RED}❌ No se encontraron directorios de backup{Color.END}")
        return False
    
    # Ordenar y tomar los 2 más recientes
    backups_encontrados.sort(reverse=True)
    backup_recuperacion = next((b for b in backups_encontrados if 'BACKUP_PRE_SINCRONIZACION' in b), None)
    backup_transportable = next((b for b in backups_encontrados if 'GESTOR_DOCUMENTAL_TRANSPORTABLE' in b), None)
    
    print(f"\n{Color.CYAN}📂 Backups encontrados:{Color.END}")
    if backup_recuperacion:
        print(f"   ✅ Recuperación: {backup_recuperacion}")
    if backup_transportable:
        print(f"   ✅ Transportable: {backup_transportable}")
    print()
    
    total_exitos = 0
    tamano_total = 0
    
    # Hacer backup en cada directorio
    for nombre_backup in [backup_recuperacion, backup_transportable]:
        if not nombre_backup:
            continue
        
        print(f"\n{Color.BOLD}{'─'*80}{Color.END}")
        print(f"{Color.BOLD}{Color.CYAN}📦 {nombre_backup}{Color.END}")
        print(f"{Color.BOLD}{'─'*80}{Color.END}")
        
        ruta_backup = os.path.join(directorio_padre, nombre_backup)
        
        # Determinar subdirectorio según tipo
        if 'TRANSPORTABLE' in nombre_backup:
            archivo_salida = os.path.join(ruta_backup, 'backup_gestor_documental.backup')
        else:
            archivo_salida = os.path.join(ruta_backup, 'base_datos', 'backup_gestor_documental.backup')
        
        exito, tamano = hacer_backup_bd(pg_dump_path, db_config, archivo_salida)
        
        if exito:
            total_exitos += 1
            tamano_total += tamano
    
    # Resumen final
    print(f"\n{Color.BOLD}{'='*80}{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}RESUMEN{Color.END}")
    print(f"{Color.BOLD}{'='*80}{Color.END}\n")
    
    if total_exitos > 0:
        print(f"{Color.GREEN}✅ Backups completados: {total_exitos}/2{Color.END}")
        print(f"{Color.GREEN}💾 Tamaño total BD: {tamano_total / (1024*1024):.2f} MB{Color.END}")
        print(f"\n{Color.CYAN}🎉 Los backups ahora incluyen la base de datos completa{Color.END}")
    else:
        print(f"{Color.RED}❌ No se completó ningún backup{Color.END}")
        return False
    
    print(f"\n{Color.BOLD}{'='*80}{Color.END}\n")
    return True

if __name__ == '__main__':
    try:
        exito = main()
        if not exito:
            exit(1)
    except KeyboardInterrupt:
        print(f"\n\n{Color.YELLOW}⚠️  Proceso interrumpido por el usuario{Color.END}")
        exit(1)
    except Exception as e:
        print(f"\n{Color.RED}❌ ERROR INESPERADO: {e}{Color.END}")
        import traceback
        traceback.print_exc()
        exit(1)
