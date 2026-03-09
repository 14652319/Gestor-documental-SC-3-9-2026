"""Estadísticas de la carga actual"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("="*80)
print("📊 ESTADÍSTICAS DE CARGA")
print("="*80)

with engine.connect() as conn:
    # 1. Total de NITs únicos en cada tabla
    print("\n🔢 NITs ÚNICOS en cada tabla:")
    
    result = conn.execute(text("SELECT COUNT(DISTINCT nit_emisor) FROM dian"))
    nits_dian = result.scalar()
    print(f"   DIAN: {nits_dian:,} NITs diferentes")
    
    result = conn.execute(text("SELECT COUNT(DISTINCT proveedor) FROM erp_financiero"))
    nits_erp_fn = result.scalar()
    print(f"   ERP Financiero: {nits_erp_fn:,} NITs diferentes")
    
    result = conn.execute(text("SELECT COUNT(DISTINCT nit_emisor) FROM maestro_dian_vs_erp"))
    nits_maestro = result.scalar()
    print(f"   Maestro: {nits_maestro:,} NITs diferentes")
    
    # 2. Registros totales
    print("\n📋 REGISTROS TOTALES:")
    
    result = conn.execute(text("SELECT COUNT(*) FROM dian"))
    count_dian = result.scalar()
    print(f"   DIAN: {count_dian:,} registros")
    
    result = conn.execute(text("SELECT COUNT(*) FROM erp_financiero"))
    count_erp = result.scalar()
    print(f"   ERP Financiero: {count_erp:,} registros")
    
    result = conn.execute(text("SELECT COUNT(*) FROM maestro_dian_vs_erp"))
    count_maestro = result.scalar()
    print(f"   Maestro: {count_maestro:,} registros")
    
    # 3. Top 10 NITs con MÁS registros en DIAN
    print("\n🔝 TOP 10 NITs con MÁS facturas en DIAN:")
    result = conn.execute(text("""
        SELECT nit_emisor, COUNT(*) as total
        FROM dian
        GROUP BY nit_emisor
        ORDER BY total DESC
        LIMIT 10
    """))
    
    for nit, total in result:
        print(f"   NIT {nit}: {total:,} facturas")
    
    # 4. Verificar NIT 805013653 específicamente
    print("\n" + "="*80)
    print(f"🔍 DETALLE NIT 805013653:")
    print("="*80)
    
    result = conn.execute(text("""
        SELECT 
            COALESCE(prefijo, 'NULL') as prefijo,
            COUNT(*) as cantidad
        FROM dian
        WHERE nit_emisor = '805013653'
        GROUP BY prefijo
        ORDER BY cantidad DESC
    """))
    
    registros = list(result)
    if registros:
        print(f"\n   Distribución por prefijo en DIAN:")
        for prefijo, cant in registros:
            print(f"   - Prefijo '{prefijo}': {cant} registro(s)")
    else:
        print(f"\n   ⚠️  NO hay registros con NIT 805013653 en tabla DIAN")
    
    # 5. Verificar en maestro
    result = conn.execute(text("""
        SELECT 
            prefijo,
            COUNT(*) as cantidad
        FROM maestro_dian_vs_erp
        WHERE nit_emisor = '805013653'
        GROUP BY prefijo
        ORDER BY cantidad DESC
    """))
    
    print(f"\n   Distribución por prefijo en MAESTRO:")
    for prefijo, cant in result:
        print(f"   - Prefijo '{prefijo}': {cant} registro(s)")

print("\n" + "="*80)
