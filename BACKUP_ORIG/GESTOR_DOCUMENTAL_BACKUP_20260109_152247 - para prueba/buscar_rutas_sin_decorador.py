#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Busca todas las rutas en los módulos y verifica si tienen decorador
"""
import os
import re

def analizar_archivo_rutas(ruta_archivo, modulo_nombre):
    """Analiza un archivo de rutas y encuentra funciones con/sin decorador"""
    if not os.path.exists(ruta_archivo):
        return None
    
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar todas las funciones que son endpoints
    # Patrón: @nombre_bp.route(...) seguido de @requiere_permiso (opcional) seguido de def
    lineas = contenido.split('\n')
    
    rutas_sin_decorador = []
    rutas_con_decorador = []
    
    i = 0
    while i < len(lineas):
        linea = lineas[i].strip()
        
        # Detectar decorador de ruta
        if '@' in linea and '.route(' in linea:
            ruta_match = re.search(r"\.route\(['\"]([^'\"]+)['\"]", linea)
            if ruta_match:
                ruta = ruta_match.group(1)
                
                # Revisar las siguientes líneas para ver si hay decorador de permiso
                tiene_decorador = False
                nombre_funcion = None
                
                j = i + 1
                while j < len(lineas) and j < i + 10:  # Revisar hasta 10 líneas adelante
                    siguiente = lineas[j].strip()
                    
                    if '@requiere_permiso' in siguiente:
                        tiene_decorador = True
                        # Extraer la acción del decorador
                        accion_match = re.search(r"@requiere_permiso(?:_html)?\(['\"]" + modulo_nombre + r"['\"],\s*['\"]([^'\"]+)['\"]", siguiente)
                        if accion_match:
                            accion = accion_match.group(1)
                            rutas_con_decorador.append({
                                'ruta': ruta,
                                'accion': accion,
                                'linea': i + 1
                            })
                        break
                    
                    if 'def ' in siguiente:
                        nombre_funcion = re.search(r'def\s+(\w+)', siguiente).group(1)
                        if not tiene_decorador:
                            rutas_sin_decorador.append({
                                'ruta': ruta,
                                'funcion': nombre_funcion,
                                'linea': i + 1
                            })
                        break
                    
                    j += 1
        
        i += 1
    
    return {
        'con_decorador': rutas_con_decorador,
        'sin_decorador': rutas_sin_decorador
    }

def main():
    print("=" * 100)
    print("🔍 ANÁLISIS DE RUTAS CON/SIN DECORADORES DE PERMISO")
    print("=" * 100)
    
    modulos = [
        {
            'nombre': 'causaciones',
            'archivo': 'modules/causaciones/routes.py'
        },
        {
            'nombre': 'facturas_digitales',
            'archivo': 'modules/facturas_digitales/routes.py'
        },
        {
            'nombre': 'archivo_digital',
            'archivo': 'modules/notas_contables/pages.py'
        },
        {
            'nombre': 'recibir_facturas',
            'archivo': 'modules/recibir_facturas/routes.py'
        },
        {
            'nombre': 'relaciones',
            'archivo': 'modules/relaciones/routes.py'
        }
    ]
    
    for modulo in modulos:
        print(f"\n{'='*100}")
        print(f"📦 MÓDULO: {modulo['nombre'].upper()}")
        print(f"📁 Archivo: {modulo['archivo']}")
        print(f"{'='*100}")
        
        resultado = analizar_archivo_rutas(modulo['archivo'], modulo['nombre'])
        
        if resultado is None:
            print("   ⚠️ Archivo no encontrado")
            continue
        
        # Rutas CON decorador
        print(f"\n✅ RUTAS CON DECORADOR ({len(resultado['con_decorador'])}):")
        if resultado['con_decorador']:
            for r in resultado['con_decorador']:
                print(f"   Línea {r['linea']:4d}: {r['ruta']:40s} → {modulo['nombre']}.{r['accion']}")
        else:
            print("   (ninguna)")
        
        # Rutas SIN decorador
        print(f"\n❌ RUTAS SIN DECORADOR ({len(resultado['sin_decorador'])}):")
        if resultado['sin_decorador']:
            for r in resultado['sin_decorador']:
                print(f"   Línea {r['linea']:4d}: {r['ruta']:40s} (función: {r['funcion']})")
        else:
            print("   (ninguna - todas protegidas ✅)")
    
    print("\n" + "=" * 100)

if __name__ == "__main__":
    main()
