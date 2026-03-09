"""
CARGAR_NAVEGADOR_REAL.py
=========================
Simula la carga desde el navegador copiando el CSV a la carpeta correcta
y usando las funciones reales de routes.py para procesar.
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Agregar path del proyecto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar Flask app contexto
os.environ['DATABASE_URL'] = 'postgresql://postgres:Vimer2024*@localhost:5432/gestor_documental'

print("="*80)
print("🔄 SIMULACIÓN DE CARGA DESDE NAVEGADOR")
print("="*80)
print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# Archivo a cargar
csv_filename = "Desde_01-01-2025_Hasta_28-02-2025_ea77100881.csv"
uploads_dir = project_root / "uploads" / "dian"
csv_path = uploads_dir / csv_filename

if not csv_path.exists():
    print(f"❌ ERROR: No se encontró el archivo en uploads/dian/")
    print(f"   Ruta buscada: {csv_path}")
    sys.exit(1)

print(f"✅ Archivo encontrado: {csv_filename}")
print(f"📁 Ubicación: uploads/dian/")
print(f"📊 Tamaño: {csv_path.stat().st_size / 1024:.2f} KB")

# Ahora cargar usando las funciones de routes.py
print("\n" + "="*80)
print("🚀 PROCESANDO CSV CON FUNCIONES DE ROUTES.PY")
print("="*80)

try:
    # Importar después de configurar DATABASE_URL
    from app import app
    from modules.dian_vs_erp.routes import actualizar_maestro
    
    # Crear contexto de Flask
    with app.app_context():
        print("\n📊 Llamando a actualizar_maestro(forzar=True)...")
        print("-"*80)
        
        resultado = actualizar_maestro(forzar=True)
        
        print("-"*80)
        print("\n✅ PROCESO COMPLETADO")
        print("="*80)
        print("📊 RESULTADO:")
        print(f"   Mensaje: {resultado.get('message', 'Sin mensaje')}")
        
        stats = resultado.get('metricas', {})
        if stats:
            print(f"\n📈 MÉTRICAS:")
            print(f"   Registros DIAN: {stats.get('registros_dian', 0):,}")
            print(f"   Registros ERP FN: {stats.get('registros_erp_fn', 0):,}")
            print(f"   Registros ERP CM: {stats.get('registros_erp_cm', 0):,}")
            print(f"   Registros Acuses: {stats.get('registros_acuses', 0):,}")
            print(f"   Tiempo proceso: {stats.get('tiempo_proceso', 0):.2f}s")
        
        print("\n" + "="*80)
        print("✅ VERIFICAR EN EL NAVEGADOR:")
        print("   http://localhost:8099/dian_vs_erp/visor_v2")
        print("="*80)
        
except Exception as e:
    print(f"\n❌ ERROR durante el procesamiento:")
    print(f"   {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
