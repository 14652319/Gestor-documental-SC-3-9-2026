"""
CONSOLIDAR_MAESTRO_SIMPLIFICADO.py
===================================
Versión simplificada que va directo a la consolidación
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Configurar entorno
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ['DATABASE_URL'] = 'postgresql://postgres:Vimer2024*@localhost:5432/gestor_documental'

print("="*80)
print("🔄 CONSOLIDACIÓN SIMPLIFICADA - MAESTRO DIAN VS ERP")
print("="*80)
print(f"📅 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
print()

# Archivos fuente
archivos_fuente = {
    "dian": Path("C:/Users/Usuario/Downloads/Ricardo/Dian.xlsx"),
    "erp_fn": Path("C:/Users/Usuario/Downloads/Ricardo/ERP Financiero 18 02 2026.xlsx"),
    "erp_cm": Path("C:/Users/Usuario/Downloads/Ricardo/ERP comercial 18 02 2026.xlsx"),
    "acuses": Path("C:/Users/Usuario/Downloads/Ricardo/acuses 2.xlsx")
}

# Carpetas destino
uploads_dir = project_root / "uploads"
carpetas_destino = {
    "dian": uploads_dir / "dian",
    "erp_fn": uploads_dir / "erp_fn",
    "erp_cm": uploads_dir / "erp_cm",
    "acuses": uploads_dir / "acuses"
}

print("📁 PASO 1: Copiar archivos a uploads/")
print("-"*80)

for nombre, carpeta in carpetas_destino.items():
    carpeta.mkdir(parents=True, exist_ok=True)

for nombre in archivos_fuente.keys():
    fuente = archivos_fuente[nombre]
    destino = carpetas_destino[nombre] / fuente.name
    
    if fuente.exists():
        shutil.copy2(fuente, destino)
        size_mb = destino.stat().st_size / (1024 * 1024)
        print(f"   ✅ {nombre:10} → {fuente.name} ({size_mb:.2f} MB)")
    else:
        print(f"   ❌ {nombre:10} → NO ENCONTRADO: {fuente}")
        sys.exit(1)

print()
print("🔧 PASO 2: Importar módulos")
print("-"*80)

try:
    from app import app
    from modules.dian_vs_erp.routes import actualizar_maestro
    print("   ✅ Módulos importados")
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")
    sys.exit(1)

print()
print("🚀 PASO 3: Ejecutar consolidación")
print("-"*80)
print("⏳ Procesando... (puede tomar 1-2 minutos)")
print()

with app.app_context():
    try:
        inicio = datetime.now()
        
        # Ejecutar consolidación (sin parámetros)
        resultado = actualizar_maestro()
        
        fin = datetime.now()
        duracion = (fin - inicio).total_seconds()
        
        print(f"✅ Consolidación completada en {duracion:.2f} segundos")
        print()
        
        if isinstance(resultado, dict):
            print(f"📋 Mensaje: {resultado.get('message', 'Sin mensaje')}")
            
            metricas = resultado.get('metricas', {})
            if metricas:
                print()
                print("📊 MÉTRICAS:")
                print(f"   DIAN:        {metricas.get('registros_dian', 0):>10,}")
                print(f"   ERP FN:      {metricas.get('registros_erp_fn', 0):>10,}")
                print(f"   ERP CM:      {metricas.get('registros_erp_cm', 0):>10,}")
                print(f"   Acuses:      {metricas.get('registros_acuses', 0):>10,}")
        else:
            print(f"📋 Resultado: {resultado}")
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

print()
print("="*80)
print("✅ PROCESO COMPLETADO")
print("="*80)
print()
print("📋 VERIFICAR EN:")
print("   http://localhost:8099/dian_vs_erp/visor_v2")
print()
print("   Buscar:")
print("   ✓ Columna 'Ver PDF' con enlaces")
print("   ✓ Columna 'Estado Aprobación' con valores")
print("   ✓ Datos de ERP_FINANCIERO presentes")
print()
print(f"📅 Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
