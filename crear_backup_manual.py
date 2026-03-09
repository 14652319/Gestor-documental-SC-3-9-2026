import os
import shutil
from datetime import datetime
import zipfile

def crear_backup_manual():
    # Configuracion
    origen = r"c:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
    # RUTA FIJA donde se guardan los backups
    destino_base = r"C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\Backup"
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_backup = os.path.join(destino_base, f"backup_completo_{fecha}.zip")
    
    # Crear carpeta de backups
    os.makedirs(destino_base, exist_ok=True)
    
    print("=" * 70)
    print("  CREANDO BACKUP MANUAL DEL GESTOR DOCUMENTAL")
    print("=" * 70)
    print(f"\nOrigen: {origen}")
    print(f"Destino: {archivo_backup}\n")
    
    # Carpetas y archivos a excluir
    excluir = {'.venv', '__pycache__', 'logs', '.git', 'node_modules'}
    
    archivos_incluidos = 0
    tamano_total = 0
    
    print("Comprimiendo archivos...")
    
    with zipfile.ZipFile(archivo_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(origen):
            # Filtrar directorios a excluir
            dirs[:] = [d for d in dirs if d not in excluir]
            
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, origen)
                
                try:
                    zipf.write(filepath, arcname)
                    archivos_incluidos += 1
                    tamano_total += os.path.getsize(filepath)
                    
                    if archivos_incluidos % 100 == 0:
                        print(f"  Archivos procesados: {archivos_incluidos}")
                        
                except Exception as e:
                    print(f"  Advertencia: No se pudo incluir {file}: {str(e)}")
    
    tamano_mb = round(os.path.getsize(archivo_backup) / (1024 * 1024), 2)
    
    print("\n" + "=" * 70)
    print("  BACKUP COMPLETADO EXITOSAMENTE")
    print("=" * 70)
    print(f"\nArchivo: {archivo_backup}")
    print(f"Archivos incluidos: {archivos_incluidos}")
    print(f"Tamano del backup: {tamano_mb} MB")
    print(f"Carpetas excluidas: {', '.join(excluir)}")
    print("\nBackup listo para usar!")
    print("=" * 70)

if __name__ == '__main__':
    try:
        crear_backup_manual()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
