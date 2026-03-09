"""
Verificar empresa_id en facturas temporales
"""
from extensions import db
from flask import Flask
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Inicio2024*@localhost/gestor_documental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("\n" + "="*70)
    print(" 📋 FACTURAS TEMPORALES - CAMPO EMPRESA_ID")
    print("="*70 + "\n")
    
    result = db.session.execute(text("""
        SELECT 
            id,
            nit, 
            prefijo, 
            folio,
            empresa_id,
            fecha_creacion
        FROM facturas_temporales 
        ORDER BY id DESC
        LIMIT 10
    """))
    
    facturas = result.fetchall()
    
    if facturas:
        print(f"{'ID':<5} {'NIT':<12} {'Pref':<6} {'Folio':<6} {'Empresa':<10} {'Fecha':<20}")
        print("-" * 70)
        for f in facturas:
            empresa = f[4] if f[4] else 'NULL'
            fecha = str(f[5])[:19] if f[5] else 'N/A'
            print(f"{f[0]:<5} {f[1]:<12} {f[2]:<6} {f[3]:<6} {empresa:<10} {fecha:<20}")
        
        # Contar con/sin empresa
        with_empresa = sum(1 for f in facturas if f[4])
        without_empresa = len(facturas) - with_empresa
        
        print("\n" + "-" * 70)
        print(f"✅ CON empresa_id: {with_empresa}")
        print(f"❌ SIN empresa_id: {without_empresa}")
    else:
        print("⚠️ No hay facturas temporales")
    
    print("\n" + "="*70 + "\n")
