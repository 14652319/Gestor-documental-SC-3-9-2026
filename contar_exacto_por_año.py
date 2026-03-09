"""
CONTAR REGISTROS EXACTOS POR AÑO
=================================
"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from extensions import db
from app import app
from modules.dian_vs_erp.models import MaestroDianVsErp
from sqlalchemy import extract, func
from datetime import datetime

with app.app_context():
    print("=" * 100)
    print("CONTEO EXACTO DE REGISTROS POR AÑO")
    print("=" * 100)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Contar por año
    resultados = db.session.query(
        extract('year', MaestroDianVsErp.fecha_emision).label('año'),
        func.count(MaestroDianVsErp.id).label('cantidad')
    ).group_by(
        extract('year', MaestroDianVsErp.fecha_emision)
    ).order_by(
        extract('year', MaestroDianVsErp.fecha_emision)
    ).all()
    
    print("DISTRIBUCIÓN POR AÑO:")
    print("-" * 100)
    
    total_general = 0
    for año, cantidad in resultados:
        print(f"  Año {int(año) if año else 'NULL':>4}: {cantidad:>12,} registros")
        if año:
            total_general += cantidad
    
    print("-" * 100)
    print(f"  TOTAL:       {total_general:>12,} registros")
    print()
    
    # Desglose por año y mes para 2025 y 2026
    print("DESGLOSE POR MES:")
    print("-" * 100)
    
    for año_check in [2025, 2026]:
        print(f"\n▶ AÑO {año_check}:")
        meses = db.session.query(
            extract('month', MaestroDianVsErp.fecha_emision).label('mes'),
            func.count(MaestroDianVsErp.id).label('cantidad')
        ).filter(
            extract('year', MaestroDianVsErp.fecha_emision) == año_check
        ).group_by(
            extract('month', MaestroDianVsErp.fecha_emision)
        ).order_by(
            extract('month', MaestroDianVsErp.fecha_emision)
        ).all()
        
        total_año = 0
        meses_nombres = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        for mes, cantidad in meses:
            mes_nombre = meses_nombres[int(mes)] if mes and mes <= 12 else 'Desconocido'
            print(f"  {mes_nombre:.<20} {cantidad:>12,} registros")
            total_año += cantidad
        
        print(f"  {'TOTAL':.<20} {total_año:>12,} registros")
    
    print()
    print("=" * 100)
