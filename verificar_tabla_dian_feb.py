# -*- coding: utf-8 -*-
"""
Consulta DIRECTA a PostgreSQL para ver si hay datos de febrero 2026
"""
import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        dbname='gestor_documental',
        user='gestor_user',
        password='Gest0rP@ssw0rd2024'
    )
    
    cur = conn.cursor()
    
    print("=" * 80)
    print("🔍 CONSULTA DIRECTA EN POSTGRESQL - TABLA 'dian'")
    print("=" * 80)
    
    # Contar registros de febrero 2026
    cur.execute("""
        SELECT COUNT(*), MIN(fecha_emision), MAX(fecha_emision)
        FROM dian 
        WHERE fecha_emision >= '2026-02-01' AND fecha_emision <= '2026-02-28'
    """)
    
    row = cur.fetchone()
    print(f"\n✅ Registros de FEBRERO 2026 en tabla 'dian':")
    print(f"   Total: {row[0]}")
    print(f"   Fecha mínima: {row[1]}")
    print(f"   Fecha máxima: {row[2]}")
    
    if row[0] == 0:
        print("\n❌ LA TABLA 'dian' NO TIENE DATOS DE FEBRERO 2026")
        print("   Los archivos que cargaste no se guardaron en esta tabla.")
        print("\n💡 REVISA:")
        print("   1. ¿Qué tabla usa el módulo de carga de archivos?")
        print("   2. ¿Es 'maestro_dian_vs_erp' en vez de 'dian'?")
    else:
        # Mostrar muestra
        cur.execute("""
            SELECT nit, razon_social, tipo_documento, prefijo, folio, total, fecha_emision
            FROM dian 
            WHERE fecha_emision >= '2026-02-01' AND fecha_emision <= '2026-02-28'
            LIMIT 5
        """)
        
        print(f"\n📋 Primeros 5 registros:")
        for r in cur.fetchall():
            print(f"   {r[0]} | {r[1][:30]:30} | {r[2]:20} | {r[3]}-{r[4]} | {r[6]}")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
