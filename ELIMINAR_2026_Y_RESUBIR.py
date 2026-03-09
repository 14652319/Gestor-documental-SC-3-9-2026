"""
Script RÁPIDO: Eliminar datos de 2026 para re-subir archivo
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from modules.dian_vs_erp.models import MaestroDianVsErp
from datetime import date

print("=" * 80)
print("🗑️  ELIMINANDO DATOS DE 2026")
print("=" * 80)

with app.app_context():
    try:
        # Contar registros antes
        total_antes = MaestroDianVsErp.query.filter(
            MaestroDianVsErp.fecha_emision >= date(2026, 1, 1)
        ).count()
        
        print(f"\n📊 Registros de 2026 encontrados: {total_antes:,}")
        
        if total_antes == 0:
            print("\n✅ No hay registros de 2026 para eliminar")
        else:
            print(f"\n🗑️  Eliminando {total_antes:,} registros...")
            
            # Eliminar
            eliminados = MaestroDianVsErp.query.filter(
                MaestroDianVsErp.fecha_emision >= date(2026, 1, 1)
            ).delete(synchronize_session=False)
            
            db.session.commit()
            
            print(f"✅ Eliminados: {eliminados:,} registros")
            
            # Verificar
            total_despues = MaestroDianVsErp.query.filter(
                MaestroDianVsErp.fecha_emision >= date(2026, 1, 1)
            ).count()
            
            print(f"✅ Registros restantes de 2026: {total_despues:,}")
            
            print("\n" + "✅" * 40)
            print("✅✅✅ ELIMINACIÓN COMPLETADA ✅✅✅")
            print("✅" * 40)
            
            print("\n📋 AHORA SIGUE ESTOS PASOS:")
            print("   1. Abre tu navegador")
            print("   2. Ve a: http://127.0.0.1:8099/dian_vs_erp/cargar_archivos")
            print("   3. Vuelve a subir el archivo: Dian.xlsx")
            print("   4. AHORA el código YA tiene el fix para leer 'fecha emisiã³n'")
            print("   5. Las fechas se cargarán correctamente")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()

print("\n" + "=" * 80)
