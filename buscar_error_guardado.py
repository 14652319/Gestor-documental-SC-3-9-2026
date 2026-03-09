"""
Buscar errores en el guardado de facturas
"""
import os

log_file = "logs/security.log"

if os.path.exists(log_file):
    print("🔍 Buscando en logs...")
    
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        lineas = f.readlines()
    
    # Buscar las últimas 50 líneas con menciones a guardado
    relevantes = []
    for i, linea in enumerate(lineas):
        if any(keyword in linea for keyword in ['GUARDAR', 'SINCRONIZ', 'ERROR', 'ME40', '772863', 'BIMBO', '1FEA', '77']):
            relevantes.append((i, linea.strip()))
    
    print(f"\n📋 Últimas 50 líneas relevantes:\n")
    for idx, linea in relevantes[-50:]:
        print(f"{idx+1:6d} | {linea}")
else:
    print("❌ No se encontró el archivo de logs")
