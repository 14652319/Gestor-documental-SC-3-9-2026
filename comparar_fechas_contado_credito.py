import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno
load_dotenv()

# Conexión a la base de datos
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ No se encontró DATABASE_URL en .env")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

print("=" * 80)
print("🔍 COMPARACIÓN: FECHAS CONTADO vs CRÉDITO")
print("=" * 80)

with engine.connect() as conn:
    # Registros Contado
    query_contado = text("""
        SELECT 
            MIN(fecha_emision) as fecha_minima,
            MAX(fecha_emision) as fecha_maxima,
            COUNT(*) as total
        FROM maestro_dian_vs_erp
        WHERE forma_pago = 'Contado'
    """)
    
    result_contado = conn.execute(query_contado).fetchone()
    
    print(f"\n💰 REGISTROS 'CONTADO' ({result_contado[2]:,}):")
    print(f"   Fecha Mínima: {result_contado[0]}")
    print(f"   Fecha Máxima: {result_contado[1]}")
    
    # Registros Crédito
    query_credito = text("""
        SELECT 
            MIN(fecha_emision) as fecha_minima,
            MAX(fecha_emision) as fecha_maxima,
            COUNT(*) as total
        FROM maestro_dian_vs_erp
        WHERE forma_pago = 'Crédito'
    """)
    
    result_credito = conn.execute(query_credito).fetchone()
    
    print(f"\n💳 REGISTROS 'CRÉDITO' ({result_credito[2]:,}):")
    print(f"   Fecha Mínima: {result_credito[0]}")
    print(f"   Fecha Máxima: {result_credito[1]}")
    
    print("\n" + "=" * 80)
    print("📊 CONCLUSIÓN:")
    print("=" * 80)
    
    if result_contado[0] and result_credito[1]:
        if result_contado[0] > result_credito[1]:
            print("\n⚠️  ¡LOS DATOS 'CONTADO' Y 'CRÉDITO' ESTÁN EN RANGOS DIFERENTES!")
            print(f"   • Crédito: hasta {result_credito[1]}")
            print(f"   • Contado: desde {result_contado[0]}")
            print("\n💡 SOLUCIÓN:")
            print("   En el visor, cambia el filtro de fechas a:")
            print(f"   • Desde: {result_contado[0]}")
            print(f"   • Hasta: {result_contado[1]}")
            print("   Así verás los registros 'Contado' ✅")
        else:
            print("\n✅ Los rangos de fechas se superponen - deberían verse ambos tipos")
    
    print("\n")
