"""Ver estructura de las tablas"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='gestor_documental',
    user='postgres',
    password='G3st0radm$2025.'
)
cursor = conn.cursor()

print("\n" + "="*80)
print("ESTRUCTURA DE TABLAS")
print("="*80 + "\n")

# Ver columnas de envios_programados
print("📋 Tabla: envios_programados_dian_vs_erp")
print("-"*80)
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'envios_programados_dian_vs_erp'
    ORDER BY ordinal_position
""")
for col in cursor.fetchall():
    print(f"  • {col[0]} ({col[1]})")

print("\n📋 Tabla: historial_envios_dian_vs_erp")
print("-"*80)
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'historial_envios_dian_vs_erp'
    ORDER BY ordinal_position
""")
for col in cursor.fetchall():
    print(f"  • {col[0]} ({col[1]})")

print("\n" + "="*80)

cursor.close()
conn.close()
