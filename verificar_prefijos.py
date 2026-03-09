"""Script para verificar cómo están guardados los prefijos en la BD"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# Conectar a la base de datos
engine = create_engine(DATABASE_URL)

print("="*80)
print("🔍 VERIFICANDO PREFIJOS EN BASE DE DATOS")
print("="*80)

# Consulta para ver prefijos únicos con ejemplos
query = """
SELECT 
    prefijo,
    folio,
    nit_emisor,
    razon_social,
    LENGTH(prefijo) as longitud,
    fecha_emision
FROM maestro_dian_vs_erp 
WHERE prefijo LIKE '%FEA%'
ORDER BY fecha_emision DESC
LIMIT 20;
"""

with engine.connect() as conn:
    result = conn.execute(text(query))
    
    print("\n📋 MUESTRA DE PREFIJOS EN LA BASE DE DATOS:")
    print("-"*120)
    print(f"{'Prefijo':<15} {'Longitud':<10} {'Folio':<15} {'NIT':<15} {'Razón Social':<30} {'Fecha'}")
    print("-"*120)
    
    for row in result:
        prefijo = row[0] or ""
        folio = row[1] or ""
        nit = row[2] or ""
        razon = (row[3] or "")[:28]
        longitud = row[4] or 0
        fecha = row[5]
        
        print(f"{prefijo:<15} {longitud:<10} {folio:<15} {nit:<15} {razon:<30} {fecha}")

print("\n" + "="*80)
print("🔍 ANÁLISIS DE PREFIJOS ÚNICOS:")
print("="*80)

# Ver todos los prefijos únicos que contienen FEA
query2 = """
SELECT DISTINCT 
    prefijo,
    LENGTH(prefijo) as longitud,
    COUNT(*) as cantidad
FROM maestro_dian_vs_erp 
WHERE prefijo LIKE '%FEA%'
GROUP BY prefijo, LENGTH(prefijo)
ORDER BY prefijo;
"""

with engine.connect() as conn:
    result = conn.execute(text(query2))
    
    print(f"\n{'Prefijo':<15} {'Longitud':<10} {'Cantidad de registros'}")
    print("-"*50)
    
    for row in result:
        prefijo = row[0] or ""
        longitud = row[1] or 0
        cantidad = row[2]
        
        print(f"{prefijo:<15} {longitud:<10} {cantidad:>20,}")

print("\n" + "="*80)
