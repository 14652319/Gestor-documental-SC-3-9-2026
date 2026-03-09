"""Ver registro específico que aparece en pantalla"""
from app import app, db
from modules.dian_vs_erp.models import MaestroDianVsErp

with app.app_context():
    # Buscar un registro visible en la captura
    print("\n" + "="*80)
    print("🔍 BUSCANDO REGISTRO ESPECÍFICO")
    print("="*80 + "\n")
    
    # Buscar cualquier registro de enero con valores NULL
    reg = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.fecha_emision >= '2026-01-01',
        MaestroDianVsErp.fecha_emision <= '2026-01-31',
        db.or_(
            MaestroDianVsErp.razon_social == None,
            MaestroDianVsErp.razon_social == '',
            MaestroDianVsErp.tipo_documento == None,
            MaestroDianVsErp.tipo_documento == ''
        )
    ).first()
    
    if reg:
        print(f"📄 REGISTRO CON DATOS FALTANTES:\n")
        print(f"   ID: {reg.id}")
        print(f"   NIT Emisor: {reg.nit_emisor}")
        print(f"   Razón Social: '{reg.razon_social}' (len={len(reg.razon_social) if reg.razon_social else 0})")
        print(f"   Tipo Tercero: '{reg.tipo_tercero}' (len={len(reg.tipo_tercero) if reg.tipo_tercero else 0})")
        print(f"   Tipo Documento: '{reg.tipo_documento}' (len={len(reg.tipo_documento) if reg.tipo_documento else 0})")
        print(f"   Fecha Emisión: {reg.fecha_emision}")
        print(f"   Prefijo-Folio: {reg.prefijo}-{reg.folio}")
        print(f"   doc_causado_por: '{reg.doc_causado_por}' (len={len(reg.doc_causado_por) if reg.doc_causado_por else 0})")
        print(f"   usuario_causacion: '{reg.usuario_causacion}' (len={len(reg.usuario_causacion) if reg.usuario_causacion else 0})")
        print(f"   Causada: {reg.causada}")
    else:
        print("❌ No se encontraron registros con datos faltantes")
    
    # Ahora buscar registros con doc_causado_por = "admin"
    print(f"\n\n" + "="*80)
    print("🔍 BUSCANDO REGISTROS CON doc_causado_por = 'admin'")
    print("="*80 + "\n")
    
    admin_regs = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.fecha_emision >= '2026-01-01',
        MaestroDianVsErp.fecha_emision <= '2026-01-31',
        MaestroDianVsErp.doc_causado_por == 'admin'
    ).limit(5).all()
    
    if admin_regs:
        print(f"✅ Encontrados {len(admin_regs)} registros con doc_causado_por = 'admin':\n")
        for i, r in enumerate(admin_regs, 1):
            print(f"   {i}. {r.prefijo}-{r.folio} | NIT: {r.nit_emisor} | Fecha: {r.fecha_emision}")
    else:
        print("❌ NO HAY REGISTROS con doc_causado_por = 'admin'")
        print("\n💡 CONCLUSIÓN: El valor 'admin' que ves debe venir del FRONTEND o de otra tabla")

print("\n" + "="*80 + "\n")
