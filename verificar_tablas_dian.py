# -*- coding: utf-8 -*-
import psycopg2

try:
    conn = psycopg2.connect(
        dbname='gestor_documental',
        user='gestor_user',
        password='Gestor2024$',
        host='localhost'
    )
    
    cur = conn.cursor()
    
    print("=" * 70)
    print("🔍 VERIFICANDO TABLAS ESPECÍFICAS")
    print("=" * 70)
    
    tablas_buscar = ['dian', 'erp_comercial', 'erp_financiero', 'acuses', 'maestro_dian_vs_erp']
    
    for tabla in tablas_buscar:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            )
        """, (tabla,))
        
        existe = cur.fetchone()[0]
        
        if existe:
            # Contar registros
            cur.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = cur.fetchone()[0]
            print(f"✅ {tabla:25} → EXISTE (Registros: {count:,})")
        else:
            print(f"❌ {tabla:25} → NO EXISTE")
    
    print("\n" + "=" * 70)
    print("📋 LISTADO DE TODAS LAS TABLAS EN PUBLIC")
    print("=" * 70)
    
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    
    todas_tablas = cur.fetchall()
    
    for i, (tabla,) in enumerate(todas_tablas, 1):
        cur.execute(f"SELECT COUNT(*) FROM {tabla}")
        count = cur.fetchone()[0]
        print(f"{i:3}. {tabla:40} → {count:,} registros")
    
    cur.close()
    conn.close()
    
    print("\n✅ Verificación completada")
    
except Exception as e:
    print(f"❌ Error: {e}")
