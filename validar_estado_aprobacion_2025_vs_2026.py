"""
VALIDACIÓN: Estado Aprobación 2025 vs 2026
===========================================
Comparar cómo se calculan los estados entre ambos años
"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from extensions import db
from app import app
from modules.dian_vs_erp.models import MaestroDianVsErp
from sqlalchemy import func, and_, extract
from datetime import datetime

with app.app_context():
    print("=" * 100)
    print("VALIDACIÓN: Estado Aprobación 2025 vs 2026")
    print("=" * 100)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # ============================================================================
    # DISTRIBUCIÓN POR AÑO
    # ============================================================================
    print("📊 DISTRIBUCIÓN DE ESTADOS POR AÑO")
    print("-" * 100)
    
    # Datos de 2025
    print("\n▶ AÑO 2025:")
    print("-" * 100)
    estados_2025 = db.session.query(
        MaestroDianVsErp.estado_aprobacion,
        func.count(MaestroDianVsErp.id).label('cantidad')
    ).filter(
        extract('year', MaestroDianVsErp.fecha_emision) == 2025
    ).group_by(
        MaestroDianVsErp.estado_aprobacion
    ).order_by(
        func.count(MaestroDianVsErp.id).desc()
    ).all()
    
    total_2025 = sum([count for _, count in estados_2025])
    print(f"Total registros 2025: {total_2025:,}")
    print("\nDistribución de estados:")
    for estado, count in estados_2025:
        porcentaje = (count / total_2025 * 100) if total_2025 > 0 else 0
        print(f"  {estado or '(NULL)':.<40} {count:>10,} registros ({porcentaje:>5.2f}%)")
    
    # Datos de 2026
    print("\n▶ AÑO 2026:")
    print("-" * 100)
    estados_2026 = db.session.query(
        MaestroDianVsErp.estado_aprobacion,
        func.count(MaestroDianVsErp.id).label('cantidad')
    ).filter(
        extract('year', MaestroDianVsErp.fecha_emision) == 2026
    ).group_by(
        MaestroDianVsErp.estado_aprobacion
    ).order_by(
        func.count(MaestroDianVsErp.id).desc()
    ).all()
    
    total_2026 = sum([count for _, count in estados_2026])
    print(f"Total registros 2026: {total_2026:,}")
    print("\nDistribución de estados:")
    for estado, count in estados_2026:
        porcentaje = (count / total_2026 * 100) if total_2026 > 0 else 0
        print(f"  {estado or '(NULL)':.<40} {count:>10,} registros ({porcentaje:>5.2f}%)")
    
    print()
    
    # ============================================================================
    # EJEMPLOS ESPECÍFICOS DE CADA AÑO
    # ============================================================================
    print("📋 EJEMPLOS DE REGISTROS - FEBRERO 2025 vs ENERO 2026")
    print("-" * 100)
    
    # Febrero 2025 (lo que muestra la imagen)
    print("\n▶ FEBRERO 2025 (primeros 10 registros):")
    print("-" * 100)
    ejemplos_feb_2025 = MaestroDianVsErp.query.filter(
        and_(
            extract('year', MaestroDianVsErp.fecha_emision) == 2025,
            extract('month', MaestroDianVsErp.fecha_emision) == 2
        )
    ).limit(10).all()
    
    for reg in ejemplos_feb_2025:
        print(f"NIT: {reg.nit_emisor} | {reg.prefijo}-{reg.folio}")
        print(f"  Fecha: {reg.fecha_emision} | Razón: {reg.razon_social}")
        print(f"  Estado Aprobación: '{reg.estado_aprobacion}' | Acuses: {reg.acuses_recibidos}")
        print(f"  Estado Contable: '{reg.estado_contable}' | Módulo: {reg.modulo}")
        print(f"  CUFE: {reg.cufe[:50] if reg.cufe else 'Sin CUFE'}...")
        print()
    
    # Enero 2026
    print("\n▶ ENERO 2026 (primeros 10 registros):")
    print("-" * 100)
    ejemplos_ene_2026 = MaestroDianVsErp.query.filter(
        and_(
            extract('year', MaestroDianVsErp.fecha_emision) == 2026,
            extract('month', MaestroDianVsErp.fecha_emision) == 1
        )
    ).limit(10).all()
    
    for reg in ejemplos_ene_2026:
        print(f"NIT: {reg.nit_emisor} | {reg.prefijo}-{reg.folio}")
        print(f"  Fecha: {reg.fecha_emision} | Razón: {reg.razon_social}")
        print(f"  Estado Aprobación: '{reg.estado_aprobacion}' | Acuses: {reg.acuses_recibidos}")
        print(f"  Estado Contable: '{reg.estado_contable}' | Módulo: {reg.modulo}")
        print(f"  CUFE: {reg.cufe[:50] if reg.cufe else 'Sin CUFE'}...")
        print()
    
    # ============================================================================
    # BUSCAR PATRONES ESPECÍFICOS
    # ============================================================================
    print("🔍 ANÁLISIS DE PATRONES SOSPECHOSOS")
    print("-" * 100)
    
    # Contar registros con estado 'Pendiente' por año
    pendientes_2025 = MaestroDianVsErp.query.filter(
        and_(
            extract('year', MaestroDianVsErp.fecha_emision) == 2025,
            MaestroDianVsErp.estado_aprobacion == 'Pendiente'
        )
    ).count()
    
    pendientes_2026 = MaestroDianVsErp.query.filter(
        and_(
            extract('year', MaestroDianVsErp.fecha_emision) == 2026,
            MaestroDianVsErp.estado_aprobacion == 'Pendiente'
        )
    ).count()
    
    print(f"\nRegistros con estado 'Pendiente':")
    print(f"  2025: {pendientes_2025:,} de {total_2025:,} ({pendientes_2025/total_2025*100:.2f}%)")
    print(f"  2026: {pendientes_2026:,} de {total_2026:,} ({pendientes_2026/total_2026*100:.2f}%)")
    
    # Contar registros SIN CUFE (lo que causaría estado 'Pendiente')
    sin_cufe_2025 = MaestroDianVsErp.query.filter(
        and_(
            extract('year', MaestroDianVsErp.fecha_emision) == 2025,
            (MaestroDianVsErp.cufe == None) | (MaestroDianVsErp.cufe == '')
        )
    ).count()
    
    sin_cufe_2026 = MaestroDianVsErp.query.filter(
        and_(
            extract('year', MaestroDianVsErp.fecha_emision) == 2026,
            (MaestroDianVsErp.cufe == None) | (MaestroDianVsErp.cufe == '')
        )
    ).count()
    
    print(f"\nRegistros SIN CUFE (deberían ser 'Pendiente'):")
    print(f"  2025: {sin_cufe_2025:,} de {total_2025:,} ({sin_cufe_2025/total_2025*100:.2f}%)")
    print(f"  2026: {sin_cufe_2026:,} de {total_2026:,} ({sin_cufe_2026/total_2026*100:.2f}%)")
    
    # Buscar registros con CUFE pero estado 'Pendiente' (sospechoso)
    print(f"\nRegistros CON CUFE pero estado='Pendiente' (POSIBLE ERROR):")
    con_cufe_pendiente_2025 = MaestroDianVsErp.query.filter(
        and_(
            extract('year', MaestroDianVsErp.fecha_emision) == 2025,
            MaestroDianVsErp.estado_aprobacion == 'Pendiente',
            MaestroDianVsErp.cufe != None,
            MaestroDianVsErp.cufe != ''
        )
    ).count()
    
    con_cufe_pendiente_2026 = MaestroDianVsErp.query.filter(
        and_(
            extract('year', MaestroDianVsErp.fecha_emision) == 2026,
            MaestroDianVsErp.estado_aprobacion == 'Pendiente',
            MaestroDianVsErp.cufe != None,
            MaestroDianVsErp.cufe != ''
        )
    ).count()
    
    print(f"  2025: {con_cufe_pendiente_2025:,} registros ⚠️")
    print(f"  2026: {con_cufe_pendiente_2026:,} registros ⚠️")
    
    # Si hay muchos con CUFE pero pendientes, mostrar ejemplos
    if con_cufe_pendiente_2026 > 0:
        print("\n  Ejemplos 2026 con CUFE pero 'Pendiente':")
        ejemplos_mal = MaestroDianVsErp.query.filter(
            and_(
                extract('year', MaestroDianVsErp.fecha_emision) == 2026,
                MaestroDianVsErp.estado_aprobacion == 'Pendiente',
                MaestroDianVsErp.cufe != None,
                MaestroDianVsErp.cufe != ''
            )
        ).limit(5).all()
        
        for reg in ejemplos_mal:
            print(f"    {reg.nit_emisor} | {reg.prefijo}-{reg.folio} | Fecha: {reg.fecha_emision}")
            print(f"      Estado: '{reg.estado_aprobacion}' pero tiene CUFE: {reg.cufe[:40]}...")
            print()
    
    print()
    
    # ============================================================================
    # RESUMEN Y DIAGNÓSTICO
    # ============================================================================
    print("=" * 100)
    print("📊 RESUMEN DEL ANÁLISIS")
    print("=" * 100)
    print(f"Total 2025: {total_2025:,} registros")
    print(f"Total 2026: {total_2026:,} registros")
    print()
    
    # Comparar porcentajes de 'Pendiente'
    porc_pend_2025 = (pendientes_2025/total_2025*100) if total_2025 > 0 else 0
    porc_pend_2026 = (pendientes_2026/total_2026*100) if total_2026 > 0 else 0
    
    if abs(porc_pend_2025 - porc_pend_2026) > 10:
        print("⚠️ ALERTA: Diferencia significativa en porcentaje de 'Pendiente'")
        print(f"   2025: {porc_pend_2025:.2f}% pendientes")
        print(f"   2026: {porc_pend_2026:.2f}% pendientes")
        print(f"   Diferencia: {abs(porc_pend_2025 - porc_pend_2026):.2f} puntos porcentuales")
        print()
    
    # Verificar si hay incoherencia entre CUFE y estado
    if con_cufe_pendiente_2026 > total_2026 * 0.10:  # Más del 10%
        print("❌ PROBLEMA DETECTADO: Muchos registros 2026 tienen CUFE pero estado 'Pendiente'")
        print(f"   Esto indica que el archivo de ACUSES 2026 NO se está procesando correctamente")
        print(f"   {con_cufe_pendiente_2026:,} registros ({con_cufe_pendiente_2026/total_2026*100:.2f}%) afectados")
        print()
    
    if con_cufe_pendiente_2025 < total_2025 * 0.05:  # Menos del 5%
        print("✅ 2025 CORRECTO: Pocos registros con CUFE y estado 'Pendiente'")
        print(f"   Solo {con_cufe_pendiente_2025:,} registros ({con_cufe_pendiente_2025/total_2025*100:.2f}%)")
        print()
    
    print("=" * 100)
