"""
Script de Ejecución Manual de Backups
Gestor Documental - Supertiendas Cañaveral

Uso:
    python ejecutar_backup.py [tipo]
    
    tipo: base_datos, archivos, codigo, todos
    
Ejemplos:
    python ejecutar_backup.py base_datos
    python ejecutar_backup.py todos
"""

import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar Flask app context
from app import app
from backup_manager import (
    ejecutar_backup_completo,
    inicializar_configuracion_backup,
    ConfiguracionBackup,
    HistorialBackup
)
from extensions import db

def mostrar_uso():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║         Sistema de Backups - Gestor Documental               ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Uso: python ejecutar_backup.py [tipo]                      ║
║                                                               ║
║  Tipos disponibles:                                          ║
║    - base_datos    Backup de PostgreSQL                     ║
║    - archivos      Backup de documentos del sistema         ║
║    - codigo        Backup del código fuente                 ║
║    - todos         Ejecutar todos los backups               ║
║                                                               ║
║  Ejemplos:                                                   ║
║    python ejecutar_backup.py base_datos                     ║
║    python ejecutar_backup.py todos                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)

def mostrar_progreso(tipo, mensaje):
    """Muestra un mensaje de progreso"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] [{tipo.upper()}] {mensaje}")

def ejecutar_backup_tipo(tipo, usuario='script'):
    """Ejecuta un backup de un tipo específico"""
    print(f"\n{'='*70}")
    print(f"  BACKUP: {tipo.upper()}")
    print(f"{'='*70}")
    
    mostrar_progreso(tipo, "Iniciando backup...")
    
    try:
        with app.app_context():
            resultado = ejecutar_backup_completo(tipo, usuario=usuario)
            
            if resultado['success']:
                print(f"\n✅ ÉXITO")
                print(f"   Archivo: {resultado.get('ruta', 'N/A')}")
                print(f"   Tamaño: {resultado.get('tamano_mb', 0)} MB")
                print(f"   Duración: {resultado.get('duracion_segundos', 0)} segundos")
                return True
            else:
                print(f"\n❌ ERROR")
                print(f"   {resultado.get('error', 'Error desconocido')}")
                return False
                
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def mostrar_configuracion():
    """Muestra la configuración actual de backups"""
    print("\n" + "="*70)
    print("  CONFIGURACIÓN ACTUAL")
    print("="*70)
    
    with app.app_context():
        configs = ConfiguracionBackup.query.all()
        
        if not configs:
            print("\n⚠️  No hay configuraciones. Se crearán las predeterminadas...")
            inicializar_configuracion_backup()
            configs = ConfiguracionBackup.query.all()
        
        for config in configs:
            print(f"\n📦 {config.tipo.upper()}")
            print(f"   Estado: {'✅ Habilitado' if config.habilitado else '❌ Deshabilitado'}")
            print(f"   Destino: {config.destino}")
            print(f"   Horario: {config.horario_cron}")
            print(f"   Retención: {config.dias_retencion} días")
            if config.ultima_ejecucion:
                print(f"   Último backup: {config.ultima_ejecucion.strftime('%Y-%m-%d %H:%M:%S')}")

def mostrar_historial_reciente():
    """Muestra los últimos 5 backups"""
    print("\n" + "="*70)
    print("  ÚLTIMOS BACKUPS REALIZADOS")
    print("="*70)
    
    with app.app_context():
        historiales = HistorialBackup.query.order_by(
            HistorialBackup.fecha_inicio.desc()
        ).limit(5).all()
        
        if not historiales:
            print("\n⚠️  No hay historial de backups aún")
            return
        
        for h in historiales:
            estado_icon = "✅" if h.estado == 'exitoso' else "❌" if h.estado == 'fallido' else "⏳"
            print(f"\n{estado_icon} {h.tipo.upper()}")
            print(f"   Fecha: {h.fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Estado: {h.estado}")
            if h.tamano_bytes:
                print(f"   Tamaño: {h.tamano_bytes / (1024*1024):.2f} MB")
            if h.duracion_segundos:
                print(f"   Duración: {h.duracion_segundos}s")
            if h.error:
                print(f"   Error: {h.error[:100]}...")

def main():
    """Función principal"""
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        mostrar_uso()
        sys.exit(1)
    
    tipo = sys.argv[1].lower()
    
    # Comandos especiales
    if tipo in ['help', '--help', '-h', '?']:
        mostrar_uso()
        sys.exit(0)
    
    if tipo in ['config', 'configuracion']:
        mostrar_configuracion()
        sys.exit(0)
    
    if tipo in ['history', 'historial']:
        mostrar_historial_reciente()
        sys.exit(0)
    
    # Verificar pg_dump para backups de BD
    if tipo in ['base_datos', 'todos']:
        import shutil
        if not shutil.which('pg_dump'):
            print("\n⚠️  ADVERTENCIA: pg_dump no encontrado en PATH")
            print("   Asegúrate de tener PostgreSQL instalado y agregado al PATH")
            print("   O instala PostgreSQL desde: https://www.postgresql.org/download/")
            respuesta = input("\n   ¿Deseas continuar de todas formas? (s/n): ")
            if respuesta.lower() != 's':
                sys.exit(1)
    
    # Mostrar configuración antes de ejecutar
    mostrar_configuracion()
    
    print("\n")
    input("Presiona ENTER para continuar con el backup...")
    
    # Ejecutar backups
    exitoso = True
    
    if tipo == 'todos':
        tipos = ['base_datos', 'archivos', 'codigo']
        for t in tipos:
            resultado = ejecutar_backup_tipo(t)
            exitoso = exitoso and resultado
            print()  # Línea en blanco
    elif tipo in ['base_datos', 'archivos', 'codigo']:
        exitoso = ejecutar_backup_tipo(tipo)
    else:
        print(f"\n❌ Tipo de backup inválido: {tipo}")
        print("   Tipos válidos: base_datos, archivos, codigo, todos")
        mostrar_uso()
        sys.exit(1)
    
    # Mostrar historial actualizado
    mostrar_historial_reciente()
    
    # Resumen final
    print("\n" + "="*70)
    if exitoso:
        print("  ✅ BACKUP COMPLETADO EXITOSAMENTE")
    else:
        print("  ❌ BACKUP COMPLETADO CON ERRORES")
    print("="*70 + "\n")
    
    sys.exit(0 if exitoso else 1)

if __name__ == '__main__':
    main()
