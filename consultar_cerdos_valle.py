"""
Consultar los 3 documentos de CERDOS DEL VALLE que se ven en el frontend
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://gestor_user:admin@localhost:5432/gestor_documental')
engine = create_engine(DATABASE_URL)

print("=" * 100)
print("🔍 CONSULTANDO LOS 3 DOCUMENTOS DE CERDOS DEL VALLE")
print("=" * 100)

with engine.connect() as conn:
    query = text("""
        SELECT 
            prefijo,
            folio,
            estado_contable,
            modulo,
            doc_causado_por,
            causada,
            razon_social
        FROM maestro_dian_vs_erp 
        WHERE nit_emisor = '805018495'
          AND razon_social ILIKE '%CERDOS DEL VALLE%'
          AND (
              (prefijo = 'DZ' AND folio = '16452')
              OR (prefijo = 'PC' AND folio = '77650')
              OR (prefijo = 'PC' AND folio = '77651')
          )
        ORDER BY prefijo, folio
    """)
    
    result = conn.execute(query)
    rows = result.fetchall()
    
    print(f"\n✅ Encontrados {len(rows)} documento(s):\n")
    
    for row in rows:
        prefijo, folio, estado, modulo, doc_causado, causada, razon = row
        
        print(f"📄 {prefijo}-{folio}")
        print(f"   Razón Social: {razon}")
        print(f"   Estado Contable: {estado}")
        print(f"   Módulo: {modulo if modulo else 'NULL'}")
        print(f"   Doc Causado Por: {doc_causado if doc_causado else 'NULL'}")
        print(f"   Causada (bool): {causada}")
        print(f"   ❓ ¿Debería ser Causada? ", end="")
        
        if modulo or doc_causado:
            print("SÍ (tiene módulo o doc_causado_por)")
        else:
            print("❌ NO (no tiene módulo ni doc_causado_por) - DEBERÍA SER RECIBIDA")
        
        print("-" * 100)
    
    # Ahora verificar si están en facturas_temporales o facturas_recibidas
    print("\n🔍 VERIFICANDO EN TABLAS DE FACTURAS:")
    print("=" * 100)
    
    for tabla in ['facturas_temporales', 'facturas_recibidas', 'facturas_recibidas_digitales']:
        query_tabla = text(f"""
            SELECT prefijo, folio, nit
            FROM {tabla}
            WHERE nit = '805018495'
              AND (
                  (prefijo = 'DZ' AND folio = '16452')
                  OR (prefijo = 'PC' AND folio = '77650')
                  OR (prefijo = 'PC' AND folio = '77651')
              )
        """)
        
        result_tabla = conn.execute(query_tabla)
        rows_tabla = result_tabla.fetchall()
        
        if rows_tabla:
            print(f"\n✅ Encontrados en {tabla}:")
            for row_t in rows_tabla:
                print(f"   - {row_t[0]}-{row_t[1]}")
        else:
            print(f"\n❌ NO encontrados en {tabla}")

print("\n" + "=" * 100)
