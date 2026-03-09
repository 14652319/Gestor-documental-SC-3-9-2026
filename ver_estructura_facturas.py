"""
Ver estructura de tabla facturas_digitales
"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    print("\n📋 COLUMNAS DE facturas_digitales:\n")
    print(f"{'COLUMNA':<40} {'TIPO':<25}")
    print("=" * 70)
    
    result = db.session.execute(text("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'facturas_digitales'
        ORDER BY ordinal_position
    """)).fetchall()
    
    for row in result:
        columna, tipo, nullable = row
        null_str = "NULL" if nullable == "YES" else "NOT NULL"
        print(f"{columna:<40} {tipo:<25} {null_str}")
    
    print(f"\n✅ Total: {len(result)} columnas")
