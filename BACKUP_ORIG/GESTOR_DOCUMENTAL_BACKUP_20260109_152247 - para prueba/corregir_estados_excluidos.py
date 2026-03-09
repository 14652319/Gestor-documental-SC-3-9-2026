"""
Script para corregir el formato JSON de estados_excluidos en la base de datos
Fecha: 26 de diciembre de 2025
"""

import json
from app import app, db
from modules.dian_vs_erp.models import EnvioProgramadoDianVsErp

def corregir_estados_excluidos():
    """Corrige el formato de estados_excluidos de string a JSON válido"""
    with app.app_context():
        # Obtener todas las configuraciones
        configuraciones = EnvioProgramadoDianVsErp.query.all()
        
        print(f"📋 Encontradas {len(configuraciones)} configuraciones")
        print("=" * 80)
        
        corregidas = 0
        
        for config in configuraciones:
            cambios = False
            print(f"\n🔍 ID {config.id}: {config.nombre}")
            print(f"   Tipo: {config.tipo}")
            
            # Corregir estados_excluidos
            if config.estados_excluidos:
                print(f"   estados_excluidos ANTES: {repr(config.estados_excluidos)}")
                
                try:
                    # Intentar parsear como JSON
                    json.loads(config.estados_excluidos)
                    print(f"   ✅ Ya es JSON válido")
                except (json.JSONDecodeError, TypeError):
                    # No es JSON válido, necesita corrección
                    if isinstance(config.estados_excluidos, str):
                        # Si es un string simple como "Causada", convertir a ["Causada"]
                        if config.estados_excluidos.strip():
                            config.estados_excluidos = json.dumps([config.estados_excluidos])
                            cambios = True
                            print(f"   ✏️  CORRIGIENDO a: {config.estados_excluidos}")
                        else:
                            config.estados_excluidos = json.dumps([])
                            cambios = True
                            print(f"   ✏️  String vacío → []")
                    else:
                        config.estados_excluidos = json.dumps([])
                        cambios = True
                        print(f"   ✏️  Tipo inválido → []")
            else:
                print(f"   estados_excluidos: NULL/vacío")
            
            # Corregir estados_incluidos también
            if config.estados_incluidos:
                print(f"   estados_incluidos ANTES: {repr(config.estados_incluidos)}")
                
                try:
                    json.loads(config.estados_incluidos)
                    print(f"   ✅ Ya es JSON válido")
                except (json.JSONDecodeError, TypeError):
                    if isinstance(config.estados_incluidos, str):
                        if config.estados_incluidos.strip():
                            config.estados_incluidos = json.dumps([config.estados_incluidos])
                            cambios = True
                            print(f"   ✏️  CORRIGIENDO a: {config.estados_incluidos}")
                        else:
                            config.estados_incluidos = json.dumps([])
                            cambios = True
                            print(f"   ✏️  String vacío → []")
                    else:
                        config.estados_incluidos = json.dumps([])
                        cambios = True
                        print(f"   ✏️  Tipo inválido → []")
            
            if cambios:
                corregidas += 1
        
        # Guardar cambios
        if corregidas > 0:
            print(f"\n💾 Guardando {corregidas} correcciones...")
            db.session.commit()
            print(f"✅ {corregidas} configuraciones corregidas")
        else:
            print(f"\n✅ No se encontraron configuraciones que necesiten corrección")
        
        print("\n" + "=" * 80)
        print("🎯 Verificación final:")
        print("=" * 80)
        
        # Verificar todas las configuraciones
        configuraciones = EnvioProgramadoDianVsErp.query.all()
        todas_validas = True
        
        for config in configuraciones:
            print(f"\n🔍 ID {config.id}: {config.nombre}")
            
            if config.estados_excluidos:
                try:
                    parsed = json.loads(config.estados_excluidos)
                    print(f"   ✅ estados_excluidos: {parsed} (JSON válido)")
                except:
                    print(f"   ❌ estados_excluidos: {repr(config.estados_excluidos)} (INVÁLIDO)")
                    todas_validas = False
            
            if config.estados_incluidos:
                try:
                    parsed = json.loads(config.estados_incluidos)
                    print(f"   ✅ estados_incluidos: {parsed} (JSON válido)")
                except:
                    print(f"   ❌ estados_incluidos: {repr(config.estados_incluidos)} (INVÁLIDO)")
                    todas_validas = False
        
        print("\n" + "=" * 80)
        if todas_validas:
            print("🎉 ÉXITO: Todas las configuraciones tienen formato JSON válido")
        else:
            print("⚠️  ADVERTENCIA: Aún hay configuraciones con formato inválido")
        print("=" * 80)

if __name__ == '__main__':
    corregir_estados_excluidos()
