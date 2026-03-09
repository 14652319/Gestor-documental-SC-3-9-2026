"""
VERIFICAR INTEGRIDAD DE DATOS 2025
===================================
Confirmar que hay datos desde enero hasta diciembre 2025
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
    print("VERIFICACIÓN DE INTEGRIDAD - AÑO 2025 COMPLETO")
    print("=" * 100)
    print(f"Fecha de verificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Obtener rango completo de fechas para 2025
    rango = db.session.query(
        func.min(MaestroDianVsErp.fecha_emision).label('primera_fecha'),
        func.max(MaestroDianVsErp.fecha_emision).label('ultima_fecha'),
        func.count(MaestroDianVsErp.id).label('total')
    ).filter(
        extract('year', MaestroDianVsErp.fecha_emision) == 2025
    ).first()
    
    print("📅 RANGO DE FECHAS 2025:")
    print("-" * 100)
    print(f"  Primera fecha: {rango.primera_fecha.strftime('%d/%m/%Y')}")
    print(f"  Última fecha:  {rango.ultima_fecha.strftime('%d/%m/%Y')}")
    print(f"  Total:         {rango.total:,} registros")
    print()
    
    # Verificar si hay fechas fuera de 2025
    fuera_rango = db.session.query(
        func.count(MaestroDianVsErp.id)
    ).filter(
        extract('year', MaestroDianVsErp.fecha_emision) == 2025,
        (MaestroDianVsErp.fecha_emision < datetime(2025, 1, 1)) | 
        (MaestroDianVsErp.fecha_emision >= datetime(2026, 1, 1))
    ).scalar()
    
    if fuera_rango > 0:
        print(f"⚠️  ADVERTENCIA: {fuera_rango} registros con año 2025 pero fecha fuera de rango")
    else:
        print("✅ Todas las fechas están dentro del rango 01/01/2025 - 31/12/2025")
    print()
    
    # Desglose por mes con fechas
    print("📊 DESGLOSE MENSUAL CON RANGOS DE FECHAS:")
    print("-" * 100)
    
    meses_nombres = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    meses_esperados = set(range(1, 13))  # 1 a 12
    meses_encontrados = set()
    
    for mes_num in range(1, 13):
        resultado = db.session.query(
            func.count(MaestroDianVsErp.id).label('cantidad'),
            func.min(MaestroDianVsErp.fecha_emision).label('primera'),
            func.max(MaestroDianVsErp.fecha_emision).label('ultima')
        ).filter(
            extract('year', MaestroDianVsErp.fecha_emision) == 2025,
            extract('month', MaestroDianVsErp.fecha_emision) == mes_num
        ).first()
        
        if resultado.cantidad > 0:
            meses_encontrados.add(mes_num)
            print(f"  {meses_nombres[mes_num]:.<15} {resultado.cantidad:>10,} registros "
                  f"│ {resultado.primera.strftime('%d/%m/%Y')} → {resultado.ultima.strftime('%d/%m/%Y')}")
        else:
            print(f"  {meses_nombres[mes_num]:.<15} {'❌ SIN DATOS':>10}")
    
    print("-" * 100)
    print(f"  {'TOTAL 2025':.<15} {rango.total:>10,} registros")
    print()
    
    # Verificar completitud
    print("🔍 VERIFICACIÓN DE COMPLETITUD:")
    print("-" * 100)
    
    meses_faltantes = meses_esperados - meses_encontrados
    
    if not meses_faltantes:
        print("  ✅ CONFIRMADO: Hay datos en TODOS los meses de 2025 (Enero - Diciembre)")
    else:
        print(f"  ⚠️  ADVERTENCIA: Faltan datos en los siguientes meses:")
        for mes in sorted(meses_faltantes):
            print(f"     - {meses_nombres[mes]}")
    
    print()
    
    # Verificar cobertura de días
    dias_con_datos = db.session.query(
        func.count(func.distinct(func.date(MaestroDianVsErp.fecha_emision)))
    ).filter(
        extract('year', MaestroDianVsErp.fecha_emision) == 2025
    ).scalar()
    
    print(f"  📆 Días diferentes con datos: {dias_con_datos} de 365 días posibles en 2025")
    print(f"  📊 Cobertura: {(dias_con_datos/365*100):.1f}%")
    print()
    
    # Top 5 días con más registros
    print("🔝 TOP 5 DÍAS CON MÁS REGISTROS:")
    print("-" * 100)
    
    top_dias = db.session.query(
        func.date(MaestroDianVsErp.fecha_emision).label('fecha'),
        func.count(MaestroDianVsErp.id).label('cantidad')
    ).filter(
        extract('year', MaestroDianVsErp.fecha_emision) == 2025
    ).group_by(
        func.date(MaestroDianVsErp.fecha_emision)
    ).order_by(
        func.count(MaestroDianVsErp.id).desc()
    ).limit(5).all()
    
    for i, (fecha, cantidad) in enumerate(top_dias, 1):
        print(f"  {i}. {fecha.strftime('%d/%m/%Y')} → {cantidad:,} registros")
    
    print()
    print("=" * 100)
    print("✅ VERIFICACIÓN COMPLETA")
    print("=" * 100)
