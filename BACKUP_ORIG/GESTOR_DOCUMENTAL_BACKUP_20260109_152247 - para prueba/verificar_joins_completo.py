"""
Verificación radical de los JOINs entre tablas
"""
from app import app, db
from modules.dian_vs_erp.models import Dian, ErpFinanciero, ErpComercial, Acuses
from sqlalchemy import and_

with app.app_context():
    print("\n" + "="*80)
    print("🔍 VERIFICACIÓN RADICAL DE JOINS")
    print("="*80)
    
    # 1. Contar registros en cada tabla
    print("\n📊 CONTEO DE REGISTROS:")
    count_dian = db.session.query(Dian).count()
    count_fin = db.session.query(ErpFinanciero).count()
    count_com = db.session.query(ErpComercial).count()
    count_acuses = db.session.query(Acuses).count()
    
    print(f"   DIAN: {count_dian:,}")
    print(f"   ERP Financiero: {count_fin:,}")
    print(f"   ERP Comercial: {count_com:,}")
    print(f"   Acuses: {count_acuses:,}")
    
    # 2. Tomar un registro de DIAN y ver si tiene matches
    print("\n🎯 PROBANDO JOIN CON 1 FACTURA ESPECÍFICA:")
    factura_prueba = db.session.query(Dian).filter(
        Dian.prefijo != None,
        Dian.folio != None
    ).first()
    
    if factura_prueba:
        print(f"\n   Factura seleccionada:")
        print(f"   NIT: {factura_prueba.nit_emisor}")
        print(f"   Prefijo: {factura_prueba.prefijo}")
        print(f"   Folio: {factura_prueba.folio}")
        print(f"   Clave Acuse: {factura_prueba.clave_acuse}")
        
        # Buscar en Acuses
        acuse_match = db.session.query(Acuses).filter(
            Acuses.clave_acuse == factura_prueba.clave_acuse
        ).first()
        
        print(f"\n   ✅ Match en ACUSES: {'SÍ' if acuse_match else 'NO'}")
        if acuse_match:
            print(f"      Estado: {acuse_match.estado_docto}")
        
        # Buscar en ERP Financiero
        fin_match = db.session.query(ErpFinanciero).filter(
            ErpFinanciero.prefijo == factura_prueba.prefijo,
            ErpFinanciero.folio == factura_prueba.folio,
            ErpFinanciero.proveedor == factura_prueba.nit_emisor
        ).first()
        
        print(f"   ✅ Match en ERP FINANCIERO: {'SÍ' if fin_match else 'NO'}")
        if fin_match:
            print(f"      Proveedor: {fin_match.proveedor}")
            print(f"      Módulo: {fin_match.modulo}")
        
        # Buscar en ERP Comercial
        com_match = db.session.query(ErpComercial).filter(
            ErpComercial.prefijo == factura_prueba.prefijo,
            ErpComercial.folio == factura_prueba.folio,
            ErpComercial.proveedor == factura_prueba.nit_emisor
        ).first()
        
        print(f"   ✅ Match en ERP COMERCIAL: {'SÍ' if com_match else 'NO'}")
        if com_match:
            print(f"      Proveedor: {com_match.proveedor}")
            print(f"      Módulo: {com_match.modulo}")
    
    # 3. Probar el query completo como está en la API
    print("\n\n🚀 PROBANDO QUERY COMPLETO (como en API):")
    query_completo = db.session.query(
        Dian,
        Acuses.estado_docto.label('estado_acuse'),
        ErpFinanciero.id.label('existe_financiero'),
        ErpComercial.id.label('existe_comercial')
    ).outerjoin(
        Acuses,
        and_(
            Dian.clave_acuse == Acuses.clave_acuse,
            Dian.clave_acuse != None,
            Dian.clave_acuse != ''
        )
    ).outerjoin(
        ErpFinanciero,
        and_(
            Dian.prefijo == ErpFinanciero.prefijo,
            Dian.folio == ErpFinanciero.folio,
            Dian.nit_emisor == ErpFinanciero.proveedor
        )
    ).outerjoin(
        ErpComercial,
        and_(
            Dian.prefijo == ErpComercial.prefijo,
            Dian.folio == ErpComercial.folio,
            Dian.nit_emisor == ErpComercial.proveedor
        )
    )
    
    # Aplicar filtro de fecha para reducir resultados
    query_completo = query_completo.filter(Dian.fecha_emision >= '2025-12-01')
    resultados = query_completo.limit(5).all()
    
    print(f"\n   Se obtuvieron {len(resultados)} registros de prueba")
    
    for i, (registro, estado_acuse, existe_financiero, existe_comercial) in enumerate(resultados, 1):
        print(f"\n   Registro {i}:")
        print(f"      NIT: {registro.nit_emisor}")
        print(f"      Prefijo-Folio: {registro.prefijo}-{registro.folio}")
        print(f"      Estado DIAN: {registro.estado}")
        print(f"      Estado Acuse (JOIN): {estado_acuse if estado_acuse else 'NULL'}")
        print(f"      Existe en Financiero: {'SÍ' if existe_financiero else 'NO'}")
        print(f"      Existe en Comercial: {'SÍ' if existe_comercial else 'NO'}")
        
        # Calcular lo que debería mostrar
        if estado_acuse:
            estado_final = estado_acuse
        elif registro.estado:
            estado_final = registro.estado
        else:
            estado_final = "Pendiente"
            
        if existe_financiero:
            contable_final = "Causado en Financiero"
        elif existe_comercial:
            contable_final = "Causado en Comercial"
        else:
            contable_final = "No Causado"
            
        print(f"      >>> ESTADO APROBACIÓN FINAL: {estado_final}")
        print(f"      >>> ESTADO CONTABLE FINAL: {contable_final}")
    
    print("\n" + "="*80)
    print("✅ Verificación completada")
    print("="*80 + "\n")
