"""
Agregar constraint de clave única a maestro_dian_vs_erp
para permitir UPSERT (INSERT ON CONFLICT)
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://gestor_user:admin@localhost:5432/gestor_documental')
engine = create_engine(DATABASE_URL)

print("🔧 Agregando constraint de clave única...")
print("=" * 80)

with engine.connect() as conn:
    # Primero verificar si ya existe
    check_query = text("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'maestro_dian_vs_erp' 
          AND constraint_type = 'UNIQUE'
          AND constraint_name = 'unique_nit_prefijo_folio'
    """)
    
    result = conn.execute(check_query)
    exists = result.fetchone()
    
    if exists:
        print("✅ Constraint 'unique_nit_prefijo_folio' ya existe")
    else:
        print("📝 Creando constraint 'unique_nit_prefijo_folio'...")
        
        # Crear el constraint
        create_constraint = text("""
            ALTER TABLE maestro_dian_vs_erp
            ADD CONSTRAINT unique_nit_prefijo_folio 
            UNIQUE (nit_emisor, prefijo, folio)
        """)
        
        conn.execute(create_constraint)
        conn.commit()
        
        print("✅ Constraint creado exitosamente")
    
    # Verificar el constraint
    verify_query = text("""
        SELECT 
            constraint_name,
            string_agg(column_name, ', ' ORDER BY ordinal_position) as columns
        FROM information_schema.constraint_column_usage
        WHERE constraint_name = 'unique_nit_prefijo_folio'
        GROUP BY constraint_name
    """)
    
    result = conn.execute(verify_query)
    row = result.fetchone()
    
    if row:
        print(f"\n✅ Constraint verificado:")
        print(f"   Nombre: {row[0]}")
        print(f"   Columnas: {row[1]}")
    
    print("\n" + "=" * 80)
    print("✅ Proceso completado")
