import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'gestor_documental'),
    'user': os.getenv('DB_USER', 'gestor_user'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    tablas = ['dian', 'erp_comercial', 'erp_financiero', 'acuses']
    
    print("\n=== VERIFICANDO TABLAS OPTIMIZADAS ===\n")
    
    for tabla in tablas:
        cur.execute(f"""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = '{tabla}'
        """)
        existe = cur.fetchone()[0]
        
        if existe:
            cur.execute(f"SELECT COUNT(*) FROM {tabla}")
            registros = cur.fetchone()[0]
            print(f"✅ {tabla:20s} - EXISTE - {registros:,} registros")
        else:
            print(f"❌ {tabla:20s} - NO EXISTE")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
