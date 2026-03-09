"""
Verificación rápida de registros en todas las tablas DIAN vs ERP
"""
from app import app
from extensions import db

with app.app_context():
    print("\n" + "="*60)
    print("📊 ESTADO DE LAS TABLAS")
    print("="*60)
    
    tables = ['dian', 'erp_comercial', 'erp_financiero', 'acuses', 'maestro_dian_vs_erp']
    
    total = 0
    for table in tables:
        count = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"{table:25s}: {count:,}")
        total += count
    
    print("="*60)
    print(f"{'TOTAL':25s}: {total:,}")
    print("="*60)
