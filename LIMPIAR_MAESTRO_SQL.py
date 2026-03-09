"""
LIMPIAR_MAESTRO_SQL.py
=======================
Limpia la tabla maestro_dian_vs_erp usando SQLAlchemy (sin leer .env)
"""

import sys
from pathlib import Path

# Agregar path del proyecto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("="*80)
print("🗑️  LIMPIAR TABLA maestro_dian_vs_erp")
print("="*80)

try:
    # Importar desde el proyecto
    from app import db, app
    from modules.dian_vs_erp.models import MaestroDianVsERP
    
    with app.app_context():
        # Contar registros actuales
        count_antes = db.session.query(MaestroDianVsERP).count()
        print(f"📊 Registros actuales: {count_antes:,}")
        
        if count_antes == 0:
            print("✅ La tabla ya está vacía")
            sys.exit(0)
        
        # Solicitar confirmación
        print(f"\n⚠️  ¿Eliminar {count_antes:,} registros? (escribe 'si' para confirmar)")
        respuesta = input("→ ").strip().lower()
        
        if respuesta != 'si':
            print("❌ Operación cancelada")
            sys.exit(0)
        
        # Eliminar todos los registros
        print(f"\n🗑️  Eliminando {count_antes:,} registros...")
        db.session.query(MaestroDianVsERP).delete()
        db.session.commit()
        
        # Verificar
        count_despues = db.session.query(MaestroDianVsERP).count()
        print(f"✅ Registros eliminados: {count_antes - count_despues:,}")
        print(f"📊 Registros restantes: {count_despues:,}")
        
        if count_despues == 0:
            print("\n" + "="*80)
            print("✅ TABLA LIMPIADA EXITOSAMENTE")
            print("="*80)
        else:
            print(f"\n⚠️  Quedaron {count_despues:,} registros")
            
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
