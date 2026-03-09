"""
TEST SIMPLE - PROCESAR SOLO TABLA DIAN
Para identificar el error específico sin procesar todo
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("🧪 TEST: PROCESAR SOLO TABLA DIAN")
print("=" * 80)

try:
    # 1. Importar app y db
    print("\n1️⃣ Importando app y db...")
    from app import app
    from extensions import db
    
    # 2. Importar funciones
    print("2️⃣ Importando funciones de procesamiento...")
    from modules.dian_vs_erp.routes import procesar_dian
    
    # 3. Ejecutar dentro del contexto
    print("3️⃣ Ejecutando dentro del contexto de Flask...")
    with app.app_context():
        print("4️⃣ Llamando a procesar_dian()...")
        print("   Archivo: uploads/dian/Dian.xlsx\n")
        
        # EJECUTAR
        registros_insertados = procesar_dian()
        
        print(f"\n✅ ÉXITO: {registros_insertados} registros de DIAN insertados")
        
        # Verificar en BD
        count = db.session.execute(db.text("SELECT COUNT(*) FROM dian")).scalar()
        print(f"✅ Verificación BD: {count} registros en tabla dian")
        
except FileNotFoundError as e:
    print(f"\n❌ ERROR: Archivo no encontrado")
    print(f"   {e}")
    print("\n💡 Verifica que exista: uploads/dian/Dian.xlsx")
    
except Exception as e:
    import traceback
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"   Mensaje: {str(e)}")
    print("\n📋 STACK TRACE:")
    print(traceback.format_exc())

print("\n" + "=" * 80)
