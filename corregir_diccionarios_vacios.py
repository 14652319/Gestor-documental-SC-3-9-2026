"""
Corregir diccionarios vacíos {} a listas vacías [] en estados_excluidos
"""

import json
from app import app, db
from modules.dian_vs_erp.models import EnvioProgramadoDianVsErp

with app.app_context():
    configuraciones = EnvioProgramadoDianVsErp.query.all()
    
    print("\n" + "=" * 80)
    print("🔧 CORRIGIENDO DICCIONARIOS VACÍOS A LISTAS VACÍAS")
    print("=" * 80)
    
    corregidas = 0
    
    for config in configuraciones:
        cambios = False
        
        # Corregir estados_excluidos
        if config.estados_excluidos == '{}':
            print(f"\n🔍 ID {config.id}: {config.nombre}")
            print(f"   estados_excluidos ANTES: '{config.estados_excluidos}'")
            config.estados_excluidos = '[]'
            print(f"   estados_excluidos DESPUÉS: '{config.estados_excluidos}'")
            cambios = True
        
        # Corregir estados_incluidos
        if config.estados_incluidos == '{}':
            if not cambios:
                print(f"\n🔍 ID {config.id}: {config.nombre}")
            print(f"   estados_incluidos ANTES: '{config.estados_incluidos}'")
            config.estados_incluidos = '[]'
            print(f"   estados_incluidos DESPUÉS: '{config.estados_incluidos}'")
            cambios = True
        
        if cambios:
            corregidas += 1
    
    if corregidas > 0:
        print(f"\n💾 Guardando {corregidas} correcciones...")
        db.session.commit()
        print(f"✅ {corregidas} configuraciones corregidas")
    else:
        print(f"\n✅ No hay diccionarios vacíos para corregir")
    
    print("\n" + "=" * 80)
    print("✅ CORRECCIÓN COMPLETADA")
    print("=" * 80)
