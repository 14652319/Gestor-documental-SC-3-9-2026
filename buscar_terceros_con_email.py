"""
Buscar terceros con email registrado
"""
from app import app, db, Tercero, SolicitudRegistro

with app.app_context():
    print("\n" + "="*80)
    print("  TERCEROS CON EMAIL REGISTRADO")
    print("="*80)
    
    terceros = Tercero.query.filter(
        Tercero.email.isnot(None),
        Tercero.email != ''
    ).all()
    
    if not terceros:
        print("\n❌ NO hay terceros con email registrado")
    else:
        print(f"\n✅ Encontrados {len(terceros)} terceros con email:\n")
        
        for t in terceros:
            # Buscar radicados
            radicados = SolicitudRegistro.query.filter_by(tercero_id=t.id).count()
            
            print(f"  NIT: {t.nit}")
            print(f"  Razón Social: {t.razon_social}")
            print(f"  Email: {t.email}")
            print(f"  Radicados: {radicados}")
            print(f"  {'-'*76}")
    
    print("\n" + "="*80)
    
    # Buscar también por nombre que contenga "MONICA"
    print("\n" + "="*80)
    print("  BÚSQUEDA POR NOMBRE 'MONICA'")
    print("="*80)
    
    monicas = Tercero.query.filter(
        Tercero.razon_social.ilike('%monica%')
    ).all()
    
    if monicas:
        print(f"\n✅ Encontrados {len(monicas)} terceros con 'MONICA':\n")
        for m in monicas:
            print(f"  NIT: {m.nit}")
            print(f"  Razón Social: {m.razon_social}")
            print(f"  Email: {m.email or 'SIN EMAIL'}")
            print(f"  {'-'*76}")
    else:
        print("\n❌ NO hay terceros con nombre MONICA")
    
    print("\n" + "="*80)
