"""
Verificar columnas existentes en tablas DIAN vs ERP
"""
from sqlalchemy import create_engine, text, inspect
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)

print("\n" + "="*80)
print("COLUMNAS EXISTENTES EN TABLAS")
print("="*80)

inspector = inspect(engine)

for tabla in ['dian', 'erp_comercial', 'erp_financiero', 'maestro_dian_vs_erp']:
    print(f"\n{tabla}:")
    print("-" * 80)
    try:
        columnas = inspector.get_columns(tabla)
        if len(columnas) == 0:
            print("  Tabla NO existe o está vacía")
        else:
            for col in columnas:
                print(f"  - {col['name']:40s} {col['type']}")
    except Exception as e:
        print(f"  ERROR: {str(e)[:100]}")

print("\n" + "="*80)
