"""
Verificar conteo de registros en tablas DIAN vs ERP
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Crear engine
database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)

print("\n" + "="*80)
print("CONTEO DE REGISTROS EN TABLAS")
print("="*80)

tablas = [
    'dian',
    'erp_comercial', 
    'erp_financiero',
    'acuses_recibidos',
    'maestro_dian_vs_erp'
]

with engine.connect() as conn:
    for tabla in tablas:
        try:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
            count = result.scalar()
            print(f"{tabla:25s}: {count:>10,} registros")
        except Exception as e:
            print(f"{tabla:25s}: ERROR - {str(e)[:50]}")

print("="*80)
print()
