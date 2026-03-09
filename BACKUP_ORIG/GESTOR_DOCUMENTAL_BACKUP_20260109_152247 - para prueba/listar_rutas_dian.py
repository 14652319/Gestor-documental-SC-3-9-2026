# -*- coding: utf-8 -*-
"""
Script para listar todas las rutas de DIAN registradas en Flask
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Deshabilitar el servidor de desarrollo
import os
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

from app import app

print("\n" + "="*80)
print("RUTAS DEL MÓDULO DIAN VS ERP REGISTRADAS EN FLASK")
print("="*80 + "\n")

rutas_dian = []
for rule in app.url_map.iter_rules():
    if 'dian' in rule.rule.lower():
        rutas_dian.append({
            'ruta': rule.rule,
            'metodos': ', '.join(sorted(rule.methods - {'OPTIONS', 'HEAD'})),
            'endpoint': rule.endpoint
        })

# Ordenar por ruta
rutas_dian.sort(key=lambda x: x['ruta'])

# Imprimir
for idx, ruta in enumerate(rutas_dian, 1):
    print(f"{idx:2d}. {ruta['ruta']:60s} [{ruta['metodos']:15s}] -> {ruta['endpoint']}")

print(f"\n{'='*80}")
print(f"TOTAL: {len(rutas_dian)} rutas encontradas")
print("="*80)

# Buscar específicamente /api/dian_v2
print("\n🔍 BUSCANDO RUTA /api/dian_v2...")
encontrada = False
for ruta in rutas_dian:
    if '/api/dian_v2' in ruta['ruta']:
        print(f"✅ ENCONTRADA: {ruta['ruta']} [{ruta['metodos']}] -> {ruta['endpoint']}")
        encontrada = True

if not encontrada:
    print("❌ NO ENCONTRADA: La ruta /api/dian_v2 NO está registrada en Flask")
    print("\nRutas de API disponibles:")
    for ruta in rutas_dian:
        if '/api/' in ruta['ruta']:
            print(f"   - {ruta['ruta']}")
