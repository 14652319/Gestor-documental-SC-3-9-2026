"""
Script para validar si las facturas se guardaron correctamente
"""
from extensions import db
from modules.recibir_facturas.models import FacturaTemporal, FacturaRecibida
from modules.dian_vs_erp.models import MaestroDianVsErp
from dotenv import load_dotenv
from app import app

load_dotenv()

# Facturas a verificar
facturas_buscar = [
    {'nit': '805002366', 'prefijo': 'ME60', 'folio': '772863'},
    {'nit': '805013653', 'prefijo': '1FEA', 'folio': '77'}
]

print("=" * 100)
print("VALIDACIÓN DE GUARDADO DE FACTURAS")
print("=" * 100)
print()

with app.app_context():
    for i, factura in enumerate(facturas_buscar, 1):
        nit = factura['nit']
        prefijo = factura['prefijo']
        folio = factura['folio']
        
        print(f"{'=' * 100}")
        print(f"FACTURA {i}: NIT {nit} | {prefijo}-{folio}")
        print(f"{'=' * 100}")
        
        # 1. Buscar en facturas_temporales
        print(f"\n1️⃣  FACTURAS_TEMPORALES:")
        temp = FacturaTemporal.query.filter_by(
            nit=nit,
            prefijo=prefijo,
            folio=folio
        ).first()
        
        if temp:
            print(f"   ❌ AÚN ESTÁ EN TEMPORALES (no se movió)")
            print(f"      ID: {temp.id}")
            print(f"      Usuario: {temp.usuario_nombre}")
            print(f"      Valor Bruto: {temp.valor_bruto}")
        else:
            print(f"   ✅ NO está en temporales (se movió correctamente)")
        
        # 2. Buscar en facturas_recibidas
        print(f"\n2️⃣  FACTURAS_RECIBIDAS:")
        recibida = FacturaRecibida.query.filter_by(
            nit=nit,
            prefijo=prefijo,
            folio=folio
        ).first()
        
        if recibida:
            print(f"   ✅ SÍ está en recibidas")
            print(f"      ID: {recibida.id}")
            print(f"      Usuario: {recibida.usuario_nombre}")
            print(f"      Estado: {recibida.estado}")
            print(f"      Fecha Radicación: {recibida.fecha_radicacion}")
        else:
            print(f"   ❌ NO está en recibidas (no se guardó)")
        
        # 3. Buscar en maestro_dian_vs_erp
        print(f"\n3️⃣  MAESTRO_DIAN_VS_ERP:")
        
        # Normalizar folio a 8 dígitos
        folio_8 = folio.zfill(8)
        
        maestro = MaestroDianVsErp.query.filter_by(
            nit_emisor=nit,
            prefijo=prefijo,
            folio=folio_8
        ).first()
        
        if maestro:
            print(f"   ✅ SÍ está en maestro")
            print(f"      Estado Contable: {maestro.estado_contable}")
            print(f"      Origen Sincronización: {maestro.origen_sincronizacion}")
            print(f"      Usuario Recibió: {maestro.usuario_recibio}")
            print(f"      Recibida: {maestro.recibida}")
            print(f"      Fecha Recibida: {maestro.fecha_recibida}")
        else:
            print(f"   ❌ NO está en maestro (no se sincronizó)")
        
        print()

print("=" * 100)
print("RESUMEN")
print("=" * 100)
print()

with app.app_context():
    # Contar registros
    total_temp = FacturaTemporal.query.count()
    total_recibidas = FacturaRecibida.query.count()
    total_maestro = MaestroDianVsErp.query.count()
    
    print(f"📊 Total facturas temporales: {total_temp}")
    print(f"📊 Total facturas recibidas: {total_recibidas}")
    print(f"📊 Total registros maestro DIAN: {total_maestro}")
    print()
    
    # Buscar logs recientes en security.log
    print("📝 LOGS RECIENTES DE GUARDADO:")
    try:
        with open('logs/security.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Últimas 50 líneas que contengan "GUARDAR" o "SINCRONIZACION"
            logs_guardado = [line for line in lines[-100:] if 'FACTURA' in line.upper() or 'SINCRONIZACION' in line.upper()]
            
            if logs_guardado:
                print("   Últimos 10 eventos:")
                for log in logs_guardado[-10:]:
                    print(f"   {log.strip()}")
            else:
                print("   ⚠️  No se encontraron logs recientes")
    except Exception as e:
        print(f"   ⚠️  Error al leer logs: {e}")

print()
print("=" * 100)
