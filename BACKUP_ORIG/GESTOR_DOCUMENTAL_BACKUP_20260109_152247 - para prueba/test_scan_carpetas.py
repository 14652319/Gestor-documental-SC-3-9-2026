"""Script para probar el escaneo de carpetas de red"""
import os
from config_carpetas import obtener_carpetas_base

carpetas = obtener_carpetas_base()

print("=" * 80)
print("VERIFICACIÓN DE CARPETAS DE RED")
print("=" * 80)

for sede, carpeta in carpetas.items():
    print(f"\n📁 SEDE: {sede}")
    print(f"   Ruta: {carpeta}")
    print(f"   Existe: {os.path.exists(carpeta)}")
    
    if os.path.exists(carpeta):
        # Contar archivos PDF
        pdf_count = 0
        try:
            for root, dirs, files in os.walk(carpeta):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_count += 1
                        if pdf_count <= 3:  # Mostrar solo los primeros 3
                            print(f"   ✓ {file}")
            
            print(f"   Total PDFs: {pdf_count}")
        except Exception as e:
            print(f"   ❌ Error al escanear: {e}")
    else:
        print(f"   ❌ CARPETA NO EXISTE O NO ES ACCESIBLE")

print("\n" + "=" * 80)
