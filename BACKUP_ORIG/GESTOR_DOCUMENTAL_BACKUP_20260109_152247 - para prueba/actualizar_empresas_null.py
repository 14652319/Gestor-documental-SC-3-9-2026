"""
Script para actualizar facturas con empresa_id NULL a 'SC'
"""
from extensions import db
from flask import Flask
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Inicio2024*@localhost/gestor_documental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("\n" + "=" * 100)
    print("ACTUALIZANDO FACTURAS CON EMPRESA_ID NULL")
    print("=" * 100)
    
    # Contar cuántas tienen NULL
    result = db.session.execute(text("""
        SELECT COUNT(*) FROM facturas_temporales WHERE empresa_id IS NULL
    """)).scalar()
    
    print(f"\nFacturas temporales con empresa_id NULL: {result}")
    
    if result > 0:
        # Actualizar a SC
        db.session.execute(text("""
            UPDATE facturas_temporales 
            SET empresa_id = 'SC' 
            WHERE empresa_id IS NULL
        """))
        db.session.commit()
        print(f"[OK] {result} facturas temporales actualizadas a empresa_id = 'SC'")
    else:
        print("[INFO] No hay facturas temporales con empresa_id NULL")
    
    # Hacer lo mismo con facturas_recibidas
    result2 = db.session.execute(text("""
        SELECT COUNT(*) FROM facturas_recibidas WHERE empresa_id IS NULL
    """)).scalar()
    
    print(f"\nFacturas recibidas con empresa_id NULL: {result2}")
    
    if result2 > 0:
        db.session.execute(text("""
            UPDATE facturas_recibidas 
            SET empresa_id = 'SC' 
            WHERE empresa_id IS NULL
        """))
        db.session.commit()
        print(f"[OK] {result2} facturas recibidas actualizadas a empresa_id = 'SC'")
    else:
        print("[INFO] No hay facturas recibidas con empresa_id NULL")
    
    print("\n" + "=" * 100)
    print("ACTUALIZACION COMPLETADA")
    print("=" * 100 + "\n")
