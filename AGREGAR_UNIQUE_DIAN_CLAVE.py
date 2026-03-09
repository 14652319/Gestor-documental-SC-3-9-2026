"""
Agregar constraint UNIQUE a columna 'clave' en tabla DIAN
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)

print("\n" + "="*80)
print("AGREGAR CONSTRAINT UNIQUE A TABLA DIAN")
print("="*80 + "\n")

with engine.connect() as conn:
    # Verificar si el constraint ya existe
    result = conn.execute(text("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'dian' AND constraint_type = 'UNIQUE'
    """))
    
    constraints = [row[0] for row in result]
    print(f"Constraints UNIQUE existentes: {constraints}")
    
    if 'dian_clave_unique' in constraints:
        print("\n✅ Constraint 'dian_clave_unique' ya existe")
    else:
        print("\n⚙️  Creando constraint UNIQUE en columna 'clave'...")
        try:
            conn.execute(text("ALTER TABLE dian ADD CONSTRAINT dian_clave_unique UNIQUE (clave)"))
            conn.commit()
            print("✅ Constraint creado exitosamente")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            conn.rollback()

print("\n" + "="*80 + "\n")
