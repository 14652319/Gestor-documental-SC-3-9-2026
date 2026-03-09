"""Verifica constraints e índices de la tabla dian"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("="*80)
print("🔍 ESQUEMA DE LA TABLA DIAN")
print("="*80)

with engine.connect() as conn:
    # 1. Columnas de la tabla
    print("\n📋 COLUMNAS:")
    result = conn.execute(text("""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'dian' AND table_schema = 'public'
        ORDER BY ordinal_position
    """))
    
    for col, tipo, max_len, nullable in result:
        len_info = f"({max_len})" if max_len else ""
        null_info = "NULL" if nullable == 'YES' else "NOT NULL"
        print(f"   {col:30s} {tipo}{len_info:15s} {null_info}")
    
    # 2. Constraints (PRIMARY KEY, UNIQUE, CHECK, etc.)
    print("\n🔒 CONSTRAINTS:")
    result = conn.execute(text("""
        SELECT 
            tc.constraint_name,
            tc.constraint_type,
            kcu.column_name
        FROM information_schema.table_constraints tc
        LEFT JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.table_name = 'dian'
            AND tc.table_schema = 'public'
        ORDER BY tc.constraint_type, tc.constraint_name
    """))
    
    constraints = list(result)
    if constraints:
        for const_name, const_type, col_name in constraints:
            print(f"   {const_type:20s} '{const_name}' en columna '{col_name}'")
    else:
        print("   (No se encontraron constraints)")
    
    # 3. Índices
    print("\n📑 ÍNDICES:")
    result = conn.execute(text("""
        SELECT 
            indexname,
            indexdef
        FROM pg_indexes
        WHERE tablename = 'dian'
            AND schemaname = 'public'
        ORDER BY indexname
    """))
    
    indices = list(result)
    if indices:
        for idx_name, idx_def in indices:
            print(f"\n   Índice: {idx_name}")
            print(f"   Definición: {idx_def}")
    else:
        print("   (No se encontraron índices)")

print("\n" + "="*80)
print("💡 INTERPRETACIÓN:")
print("="*80)
print("""
Si encuentras un constraint UNIQUE en columnas como:
  - nit_emisor
  - cufe_cude
  - (nit_emisor, prefijo, folio)

→ Eso explicaría por qué solo se carga 1 registro por NIT
→ Los registros subsecuentes se rechazan como duplicados
""")
print("="*80)
