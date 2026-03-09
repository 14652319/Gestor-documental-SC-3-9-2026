"""
CARGA AUTOMÁTICA MASIVA DE TODOS LOS ARCHIVOS
Procesa todos los archivos DIAN + ERP Financiero + ERP Comercial
Diciembre 30, 2025
"""

import subprocess
from pathlib import Path
import time

print("=" * 80)
print("🚀 CARGA AUTOMÁTICA MASIVA - DIAN VS ERP")
print("=" * 80)

# Ruta base
BASE_PATH = Path(r"D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025")

# Carpetas a procesar
CARPETAS = {
    "DIAN": BASE_PATH / "Dian",
    "ERP Financiero": BASE_PATH / "ERP Financiero",
    "ERP Comercial": BASE_PATH / "ERP Comercial"
}

# Recopilar archivos
archivos_a_cargar = []
for nombre, carpeta in CARPETAS.items():
    if not carpeta.exists():
        print(f"⚠️ Carpeta {nombre} no encontrada: {carpeta}")
        continue
    
    archivos = [
        a for a in carpeta.glob("*") 
        if a.is_file() and a.suffix.lower() in ['.xlsx', '.xlsm', '.csv', '.ods']
    ]
    
    for archivo in archivos:
        archivos_a_cargar.append((nombre, archivo))

print(f"\n📊 ARCHIVOS A CARGAR: {len(archivos_a_cargar)}")
for tipo, archivo in archivos_a_cargar:
    tamano_mb = archivo.stat().st_size / (1024 * 1024)
    print(f"   • [{tipo}] {archivo.name} ({tamano_mb:.2f} MB)")

if len(archivos_a_cargar) == 0:
    print("\n❌ No se encontraron archivos para cargar")
    exit(1)

# Confirmar
input(f"\n⏸️  Presiona ENTER para iniciar la carga de {len(archivos_a_cargar)} archivos...")

# Procesar cada archivo
print("\n" + "=" * 80)
print("📥 PROCESANDO ARCHIVOS")
print("=" * 80)

exitosos = 0
fallidos = 0
tiempo_total_inicio = time.time()

for idx, (tipo, archivo) in enumerate(archivos_a_cargar, 1):
    print(f"\n[{idx}/{len(archivos_a_cargar)}] 📂 {tipo}: {archivo.name}")
    print("-" * 60)
    
    inicio = time.time()
    
    try:
        # Ejecutar CARGA_DIRECTA_SIMPLE.py con el archivo
        resultado = subprocess.run(
            ["python", "CARGA_DIRECTA_SIMPLE.py", str(archivo)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        fin = time.time()
        duracion = fin - inicio
        
        if resultado.returncode == 0:
            print(f"✅ ÉXITO ({duracion:.1f}s)")
            exitosos += 1
            
            # Mostrar últimas líneas del output
            lineas = resultado.stdout.strip().split('\n')
            for linea in lineas[-5:]:
                if linea.strip():
                    print(f"   {linea}")
        else:
            print(f"❌ ERROR ({duracion:.1f}s)")
            fallidos += 1
            print(f"   Error: {resultado.stderr[-200:] if resultado.stderr else 'Sin detalles'}")
            
    except Exception as e:
        print(f"❌ EXCEPCIÓN: {e}")
        fallidos += 1

tiempo_total = time.time() - tiempo_total_inicio

# Resumen final
print("\n" + "=" * 80)
print("📊 RESUMEN FINAL")
print("=" * 80)
print(f"✅ Exitosos:  {exitosos}/{len(archivos_a_cargar)}")
print(f"❌ Fallidos:   {fallidos}/{len(archivos_a_cargar)}")
print(f"⏱️  Tiempo total: {tiempo_total/60:.1f} minutos ({tiempo_total:.1f}s)")
print(f"⚡ Promedio:    {tiempo_total/len(archivos_a_cargar):.1f}s por archivo")
print("=" * 80)

if exitosos == len(archivos_a_cargar):
    print("\n🎉 ¡TODOS LOS ARCHIVOS CARGADOS EXITOSAMENTE!")
else:
    print(f"\n⚠️  {fallidos} archivo(s) con errores. Revisar logs arriba.")
