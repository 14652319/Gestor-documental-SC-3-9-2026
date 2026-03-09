"""
Actualizar DS-1 con empresa SC
"""
from extensions import db
from flask import Flask
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Inicio2024*@localhost/gestor_documental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Actualizar DS-1 con empresa SC
    result = db.session.execute(text("""
        UPDATE facturas_temporales 
        SET empresa_id = 'SC'
        WHERE nit = '900438510' AND prefijo = 'DS' AND folio = '1'
        RETURNING id, nit, prefijo, folio, empresa_id
    """))
    
    db.session.commit()
    
    factura = result.fetchone()
    if factura:
        print("✅ FACTURA ACTUALIZADA:")
        print(f"   ID: {factura[0]}")
        print(f"   NIT: {factura[1]}")
        print(f"   Prefijo: {factura[2]}")
        print(f"   Folio: {factura[3]}")
        print(f"   Empresa: {factura[4]}")
    else:
        print("❌ No se encontró la factura")
