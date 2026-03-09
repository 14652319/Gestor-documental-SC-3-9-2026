import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("=" * 80)
print("🔍 VERIFICANDO COLUMNAS DE FECHA EN CADA TABLA")
print("=" * 80)

tablas = ['dian', 'erp_comercial', 'erp_financiero', 'acuses', 'maestro_dian_vs_erp']

with engine.connect() as conn:
    for tabla in tablas:
        print(f"\n📊 TABLA: {tabla}")
        print("-" * 60)
        
        # Obtener todas las columnas de la tabla
        query = text(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{tabla}'
            AND column_name LIKE '%fecha%'
            ORDER BY ordinal_position
        """)
        
        rows = conn.execute(query).fetchall()
        
        if rows:
            print(f"   Columnas con 'fecha' en el nombre:")
            for col_name, data_type in rows:
                print(f"   • {col_name:<30} ({data_type})")
        else:
            print("   ⚠️ No se encontraron columnas con 'fecha' en el nombre")

print("\n" + "=" * 80)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 80)
