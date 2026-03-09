"""
Verificar qué archivos se cargaron correctamente
"""

from app import app, db
from modules.dian_vs_erp.models import MaestroDianVsErp
from sqlalchemy import func
from datetime import datetime, timedelta

with app.app_context():
    print("\n" + "="*80)
    print("📊 VERIFICACIÓN DE CARGA COMPLETA - DIAN vs ERP")
    print("="*80 + "\n")
    
    # Fecha de hoy y últimos 7 días
    hoy = datetime.now().date()
    hace_7_dias = hoy - timedelta(days=7)
    
    print(f"🗓️  Rango de fechas: {hace_7_dias} a {hoy}\n")
    
    # 1. Total de registros por mes en 2026
    print("📅 REGISTROS POR MES EN 2026:")
    print("-" * 80)
    
    meses_2026 = db.session.query(
        func.date_trunc('month', MaestroDianVsErp.fecha_emision).label('mes'),
        func.count(MaestroDianVsErp.id).label('total')
    ).filter(
        MaestroDianVsErp.fecha_emision >= '2026-01-01',
        MaestroDianVsErp.fecha_emision <= '2026-12-31'
    ).group_by('mes').order_by('mes').all()
    
    for mes, total in meses_2026:
        print(f"   {mes.strftime('%Y-%m')}: {total:>10,} registros")
    
    # 2. Registros de las últimas 24 horas
    print(f"\n\n⏰ REGISTROS DE LAS ÚLTIMAS 24 HORAS:")
    print("-" * 80)
    
    hace_24h = datetime.now() - timedelta(hours=24)
    
    registros_24h = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.fecha_registro >= hace_24h
    ).count()
    
    print(f"   Total registros nuevos: {registros_24h:,}")
    
    if registros_24h > 0:
        # Desglose por tipo de documento
        print(f"\n   📋 Desglose por tipo de documento:")
        tipos_nuevos = db.session.query(
            MaestroDianVsErp.tipo_documento,
            func.count(MaestroDianVsErp.id)
        ).filter(
            MaestroDianVsErp.fecha_registro >= hace_24h
        ).group_by(MaestroDianVsErp.tipo_documento).all()
        
        for tipo, count in tipos_nuevos:
            tipo_display = tipo if tipo and tipo != 'None' else "(Sin tipo)"
            print(f"      {tipo_display:30s}: {count:>8,} registros")
        
        # Desglose por módulo
        print(f"\n   📦 Desglose por módulo (si aplica):")
        modulos_nuevos = db.session.query(
            MaestroDianVsErp.modulo,
            func.count(MaestroDianVsErp.id)
        ).filter(
            MaestroDianVsErp.fecha_registro >= hace_24h
        ).group_by(MaestroDianVsErp.modulo).all()
        
        for modulo, count in modulos_nuevos:
            modulo_display = modulo if modulo and modulo != 'None' else "(Sin módulo)"
            print(f"      {modulo_display:30s}: {count:>8,} registros")
    
    # 3. Verificar si hay registros con causación reciente
    print(f"\n\n✅ REGISTROS CAUSADOS (ÚLTIMAS 24H):")
    print("-" * 80)
    
    causados_24h = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.fecha_causacion >= hace_24h
    ).count()
    
    print(f"   Total causados: {causados_24h:,}")
    
    # 4. Verificar distribución de estados
    print(f"\n\n📈 ESTADOS DE APROBACIÓN (ÚLTIMAS 24H):")
    print("-" * 80)
    
    estados_nuevos = db.session.query(
        MaestroDianVsErp.estado_aprobacion,
        func.count(MaestroDianVsErp.id)
    ).filter(
        MaestroDianVsErp.fecha_registro >= hace_24h
    ).group_by(MaestroDianVsErp.estado_aprobacion).all()
    
    for estado, count in estados_nuevos:
        estado_display = estado if estado and estado != 'None' else "(Sin estado)"
        print(f"   {estado_display:40s}: {count:>8,} registros")
    
    # 5. Verificar últimos 10 registros insertados
    print(f"\n\n📄 ÚLTIMOS 10 REGISTROS INSERTADOS:")
    print("-" * 80)
    
    ultimos = MaestroDianVsErp.query.order_by(
        MaestroDianVsErp.fecha_registro.desc()
    ).limit(10).all()
    
    print(f"\n{'Fecha Reg':<20} | {'Fecha Emisión':<12} | {'NIT':<15} | {'Prefijo-Folio':<20} | {'Causada'}")
    print("-" * 100)
    
    for reg in ultimos:
        fecha_reg = reg.fecha_registro.strftime('%Y-%m-%d %H:%M:%S') if reg.fecha_registro else 'N/A'
        fecha_em = reg.fecha_emision.strftime('%Y-%m-%d') if reg.fecha_emision else 'N/A'
        causada_mark = "✅" if reg.causada else "❌"
        print(f"{fecha_reg:<20} | {fecha_em:<12} | {reg.nit_emisor:<15} | {reg.prefijo}-{reg.folio:<20} | {causada_mark}")
    
    # 6. RESUMEN FINAL
    print(f"\n\n" + "="*80)
    print("📊 RESUMEN FINAL DE LA CARGA")
    print("="*80 + "\n")
    
    print(f"✅ Total registros en BD: {MaestroDianVsErp.query.count():,}")
    print(f"✅ Registros 2026: {MaestroDianVsErp.query.filter(MaestroDianVsErp.fecha_emision >= '2026-01-01').count():,}")
    print(f"✅ Registros nuevos (24h): {registros_24h:,}")
    print(f"✅ Causados (24h): {causados_24h:,}")
    
    # Verificar si hay datos de ERP
    con_modulo = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.modulo != None,
        MaestroDianVsErp.modulo != '',
        MaestroDianVsErp.modulo != 'None'
    ).count()
    
    print(f"\n🏢 Registros con módulo ERP detectado: {con_modulo:,}")
    
    if registros_24h > 0:
        if con_modulo > 0:
            print("\n✅ CARGA EXITOSA: Se detectaron archivos DIAN + ERP + Acuses")
        else:
            print("\n⚠️  CARGA PARCIAL: Solo se cargó DIAN (sin archivos ERP)")
    else:
        print("\n❌ NO HAY CARGA RECIENTE - Los archivos no se procesaron en las últimas 24h")

print("\n" + "="*80 + "\n")
