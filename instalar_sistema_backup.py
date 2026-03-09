"""
Script de Instalación del Sistema de Backup
Gestor Documental - Supertiendas Cañaveral

Este script:
1. Crea las tablas de configuración y historial de backups
2. Inicializa la configuración por defecto
3. Crea los directorios de destino
4. Verifica que pg_dump esté disponible
5. Ejecuta un backup de prueba (opcional)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from backup_manager import (
    ConfiguracionBackup,
    HistorialBackup,
    inicializar_configuracion_backup
)

def print_header(titulo):
    print("\n" + "="*70)
    print(f"  {titulo}")
    print("="*70)

def verificar_pg_dump():
    """Verifica que pg_dump esté disponible"""
    print_header("VERIFICANDO POSTGRESQL")
    
    pg_dump_path = shutil.which('pg_dump')
    
    if pg_dump_path:
        print(f"✅ pg_dump encontrado: {pg_dump_path}")
        
        # Intentar obtener versión
        try:
            resultado = subprocess.run(
                ['pg_dump', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            print(f"   Versión: {resultado.stdout.strip()}")
            return True
        except:
            print("   ⚠️  No se pudo obtener la versión")
            return True
    else:
        print("❌ pg_dump NO encontrado en PATH")
        print("\n⚠️  ACCIÓN REQUERIDA:")
        print("   1. Instala PostgreSQL desde: https://www.postgresql.org/download/")
        print("   2. Durante instalación, marca 'Incluir en PATH'")
        print("   3. O agrega manualmente: C:\\Program Files\\PostgreSQL\\XX\\bin")
        print("\n   Sin pg_dump, NO podrás hacer backups de base de datos.")
        return False

def crear_tablas():
    """Crea las tablas de backup en la base de datos"""
    print_header("CREANDO TABLAS DE BACKUP")
    
    try:
        with app.app_context():
            # Verificar si las tablas ya existen
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tablas_existentes = inspector.get_table_names()
            
            if 'configuracion_backup' in tablas_existentes and 'historial_backup' in tablas_existentes:
                print("ℹ️  Las tablas ya existen, saltando creación...")
                return True
            
            # Crear tablas
            print("📝 Creando tablas...")
            ConfiguracionBackup.__table__.create(db.engine, checkfirst=True)
            HistorialBackup.__table__.create(db.engine, checkfirst=True)
            
            print("✅ Tablas creadas exitosamente:")
            print("   - configuracion_backup")
            print("   - historial_backup")
            return True
            
    except Exception as e:
        print(f"❌ Error al crear tablas: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def inicializar_configuracion():
    """Inicializa la configuración por defecto"""
    print_header("INICIALIZANDO CONFIGURACIÓN")
    
    try:
        with app.app_context():
            # Verificar si ya existe configuración
            configs = ConfiguracionBackup.query.all()
            
            if configs:
                print("ℹ️  Ya existe configuración:")
                for cfg in configs:
                    print(f"   - {cfg.tipo}: {cfg.destino}")
                
                respuesta = input("\n¿Deseas reinicializar la configuración? (s/n): ")
                if respuesta.lower() != 's':
                    print("   Manteniendo configuración actual...")
                    return True
                
                # Eliminar configuración actual
                ConfiguracionBackup.query.delete()
                db.session.commit()
            
            # Inicializar configuración por defecto
            print("📝 Creando configuración por defecto...")
            inicializar_configuracion_backup()
            
            configs = ConfiguracionBackup.query.all()
            
            print("✅ Configuración creada:")
            for cfg in configs:
                print(f"\n   📦 {cfg.tipo.upper()}")
                print(f"      Destino: {cfg.destino}")
                print(f"      Horario: {cfg.horario_cron}")
                print(f"      Retención: {cfg.dias_retencion} días")
            
            return True
            
    except Exception as e:
        print(f"❌ Error al inicializar configuración: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def crear_directorios():
    """Crea los directorios de destino para backups"""
    print_header("CREANDO DIRECTORIOS DE DESTINO")
    
    try:
        with app.app_context():
            configs = ConfiguracionBackup.query.all()
            
            for config in configs:
                destino = Path(config.destino)
                
                if destino.exists():
                    print(f"✅ {config.tipo}: Ya existe ({config.destino})")
                else:
                    print(f"📁 {config.tipo}: Creando {config.destino}...")
                    destino.mkdir(parents=True, exist_ok=True)
                    print(f"   ✅ Creado exitosamente")
            
            return True
            
    except Exception as e:
        print(f"❌ Error al crear directorios: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def ejecutar_backup_prueba():
    """Ejecuta un backup de prueba de código fuente"""
    print_header("BACKUP DE PRUEBA")
    
    respuesta = input("\n¿Deseas ejecutar un backup de prueba del código fuente? (s/n): ")
    if respuesta.lower() != 's':
        print("   Saltando backup de prueba...")
        return True
    
    try:
        from backup_manager import ejecutar_backup_completo
        
        print("\n📦 Ejecutando backup de código fuente...")
        
        with app.app_context():
            resultado = ejecutar_backup_completo('codigo', usuario='instalador')
            
            if resultado['success']:
                print("\n✅ BACKUP DE PRUEBA EXITOSO")
                print(f"   Archivo: {resultado.get('ruta', 'N/A')}")
                print(f"   Tamaño: {resultado.get('tamano_mb', 0):.2f} MB")
                print(f"   Duración: {resultado.get('duracion_segundos', 0)} segundos")
                return True
            else:
                print(f"\n❌ ERROR EN BACKUP DE PRUEBA")
                print(f"   {resultado.get('error', 'Error desconocido')}")
                return False
                
    except Exception as e:
        print(f"\n❌ Error en backup de prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def mostrar_resumen():
    """Muestra resumen final con instrucciones"""
    print_header("INSTALACIÓN COMPLETADA")
    
    print("""
