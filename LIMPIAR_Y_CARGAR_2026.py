"""
Script para LIMPIAR la tabla maestro_dian_vs_erp y cargar SOLO el archivo actual (febrero 2026)
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar Flask
os.environ['FLASK_ENV'] = 'development'

from app import app, db
from modules.dian_vs_erp.models import MaestroDianVsErp
from modules.dian_vs_erp.routes import actualizar_maestro
from datetime import datetime

def main():
    with app.app_context():
        print("=" * 80)
        print("🗑️  LIMPIANDO TABLA maestro_dian_vs_erp")
        print("=" * 80)
        
        # 1. Contar registros actuales
        total_antes = MaestroDianVsErp.query.count()
        print(f"\n📊 Registros actuales: {total_antes:,}")
        
        if total_antes == 0:
            print("\n✅ La tabla ya está vacía")
        else:
            # Confirmar eliminación
            print(f"\n⚠️  Se eliminarán {total_antes:,} registros")
            print("   Esto incluye todos los datos históricos de 2025")
            print("   Solo quedarán los datos del archivo actual (2026)")
            
            # 2. ELIMINAR TODO
            print("\n🗑️  Eliminando...")
            try:
                MaestroDianVsErp.query.delete()
                db.session.commit()
                print(f"✅ Eliminados: {total_antes:,} registros")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error eliminando: {e}")
                return
        
        # 3. Verificar que quedó vacía
        total_despues = MaestroDianVsErp.query.count()
        print(f"✅ Registros restantes: {total_despues:,}")
        
        print("\n" + "=" * 80)
        print("🔄 CARGANDO ARCHIVO ACTUAL CON FIX DE FECHA")
        print("=" * 80)
        
        # 4. Ejecutar actualizar_maestro() que tiene el fix de formato de fecha
        try:
            print("\n⚙️  Iniciando carga...")
            print("   Archivo: uploads/dian/Dian_bc63e290ca.csv")
            print("   Con fix: día-mes-año (14-02-2026)")
            
            inicio = datetime.now()
            
            # Esta función ya tiene el fix de formato de fecha día-mes-año
            resultado = actualizar_maestro()
            
            fin = datetime.now()
            duracion = (fin - inicio).total_seconds()
            
            # 5. Contar registros nuevos
            total_final = MaestroDianVsErp.query.count()
            
            print("\n" + "=" * 80)
            print("✅✅✅ CARGA COMPLETADA ✅✅✅")
            print("=" * 80)
            
            print(f"\n📊 RESULTADO:")
            print(f"   • Registros cargados: {total_final:,}")
            print(f"   • Tiempo: {duracion:.1f}s")
            print(f"   • Velocidad: {total_final/duracion:.0f} registros/segundo")
            
            # 6. Verificar distribución de fechas
            print(f"\n📅 VERIFICANDO FECHAS CARGADAS:")
            from sqlalchemy import func
            fechas = db.session.query(
                MaestroDianVsErp.fecha_emision,
                func.count(MaestroDianVsErp.id).label('cantidad')
            ).group_by(MaestroDianVsErp.fecha_emision).order_by(func.count(MaestroDianVsErp.id).desc()).limit(10).all()
            
            for fecha, cantidad in fechas:
                print(f"   • {fecha}: {cantidad:,} registros")
            
            # 7. Contar específicamente fechas de 2026
            from datetime import date
            registros_2026 = MaestroDianVsErp.query.filter(
                MaestroDianVsErp.fecha_emision >= date(2026, 1, 1)
            ).count()
            
            porcentaje = (registros_2026 / total_final * 100) if total_final > 0 else 0
            
            print(f"\n✅ REGISTROS DE 2026: {registros_2026:,} ({porcentaje:.1f}%)")
            
            if registros_2026 > 0:
                print("\n🎉 ¡ÉXITO! Las fechas de 2026 están en la base de datos")
                print("   Ahora haz HARD REFRESH en el navegador:")
                print("   → Ctrl + Shift + R (Chrome/Edge)")
                print("   → http://127.0.0.1:8099/dian_vs_erp/visor_v2")
            else:
                print("\n⚠️  No se cargaron fechas de 2026")
                print("   Revisa el CSV y el código de parseo")
            
        except Exception as e:
            print(f"\n❌ Error durante la carga: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\nPresiona ENTER para salir...")
