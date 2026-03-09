"""
Ver exactamente qué contiene estados_excluidos en la base de datos
"""

import json
from app import app, db
from modules.dian_vs_erp.models import EnvioProgramadoDianVsErp

with app.app_context():
    configuraciones = EnvioProgramadoDianVsErp.query.all()
    
    print("\n" + "=" * 80)
    print("📋 CONTENIDO EXACTO DE LA BASE DE DATOS")
    print("=" * 80)
    
    for config in configuraciones:
        print(f"\n🔍 ID {config.id}: {config.nombre}")
        print(f"   Tipo: {config.tipo}")
        
        # Mostrar el contenido exacto
        print(f"   estados_excluidos RAW: {repr(config.estados_excluidos)}")
        print(f"   estados_excluidos TYPE: {type(config.estados_excluidos)}")
        
        if config.estados_excluidos:
            # Intentar mostrar cada carácter
            print(f"   CARACTERES: {[c for c in config.estados_excluidos[:50]]}")
            
            # Intentar parsear
            try:
                parsed = json.loads(config.estados_excluidos)
                print(f"   ✅ PARSEADO: {parsed} (tipo: {type(parsed)})")
            except Exception as e:
                print(f"   ❌ ERROR AL PARSEAR: {e}")
        
        print(f"   estados_incluidos RAW: {repr(config.estados_incluidos)}")
        if config.estados_incluidos:
            try:
                parsed = json.loads(config.estados_incluidos)
                print(f"   ✅ PARSEADO: {parsed}")
            except Exception as e:
                print(f"   ❌ ERROR AL PARSEAR: {e}")
    
    print("\n" + "=" * 80)
