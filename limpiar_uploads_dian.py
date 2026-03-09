"""
🧹 SCRIPT DE LIMPIEZA DE CARPETAS UPLOADS - MÓDULO DIAN VS ERP
Fecha: 18 Febrero 2026
Autor: GitHub Copilot
Propósito: Limpiar archivos antiguos de las carpetas uploads/ antes de cargar nuevos
"""

import os
from pathlib import Path
import shutil

def limpiar_carpeta_uploads():
    """Limpia TODAS las carpetas de uploads del módulo DIAN vs ERP"""
    
    # Rutas de las carpetas de uploads
    BASE_DIR = Path(__file__).parent
    carpetas_uploads = {
        "DIAN": BASE_DIR / "uploads" / "dian",
        "ERP Financiero": BASE_DIR / "uploads" / "erp_fn", 
        "ERP Comercial": BASE_DIR / "uploads" / "erp_cm",
        "Acuses": BASE_DIR / "uploads" / "acuses",
        "Errores ERP": BASE_DIR / "uploads" / "rg_erp_er",
    }
    
    print("=" * 80)
    print("🧹 LIMPIEZA DE CARPETAS UPLOADS - MÓDULO DIAN VS ERP")
    print("=" * 80)
    print()
    
    archivos_eliminados = 0
    
    for nombre, ruta in carpetas_uploads.items():
        if not ruta.exists():
            print(f"⚠️  {nombre}: Carpeta no existe ({ruta})")
            continue
        
        # Contar archivos existentes
        archivos = list(ruta.glob("*.*"))
        if len(archivos) == 0:
            print(f"✅ {nombre}: Ya está limpia (0 archivos)")
            continue
        
        print(f"🧹 {nombre}: {len(archivos)} archivo(s) encontrados")
        
        # Eliminar archivos
        for archivo in archivos:
            try:
                archivo.unlink()
                print(f"   ❌ Eliminado: {archivo.name}")
                archivos_eliminados += 1
            except Exception as e:
                print(f"   ⚠️  No se pudo eliminar {archivo.name}: {e}")
        
        print()
    
    print("=" * 80)
    print(f"✅ LIMPIEZA COMPLETADA: {archivos_eliminados} archivo(s) eliminados")
    print("=" * 80)
    print()
    print("💡 AHORA PUEDES:")
    print("   1. Acceder a http://127.0.0.1:8099/dian_vs_erp/cargar_archivos")
    print("   2. Cargar tus archivos nuevos (.xlsx)")
    print("   3. Procesar sin errores de formato")
    print()

if __name__ == "__main__":
    try:
        # Pedir confirmación
        print()
        print("⚠️  ADVERTENCIA: Este script eliminará TODOS los archivos de uploads/")
        print()
        respuesta = input("¿Confirmas que deseas limpiar las carpetas? (si/no): ")
        
        if respuesta.lower() in ['si', 's', 'sí', 'yes', 'y']:
            limpiar_carpeta_uploads()
        else:
            print()
            print("❌ Operación cancelada. No se eliminó ningún archivo.")
    except KeyboardInterrupt:
        print()
        print()
        print("❌ Operación cancelada por el usuario.")
