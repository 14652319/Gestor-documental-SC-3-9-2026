"""
Script para probar el envío de documentos de crédito sin acuses
"""
from app import app, db
from modules.dian_vs_erp.models import MaestroDianVsErp, EnvioProgramadoDianVsErp

with app.app_context():
    print("\n" + "="*60)
    print("DIAGNÓSTICO: Documentos de Crédito sin Acuses")
    print("="*60 + "\n")
    
    # 1. Total de documentos de crédito
    total_credito = MaestroDianVsErp.query.filter(
        db.or_(
            MaestroDianVsErp.forma_pago.ilike('%crédito%'),
            MaestroDianVsErp.forma_pago.ilike('%credit%')
        )
    ).count()
    print(f"📊 Total documentos de CRÉDITO en BD: {total_credito}")
    
    # 2. Documentos con acuses < 2
    requiere_acuses = 2
    docs_sin_acuses = MaestroDianVsErp.query.filter(
        db.or_(
            MaestroDianVsErp.forma_pago.ilike('%crédito%'),
            MaestroDianVsErp.forma_pago.ilike('%credit%')
        ),
        MaestroDianVsErp.acuses_recibidos < requiere_acuses
    ).all()
    
    print(f"📄 Docs con menos de {requiere_acuses} acuses: {len(docs_sin_acuses)}")
    
    if docs_sin_acuses:
        # Mostrar primeros 5 documentos
        print(f"\n📋 Primeros 5 documentos:")
        for i, doc in enumerate(docs_sin_acuses[:5], 1):
            print(f"  {i}. NIT: {doc.nit_emisor} | Factura: {doc.prefijo}-{doc.folio}")
            print(f"     Forma Pago: {doc.forma_pago} | Acuses: {doc.acuses_recibidos}")
            print(f"     Días: {doc.dias_desde_emision} | Valor: ${doc.valor:,.0f}")
        
        # Agrupar por NIT
        docs_por_nit = {}
        for doc in docs_sin_acuses:
            nit = doc.nit_emisor
            if nit not in docs_por_nit:
                docs_por_nit[nit] = []
            docs_por_nit[nit].append(doc)
        
        print(f"\n🏢 NITs con documentos: {len(docs_por_nit)}")
        
        # Buscar usuarios por NIT
        usuarios_encontrados = 0
        for nit, docs in docs_por_nit.items():
            query = """
                SELECT correo, nombres, apellidos 
                FROM usuarios_asignados 
                WHERE nit = :nit AND activo = true
            """
            result = db.session.execute(db.text(query), {'nit': nit})
            usuarios = result.fetchall()
            
            if usuarios:
                usuarios_encontrados += len(usuarios)
                print(f"\n  NIT: {nit} ({len(docs)} docs)")
                for usuario in usuarios:
                    print(f"    ✅ Usuario: {usuario[1]} {usuario[2]} - {usuario[0]}")
            else:
                print(f"\n  NIT: {nit} ({len(docs)} docs)")
                print(f"    ⚠️ Sin usuarios asignados")
        
        print(f"\n👥 Total usuarios encontrados: {usuarios_encontrados}")
        
        if usuarios_encontrados == 0:
            print("\n❌ PROBLEMA: No hay usuarios asignados para los NITs con documentos de crédito")
            print("   Solución: Agregar usuarios en la pestaña 'Usuarios por NIT'")
    else:
        print("\n⚠️ No se encontraron documentos de crédito con menos de 2 acuses")
    
    print("\n" + "="*60)
    print("FIN DEL DIAGNÓSTICO")
    print("="*60 + "\n")
