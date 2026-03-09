"""Verifica que los prefijos NUEVOS sean alfanuméricos (con números)"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("="*80)
print("🔍 VERIFICANDO PREFIJOS DESPUÉS DE LA CARGA")
print("="*80)

with engine.connect() as conn:
    # Contar registros totales
    result = conn.execute(text("SELECT COUNT(*) FROM maestro_dian_vs_erp"))
    total = result.scalar()
    print(f"\n📊 Total registros en maestro: {total:,}")
    
    # Buscar prefijos que EMPIECEN con números (3FEA, 2FEA, 1FEA, etc.)
    query_numerico = text("""
        SELECT DISTINCT prefijo, COUNT(*) as cantidad
        FROM maestro_dian_vs_erp
        WHERE prefijo ~ '^[0-9]'
        GROUP BY prefijo
        ORDER BY cantidad DESC
        LIMIT 10
    """)
    
    result = conn.execute(query_numerico)
    prefijos_numericos = result.fetchall()
    
    print(f"\n✅ PREFIJOS QUE EMPIEZAN CON NÚMERO (CORRECTO):")
    print("-" * 50)
    if prefijos_numericos:
        for prefijo, cantidad in prefijos_numericos:
            print(f"   {prefijo:10s} → {cantidad:,} registros")
    else:
        print("   ⚠️  Ninguno encontrado (esto es un problema)")
    
    # Buscar todos los prefijos únicos
    query_todos = text("""
        SELECT DISTINCT prefijo, COUNT(*) as cantidad
        FROM maestro_dian_vs_erp
        GROUP BY prefijo
        ORDER BY cantidad DESC
        LIMIT 20
    """)
    
    result = conn.execute(query_todos)
    todos_prefijos = result.fetchall()
    
    print(f"\n📋 TOP 20 PREFIJOS MÁS USADOS:")
    print("-" * 50)
    for prefijo, cantidad in todos_prefijos:
        # Marcar si empieza con número
        marca = "✅" if prefijo and prefijo[0].isdigit() else "⚪"
        print(f"   {marca} {prefijo:10s} → {cantidad:,} registros")

print("\n" + "="*80)
print("💡 Si ves prefijos como 3FEA, 2FEA, 1FEA → ✅ FIX FUNCIONANDO")
print("   Si solo ves FEA, FEAA, FEAC → ❌ Problema persiste")
print("="*80)
