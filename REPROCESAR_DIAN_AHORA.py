"""
Script para FORZAR REPROCESAMIENTO de archivos DIAN
Ejecuta actualizar_maestro() directamente sin necesitar login
"""
import sys
import os

# Añadir ruta del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("🔄 REPROCESANDO ARCHIVOS DIAN CON FIX APLICADO")
print("=" * 80)
print()

# Importar Flask app y función
from app import app
from modules.dian_vs_erp.routes import actualizar_maestro

# Ejecutar dentro del contexto de la app
with app.app_context():
    print("⚙️ Iniciando reprocesamiento...")
    print()
    
    try:
        mensaje = actualizar_maestro()
        print()
        print("✅" * 40)
        print("✅✅✅ REPROCESAMIENTO COMPLETADO ✅✅✅")
        print("✅" * 40)
        print()
        print("📊 RESULTADO:")
        print(mensaje)
        print()
        print("🔍 AHORA VERIFICA EN EL VISOR:")
        print("   → http://127.0.0.1:8099/dian_vs_erp/visor_v2")
        print()
        print("   Las fechas ya NO deberían ser todas '17-Feb'")
        print("   Deberías ver fechas variadas: 14-Feb, 15-Feb, 16-Feb, etc.")
        print()
    except Exception as e:
        print()
        print("❌" * 40)
        print(f"❌ ERROR: {e}")
        print("❌" * 40)
        import traceback
        traceback.print_exc()
        
print("=" * 80)
