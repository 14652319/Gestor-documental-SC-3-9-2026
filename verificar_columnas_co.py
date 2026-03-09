"""
Script para verificar las columnas de la tabla centros_operacion
"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    # Obtener columnas de la tabla
    result = db.session.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'centros_operacion'
        ORDER BY ordinal_position
    """))
    
    print("=" * 60)
    print("COLUMNAS DE LA TABLA centros_operacion:")
    print("=" * 60)
    for row in result:
        print(f"  {row[0]:30} -> {row[1]}")
    
    print("\n" + "=" * 60)
    print("DATOS DE EJEMPLO:")
    print("=" * 60)
    
    # Ver algunos datos de ejemplo
    result2 = db.session.execute(text("""
        SELECT * FROM centros_operacion LIMIT 5
    """))
    
    for row in result2:
        print(f"  {row}")
