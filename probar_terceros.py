#!/usr/bin/env python3
"""
Script para probar las funcionalidades del módulo de terceros
"""

from app import app, db
from modules.terceros.models import TerceroStats, TerceroHelper

def test_estadisticas():
    """Prueba las estadísticas de terceros"""
    with app.app_context():
        print("🧪 Probando estadísticas de terceros...")
        stats = TerceroStats.obtener_estadisticas()
        print(f"📊 Total de terceros: {stats['total_terceros']}")
        print(f"👥 Terceros activos: {stats['terceros_activos']}")
        print(f"🆕 Terceros recientes: {stats['terceros_recientes']}")
        print(f"👤 Personas naturales: {stats['personas_naturales']}")
        print(f"🏢 Personas jurídicas: {stats['personas_juridicas']}")
        print(f"📈 Tasa de crecimiento: {stats['tasa_crecimiento']}%")
        return True

def test_listar_terceros():
    """Prueba el listado de terceros"""
    with app.app_context():
        print("\n🧪 Probando listado de terceros...")
        terceros_paginados = TerceroHelper.listar_terceros(page=1, per_page=5)
        if terceros_paginados:
            print(f"📋 Total de terceros: {terceros_paginados.total}")
            print(f"📄 Página actual: {terceros_paginados.page}")
            print(f"🔢 Terceros en esta página: {len(terceros_paginados.items)}")
            
            print("\n👥 Primeros terceros:")
            for tercero in terceros_paginados.items[:3]:
                print(f"  • {tercero.nit} - {tercero.razon_social}")
            return True
        return False

def test_buscar_por_nit():
    """Prueba la búsqueda por NIT"""
    with app.app_context():
        print("\n🧪 Probando búsqueda por NIT...")
        tercero = TerceroHelper.buscar_por_nit("900803176")
        if tercero:
            print(f"🎯 Tercero encontrado: {tercero.razon_social}")
            return True
        else:
            print("❌ No se encontró tercero con ese NIT")
            return False

if __name__ == "__main__":
    print("🚀 PROBANDO MÓDULO DE TERCEROS")
    print("=" * 50)
    
    try:
        success = True
        success &= test_estadisticas()
        success &= test_listar_terceros()
        success &= test_buscar_por_nit()
        
        if success:
            print("\n✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
            print("🎉 El módulo de terceros está funcionando correctamente")
        else:
            print("\n❌ ALGUNAS PRUEBAS FALLARON")
            
    except Exception as e:
        print(f"\n💥 ERROR EN LAS PRUEBAS: {e}")