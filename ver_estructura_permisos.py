"""Ver estructura de permisos_modulos"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    result = db.session.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name='permisos_modulos' 
        ORDER BY ordinal_position
    """))
    
    print("\n=== ESTRUCTURA permisos_modulos ===\n")
    for row in result:
        print(f"{row[0]:30} {row[1]}")
    
    # Ver datos ejemplo
    result = db.session.execute(text("SELECT * FROM permisos_modulos LIMIT 5"))
    print("\n=== DATOS DE EJEMPLO ===\n")
    for row in result:
        print(row)