✅ Sistema de Backup instalado exitosamente

📋 PRÓXIMOS PASOS:

1. EJECUCIÓN MANUAL:
   python ejecutar_backup.py base_datos
   python ejecutar_backup.py archivos
   python ejecutar_backup.py codigo
   python ejecutar_backup.py todos

2. CONFIGURACIÓN:
   Accede al panel de monitoreo:
   http://localhost:8099/admin/monitoreo/dashboard
   
3. VER ESTADO:
   python ejecutar_backup.py config
   python ejecutar_backup.py historial

4. BACKUPS AUTOMÁTICOS:
   Los backups se ejecutarán automáticamente según horarios:
   - Base de Datos: 2 AM diario
   - Archivos: 3 AM diario
   - Código: 4 AM cada domingo
   
   (Nota: Requiere configurar Task Scheduler en Windows)

📁 UBICACIÓN DE BACKUPS:
   C:\\Backups_GestorDocumental\\
   ├── base_datos\\     (Backups PostgreSQL .backup)
   ├── documentos\\     (Backups archivos .zip)
   └── codigo\\         (Backups código fuente .zip)

📊 LOGS:
   logs\\backup.log     (Registro de backups)

⚙️ CONFIGURACIÓN AVANZADA:
   Puedes cambiar destinos y horarios desde el panel web
   o modificando directamente en la tabla configuracion_backup

╔═══════════════════════════════════════════════════════════════╗
║  ⚠️  IMPORTANTE: Para backups automáticos, configura una    ║
║     tarea en Windows Task Scheduler que ejecute:             ║
║     python ejecutar_backup.py todos                          ║
╚═══════════════════════════════════════════════════════════════╝
    """)

def main():
    """Función principal de instalación"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║      INSTALADOR DEL SISTEMA DE BACKUP AUTOMÁTICO            ║
║      Gestor Documental - Supertiendas Cañaveral             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    input("Presiona ENTER para comenzar la instalación...")
    
    # Paso 1: Verificar pg_dump
    pg_dump_ok = verificar_pg_dump()
    if not pg_dump_ok:
        respuesta = input("\n¿Deseas continuar sin pg_dump? (s/n): ")
        if respuesta.lower() != 's':
            print("\n❌ Instalación cancelada")
            sys.exit(1)
    
    # Paso 2: Crear tablas
    if not crear_tablas():
        print("\n❌ Error al crear tablas. Instalación abortada.")
        sys.exit(1)
    
    # Paso 3: Inicializar configuración
    if not inicializar_configuracion():
        print("\n❌ Error al inicializar configuración. Instalación abortada.")
        sys.exit(1)
    
    # Paso 4: Crear directorios
    if not crear_directorios():
        print("\n❌ Error al crear directorios. Instalación abortada.")
        sys.exit(1)
    
    # Paso 5: Backup de prueba (opcional)
    ejecutar_backup_prueba()
    
    # Mostrar resumen
    mostrar_resumen()
    
    print("\n✅ ¡Instalación completada exitosamente!")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
