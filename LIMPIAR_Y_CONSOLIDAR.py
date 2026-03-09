"""
LIMPIAR_Y_CONSOLIDAR.py
========================
Solución al problema: "Permission denied" por archivos temporales de Excel

PROBLEMA:
- Excel crea archivos temporales: ~$nombre.xlsx, -$nombre.xlsx
- Estos archivos causan "Permission denied" al procesarlos
- Necesitamos limpiarlos antes de consolidar
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ['DATABASE_URL'] = 'postgresql://postgres:Vimer2024*@localhost:5432/gestor_documental'

print("="*80)
print("🧹 LIMPIEZA Y CONSOLIDACIÓN - SOLUCIÓN DEFINITIVA")
print("="*80)
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
print()

# ============================================================================
# PASO 1: Cerrar Excel si está abierto
# ============================================================================
print("📊 PASO 1: Verificar y cerrar Excel")
print("-"*80)

try:
    result = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq EXCEL.EXE"],
        capture_output=True,
        text=True
    )
    
    if "EXCEL.EXE" in result.stdout:
        print("   ⚠️  Excel está abierto - intentando cerrar...")
        subprocess.run(["taskkill", "/F", "/IM", "EXCEL.EXE"], capture_output=True)
        print("   ✅ Excel cerrado")
    else:
        print("   ✅ Excel no está abierto")
except Exception as e:
    print(f"   ⚠️  No se pudo verificar Excel: {str(e)}")

print()

# ============================================================================
# PASO 2: Limpiar archivos temporales en Downloads
# ============================================================================
print("🗑️  PASO 2: Limpiar archivos temporales en Downloads")
print("-"*80)

downloads_dir = Path("C:/Users/Usuario/Downloads/Ricardo")
if downloads_dir.exists():
    temp_files = []
    for pattern in ["~$*.xlsx", "-$*.xlsx", "~$*.xls", ".~lock.*"]:
        temp_files.extend(downloads_dir.glob(pattern))
    
    if temp_files:
        print(f"   🗑️  Encontrados {len(temp_files)} archivos temporales:")
        for f in temp_files:
            try:
                f.unlink()
                print(f"      ✅ Eliminado: {f.name}")
            except Exception as e:
                print(f"      ⚠️  No se pudo eliminar {f.name}: {str(e)}")
    else:
        print("   ✅ No hay archivos temporales en Downloads")
else:
    print("   ⚠️  Carpeta Downloads no encontrada")

print()

# ============================================================================
# PASO 3: Limpiar archivos temporales en uploads/
# ============================================================================
print("🗑️  PASO 3: Limpiar archivos temporales en uploads/")
print("-"*80)

uploads_dir = project_root / "uploads"
carpetas = ["dian", "erp_fn", "erp_cm", "acuses", "rg_erp_er"]

total_eliminados = 0
for carpeta in carpetas:
    carpeta_path = uploads_dir / carpeta
    if carpeta_path.exists():
        temp_files = []
        for pattern in ["~$*", "-$*", ".~lock.*", "*.tmp"]:
            temp_files.extend(carpeta_path.glob(pattern))
        
        if temp_files:
            print(f"   📁 {carpeta}:")
            for f in temp_files:
                try:
                    f.unlink()
                    print(f"      ✅ Eliminado: {f.name}")
                    total_eliminados += 1
                except Exception as e:
                    print(f"      ⚠️  No se pudo eliminar {f.name}: {str(e)}")

if total_eliminados == 0:
    print("   ✅ No hay archivos temporales en uploads/")
else:
    print(f"   ✅ Total eliminados: {total_eliminados}")

print()

# ============================================================================
# PASO 4: Verificar archivos fuente
# ============================================================================
print("📁 PASO 4: Verificar archivos fuente")
print("-"*80)

archivos_fuente = {
    "dian": Path("C:/Users/Usuario/Downloads/Ricardo/Dian.xlsx"),
    "erp_fn": Path("C:/Users/Usuario/Downloads/Ricardo/ERP Financiero 18 02 2026.xlsx"),
    "erp_cm": Path("C:/Users/Usuario/Downloads/Ricardo/ERP comercial 18 02 2026.xlsx"),
    "acuses": Path("C:/Users/Usuario/Downloads/Ricardo/acuses 2.xlsx")
}

for nombre, ruta in archivos_fuente.items():
    if ruta.exists():
        # Verificar que NO sea un archivo temporal
        if not ruta.name.startswith("~$") and not ruta.name.startswith("-$"):
            size_mb = ruta.stat().st_size / (1024 * 1024)
            print(f"   ✅ {nombre:10} → {ruta.name} ({size_mb:.2f} MB)")
        else:
            print(f"   ❌ {nombre:10} → ARCHIVO TEMPORAL: {ruta.name}")
            sys.exit(1)
    else:
        print(f"   ❌ {nombre:10} → NO ENCONTRADO: {ruta}")
        sys.exit(1)

print()

# ============================================================================
# PASO 5: Limpiar completamente uploads/ y recopiar
# ============================================================================
print("🔄 PASO 5: Limpiar uploads/ y copiar archivos limpios")
print("-"*80)

carpetas_destino = {
    "dian": uploads_dir / "dian",
    "erp_fn": uploads_dir / "erp_fn",
    "erp_cm": uploads_dir / "erp_cm",
    "acuses": uploads_dir / "acuses"
}

# Limpiar carpetas uploads/
for nombre, carpeta in carpetas_destino.items():
    if carpeta.exists():
        # Eliminar todos los archivos de la carpeta
        for f in carpeta.glob("*"):
            try:
                if f.is_file():
                    f.unlink()
            except Exception as e:
                print(f"   ⚠️  No se pudo eliminar {f.name}: {str(e)}")
    
    # Crear carpeta si no existe
    carpeta.mkdir(parents=True, exist_ok=True)

print("   ✅ Carpetas limpiadas")
print()

# Copiar archivos limpios
print("   📋 Copiando archivos:")
for nombre in archivos_fuente.keys():
    fuente = archivos_fuente[nombre]
    destino = carpetas_destino[nombre] / fuente.name
    
    try:
        shutil.copy2(fuente, destino)
        size_mb = destino.stat().st_size / (1024 * 1024)
        print(f"      ✅ {nombre:10} → {fuente.name} ({size_mb:.2f} MB)")
    except Exception as e:
        print(f"      ❌ ERROR copiando {nombre}: {str(e)}")
        sys.exit(1)

print()

# ============================================================================
# PASO 6: Verificar que NO hay archivos temporales en uploads/
# ============================================================================
print("✅ PASO 6: Verificar carpetas uploads/ limpias")
print("-"*80)

archivos_problema = []
for carpeta in carpetas_destino.values():
    for pattern in ["~$*", "-$*", ".~lock.*"]:
        archivos_problema.extend(carpeta.glob(pattern))

if archivos_problema:
    print("   ❌ ERROR: Todavía hay archivos temporales:")
    for f in archivos_problema:
        print(f"      {f}")
    sys.exit(1)
else:
    print("   ✅ No hay archivos temporales")

print()

# ============================================================================
# PASO 7: Importar y ejecutar consolidación
# ============================================================================
print("🔧 PASO 7: Ejecutar consolidación")
print("-"*80)

try:
    from app import app
    from modules.dian_vs_erp.routes import actualizar_maestro
    print("   ✅ Módulos importados")
except Exception as e:
    print(f"   ❌ ERROR importando: {str(e)}")
    sys.exit(1)

print()
print("🚀 PROCESANDO...")
print("   (Esto puede tomar 1-2 minutos)")
print()

with app.app_context():
    try:
        inicio = datetime.now()
        resultado = actualizar_maestro()
        fin = datetime.now()
        
        duracion = (fin - inicio).total_seconds()
        print(f"✅ Consolidación completada en {duracion:.2f} segundos")
        print()
        
        if isinstance(resultado, dict):
            print(f"📋 {resultado.get('message', 'Sin mensaje')}")
            metricas = resultado.get('metricas', {})
            if metricas:
                print()
                print("📊 MÉTRICAS:")
                print(f"   DIAN:     {metricas.get('registros_dian', 0):>10,}")
                print(f"   ERP FN:   {metricas.get('registros_erp_fn', 0):>10,}")
                print(f"   ERP CM:   {metricas.get('registros_erp_cm', 0):>10,}")
                print(f"   Acuses:   {metricas.get('registros_acuses', 0):>10,}")
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

print()
print("="*80)
print("✅ PROCESO COMPLETADO EXITOSAMENTE")
print("="*80)
print()
print("📋 VERIFICAR EN NAVEGADOR:")
print("   http://localhost:8099/dian_vs_erp/visor_v2")
print()
print("   Buscar:")
print("   ✓ Datos cargados")
print("   ✓ Columna 'Ver PDF'")
print("   ✓ Columna 'Estado Aprobación'")
print("   ✓ ERP_FINANCIERO presente")
print()
print("="*80)
