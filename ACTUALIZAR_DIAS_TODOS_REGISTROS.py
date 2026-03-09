"""
ACTUALIZAR DÍAS DESDE EMISIÓN - TODOS LOS REGISTROS
Script para calcular días desde emisión en registros antiguos
Fecha: 30 de Diciembre de 2025
"""

import sys
sys.path.insert(0, '.')

from extensions import db
from flask import Flask
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gestor_user:Gestor2024$@localhost/gestor_documental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    print("=" * 80)
    print("📅 ACTUALIZANDO DÍAS DESDE EMISIÓN PARA TODOS LOS REGISTROS")
    print("=" * 80)
    
    try:
        fecha_hoy = date.today()
        print(f"📆 Fecha de hoy: {fecha_hoy}")
        
        # 1. Contar cuántos registros necesitan actualización
        resultado_count = db.session.execute(
            db.text("""
                SELECT COUNT(*) 
                FROM maestro_dian_vs_erp
                WHERE fecha_emision IS NOT NULL
                  AND (dias_desde_emision IS NULL OR dias_desde_emision = 0)
            """)
        )
        pendientes = resultado_count.scalar()
        print(f"📊 Registros con días pendientes: {pendientes:,}")
        
        if pendientes == 0:
            print("✅ Todos los registros ya tienen días calculados")
        else:
            # 2. Actualizar días desde emisión
            print("\n🔄 Actualizando días desde emisión...")
            resultado_update = db.session.execute(
                db.text("""
                    UPDATE maestro_dian_vs_erp
                    SET dias_desde_emision = (:fecha_hoy - fecha_emision)
                    WHERE fecha_emision IS NOT NULL
                      AND (dias_desde_emision IS NULL OR dias_desde_emision = 0)
                """),
                {'fecha_hoy': fecha_hoy}
            )
            db.session.commit()
            print(f"✅ {resultado_update.rowcount:,} registros actualizados")
        
        # 3. Mostrar estadísticas por rango de días
        print("\n" + "=" * 80)
        print("📈 ESTADÍSTICAS POR RANGO DE DÍAS")
        print("=" * 80)
        
        resultado_stats = db.session.execute(
            db.text("""
                SELECT 
                    CASE 
                        WHEN dias_desde_emision <= 30 THEN '0-30 días'
                        WHEN dias_desde_emision <= 60 THEN '31-60 días'
                        WHEN dias_desde_emision <= 90 THEN '61-90 días'
                        WHEN dias_desde_emision <= 180 THEN '91-180 días'
                        ELSE 'Más de 180 días'
                    END AS rango,
                    COUNT(*) as cantidad
                FROM maestro_dian_vs_erp
                WHERE dias_desde_emision IS NOT NULL
                GROUP BY rango
                ORDER BY 
                    CASE rango
                        WHEN '0-30 días' THEN 1
                        WHEN '31-60 días' THEN 2
                        WHEN '61-90 días' THEN 3
                        WHEN '91-180 días' THEN 4
                        ELSE 5
                    END
            """)
        )
        
        for rango, cantidad in resultado_stats:
            print(f"  {rango:20} {cantidad:,} registros")
        
        # 4. Mostrar registros sin fecha de emisión
        print("\n" + "=" * 80)
        print("⚠️ REGISTROS SIN FECHA DE EMISIÓN")
        print("=" * 80)
        
        resultado_sin_fecha = db.session.execute(
            db.text("""
                SELECT COUNT(*) 
                FROM maestro_dian_vs_erp
                WHERE fecha_emision IS NULL
            """)
        )
        sin_fecha = resultado_sin_fecha.scalar()
        print(f"  {sin_fecha:,} registros sin fecha (no se pueden calcular días)")
        
        print("\n" + "=" * 80)
        print("✅ PROCESO COMPLETADO")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
