"""
Script para consultar y actualizar el estado_contable de CERDOS DEL VALLE
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Conexión a PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://gestor_user:admin@localhost:5432/gestor_documental')
engine = create_engine(DATABASE_URL)

print("🔍 Consultando CERDOS DEL VALLE (PC-77651)...")
print("=" * 80)

# Consultar estado actual
with engine.connect() as conn:
    query = text("""
        SELECT 
            nit_emisor, 
            razon_social, 
            prefijo, 
            folio,
            modulo,
            estado_contable,
            doc_causado_por,
            causada
        FROM maestro_dian_vs_erp 
        WHERE prefijo = 'PC' 
          AND folio = '77651'
        LIMIT 5
    """)
    
    result = conn.execute(query)
    rows = result.fetchall()
    
    if not rows:
        print("❌ No se encontró el documento PC-77651")
        sys.exit(1)
    
    print(f"✅ Encontrados {len(rows)} registro(s):\n")
    
    for row in rows:
        print(f"NIT Emisor: {row[0]}")
        print(f"Razón Social: {row[1]}")
        print(f"Prefijo-Folio: {row[2]}-{row[3]}")
        print(f"Módulo: {row[4]}")
        print(f"Estado Contable: {row[5]}")
        print(f"Doc Causado Por: {row[6]}")
        print(f"Causada: {row[7]}")
        print("-" * 80)
        
        # Si NO está como "Causada", actualizar
        if row[5] != 'Causada':
            print(f"\n⚠️ Estado incorrecto: '{row[5]}' (debería ser 'Causada')")
            print("🔧 Actualizando a 'Causada'...\n")
            
            update_query = text("""
                UPDATE maestro_dian_vs_erp
                SET estado_contable = 'Causada',
                    fecha_actualizacion = NOW()
                WHERE prefijo = 'PC' 
                  AND folio = '77651'
            """)
            
            conn.execute(update_query)
            conn.commit()
            
            print("✅ Estado actualizado correctamente")
            print("🔄 Recarga la página para ver los cambios\n")
        else:
            print(f"\n✅ Estado correcto: '{row[5]}'")
            print("ℹ️ Si el frontend muestra 'Recibida', presiona F5 para recargar la página\n")

print("=" * 80)
print("✅ Script completado")
