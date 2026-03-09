"""Script para verificar si los nuevos datos tienen prefijos con números"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# Conectar a la base de datos
engine = create_engine(DATABASE_URL)

print("="*80)
print("🔍 VERIFICANDO PREFIJOS RECIENTES EN BASE DE DATOS")
print("="*80)

# Consulta para ver los prefijos más recientes (hoy)
query = """
SELECT 
    prefijo,
    folio,
    nit_emisor,
    razon_social,
    fecha_emision,
    fecha_registro
FROM maestro_dian_vs_erp 
WHERE DATE(fecha_registro) = CURRENT_DATE
ORDER BY fecha_registro DESC
LIMIT 20;
"""

with engine.connect() as conn:
    result = conn.execute(text(query))
    
    print("\n📋 PREFIJOS CARGADOS HOY (23/02/2026):")
    print("-"*120)
    print(f"{'Prefijo':<15} {'Folio':<15} {'NIT':<15} {'Razón Social':<30} {'Fecha Emisión':<15} {'Fecha Registro'}")
    print("-"*120)
    
    count = 0
    for row in result:
        prefijo = row[0] or ""
        folio = row[1] or ""
        nit = row[2] or ""
        razon = (row[3] or "")[:28]
        fecha_emision = row[4]
        fecha_registro = row[5]
        
        print(f"{prefijo:<15} {folio:<15} {nit:<15} {razon:<30} {str(fecha_emision):<15} {str(fecha_registro)}")
        count += 1
    
    if count == 0:
        print("⚠️ NO SE ENCONTRARON REGISTROS CARGADOS HOY")
        print("\n📋 Mostrando últimos 20 registros en la base:")
        print("-"*120)
        
        query2 = """
        SELECT prefijo, folio, nit_emisor, razon_social, fecha_emision, fecha_registro
        FROM maestro_dian_vs_erp 
        ORDER BY fecha_registro DESC
        LIMIT 20;
        """
        result2 = conn.execute(text(query2))
        for row in result2:
            prefijo = row[0] or ""
            folio = row[1] or ""
            nit = row[2] or ""
            razon = (row[3] or "")[:28]
            fecha_emision = row[4]
            fecha_registro = row[5]
            print(f"{prefijo:<15} {folio:<15} {nit:<15} {razon:<30} {str(fecha_emision):<15} {str(fecha_registro)}")

print("\n" + "="*80)
print("🔍 VERIFICANDO TABLA DIAN (tabla intermedia):")
print("="*80)

# Ver si en la tabla dian (antes de pasar al maestro) hay prefijos con números
query3 = """
SELECT 
    prefijo,
    folio,
    nit_emisor,
    razon_social
FROM dian 
WHERE prefijo LIKE '%FEA%'
LIMIT 20;
"""

with engine.connect() as conn:
    result = conn.execute(text(query3))
    
    print(f"\n{'Prefijo':<15} {'Folio':<15} {'NIT':<15} {'Razón Social':<30}")
    print("-"*90)
    
    for row in result:
        prefijo = row[0] or ""
        folio = row[1] or ""
        nit = row[2] or ""
        razon = (row[3] or "")[:28]
        
        print(f"{prefijo:<15} {folio:<15} {nit:<15} {razon:<30}")

print("\n" + "="*80)
