import sys
sys.path.insert(0, '.')

from extensions import db
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gestor_user:Gestor2024$@localhost/gestor_documental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    tablas = ['dian', 'erp_comercial', 'erp_financiero', 'acuses', 'maestro_dian_vs_erp']
    
    print("=" * 70)
    print("VERIFICACION DE TABLAS ESPECIFICAS")
    print("=" * 70)
    
    for tabla in tablas:
        try:
            resultado = db.session.execute(
                db.text(f"SELECT COUNT(*) FROM {tabla}")
            )
            count = resultado.scalar()
            print(f"✓ {tabla:25} EXISTE - {count:,} registros")
        except Exception as e:
            print(f"X {tabla:25} NO EXISTE")
    
    print("\n" + "=" * 70)
    print("TODAS LAS TABLAS EN PUBLIC")
    print("=" * 70)
    
    resultado = db.session.execute(
        db.text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
    )
    
    for i, (tabla,) in enumerate(resultado, 1):
        try:
            count_result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {tabla}"))
            count = count_result.scalar()
            print(f"{i:2}. {tabla:35} {count:,} registros")
        except:
            print(f"{i:2}. {tabla:35} ERROR")
    
    print("=" * 70)
