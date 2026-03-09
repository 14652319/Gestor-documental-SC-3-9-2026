"""Script para verificar cuántos registros hay en cada tabla"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# Conectar a la base de datos
engine = create_engine(DATABASE_URL)

print("="*80)
print("🔍 VERIFICANDO REGISTROS EN TODAS LAS TABLAS")
print("="*80)

tablas = [
    'dian',
    'erp_comercial', 
    'erp_financiero',
    'acuses',
    'maestro_dian_vs_erp'
]

with engine.connect() as conn:
    print(f"\n{'Tabla':<25} {'Registros':>15}")
    print("-"*45)
    
    for tabla in tablas:
        try:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
            count = result.scalar()
            print(f"{tabla:<25} {count:>15,}")
        except Exception as e:
            print(f"{tabla:<25} {'ERROR':>15}")
            print(f"   {str(e)[:60]}...")

print("\n" + "="*80)
