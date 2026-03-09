"""
Script para verificar y corregir fechas incorrectas del 2026 al 2025
en la tabla maestro_dian_vs_erp
"""
from extensions import db
from app import app
from modules.dian_vs_erp.models import MaestroDianVsErp
from datetime import datetime, date
from sqlalchemy import text

print("=" * 60)
print("🔍 DIAGNÓSTICO DE FECHAS EN MAESTRO DIAN VS ERP")
print("=" * 60)

with app.app_context():
    # 1. Contar registros por año
    registros_2026 = db.session.query(MaestroDianVsErp).filter(
        MaestroDianVsErp.fecha_emision >= date(2026, 1, 1)
    ).count()
    
    registros_2025 = db.session.query(MaestroDianVsErp).filter(
        MaestroDianVsErp.fecha_emision >= date(2025, 1, 1),
        MaestroDianVsErp.fecha_emision < date(2026, 1, 1)
    ).count()
    
    registros_anteriores = db.session.query(MaestroDianVsErp).filter(
        MaestroDianVsErp.fecha_emision < date(2025, 1, 1)
    ).count()
    
    total = db.session.query(MaestroDianVsErp).count()
    
    print(f"\n📊 RESUMEN DE FECHAS:")
    print(f"   Total de registros: {total:,}")
    print(f"   └─ Año 2026 (INCORRECTO): {registros_2026:,}")
    print(f"   └─ Año 2025: {registros_2025:,}")
    print(f"   └─ Años anteriores: {registros_anteriores:,}")
    
    if registros_2026 > 0:
        print(f"\n⚠️  PROBLEMA DETECTADO:")
        print(f"   {registros_2026:,} registros tienen fecha del 2026")
        print(f"   cuando deberían ser del 2025")
        
        # Mostrar ejemplos
        print(f"\n📋 EJEMPLOS DE REGISTROS CON FECHA INCORRECTA:")
        ejemplos = db.session.query(
            MaestroDianVsErp.nit_emisor,
            MaestroDianVsErp.razon_social,
            MaestroDianVsErp.prefijo,
            MaestroDianVsErp.folio,
            MaestroDianVsErp.fecha_emision,
            MaestroDianVsErp.valor
        ).filter(
            MaestroDianVsErp.fecha_emision >= date(2026, 1, 1)
        ).limit(5).all()
        
        for i, ej in enumerate(ejemplos, 1):
            print(f"\n   {i}. NIT: {ej.nit_emisor}")
            print(f"      Razón Social: {ej.razon_social}")
            print(f"      Prefijo-Folio: {ej.prefijo}-{ej.folio}")
            print(f"      Fecha (INCORRECTA): {ej.fecha_emision}")
            print(f"      Valor: ${float(ej.valor) if ej.valor else 0:,.2f}")
        
        # Preguntar si corregir
        print(f"\n" + "=" * 60)
        print(f"💡 SOLUCIÓN PROPUESTA:")
        print(f"=" * 60)
        print(f"   Cambiar todas las fechas del 2026 → 2025")
        print(f"   Registros afectados: {registros_2026:,}")
        print(f"\n   Método: UPDATE maestro_dian_vs_erp")
        print(f"           SET fecha_emision = fecha_emision - INTERVAL '1 year'")
        print(f"           WHERE fecha_emision >= '2026-01-01'")
        
        respuesta = input(f"\n❓ ¿Aplicar corrección? (S/N): ").strip().upper()
        
        if respuesta == 'S':
            print(f"\n🔧 Aplicando corrección...")
            try:
                # Usar SQL directo para mayor eficiencia
                sql = text("""
                    UPDATE maestro_dian_vs_erp 
                    SET fecha_emision = fecha_emision - INTERVAL '1 year'
                    WHERE fecha_emision >= '2026-01-01'
                """)
                result = db.session.execute(sql)
                db.session.commit()
                
                print(f"✅ CORRECCIÓN APLICADA EXITOSAMENTE")
                print(f"   {registros_2026:,} registros actualizados")
                
                # Verificar después de la corrección
                nuevos_2026 = db.session.query(MaestroDianVsErp).filter(
                    MaestroDianVsErp.fecha_emision >= date(2026, 1, 1)
                ).count()
                
                nuevos_2025 = db.session.query(MaestroDianVsErp).filter(
                    MaestroDianVsErp.fecha_emision >= date(2025, 1, 1),
                    MaestroDianVsErp.fecha_emision < date(2026, 1, 1)
                ).count()
                
                print(f"\n📊 DESPUÉS DE LA CORRECCIÓN:")
                print(f"   Año 2026: {nuevos_2026:,} (debería ser 0)")
                print(f"   Año 2025: {nuevos_2025:,}")
                
            except Exception as e:
                print(f"❌ ERROR al aplicar corrección: {e}")
                db.session.rollback()
        else:
            print(f"\n⚠️  Corrección cancelada por el usuario")
    else:
        print(f"\n✅ NO HAY PROBLEMAS DE FECHAS")
        print(f"   Todas las fechas son correctas")

print(f"\n" + "=" * 60)
print(f"✅ DIAGNÓSTICO COMPLETADO")
print(f"=" * 60)
