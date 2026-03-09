"""
BACKUP COMPLETO DEL SISTEMA GESTOR DOCUMENTAL
==============================================
Fecha: 23 de Febrero de 2026
Propósito: Backup completo antes de implementar cambios de paginación

Este script realiza:
1. Backup de todos los archivos del proyecto
2. Backup de la base de datos PostgreSQL
3. Guarda todo en: D:\0.1. Backup Equipo Contablilidad\Gestor Documental\Backups
"""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

def crear_backup_completo():
    """Crea backup completo del sistema"""
    
    # 1. CONFIGURACIÓN
    PROYECTO_ORIGEN = r"D:\0.1. Backup Equipo Contablilidad\Gestor Documental\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
    DESTINO_BASE = r"D:\0.1. Backup Equipo Contablilidad\Gestor Documental\Backups"
    
    # Generar nombre con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_backup = f"GESTOR_DOCUMENTAL_BACKUP_{timestamp}"
    ruta_backup = os.path.join(DESTINO_BASE, nombre_backup)
    
    print("=" * 80)
    print("🔧 BACKUP COMPLETO DEL SISTEMA GESTOR DOCUMENTAL")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Origen: {PROYECTO_ORIGEN}")
    print(f"💾 Destino: {ruta_backup}")
    print("=" * 80)
    print()
    
    # 2. VERIFICAR QUE EXISTE LA CARPETA DE DESTINO
    if not os.path.exists(DESTINO_BASE):
        print(f"❌ Error: No existe la carpeta de destino: {DESTINO_BASE}")
        return False
    
    # 3. CREAR CARPETA DE BACKUP
    print("📁 Paso 1/3: Creando carpeta de backup...")
    try:
        os.makedirs(ruta_backup, exist_ok=True)
        print(f"   ✅ Carpeta creada: {ruta_backup}")
    except Exception as e:
        print(f"   ❌ Error creando carpeta: {e}")
        return False
    
    # 4. COPIAR ARCHIVOS DEL PROYECTO
    print("\n📦 Paso 2/3: Copiando archivos del proyecto...")
    print("   ⏳ Esto puede tomar varios minutos...")
    
    # Directorios a EXCLUIR del backup (para hacerlo más rápido)
    excluir = {
        '.venv',
        '__pycache__',
        'node_modules',
        '.git',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.Python',
        'env',
        'venv',
        'ENV',
        'logs'  # Logs se pueden recrear
    }
    
    archivos_copiados = 0
    archivos_omitidos = 0
    
    try:
        for root, dirs, files in os.walk(PROYECTO_ORIGEN):
            # Filtrar directorios a excluir
            dirs[:] = [d for d in dirs if d not in excluir]
            
            # Calcular ruta relativa
            ruta_relativa = os.path.relpath(root, PROYECTO_ORIGEN)
            destino_dir = os.path.join(ruta_backup, ruta_relativa)
            
            # Crear directorio en destino
            os.makedirs(destino_dir, exist_ok=True)
            
            # Copiar archivos
            for archivo in files:
                # Omitir archivos temporales
                if archivo.endswith(('.pyc', '.pyo', '.pyd', '.log')):
                    archivos_omitidos += 1
                    continue
                
                origen_archivo = os.path.join(root, archivo)
                destino_archivo = os.path.join(destino_dir, archivo)
                
                try:
                    shutil.copy2(origen_archivo, destino_archivo)
                    archivos_copiados += 1
                    
                    # Mostrar progreso cada 100 archivos
                    if archivos_copiados % 100 == 0:
                        print(f"   📄 Archivos copiados: {archivos_copiados}")
                except Exception as e:
                    print(f"   ⚠️  Error copiando {archivo}: {e}")
                    archivos_omitidos += 1
        
        print(f"   ✅ Archivos copiados exitosamente: {archivos_copiados}")
        print(f"   ⏭️  Archivos omitidos (temporales/cache): {archivos_omitidos}")
        
    except Exception as e:
        print(f"   ❌ Error copiando archivos: {e}")
        return False
    
    # 5. BACKUP DE LA BASE DE DATOS POSTGRESQL
    print("\n💾 Paso 3/3: Respaldando base de datos PostgreSQL...")
    
    # Configuración de la base de datos
    DB_NAME = "gestor_documental"
    DB_USER = "gestor_user"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    
    # Archivo de backup SQL
    archivo_sql = os.path.join(ruta_backup, f"backup_bd_{timestamp}.sql")
    
    try:
        # Comando pg_dump
        comando = [
            "pg_dump",
            "-h", DB_HOST,
            "-p", DB_PORT,
            "-U", DB_USER,
            "-d", DB_NAME,
            "-f", archivo_sql,
            "--verbose"
        ]
        
        print(f"   🔧 Ejecutando: pg_dump -d {DB_NAME}...")
        print(f"   📝 Guardando en: {archivo_sql}")
        
        # Ejecutar pg_dump
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            env={**os.environ, "PGPASSWORD": "Frayb@123"}  # Password desde .env
        )
        
        if resultado.returncode == 0:
            # Verificar que el archivo se creó
            if os.path.exists(archivo_sql):
                tamano_mb = os.path.getsize(archivo_sql) / (1024 * 1024)
                print(f"   ✅ Base de datos respaldada exitosamente")
                print(f"   📊 Tamaño del backup: {tamano_mb:.2f} MB")
            else:
                print(f"   ⚠️  Advertencia: No se encontró el archivo de backup")
        else:
            print(f"   ❌ Error en pg_dump:")
            print(f"      {resultado.stderr}")
            print()
            print(f"   ℹ️  NOTA: El backup de archivos SÍ se completó.")
            print(f"   ℹ️  Solo faltó el backup de la base de datos.")
            print(f"   ℹ️  Puedes hacer el backup manualmente con:")
            print(f"      pg_dump -U gestor_user -d gestor_documental -f {archivo_sql}")
            
    except FileNotFoundError:
        print(f"   ⚠️  Advertencia: No se encontró pg_dump en el PATH")
        print(f"   ℹ️  El backup de archivos SÍ se completó.")
        print(f"   ℹ️  Para backup manual de BD, ejecuta:")
        print(f"      pg_dump -U gestor_user -d gestor_documental -f {archivo_sql}")
    except Exception as e:
        print(f"   ⚠️  Error respaldando base de datos: {e}")
        print(f"   ℹ️  El backup de archivos SÍ se completó.")
    
    # 6. RESUMEN FINAL
    print("\n" + "=" * 80)
    print("✅ BACKUP COMPLETADO")
    print("=" * 80)
    print(f"📂 Ubicación: {ruta_backup}")
    print(f"📦 Archivos copiados: {archivos_copiados}")
    print(f"💾 Base de datos: {'✅ Incluida' if os.path.exists(archivo_sql) else '⚠️ No incluida (hacer manual)'}")
    
    # Calcular tamaño total del backup
    try:
        tamano_total = 0
        for root, dirs, files in os.walk(ruta_backup):
            tamano_total += sum(os.path.getsize(os.path.join(root, f)) for f in files)
        tamano_total_mb = tamano_total / (1024 * 1024)
        print(f"💿 Tamaño total: {tamano_total_mb:.2f} MB")
    except:
        pass
    
    print()
    print("🎯 Siguiente paso: Implementar cambios de paginación")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        exito = crear_backup_completo()
        if exito:
            print("\n✅ Proceso completado exitosamente")
        else:
            print("\n❌ El proceso tuvo errores")
    except KeyboardInterrupt:
        print("\n⚠️  Backup interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
