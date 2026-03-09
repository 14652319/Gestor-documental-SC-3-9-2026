"""
VERIFICAR PROCESAMIENTO DE ACUSES
==================================
Revisar si los acuses de 2026 se cargaron correctamente
"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from extensions import db
from app import app
from modules.dian_vs_erp.models import MaestroDianVsErp
from sqlalchemy import func, and_, extract, or_
from datetime import datetime

with app.app_context():
    print("=" * 100)
    print("VERIFICACIÓN: Procesamiento de Acuses 2026")
    print("=" * 100)
    print()
    
    # ============================================================================
    # BUSCAR REGISTROS CON ESTADOS DE ACUSES EN 2026
    # ============================================================================
    print("🔍 BUSCAR REGISTROS 2026 QUE TENGAN ESTADOS DE ACUSES")
    print("-" * 100)
    
    # Estados que SOLO vienen de acuses (no son 'Pendiente')
    estados_de_acuses = [
        'Acuse Recibido',
        'Acuse Bien/Servicio',
        'Rechazada',
        'Aceptación Expresa',
        'Aceptación Tácita',
        'Aprobación Expresa',  # variantes
        'Aprobación Tácita',
        'Aceptacion Expresa',  # sin tilde
        'Aceptacion Tacita'
    ]
    
    for estado in estados_de_acuses:
        count = MaestroDianVsErp.query.filter(
            and_(
                extract('year', MaestroDianVsErp.fecha_emision) == 2026,
                MaestroDianVsErp.estado_aprobacion == estado
            )
        ).count()
        
        if count > 0:
            print(f"  ✅ '{estado}': {count:,} registros")
        else:
            print(f"  ❌ '{estado}': 0 registros")
    
    print()
    
    # ============================================================================
    # VERIFICAR SI HAY CUFES DUPLICADOS ENTRE 2025 Y 2026
    # ============================================================================
    print("🔍 VERIFICAR CUFES DUPLICADOS ENTRE AÑOS")
    print("-" * 100)
    
    # Tomar 10 CUFEs de 2025 que SÍ tienen acuse
    cufes_2025_con_acuse = MaestroDianVsErp.query.filter(
        and_(
            extract('year', MaestroDianVsErp.fecha_emision) == 2025,
            MaestroDianVsErp.estado_aprobacion != 'Pendiente',
            MaestroDianVsErp.cufe != None,
            MaestroDianVsErp.cufe != ''
        )
    ).limit(10).all()
    
    print(f"\n10 CUFEs de 2025 que SÍ tienen acuse:")
    for reg in cufes_2025_con_acuse:
        print(f"  {reg.cufe[:50]}... → Estado: '{reg.estado_aprobacion}'")
    
    # Tomar 10 CUFEs de 2026
    cufes_2026 = MaestroDianVsErp.query.filter(
        and_(
            extract('year', MaestroDianVsErp.fecha_emision) == 2026,
            MaestroDianVsErp.cufe != None,
            MaestroDianVsErp.cufe != ''
        )
    ).limit(10).all()
    
    print(f"\n10 CUFEs de 2026 (todos Pendiente):")
    for reg in cufes_2026:
        print(f"  {reg.cufe[:50]}... → Estado: '{reg.estado_aprobacion}'")
    
    print()
    
    # ============================================================================
    # BUSCAR SI HAY REGISTROS RECIENTES (ÚLTIMAS 24 HORAS)
    # ============================================================================
    print("🕐 REGISTROS DE LAS ÚLTIMAS 24 HORAS")
    print("-" * 100)
    
    # Contar por hora de inserción (no de emisión)
    from datetime import timedelta
    hace_24h = datetime.now() - timedelta(hours=24)
    
    recientes = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.fecha_actualizacion >= hace_24h
    ).count()
    
    print(f"Registros insertados/actualizados últimas 24h: {recientes:,}")
    
    if recientes > 0:
        # Ver distribución de estados en registros recientes
        print("\nDistribución de estados en registros recientes:")
        estados_recientes = db.session.query(
            MaestroDianVsErp.estado_aprobacion,
            func.count(MaestroDianVsErp.id).label('cantidad')
        ).filter(
            MaestroDianVsErp.fecha_actualizacion >= hace_24h
        ).group_by(
            MaestroDianVsErp.estado_aprobacion
        ).order_by(
            func.count(MaestroDianVsErp.id).desc()
        ).all()
        
        for estado, count in estados_recientes:
            print(f"  {estado or '(NULL)':.<40} {count:>10,} registros")
    
    print()
    
    # ============================================================================
    # ANÁLISIS DE CUFES: LONGITUD Y FORMATO
    # ============================================================================
    print("📏 ANÁLISIS DE FORMATO DE CUFES")
    print("-" * 100)
    
    # Longitud promedio de CUFEs
    cufe_2025_ejemplo = cufes_2025_con_acuse[0].cufe if cufes_2025_con_acuse else ""
    cufe_2026_ejemplo = cufes_2026[0].cufe if cufes_2026 else ""
    
    print(f"\nEjemplo CUFE 2025 (con acuse):")
    print(f"  Longitud: {len(cufe_2025_ejemplo)} caracteres")
    print(f"  Valor: {cufe_2025_ejemplo}")
    
    print(f"\nEjemplo CUFE 2026 (pendiente):")
    print(f"  Longitud: {len(cufe_2026_ejemplo)} caracteres")
    print(f"  Valor: {cufe_2026_ejemplo}")
    
    # Comparar si tienen el mismo formato
    if len(cufe_2025_ejemplo) != len(cufe_2026_ejemplo):
        print(f"\n⚠️ ALERTA: Los CUFEs tienen longitudes diferentes!")
        print(f"   2025: {len(cufe_2025_ejemplo)} chars")
        print(f"   2026: {len(cufe_2026_ejemplo)} chars")
    else:
        print(f"\n✅ Los CUFEs tienen la misma longitud: {len(cufe_2025_ejemplo)} chars")
    
    print()
    
    # ============================================================================
    # CONCLUSIÓN
    # ============================================================================
    print("=" * 100)
    print("📊 CONCLUSIÓN")
    print("=" * 100)
    
    tiene_acuses_2026 = any([
        MaestroDianVsErp.query.filter(
            and_(
                extract('year', MaestroDianVsErp.fecha_emision) == 2026,
                MaestroDianVsErp.estado_aprobacion == estado
            )
        ).count() > 0
        for estado in estados_de_acuses
    ])
    
    if not tiene_acuses_2026:
        print("❌ CONFIRMADO: NO hay ningún registro de 2026 con estados de acuses")
        print()
        print("POSIBLES CAUSAS:")
        print("  1. El archivo de ACUSES de 2026 NO se subió en la última carga")
        print("  2. El archivo de ACUSES tiene formato diferente (columnas renombradas)")
        print("  3. Los CUFEs del archivo DIAN no coinciden con los del archivo ACUSES")
        print("  4. Hay espacios o caracteres extra en los CUFEs")
        print()
        print("SOLUCIÓN:")
        print("  → Volver a subir el archivo de ACUSES de 2026")
        print("  → Asegurarse que tenga la columna 'CUFE/CUDE' correctamente nombrada")
        print("  → Verificar que los CUFEs coincidan exactamente con el archivo DIAN")
    else:
        print("✅ Hay algunos registros 2026 con acuses (investigar por qué tan pocos)")
    
    print()
    print("=" * 100)
