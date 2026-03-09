"""
Test del módulo de causaciones - Verificar escaneo de carpetas
"""
from config_carpetas import escanear_sedes_y_carpetas, obtener_sedes_disponibles, obtener_carpetas_base
import os

def test_escaneo():
    print("=" * 80)
    print("TEST DEL MÓDULO DE CAUSACIONES")
    print("=" * 80)
    
    # 1. Verificar carpetas base
    print("\n📁 CARPETAS BASE CONFIGURADAS:")
    carpetas = obtener_carpetas_base()
    for sede, ruta in carpetas.items():
        accesible = "✅" if os.path.exists(ruta) else "❌"
        print(f"  {accesible} {sede:8} -> {ruta}")
    
    # 2. Obtener sedes disponibles
    print("\n🏢 SEDES DISPONIBLES:")
    sedes = obtener_sedes_disponibles()
    print(f"  {sedes}")
    
    # 3. Escanear todas las sedes
    print("\n🔍 ESCANEANDO TODAS LAS SEDES...")
    archivos, carpetas = escanear_sedes_y_carpetas(sedes, filtro="")
    
    print(f"\n📊 RESULTADOS:")
    print(f"  Total archivos PDF encontrados: {len(archivos)}")
    print(f"  Total carpetas/subcarpetas: {len(carpetas)}")
    
    # 4. Mostrar distribución por sede
    print("\n📈 DISTRIBUCIÓN POR SEDE:")
    distribucion = {}
    for archivo in archivos:
        sede = archivo['sede']
        distribucion[sede] = distribucion.get(sede, 0) + 1
    
    for sede in sorted(distribucion.keys()):
        print(f"  {sede}: {distribucion[sede]} archivos")
    
    # 5. Mostrar primeras 10 carpetas encontradas
    if carpetas:
        print("\n📂 PRIMERAS 10 CARPETAS ENCONTRADAS:")
        for i, carpeta in enumerate(sorted(carpetas)[:10], 1):
            print(f"  {i}. {carpeta}")
    
    # 6. Mostrar primeros 5 archivos
    if archivos:
        print("\n📄 PRIMEROS 5 ARCHIVOS ENCONTRADOS:")
        archivos_ordenados = sorted(archivos, key=lambda x: x['fecha'], reverse=True)
        for i, archivo in enumerate(archivos_ordenados[:5], 1):
            nombre = os.path.basename(archivo['rel_pdf'])
            carpeta = os.path.dirname(archivo['rel_pdf'])
            print(f"  {i}. [{archivo['sede']}] {nombre}")
            print(f"     📁 {carpeta}")
    
    # 7. Test con filtro
    print("\n🔎 TEST CON FILTRO 'factura':")
    archivos_filtrados, _ = escanear_sedes_y_carpetas(sedes, filtro="factura")
    print(f"  Archivos encontrados con 'factura' en el nombre: {len(archivos_filtrados)}")
    
    # 8. Test con una sola sede
    if sedes:
        sede_test = sedes[0]
        print(f"\n🎯 TEST SOLO SEDE '{sede_test}':")
        archivos_sede, carpetas_sede = escanear_sedes_y_carpetas([sede_test], filtro="")
        print(f"  Archivos: {len(archivos_sede)}")
        print(f"  Carpetas: {len(carpetas_sede)}")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETADO")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_escaneo()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
