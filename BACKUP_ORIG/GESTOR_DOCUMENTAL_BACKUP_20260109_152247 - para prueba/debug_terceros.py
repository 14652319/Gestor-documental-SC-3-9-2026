#!/usr/bin/env python3
"""
Script para debuggear el listado de terceros directamente
"""

from app import app, db
from modules.terceros.models import TerceroHelper

def test_tercero_helper():
    """Prueba directa del TerceroHelper"""
    with app.app_context():
        print("🔍 DEBUGGEANDO TERCERO HELPER")
        print("=" * 50)
        
        try:
            # Probar con parámetros básicos
            print("1. Probando con parámetros básicos...")
            result = TerceroHelper.listar_terceros(page=1, per_page=5)
            
            if result is None:
                print("❌ El helper devolvió None")
                return False
                
            print(f"✅ Helper funcionó! Total: {result.total}, Items: {len(result.items)}")
            
            # Mostrar algunos terceros
            print("\n👥 Primeros terceros encontrados:")
            for i, tercero in enumerate(result.items[:3]):
                print(f"  {i+1}. {tercero.nit} - {tercero.razon_social}")
                print(f"     ID: {tercero.id}")
                print(f"     Tipo: {getattr(tercero, 'tipo_persona', 'No especificado')}")
                if hasattr(tercero, 'fecha_registro'):
                    print(f"     Fecha: {tercero.fecha_registro}")
                print()
            
            # Probar con búsqueda
            print("2. Probando búsqueda por '900'...")
            result_busqueda = TerceroHelper.listar_terceros(page=1, per_page=5, search='900')
            
            if result_busqueda:
                print(f"✅ Búsqueda funcionó! Encontrados: {result_busqueda.total}")
                if result_busqueda.items:
                    primer_resultado = result_busqueda.items[0]
                    print(f"   Primer resultado: {primer_resultado.nit} - {primer_resultado.razon_social}")
            else:
                print("❌ Error en búsqueda")
            
            return True
            
        except Exception as e:
            print(f"💥 ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_estructura_tercero():
    """Prueba la estructura del modelo Tercero"""
    with app.app_context():
        print("\n🔍 DEBUGGEANDO ESTRUCTURA DEL MODELO")
        print("=" * 50)
        
        try:
            from app import Tercero
            
            # Obtener un tercero de ejemplo
            tercero = Tercero.query.first()
            
            if tercero:
                print(f"📋 Tercero de ejemplo: {tercero.nit} - {tercero.razon_social}")
                print(f"   ID: {tercero.id}")
                
                # Listar todos los atributos disponibles
                print("\n📝 Atributos disponibles:")
                for attr in dir(tercero):
                    if not attr.startswith('_') and not callable(getattr(tercero, attr)):
                        try:
                            valor = getattr(tercero, attr)
                            tipo = type(valor).__name__
                            print(f"   {attr}: {tipo} = {str(valor)[:50]}...")
                        except:
                            print(f"   {attr}: (error al acceder)")
                
                return True
            else:
                print("❌ No se encontró ningún tercero")
                return False
                
        except Exception as e:
            print(f"💥 ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🚀 DEBUGGEO COMPLETO DE TERCEROS")
    
    # Probar estructura primero
    if test_estructura_tercero():
        print("\n" + "="*50)
        # Luego probar el helper
        test_tercero_helper()
    
    print("\n🎯 Debugging completado")