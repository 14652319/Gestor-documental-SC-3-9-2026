"""
Script de prueba para verificar acceso a carpetas de red
"""
from config_carpetas import verificar_acceso_carpetas, obtener_carpetas_base

print("=" * 70)
print("VERIFICACIÓN DE ACCESO A CARPETAS DE RED")
print("=" * 70)
print()

# Mostrar configuración
print("📁 CARPETAS CONFIGURADAS:")
print("-" * 70)
carpetas = obtener_carpetas_base()
for sede, ruta in carpetas.items():
    tipo = "CAUSADAS" if "_C" in sede else "APROBADAS"
    print(f"  {sede:8} ({tipo:9}): {ruta}")
print()

# Verificar acceso
print("🔍 VERIFICANDO ACCESO:")
print("-" * 70)
estado = verificar_acceso_carpetas()

accesibles = 0
no_accesibles = 0

for sede, info in estado.items():
    simbolo = "✅" if info['accesible'] else "❌"
    status = "ACCESIBLE" if info['accesible'] else "NO ACCESIBLE"
    
    print(f"{simbolo} {sede:8} - {status:15} | {info['ruta']}")
    
    if info['accesible']:
        accesibles += 1
    else:
        no_accesibles += 1
        if 'error' in info:
            print(f"           Error: {info['error']}")

print()
print("=" * 70)
print(f"RESUMEN: {accesibles} accesibles | {no_accesibles} no accesibles")
print("=" * 70)

# Listar algunos archivos de prueba si hay carpetas accesibles
if accesibles > 0:
    print()
    print("📄 LISTANDO ARCHIVOS DE PRUEBA:")
    print("-" * 70)
    import os
    
    for sede, info in estado.items():
        if info['accesible']:
            try:
                archivos = [f for f in os.listdir(info['ruta']) if f.lower().endswith('.pdf')]
                print(f"\n{sede} ({info['nombre']}):")
                print(f"  Total PDFs: {len(archivos)}")
                if archivos:
                    print(f"  Primeros 3 archivos:")
                    for archivo in archivos[:3]:
                        print(f"    - {archivo}")
            except Exception as e:
                print(f"  Error al listar: {e}")
