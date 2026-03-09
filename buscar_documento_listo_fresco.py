"""
Buscar documento de LISTO Y FRESCO S.A.S.
NIT: 805003786
Folio: 29065
Prefijo: LF (posible)
Fecha: 2025-12-18
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from modules.dian_vs_erp.models import MaestroDianVsErp
from modules.recibir_facturas.models import FacturaRecibida, FacturaTemporal
from modules.relaciones.models import RelacionFactura, FacturaRecibidaDigital
from sqlalchemy import text

# Datos del documento
NIT = '805003786'
FOLIO = '29065'
FOLIO_8 = '00029065'
PREFIJO = 'LF'

print("=" * 80)
print(f"🔍 BUSCANDO DOCUMENTO: {NIT} - Prefijo: {PREFIJO} - Folio: {FOLIO}")
print("=" * 80)

with app.app_context():
    
    # ========================================
    # 1. MAESTRO DIAN VS ERP
    # ========================================
    print("\n📋 1. MAESTRO_DIAN_VS_ERP:")
    print("-" * 80)
    
    # Buscar por NIT y folio (sin prefijo)
    docs_maestro = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.nit_emisor == NIT,
        db.or_(
            MaestroDianVsErp.folio == FOLIO,
            MaestroDianVsErp.folio == FOLIO_8
        )
    ).all()
    
    if docs_maestro:
        print(f"✅ ENCONTRADO - {len(docs_maestro)} registro(s)")
        for doc in docs_maestro:
            print(f"   • Prefijo: {doc.prefijo} | Folio: {doc.folio}")
            print(f"   • Estado Contable: {doc.estado_contable}")
            print(f"   • Recibida: {doc.recibida}")
            print(f"   • Causada: {doc.causada}")
            print(f"   • Rechazada: {doc.rechazada}")
            print(f"   • Fecha Emisión: {doc.fecha_emision}")
            print(f"   • Estado Aprobación: {doc.estado_aprobacion}")
            print(f"   • Valor: ${doc.valor:,.2f}" if doc.valor else "   • Valor: N/A")
            print(f"   • Origen Sync: {doc.origen_sincronizacion}")
            print()
    else:
        print("❌ NO ENCONTRADO")
    
    # ========================================
    # 2. FACTURAS RECIBIDAS
    # ========================================
    print("\n📦 2. FACTURAS_RECIBIDAS:")
    print("-" * 80)
    
    docs_recibidas = FacturaRecibida.query.filter(
        FacturaRecibida.nit_proveedor == NIT,
        db.or_(
            FacturaRecibida.numero_factura == FOLIO,
            FacturaRecibida.numero_factura == FOLIO_8,
            FacturaRecibida.prefijo_numero == f"{PREFIJO}{FOLIO}",
            FacturaRecibida.prefijo_numero == f"{PREFIJO}{FOLIO_8}"
        )
    ).all()
    
    if docs_recibidas:
        print(f"✅ ENCONTRADO - {len(docs_recibidas)} registro(s)")
        for doc in docs_recibidas:
            print(f"   • ID: {doc.id}")
            print(f"   • Prefijo: {doc.prefijo} | Número: {doc.numero_factura}")
            print(f"   • Prefijo-Número: {doc.prefijo_numero}")
            print(f"   • Fecha Emisión: {doc.fecha_emision}")
            print(f"   • Valor: ${doc.valor_factura:,.2f}")
            print(f"   • Usuario: {doc.usuario_recibe}")
            print(f"   • Fecha Registro: {doc.fecha_registro}")
            print()
    else:
        print("❌ NO ENCONTRADO")
    
    # ========================================
    # 3. FACTURAS TEMPORALES
    # ========================================
    print("\n⏳ 3. FACTURAS_TEMPORALES:")
    print("-" * 80)
    
    docs_temporales = FacturaTemporal.query.filter(
        FacturaTemporal.nit_proveedor == NIT,
        db.or_(
            FacturaTemporal.numero_factura == FOLIO,
            FacturaTemporal.numero_factura == FOLIO_8,
            FacturaTemporal.prefijo_numero == f"{PREFIJO}{FOLIO}",
            FacturaTemporal.prefijo_numero == f"{PREFIJO}{FOLIO_8}"
        )
    ).all()
    
    if docs_temporales:
        print(f"✅ ENCONTRADO - {len(docs_temporales)} registro(s)")
        for doc in docs_temporales:
            print(f"   • ID: {doc.id}")
            print(f"   • Prefijo: {doc.prefijo} | Número: {doc.numero_factura}")
            print(f"   • Prefijo-Número: {doc.prefijo_numero}")
            print(f"   • Fecha Emisión: {doc.fecha_emision}")
            print(f"   • Valor: ${doc.valor_factura:,.2f}")
            print(f"   • Usuario: {doc.usuario_actual}")
            print(f"   • Fecha Creación: {doc.fecha_creacion}")
            print()
    else:
        print("❌ NO ENCONTRADO")
    
    # ========================================
    # 4. RELACIONES_FACTURAS
    # ========================================
    print("\n🔗 4. RELACIONES_FACTURAS:")
    print("-" * 80)
    
    # Buscar en tabla de relaciones (esta tabla tiene las facturas relacionadas)
    query_relaciones = text("""
        SELECT rf.*, r.numero_relacion, r.fecha_generacion, r.tipo_generacion
        FROM facturas_recibidas_digitales rf
        LEFT JOIN relaciones_facturas r ON rf.numero_relacion = r.numero_relacion
        WHERE r.tercero_nit = :nit
        AND (rf.folio = :folio OR rf.folio = :folio_8)
    """)
    
    result = db.session.execute(query_relaciones, {
        'nit': NIT,
        'folio': FOLIO,
        'folio_8': FOLIO_8
    })
    
    relaciones = result.fetchall()
    
    if relaciones:
        print(f"✅ ENCONTRADO - {len(relaciones)} registro(s)")
        for rel in relaciones:
            print(f"   • Relación: {rel.numero_relacion}")
            print(f"   • Prefijo: {rel.prefijo} | Folio: {rel.folio}")
            print(f"   • Recibida: {rel.recibida}")
            print(f"   • Usuario Receptor: {rel.usuario_receptor}")
            print(f"   • Fecha Recepción: {rel.fecha_recepcion}")
            print(f"   • Tipo Generación: {rel.tipo_generacion}")
            print(f"   • Fecha Generación: {rel.fecha_generacion}")
            print()
    else:
        print("❌ NO ENCONTRADO")
    
    # ========================================
    # 5. BÚSQUEDA DIRECTA EN BD (SQL)
    # ========================================
    print("\n🔎 5. BÚSQUEDA SQL DIRECTA (Todas las tablas):")
    print("-" * 80)
    
    # Buscar en todas las tablas con campos relacionados
    tablas_queries = {
        'maestro_dian_vs_erp': f"SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE nit_emisor = '{NIT}' AND folio IN ('{FOLIO}', '{FOLIO_8}')",
        'facturas_recibidas': f"SELECT COUNT(*) FROM facturas_recibidas WHERE nit_proveedor = '{NIT}' AND numero_factura IN ('{FOLIO}', '{FOLIO_8}')",
        'facturas_temporales': f"SELECT COUNT(*) FROM facturas_temporales WHERE nit_proveedor = '{NIT}' AND numero_factura IN ('{FOLIO}', '{FOLIO_8}')",
        'facturas_recibidas_digitales': f"SELECT COUNT(*) FROM facturas_recibidas_digitales WHERE folio IN ('{FOLIO}', '{FOLIO_8}')",
    }
    
    for tabla, query in tablas_queries.items():
        try:
            result = db.session.execute(text(query))
            count = result.scalar()
            if count > 0:
                print(f"   ✅ {tabla}: {count} registro(s)")
            else:
                print(f"   ❌ {tabla}: 0 registros")
        except Exception as e:
            print(f"   ⚠️  {tabla}: Error - {str(e)}")

print("\n" + "=" * 80)
print("✅ BÚSQUEDA COMPLETADA")
print("=" * 80)
