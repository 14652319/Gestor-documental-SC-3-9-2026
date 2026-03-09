"""
Verificar EXACTAMENTE qué fechas hay en la base de datos
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from modules.dian_vs_erp.models import MaestroDianVsErp
from datetime import date

print("=" * 80)
print("🔍 VERIFICANDO FECHAS EN BASE DE DATOS")
print("=" * 80)

with app.app_context():
    try:
        # Consultar las primeras 20 facturas
        print("\n📊 PRIMERAS 20 FACTURAS EN BASE DE DATOS:\n")
        
        facturas = MaestroDianVsErp.query.order_by(MaestroDianVsErp.id).limit(20).all()
        
        for f in facturas:
            print(f"NIT: {f.nit_emisor:15} | Fecha BD: {f.fecha_emision} | Prefijo: {f.prefijo:4} | Folio: {f.folio:8} | Valor: {f.valor:12,.2f}")
        
        # Contar fechas únicas
        print("\n" + "=" * 80)
        print("📅 FECHAS ÚNICAS EN BASE DE DATOS:")
        print("=" * 80)
        
        query = db.session.query(
            MaestroDianVsErp.fecha_emision,
            db.func.count(MaestroDianVsErp.id).label('cantidad')
        ).group_by(MaestroDianVsErp.fecha_emision).order_by(MaestroDianVsErp.fecha_emision).all()
        
        print(f"\nTotal de fechas únicas: {len(query)}")
        print()
        
        for fecha, cantidad in query[:30]:  # Mostrar primeras 30 fechas
            print(f"   {fecha} → {cantidad:,} registros")
        
        # Verificar si TODAS son 17-Feb
        if len(query) == 1 and query[0][0] == date(2026, 2, 17):
            print("\n" + "❌" * 40)
            print("❌ PROBLEMA CONFIRMADO: TODAS LAS FECHAS SON 2026-02-17")
            print("❌ El código NO está leyendo correctamente las fechas del CSV")
            print("❌" * 40)
        else:
            print("\n" + "✅" * 40)
            print("✅ HAY VARIEDAD DE FECHAS - El problema está resuelto")
            print("✅" * 40)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
