from app import app, db
from modules.dian_vs_erp.models import Dian, ErpComercial, ErpFinanciero, Acuses

with app.app_context():
    print("\n=== VERIFICANDO TABLAS OPTIMIZADAS ===\n")
    
    tablas = [
        ('dian', Dian),
        ('erp_comercial', ErpComercial),
        ('erp_financiero', ErpFinanciero),
        ('acuses', Acuses)
    ]
    
    for nombre, modelo in tablas:
        try:
            count = modelo.query.count()
            print(f"✅ {nombre:20s} - {count:,} registros")
        except Exception as e:
            print(f"❌ {nombre:20s} - ERROR: {str(e)[:80]}")
