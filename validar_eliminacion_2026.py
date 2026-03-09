"""
Script para validar que los datos de 2026 fueron eliminados correctamente
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener conexión PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ No se encontró DATABASE_URL en .env")
    exit(1)

# Crear engine
engine = create_engine(DATABASE_URL)

print("=" * 80)
print("🔍 VALIDACIÓN DE ELIMINACIÓN - DATOS 2026")
print("=" * 80)

with engine.connect() as conn:
    # 1. Contar registros totales
    result = conn.execute(text("""
        SELECT COUNT(*) as total
        FROM maestro_dian_vs_erp
    """))
    total = result.fetchone()[0]
    print(f"\n📊 Total de registros en maestro_dian_vs_erp: {total:,}")
    
    # 2. Contar registros de 2026
    result = conn.execute(text("""
        SELECT COUNT(*) as total_2026
        FROM maestro_dian_vs_erp
        WHERE fecha_emision >= '2026-01-01' AND fecha_emision < '2027-01-01'
    """))
    total_2026 = result.fetchone()[0]
    
    if total_2026 == 0:
        print(f"✅ Registros de 2026: {total_2026} (ELIMINACIÓN EXITOSA)")
    else:
        print(f"❌ Registros de 2026: {total_2026:,} (¡AÚN HAY DATOS!)")
    
    # 3. Contar registros de 2025 (deberían seguir ahí)
    result = conn.execute(text("""
        SELECT COUNT(*) as total_2025
        FROM maestro_dian_vs_erp
        WHERE fecha_emision >= '2025-01-01' AND fecha_emision < '2026-01-01'
    """))
    total_2025 = result.fetchone()[0]
    print(f"📋 Registros de 2025 (deben estar): {total_2025:,}")
    
    # 4. Ver rango de fechas actual
    result = conn.execute(text("""
        SELECT 
            MIN(fecha_emision) as fecha_min,
            MAX(fecha_emision) as fecha_max
        FROM maestro_dian_vs_erp
    """))
    row = result.fetchone()
    if row and row[0]:
        print(f"\n📅 Rango de fechas actual:")
        print(f"   Desde: {row[0]}")
        print(f"   Hasta: {row[1]}")
    
    # 5. Si hay registros de 2026, mostrar algunos ejemplos
    if total_2026 > 0:
        print(f"\n⚠️  SE ENCONTRARON {total_2026:,} REGISTROS DE 2026:")
        result = conn.execute(text("""
            SELECT 
                id,
                nit_emisor,
                razon_social,
                fecha_emision,
                prefijo,
                folio,
                valor
            FROM maestro_dian_vs_erp
            WHERE fecha_emision >= '2026-01-01' AND fecha_emision < '2027-01-01'
            ORDER BY fecha_emision
            LIMIT 5
        """))
        
        print("\n   Primeros 5 registros:")
        for row in result:
            print(f"   • ID: {row[0]} | NIT: {row[1]} | Fecha: {row[3]} | Folio: {row[4]}{row[5]} | Valor: ${row[6]:,.2f}")
    
    # 6. Distribución por año
    print(f"\n📊 DISTRIBUCIÓN POR AÑO:")
    result = conn.execute(text("""
        SELECT 
            EXTRACT(YEAR FROM fecha_emision) as año,
            COUNT(*) as cantidad
        FROM maestro_dian_vs_erp
        GROUP BY EXTRACT(YEAR FROM fecha_emision)
        ORDER BY año
    """))
    
    for row in result:
        año = int(row[0]) if row[0] else 'NULL'
        cantidad = row[1]
        print(f"   {año}: {cantidad:,} registros")

print("\n" + "=" * 80)
if total_2026 == 0:
    print("✅ VALIDACIÓN EXITOSA: Todos los datos de 2026 fueron eliminados")
    print("✅ Los datos de 2025 se mantienen intactos")
    print("\n🚀 SIGUIENTE PASO: Re-importar archivos Excel de 2026 con script corregido")
else:
    print("❌ VALIDACIÓN FALLIDA: Aún hay datos de 2026 en la base de datos")
    print("⚠️  Puede que la eliminación no se completó o hubo un error")
print("=" * 80)
