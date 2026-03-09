"""
Script para verificar la factura FE-8367 del NIT 900161900
Verifica en todas las tablas relevantes
"""
from app import app, db
from modules.dian_vs_erp.models import Dian
from modules.recibir_facturas.models import FacturaTemporal, FacturaRecibida

print("\n" + "="*80)
print("🔍 VERIFICACIÓN DE FACTURA FE-8367 - NIT 900161900")
print("="*80)

with app.app_context():
    nit = "900161900"
    prefijo = "FE"
    folio = "8367"
    
    print(f"\n📋 Buscando: {prefijo}-{folio} del NIT {nit}")
    print("-"*80)
    
    # 1. VERIFICAR EN DIAN
    print("\n1️⃣ TABLA DIAN:")
    dian_registro = Dian.query.filter_by(
        nit_emisor=nit,
        prefijo=prefijo,
        folio=folio
    ).first()
    
    if dian_registro:
        print(f"   ✅ ENCONTRADA EN DIAN")
        print(f"      ID: {dian_registro.id}")
        print(f"      Fecha Emisión: {dian_registro.fecha_emision}")
        print(f"      Tipo Documento: {dian_registro.tipo_documento}")
        print(f"      Valor Total: ${dian_registro.valor_total:,.2f}" if dian_registro.valor_total else "   N/A")
        print(f"      Razón Social: {dian_registro.razon_social_emisor}")
    else:
        print(f"   ❌ NO ENCONTRADA EN DIAN")
    
    # 2. VERIFICAR EN FACTURAS TEMPORALES
    print("\n2️⃣ TABLA FACTURAS_TEMPORALES:")
    temp_registro = FacturaTemporal.query.filter_by(
        nit=nit,
        prefijo=prefijo,
        folio=folio
    ).first()
    
    if temp_registro:
        print(f"   ✅ ENCONTRADA EN TEMPORALES")
        print(f"      ID: {temp_registro.id}")
        print(f"      Usuario: {temp_registro.usuario_id}")
        print(f"      Fecha Ingreso: {temp_registro.fecha_ingreso}")
        print(f"      Valor: ${temp_registro.valor_total:,.2f}" if temp_registro.valor_total else "   N/A")
    else:
        print(f"   ❌ NO ENCONTRADA EN TEMPORALES")
    
    # 3. VERIFICAR EN FACTURAS RECIBIDAS
    print("\n3️⃣ TABLA FACTURAS_RECIBIDAS:")
    rec_registro = FacturaRecibida.query.filter_by(
        nit=nit,
        prefijo=prefijo,
        folio=folio
    ).first()
    
    if rec_registro:
        print(f"   ✅ ENCONTRADA EN RECIBIDAS")
        print(f"      ID: {rec_registro.id}")
        print(f"      Radicado: {rec_registro.radicado}")
        print(f"      Fecha Recibido: {rec_registro.fecha_recibido}")
    else:
        print(f"   ❌ NO ENCONTRADA EN RECIBIDAS")
    
    # 4. RESUMEN
    print("\n" + "="*80)
    print("📊 RESUMEN:")
    print("-"*80)
    
    if dian_registro and temp_registro:
        print("✅ ESTADO: La factura DEBE aparecer como 'Recibida' en el visor")
        print("   Motivo: Está en DIAN y en Facturas Temporales")
    elif dian_registro and rec_registro:
        print("✅ ESTADO: La factura DEBE aparecer como 'Recibida' en el visor")
        print("   Motivo: Está en DIAN y en Facturas Recibidas")
    elif dian_registro:
        print("⚠️  ESTADO: La factura aparecerá como 'No Registrada' en el visor")
        print("   Motivo: Está en DIAN pero NO en ninguna tabla de facturas")
    else:
        print("❌ PROBLEMA: La factura NO existe en DIAN")
        print("   Solución: Debe cargarse el archivo de DIAN que contenga esta factura")
    
    # 5. QUERY PARA VERIFICAR LEFT JOIN
    print("\n" + "="*80)
    print("🔍 SIMULANDO LEFT JOIN DEL VISOR V2:")
    print("-"*80)
    
    if dian_registro:
        from sqlalchemy import func
        
        query = db.session.query(
            Dian,
            FacturaTemporal.id.label('temp_id'),
            FacturaRecibida.id.label('rec_id')
        ).outerjoin(
            FacturaTemporal,
            (Dian.nit_emisor == FacturaTemporal.nit) &
            (Dian.prefijo == FacturaTemporal.prefijo) &
            (Dian.folio == FacturaTemporal.folio)
        ).outerjoin(
            FacturaRecibida,
            (Dian.nit_emisor == FacturaRecibida.nit) &
            (Dian.prefijo == FacturaRecibida.prefijo) &
            (Dian.folio == FacturaRecibida.folio)
        ).filter(
            Dian.nit_emisor == nit,
            Dian.prefijo == prefijo,
            Dian.folio == folio
        ).first()
        
        if query:
            registro_dian, temp_id, rec_id = query
            
            print(f"   Registro DIAN: ✅ ID {registro_dian.id}")
            print(f"   Temporal ID: {'✅ ' + str(temp_id) if temp_id else '❌ NULL'}")
            print(f"   Recibida ID: {'✅ ' + str(rec_id) if rec_id else '❌ NULL'}")
            
            if temp_id or rec_id:
                print(f"\n   🎯 ESTADO CONTABLE: 'Recibida'")
            else:
                print(f"\n   ⚠️  ESTADO CONTABLE: 'No Registrada'")
        else:
            print("   ❌ Error en LEFT JOIN")

print("\n" + "="*80)
print("✅ Verificación completada")
print("="*80 + "\n")
