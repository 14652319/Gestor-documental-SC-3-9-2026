# -*- coding: utf-8 -*-
"""Script para remover app_principal.app_context() y arreglar indentación"""
import os
import re

# Ruta al archivo
archivo = r"C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\✏️Gestionar Terceros\app.py"

# Leer contenido
with open(archivo, 'r', encoding='utf-8') as f:
    lineas = f.readlines()

lineas_corregidas = []
i = 0
while i < len(lineas):
    linea = lineas[i]
    
    # Si encuentra una línea con app_context, la elimina
    if 'with app_principal.app_context():' in linea:
        print(f"Línea {i+1}: Eliminando app_context")
        i += 1
        
        # Reducir indentación de las siguientes líneas hasta encontrar el except o return al mismo nivel
        espacios_originales = len(linea) - len(linea.lstrip())
        while i < len(lineas):
            siguiente = lineas[i]
            espacios_siguiente = len(siguiente) - len(siguiente.lstrip())
            
            # Si la siguiente línea está al mismo nivel o menos indentada que el with, terminar
            if espacios_siguiente <= espacios_originales and siguiente.strip():
                break
            
            # Si está más indentada, reducir 4 espacios
            if espacios_siguiente > espacios_originales:
                lineas_corregidas.append(' ' * (espacios_siguiente - 4) + siguiente.lstrip())
            else:
                lineas_corregidas.append(siguiente)
            i += 1
    else:
        lineas_corregidas.append(linea)
        i += 1

# Guardar
with open(archivo, 'w', encoding='utf-8') as f:
    f.writelines(lineas_corregidas)

print("✅ Archivo actualizado - Removidas referencias a app_principal.app_context() y corregida indentación")
