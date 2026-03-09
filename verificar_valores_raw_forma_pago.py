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
print("🔍 VALORES RAW DE FORMA_PAGO EN TABLA DIAN")
print("=" * 80)

with engine.connect() as conn:
    # Contar valores distintos de forma_pago en tabla dian
    query = text("""
        SELECT 
            forma_pago,
            COUNT(*) as total
        FROM dian
        WHERE fecha_emision BETWEEN '2026-01-01' AND '2026-02-26'
        GROUP BY forma_pago
        ORDER BY total DESC
    """)
    
    rows = conn.execute(query).fetchall()
    
    print(f"\n📊 VALORES DE forma_pago EN TABLA DIAN (2026-01-01 a 2026-02-26):")
    print("-" * 60)
    print(f"{'Valor forma_pago':<25} {'Registros':<15} {'%':<10}")
    print("-" * 60)
    
    total_registros = sum(row[1] for row in rows)
    
    for forma_pago, total in rows:
        valor_mostrar = f"'{forma_pago}'" if forma_pago else "(null)"
        porcentaje = (total / total_registros * 100) if total_registros > 0 else 0
        print(f"{valor_mostrar:<25} {total:>10,} {porcentaje:>9.2f}%")
        
        # Mostrar qué debería convertirse según la lógica
        if forma_pago == "1" or forma_pago == "01":
            print(f"   └─> ✅ Debería convertirse a: 'Contado'")
        elif forma_pago == "2" or forma_pago == "02":
            print(f"   └─> ✅ Debería convertirse a: 'Crédito'")
        else:
            print(f"   └─> ⚠️ Default: 'Crédito' (no matchea 1, 01, 2 o 02)")
    
    print("-" * 60)
    print(f"{'TOTAL':<25} {total_registros:>10,}")
    
    # Contar en maestro_dian_vs_erp para comparar
    query_maestro = text("""
        SELECT 
            forma_pago,
            COUNT(*) as total
        FROM maestro_dian_vs_erp
        WHERE fecha_emision BETWEEN '2026-01-01' AND '2026-02-26'
        GROUP BY forma_pago
        ORDER BY total DESC
    """)
    
    rows_maestro = conn.execute(query_maestro).fetchall()
    
    print(f"\n📊 VALORES DE forma_pago EN TABLA MAESTRO_DIAN_VS_ERP (2026-01-01 a 2026-02-26):")
    print("-" * 60)
    print(f"{'Valor forma_pago':<25} {'Registros':<15} {'%':<10}")
    print("-" * 60)
    
    total_maestro = sum(row[1] for row in rows_maestro)
    
    for forma_pago, total in rows_maestro:
        valor_mostrar = f"'{forma_pago}'" if forma_pago else "(null)"
        porcentaje = (total / total_maestro * 100) if total_maestro > 0 else 0
        print(f"{valor_mostrar:<25} {total:>10,} {porcentaje:>9.2f}%")
    
    print("-" * 60)
    print(f"{'TOTAL':<25} {total_maestro:>10,}")
    
    print("\n" + "=" * 80)
    print("💡 CONCLUSIÓN:")
    print("=" * 80)
    print("\n1. La tabla DIAN tiene los valores RAW ('1', '2', null, etc.)")
    print("2. La API V2 DEBE hacer la transformación según:")
    print("   • '1' o '01' → 'Contado'")
    print("   • '2' o '02' → 'Crédito'")
    print("   • Todo lo demás → 'Crédito' (default)")
    print("\n3. Si la API retorna solo 'Crédito', el problema está en:")
    print("   • Los valores RAW no son '1' o '01'")
    print("   • O la lógica de transformación no se está ejecutando")
    print("\n")
