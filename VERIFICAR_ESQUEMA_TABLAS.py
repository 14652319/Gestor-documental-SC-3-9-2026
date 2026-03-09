"""
Verificar esquema real de tablas PostgreSQL
"""
from sqlalchemy import create_engine, text, inspect
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)

print("\n" + "="*80)
print("ESQUEMA DE TABLAS - VERIFICACIÓN")
print("="*80 + "\n")

inspector = inspect(engine)

tablas = ['dian', 'erp_comercial', 'erp_financiero']

for tabla in tablas:
    print(f"📋 TABLA: {tabla}")
    print("-" * 80)
    
    if tabla not in inspector.get_table_names():
        print(f"   ❌ La tabla '{tabla}' no existe\n")
        continue
    
    columns = inspector.get_columns(tabla)
    
    print(f"   Total columnas: {len(columns)}\n")
    
    for i, col in enumerate(columns, 1):
        col_name = col['name']
        col_type = str(col['type'])
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        print(f"   {i:2}. {col_name:30} | {col_type:20} | {nullable}")
    
    print("\n")

print("="*80 + "\n")
