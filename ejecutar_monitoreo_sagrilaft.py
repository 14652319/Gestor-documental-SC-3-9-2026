"""
Script para ejecutar el monitoreo de vencimientos de SAGRILAFT
Puede ejecutarse manualmente o programarse con cron/Task Scheduler

USO:
  python ejecutar_monitoreo_sagrilaft.py

PROGRAMACIÓN AUTOMÁTICA:
  Windows Task Scheduler: Ejecutar diariamente a las 8:00 AM
  Linux cron: 0 8 * * * /path/to/python ejecutar_monitoreo_sagrilaft.py
"""
import sys
import os
from datetime import datetime

# Agregar ruta del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from modules.sagrilaft.monitor_vencimientos import MonitorVencimientos

def ejecutar():
    """Ejecuta el monitoreo de vencimientos"""
    print(f"\n{'='*70}")
    print(f"  MONITOREO SAGRILAFT - ALERTAS DE VENCIMIENTO")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    with app.app_context():
        monitor = MonitorVencimientos()
        stats = monitor.enviar_alertas_automaticas()
        
        print(f"\n{'='*70}")
        print(f"  RESUMEN DE EJECUCIÓN")
        print(f"{'='*70}")
        print(f"  📊 Radicados procesados: {stats['procesados']}")
        print(f"  📧 Alertas iniciales enviadas: {stats['alertas_enviadas']}")
        print(f"  🔔 Recordatorios enviados: {stats['recordatorios_enviados']}")
        print(f"  ❌ Errores: {stats['errores']}")
        print(f"{'='*70}\n")
        
        # Retornar código de salida
        if stats['errores'] > 0:
            print("⚠️  Ejecución completada con errores")
            return 1
        else:
            print("✅ Ejecución completada exitosamente")
            return 0

if __name__ == '__main__':
    exit_code = ejecutar()
    sys.exit(exit_code)
