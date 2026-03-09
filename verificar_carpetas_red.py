"""
Script para verificar conexión a carpetas de red del módulo de Causaciones
Valida si todas las 12 carpetas configuradas en .env son accesibles
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("=" * 80)
print("🔍 VERIFICACIÓN DE CARPETAS DE RED - MÓDULO CAUSACIONES")
print("=" * 80)
print()

# Definir carpetas según config_carpetas.py
carpetas_config = {
    "CYS (Aprobadas)": "CARPETA_CYS",
    "CYS (Causadas)": "CARPETA_CYS_C",
    "DOM (Aprobadas)": "CARPETA_DOM",
    "DOM (Causadas)": "CARPETA_DOM_C",
    "TIC (Aprobadas)": "CARPETA_TIC",
    "TIC (Causadas)": "CARPETA_TIC_C",
    "MER (Aprobadas)": "CARPETA_MER",
    "MER (Causadas)": "CARPETA_MER_C",
    "MYP (Aprobadas)": "CARPETA_MYP",
    "MYP (Causadas)": "CARPETA_MYP_C",
    "FIN (Aprobadas)": "CARPETA_FIN",
    "FIN (Causadas)": "CARPETA_FIN_C",
}

accesibles = 0
no_accesibles = 0
no_configuradas = 0

for nombre, variable in carpetas_config.items():
    ruta = os.getenv(variable)
    
    print(f"📁 {nombre}")
    print(f"   Variable: {variable}")
    
    if not ruta:
        print(f"   ❌ NO CONFIGURADA en .env")
        no_configuradas += 1
        print()
        continue
    
    print(f"   Ruta: {ruta}")
    
    # Verificar acceso
    try:
        if os.path.exists(ruta):
            # Contar archivos PDF
            pdf_count = 0
            try:
                for root, dirs, files in os.walk(ruta):
                    pdf_count += sum(1 for f in files if f.lower().endswith('.pdf'))
                    if pdf_count > 100:  # Optimización: no contar todos si hay muchos
                        break
            except Exception as e:
                pdf_count = 0
            
            print(f"   ✅ ACCESIBLE ({pdf_count}+ archivos PDF)")
            accesibles += 1
        else:
            print(f"   ❌ NO ACCESIBLE (carpeta no existe)")
            no_accesibles += 1
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        no_accesibles += 1
    
    print()

# Resumen
print("=" * 80)
print("📊 RESUMEN")
print("=" * 80)
print(f"✅ Carpetas accesibles: {accesibles}/12")
print(f"❌ Carpetas no accesibles: {no_accesibles}/12")
print(f"⚠️  Carpetas no configuradas: {no_configuradas}/12")
print()

if accesibles == 12:
    print("🎉 ¡PERFECTO! Todas las carpetas están accesibles")
elif accesibles > 0:
    print("⚠️  ATENCIÓN: No todas las carpetas son accesibles")
    print("   El módulo solo mostrará archivos de las carpetas accesibles")
else:
    print("🚨 CRÍTICO: Ninguna carpeta es accesible")
    print("   Verifica las rutas en el archivo .env")

print()
print("=" * 80)
