# -*- coding: utf-8 -*-
"""
Agregar columna empresa faltante
"""
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="gestor_documental",
        user="postgres",
        password="Inicio2024*"
    )
    cur = conn.cursor()
    
    print("\n" + "="*70)
    print("AGREGANDO COLUMNA EMPRESA")
    print("="*70 + "\n")
    
    # Agregar columna empresa
    try:
        cur.execute("""
            ALTER TABLE facturas_digitales 
            ADD COLUMN empresa VARCHAR(10) NOT NULL DEFAULT 'SC'
        """)
        conn.commit()
        print("✅ Columna 'empresa' agregada correctamente")
    except Exception as e:
        if "already exists" in str(e) or "ya existe" in str(e):
            print("⚠️  Columna 'empresa' ya existe")
            conn.rollback()
        else:
            print(f"❌ Error: {e}")
            conn.rollback()
    
    # Verificar
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'facturas_digitales' AND column_name = 'empresa'
    """)
    
    if cur.fetchone():
        print("✅ Columna 'empresa' verificada en la base de datos")
    else:
        print("❌ Columna 'empresa' NO existe")
    
    cur.close()
    conn.close()
    
    print("\n" + "="*70)
    print("PROCESO COMPLETADO")
    print("="*70)
    
except Exception as e:
    print(f"❌ Error de conexión: {e}")
