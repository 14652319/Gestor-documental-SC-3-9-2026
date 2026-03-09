"""Analiza de dónde vienen los registros del NIT 805013653"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("="*80)
print("🔍 ANÁLISIS DEL NIT 805013653")
print("="*80)

with engine.connect() as conn:
    # 1. DIAN
    result = conn.execute(text("""
        SELECT COUNT(*), STRING_AGG(DISTINCT prefijo, ', ') as prefijos
        FROM dian 
        WHERE nit_emisor = '805013653'
    """))
    count, prefijos = result.fetchone()
    print(f"\n📋 TABLA DIAN (facturas electrónicas DIAN):")
    print(f"   Total: {count} registros")
    print(f"   Prefijos: {prefijos if prefijos else 'Ninguno'}")
    
    # 2. ERP Financiero
    result = conn.execute(text("""
        SELECT COUNT(*), STRING_AGG(DISTINCT prefijo, ', ') as prefijos
        FROM erp_financiero 
        WHERE proveedor = '805013653'
    """))
    count, prefijos = result.fetchone()
    print(f"\n📊 TABLA ERP_FINANCIERO (módulo financiero interno):")
    print(f"   Total: {count} registros")
    print(f"   Prefijos: {prefijos if prefijos else 'Ninguno'}")
    
    # 3. ERP Comercial
    result = conn.execute(text("""
        SELECT COUNT(*), STRING_AGG(DISTINCT prefijo, ', ') as prefijos
        FROM erp_comercial 
        WHERE nit_proveedor = '805013653'
    """))
    count, prefijos = result.fetchone()
    print(f"\n🛒 TABLA ERP_COMERCIAL (módulo comercial interno):")
    print(f"   Total: {count} registros")
    print(f"   Prefijos: {prefijos if prefijos else 'Ninguno'}")
    
    # 4. Maestro
    result = conn.execute(text("""
        SELECT COUNT(*), STRING_AGG(DISTINCT prefijo, ', ') as prefijos
        FROM maestro_dian_vs_erp 
        WHERE nit_emisor = '805013653'
    """))
    count, prefijos = result.fetchone()
    print(f"\n📕 TABLA MAESTRO (consolidado):")
    print(f"   Total: {count} registros")
    print(f"   Prefijos: {prefijos if prefijos else 'Ninguno'}")
    
    # 5. Análisis de Estado Contable
    print(f"\n" + "="*80)
    print("🔍 ANÁLISIS DE ESTADO CONTABLE")
    print("="*80)
    
    result = conn.execute(text("""
        SELECT 
            estado_contable,
            COUNT(*) as cantidad,
            STRING_AGG(DISTINCT prefijo, ', ' ORDER BY prefijo) as prefijos_ejemplo
        FROM maestro_dian_vs_erp 
        WHERE nit_emisor = '805013653'
        GROUP BY estado_contable
        ORDER BY cantidad DESC
    """))
    
    for estado, cantidad, prefijos in result:
        print(f"\n   Estado: {estado if estado else 'No Registrada'}")
        print(f"   Cantidad: {cantidad}")
        print(f"   Prefijos: {prefijos[:100] if prefijos else 'Ninguno'}")
    
    # 6. Análisis de clave_erp_financiero
    print(f"\n" + "="*80)
    print("🔑 ANÁLISIS DE CLAVE (para cross-reference)")
    print("="*80)
    
    result = conn.execute(text("""
        SELECT 
            prefijo,
            folio,
            clave_erp_financiero,
            estado_contable
        FROM maestro_dian_vs_erp 
        WHERE nit_emisor = '805013653'
        ORDER BY prefijo, folio
        LIMIT 5
    """))
    
    print("\nPrimeros 5 registros:")
    for prefijo, folio, clave, estado in result:
        print(f"   {prefijo}-{folio} | Clave: {clave[:30] if clave else 'NULL'} | Estado: {estado if estado else 'No Registrada'}")

print("\n" + "="*80)
print("💡 INTERPRETACIÓN:")
print("="*80)
print("""
Si los registros están en ERP_FINANCIERO pero NO en DIAN:
  → Son facturas que están en el sistema contable interno
  → Pero NO se han reportado a DIAN (o no están en el archivo Dian.xlsx)
  → Por eso aparecen como "No Registrada"

Posibles causas:
  1. El archivo Dian.xlsx no contiene esas facturas del proveedor
  2. Las facturas son de otro tipo (notas crédito, débito)
  3. Las facturas aún no se han enviado a DIAN
  4. Hay un error en el cruce de claves (NIT+Prefijo+Folio)
""")
print("="*80)
