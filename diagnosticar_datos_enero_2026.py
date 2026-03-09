"""
Script para diagnosticar datos faltantes de enero 2026
"""

from app import app, db
from modules.dian_vs_erp.models import MaestroDianVsErp
from sqlalchemy import func

with app.app_context():
    print("\n" + "="*80)
    print("🔍 DIAGNÓSTICO DE DATOS - ENERO 2026")
    print("="*80 + "\n")
    
    # 1. Contar registros de enero 2026
    total = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.fecha_emision >= '2026-01-01',
        MaestroDianVsErp.fecha_emision <= '2026-01-31'
    ).count()
    
    print(f"📊 Total registros enero 2026: {total}")
    
    # 2. Contar registros con razón social NULL
    sin_razon_social = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.fecha_emision >= '2026-01-01',
        MaestroDianVsErp.fecha_emision <= '2026-01-31',
        db.or_(
            MaestroDianVsErp.razon_social == None,
            MaestroDianVsErp.razon_social == ''
        )
    ).count()
    
    print(f"❌ Sin razón social: {sin_razon_social} ({sin_razon_social*100/total:.1f}%)")
    
    # 3. Contar registros con tipo_tercero NULL
    sin_tipo_tercero = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.fecha_emision >= '2026-01-01',
        MaestroDianVsErp.fecha_emision <= '2026-01-31',
        db.or_(
            MaestroDianVsErp.tipo_tercero == None,
            MaestroDianVsErp.tipo_tercero == ''
        )
    ).count()
    
    print(f"❌ Sin tipo tercero: {sin_tipo_tercero} ({sin_tipo_tercero*100/total:.1f}%)")
    
    # 4. Contar registros con tipo_documento NULL
    sin_tipo_documento = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.fecha_emision >= '2026-01-01',
        MaestroDianVsErp.fecha_emision <= '2026-01-31',
        db.or_(
            MaestroDianVsErp.tipo_documento == None,
            MaestroDianVsErp.tipo_documento == ''
        )
    ).count()
    
    print(f"❌ Sin tipo documento: {sin_tipo_documento} ({sin_tipo_documento*100/total:.1f}%)")
    
    # 5. Ver distribución de doc_causado_por
    print(f"\n📋 Distribución de doc_causado_por:")
    result = db.session.query(
        MaestroDianVsErp.doc_causado_por,
        func.count(MaestroDianVsErp.id)
    ).filter(
        MaestroDianVsErp.fecha_emision >= '2026-01-01',
        MaestroDianVsErp.fecha_emision <= '2026-01-31'
    ).group_by(MaestroDianVsErp.doc_causado_por).all()
    
    for causador, count in result:
        causador_display = causador if causador else "(NULL)"
        porcentaje = count * 100 / total
        print(f"   {causador_display:30s}: {count:5} registros ({porcentaje:.1f}%)")
    
    # 6. Mostrar 5 ejemplos de registros
    print(f"\n📄 Primeros 5 registros de enero 2026:")
    ejemplos = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.fecha_emision >= '2026-01-01',
        MaestroDianVsErp.fecha_emision <= '2026-01-31'
    ).limit(5).all()
    
    print(f"\n{'NIT':<15} | {'Razón Social':<40} | {'Tipo Tercero':<20} | {'Tipo Doc':<20} | Causador")
    print("-" * 140)
    for reg in ejemplos:
        print(f"{reg.nit_emisor or '(NULL)':<15} | "
              f"{(reg.razon_social or '(NULL)')[:40]:<40} | "
              f"{(reg.tipo_tercero or '(NULL)'):<20} | "
              f"{(reg.tipo_documento or '(NULL)'):<20} | "
              f"{reg.doc_causado_por or '(NULL)'}")
    
    # 7. Comparar con febrero 2026
    print(f"\n\n" + "="*80)
    print("📊 COMPARACIÓN CON FEBRERO 2026")
    print("="*80 + "\n")
    
    total_feb = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.fecha_emision >= '2026-02-01',
        MaestroDianVsErp.fecha_emision <= '2026-02-28'
    ).count()
    
    sin_razon_feb = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.fecha_emision >= '2026-02-01',
        MaestroDianVsErp.fecha_emision <= '2026-02-28',
        db.or_(
            MaestroDianVsErp.razon_social == None,
            MaestroDianVsErp.razon_social == ''
        )
    ).count()
    
    print(f"📊 Total registros febrero 2026: {total_feb}")
    if total_feb > 0:
        print(f"❌ Sin razón social: {sin_razon_feb} ({sin_razon_feb*100/total_feb:.1f}%)")
    else:
        print(f"❌ Sin razón social: 0 (0%)")
    
print("\n" + "="*80 + "\n")
print("✅ Diagnóstico completado")
