"""
Ver qué fechas están actualmente en maestro_dian_vs_erp
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from extensions import db
from modules.dian_vs_erp.models import MaestroDianVsErp
from app import app

with app.app_context():
    # Contar registros por fecha
    from sqlalchemy import func
    
    resultado = db.session.query(
        MaestroDianVsErp.fecha_emision,
        func.count(MaestroDianVsErp.id).label('registros')
    ).group_by(
        MaestroDianVsErp.fecha_emision
    ).order_by(
        func.count(MaestroDianVsErp.id).desc()
    ).limit(20).all()
    
    print("\n" + "="*80)
    print("📅 FECHAS EN TABLA maestro_dian_vs_erp")
    print("="*80)
    
    if not resultado:
        print("⚠️  TABLA VACÍA - No hay registros")
    else:
        print(f"\n{'FECHA':<15} | {'REGISTROS':>10}")
        print("-"*30)
        for fecha, cantidad in resultado:
            print(f"{str(fecha) if fecha else 'NULL':<15} | {cantidad:>10,}")
        
        # Total
        total = db.session.query(func.count(MaestroDianVsErp.id)).scalar()
        print("-"*30)
        print(f"{'TOTAL':<15} | {total:>10,}")
    
    print("="*80)
