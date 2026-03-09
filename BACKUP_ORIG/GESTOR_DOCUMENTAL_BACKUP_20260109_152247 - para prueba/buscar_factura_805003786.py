"""
Buscar factura específica en todas las tablas
NIT: 805003786, PREFIJO: LF, FOLIO: 29065
"""
from app import app, db
from modules.recibir_facturas.models import FacturaTemporal, FacturaRecibida
from modules.relaciones.models import FacturaRecibidaDigital
from modules.dian_vs_erp.models import MaestroDianVsErp

# Datos a buscar
NIT = "805003786"
PREFIJO = "LF"
FOLIO = "29065"

print("\n" + "="*80)
print(f"🔍 BUSCANDO FACTURA: NIT={NIT} | PREFIJO={PREFIJO} | FOLIO={FOLIO}")
print("="*80)

with app.app_context():
    resultados_totales = 0
    
    # 1. FACTURAS TEMPORALES
    print("\n📋 1. TABLA: facturas_temporales")
    print("-" * 80)
    temporales = FacturaTemporal.query.filter_by(
        nit=NIT,
        prefijo=PREFIJO,
        folio=FOLIO
    ).all()
    
    if temporales:
        for idx, ft in enumerate(temporales, 1):
            resultados_totales += 1
            print(f"\n✅ ENCONTRADA #{idx}:")
            print(f"   ID: {ft.id}")
            print(f"   Clave: {ft.nit}-{ft.prefijo}-{ft.folio}")
            print(f"   Usuario: {ft.usuario_id}")
            print(f"   Fecha Registro: {ft.fecha_registro}")
            print(f"   Valor: ${ft.valor_total:,.2f}" if ft.valor_total else "   Valor: N/A")
    else:
        print("❌ NO ENCONTRADA")
    
    # 2. FACTURAS RECIBIDAS
    print("\n📋 2. TABLA: facturas_recibidas")
    print("-" * 80)
    recibidas = FacturaRecibida.query.filter_by(
        nit=NIT,
        prefijo=PREFIJO,
        folio=FOLIO
    ).all()
    
    if recibidas:
        for idx, fr in enumerate(recibidas, 1):
            resultados_totales += 1
            print(f"\n✅ ENCONTRADA #{idx}:")
            print(f"   ID: {fr.id}")
            print(f"   Clave: {fr.nit}-{fr.prefijo}-{fr.folio}")
            print(f"   Razón Social: {fr.razon_social}")
            print(f"   Fecha Expedición: {fr.fecha_expedicion}")
            print(f"   Fecha Radicación: {fr.fecha_radicacion}")
            print(f"   Valor Bruto: ${fr.valor_bruto:,.2f}" if fr.valor_bruto else "   Valor Bruto: N/A")
            print(f"   Valor Neto: ${fr.valor_neto:,.2f}" if fr.valor_neto else "   Valor Neto: N/A")
            print(f"   Forma Pago: {fr.forma_pago}")
            print(f"   Plazo: {fr.plazo} días")
            print(f"   Usuario Solicita: {fr.usuario_solicita}")
            print(f"   Comprador: {fr.comprador}")
            print(f"   Quien Recibe: {fr.quien_recibe}")
            print(f"   Fecha Creación: {fr.fecha_creacion}")
    else:
        print("❌ NO ENCONTRADA")
    
    # 3. FACTURAS RECIBIDAS DIGITALES
    print("\n📋 3. TABLA: facturas_recibidas_digitales")
    print("-" * 80)
    # Buscar por NIT y folio (la tabla tiene numero_relacion, no prefijo directo)
    digitales = db.session.query(FacturaRecibidaDigital).filter(
        FacturaRecibidaDigital.folio == FOLIO
    ).all()
    
    # Filtrar por prefijo si existe
    digitales_filtradas = [d for d in digitales if d.prefijo == PREFIJO]
    
    if digitales_filtradas:
        for idx, fd in enumerate(digitales_filtradas, 1):
            resultados_totales += 1
            print(f"\n✅ ENCONTRADA #{idx}:")
            print(f"   ID: {fd.id}")
            print(f"   Clave: {fd.prefijo}-{fd.folio}")
            print(f"   Número Relación: {fd.numero_relacion}")
            print(f"   Recibida: {'SÍ' if fd.recibida else 'NO'}")
            print(f"   Usuario Receptor: {fd.usuario_receptor}")
            print(f"   Fecha Recepción: {fd.fecha_recepcion}")
    else:
        print("❌ NO ENCONTRADA")
    
    # 4. MAESTRO DIAN VS ERP
    print("\n📋 4. TABLA: maestro_dian_vs_erp")
    print("-" * 80)
    maestro = MaestroDianVsErp.query.filter_by(
        nit_emisor=NIT,
        prefijo=PREFIJO,
        folio=FOLIO
    ).all()
    
    if maestro:
        for idx, m in enumerate(maestro, 1):
            resultados_totales += 1
            print(f"\n✅ ENCONTRADA #{idx}:")
            print(f"   ID: {m.id}")
            print(f"   Clave: {m.nit_emisor}-{m.prefijo}-{m.folio}")
            print(f"   Razón Social: {m.razon_social}")
            print(f"   Fecha Emisión: {m.fecha_emision}")
            print(f"   Valor: ${m.valor:,.2f}" if m.valor else "   Valor: N/A")
            print(f"   📊 ESTADO CONTABLE: {m.estado_contable}")
            print(f"   Estado Aprobación: {m.estado_aprobacion}")
            print(f"   Tipo Documento: {m.tipo_documento}")
            print(f"   Forma Pago: {m.forma_pago}")
            print(f"   🔄 Recibida: {'SÍ' if m.recibida else 'NO'}")
            print(f"   🔄 Causada: {'SÍ' if m.causada else 'NO'}")
            print(f"   🔄 Rechazada: {'SÍ' if m.rechazada else 'NO'}")
            print(f"   Usuario Recibió: {m.usuario_recibio}")
            print(f"   Fecha Recibida: {m.fecha_recibida}")
            print(f"   Origen Sync: {m.origen_sincronizacion}")
    else:
        print("❌ NO ENCONTRADA")
    
    # RESUMEN FINAL
    print("\n" + "="*80)
    print(f"📊 RESUMEN FINAL")
    print("="*80)
    print(f"🔍 Búsqueda: NIT={NIT} | PREFIJO={PREFIJO} | FOLIO={FOLIO}")
    print(f"✅ Total de registros encontrados: {resultados_totales}")
    print(f"\n   • facturas_temporales: {len(temporales)}")
    print(f"   • facturas_recibidas: {len(recibidas)}")
    print(f"   • facturas_recibidas_digitales: {len(digitales_filtradas)}")
    print(f"   • maestro_dian_vs_erp: {len(maestro)}")
    print("="*80 + "\n")
