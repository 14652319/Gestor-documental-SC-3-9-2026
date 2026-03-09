"""
Verificar logs de sincronización
"""
import os
from datetime import datetime

log_file = "logs/security.log"

if os.path.exists(log_file):
    print("🔍 Buscando errores de sincronización...\n")
    
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        lineas = f.readlines()
    
    # Buscar las últimas líneas con SINCRONIZ
    relevantes = []
    for linea in lineas:
        if 'SINCRONIZ' in linea.upper() or 'GUARDAR' in linea.upper():
            relevantes.append(linea.strip())
    
    print(f"📋 Últimas 30 líneas con SINCRONIZ o GUARDAR:\n")
    for linea in relevantes[-30:]:
        print(linea)
else:
    print("❌ No se encontró archivo de logs")
