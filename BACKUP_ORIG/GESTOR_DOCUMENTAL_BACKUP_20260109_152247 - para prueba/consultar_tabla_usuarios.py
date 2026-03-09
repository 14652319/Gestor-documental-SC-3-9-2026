"""Script para consultar la estructura de la tabla usuarios_asignados"""
from app import app, db

with app.app_context():
    # Consultar columnas
    query = """
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name='usuarios_asignados' 
    ORDER BY ordinal_position
    """
    
    result = db.session.execute(db.text(query))
    print("\n" + "="*80)
    print("📋 ESTRUCTURA DE LA TABLA 'usuarios_asignados'")
    print("="*80)
    
    for row in result:
        print(f"   {row[0]:<30} {row[1]}")
    
    print("="*80)
    
    # Consultar datos
    query2 = "SELECT * FROM usuarios_asignados LIMIT 5"
    result2 = db.session.execute(db.text(query2))
    
    print("\n📊 DATOS EN LA TABLA (primeros 5 registros):")
    print("="*80)
    for row in result2:
        print(row)
    print("="*80)
