from extensions import db
from app import app
from modules.dian_vs_erp.models import MaestroDianVsErp
from datetime import date

with app.app_context():
    print("=" * 80)
    print("VERIFICACIÓN DE FECHAS EN BASE DE DATOS - 2026")
    print("=" * 80)
    
    # Contar total 2026
    total = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.fecha_emision >= date(2026, 1, 1)
    ).count()
    
    print(f"\nTotal registros 2026: {total:,}")
    
    if total == 0:
        print("❌ NO HAY REGISTROS DE 2026")
    else:
        # Obtener fechas únicas
        fechas = db.session.query(
            MaestroDianVsErp.fecha_emision,
            db.func.count(MaestroDianVsErp.id).label('cantidad')
        ).filter(
            MaestroDianVsErp.fecha_emision >= date(2026, 1, 1)
        ).group_by(
            MaestroDianVsErp.fecha_emision
        ).order_by(
            MaestroDianVsErp.fecha_emision
        ).limit(30).all()
        
        print(f"\nTotal de fechas únicas: {len(fechas)}")
        print("\nPrimeras 30 fechas:")
        print("-" * 50)
        
        for fecha, cantidad in fechas:
            print(f"{fecha} | Registros: {cantidad:,}")
        
        # Si todas son 2026-02-17, mostrar advertencia
        if len(fechas) == 1 and fechas[0][0] == date(2026, 2, 17):
            print("\n" + "=" * 80)
            print("❌ PROBLEMA: TODAS LAS FECHAS SON 2026-02-17")
            print("=" * 80)
            print("\nEsto significa que NO se leyó correctamente 'Fecha Emisión' del Excel")
            print("El código está usando date.today() como default")
        else:
            print("\n✅ HAY VARIEDAD DE FECHAS (correcto)")
        
        # Mostrar muestra de valores
        print("\n" + "=" * 80)
        print("MUESTRA DE REGISTROS")
        print("=" * 80)
        
        muestra = MaestroDianVsErp.query.filter(
            MaestroDianVsErp.fecha_emision >= date(2026, 1, 1)
        ).limit(10).all()
        
        for r in muestra:
            print(f"NIT: {r.nit_emisor} | Fecha: {r.fecha_emision} | Valor: {r.valor} | {r.prefijo}-{r.folio}")
