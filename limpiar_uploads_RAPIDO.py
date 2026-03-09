"""
🧹 LIMPIEZA RÁPIDA DE UPLOADS - Sin confirmación
Elimina archivos .xls antiguos de uploads/
Ejecutar antes de cargar archivos nuevos
"""
import os
from pathlib import Path

# Rutas
BASE_DIR = Path(__file__).parent
folders = {
    "dian": BASE_DIR / "uploads" / "dian",
    "erp_fn": BASE_DIR / "uploads" / "erp_fn",
    "erp_cm": BASE_DIR / "uploads" / "erp_cm",
    "acuses": BASE_DIR / "uploads" / "acuses",
    "errores": BASE_DIR / "uploads" / "rg_erp_er",
}

print("=" * 80)
print("🧹 LIMPIANDO CARPETAS UPLOADS (TODOS los archivos)")
print("=" * 80)
print()

total = 0
for nombre, folder in folders.items():
    if not folder.exists():
        print(f"⚠️  {nombre}: No existe")
        continue
    
    archivos = list(folder.glob("*.*"))
    if len(archivos) == 0:
        print(f"✅ {nombre}: Ya limpia")
        continue
    
    print(f"🧹 {nombre}: {len(archivos)} archivo(s)")
    for archivo in archivos:
        archivo.unlink()
        print(f"   ❌ {archivo.name}")
        total += 1
    print()

print("=" * 80)
print(f"✅ LIMPIEZA COMPLETA: {total} archivo(s) eliminados")
print("=" * 80)
print()
print("💡 Ahora puedes cargar archivos nuevos sin conflictos")
