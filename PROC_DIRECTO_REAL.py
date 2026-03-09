"""
EJECUTA EL PROCESAMIENTO DIRECTAMENTE
Llama a la función actualizar_maestro() que es la que hace todo el trabajo
Este es el código REAL que se ejecuta cuando cargas archivos desde el navegador
"""

import sys
import os

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("🚀 EJECUTANDO PROCESAMIENTO REAL DE ARCHIVOS")
print("=" * 80)
print("\n⚠️  ESTE ES EL CÓDIGO REAL QUE USA EL SISTEMA EN PRODUCCIÓN")
print("   Los archivos en uploads/ serán procesados e insertados en la BD\n")

try:
    # Importar app para contexto de Flask
    from app import app
    from modules.dian_vs_erp.routes import actualizar_maestro
    
    # Ejecutar dentro del contexto de Flask (necesario para db.session)
    with app.app_context():
        print("📋 Llamando a actualizar_maestro()...")
        print("   Esta función:")
        print("   1. Lee archivos Excel de uploads/")
        print("   2. Procesa DIAN, ERP Comercial, ERP Financiero, Acuses")
        print("   3. Inserta registros en PostgreSQL")
        print("   4. Consolida tabla maestro_dian_vs_erp")
        print("\n" + "-" * 80 + "\n")
        
        # EJECUTAR LA FUNCIÓN REAL
        resultado = actualizar_maestro()
        
        print("\n" + "-" * 80)
        print("\n✅ PROCESAMIENTO COMPLETADO")
        print("\n📋 RESULTADO:")
        print(resultado)
        print("\n" + "=" * 80)
        
except Exception as e:
    import traceback
    error_completo = traceback.format_exc()
    
    print("\n" + "=" * 80)
    print("❌ ERROR DURANTE EL PROCESAMIENTO")
    print("=" * 80)
    print(f"\nTipo de error: {type(e).__name__}")
    print(f"Mensaje: {str(e)}")
    print("\n📋 STACK TRACE COMPLETO:")
    print(error_completo)
    print("=" * 80)
    
    sys.exit(1)
