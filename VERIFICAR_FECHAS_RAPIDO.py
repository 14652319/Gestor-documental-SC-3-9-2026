"""Script rápido para ver fechas en BD"""
import psycopg2

conn = psycopg2.connect(
    dbname='gestor_documental',
    user='postgres',
    password=r'G3st0radm$2025.',
    host='localhost',
    port=5432
)

cursor = conn.cursor()

# Total
cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
total = cursor.fetchone()[0]
print(f"\n📊 Total registros: {total:,}")

# Distribución de fechas
cursor.execute("""
    SELECT fecha_emision, COUNT(*) as cant
    FROM maestro_dian_vs_erp
    GROUP BY fecha_emision
    ORDER BY cant DESC
    LIMIT 15
""")

print("\n📅 DISTRIBUCIÓN DE FECHAS:")
print("=" * 60)
for fecha, cant in cursor.fetchall():
    porcentaje = (cant / total * 100) if total > 0 else 0
    print(f"  {fecha} : {cant:>8,} registros ({porcentaje:>6.2f}%)")

# Contar 2026-02-17
cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE fecha_emision = '2026-02-17'")
con_17 = cursor.fetchone()[0]
print(f"\n⚠️  Registros con 2026-02-17: {con_17:,} ({con_17/total*100:.2f}%)")

# Mostrar primeras 5 facturas
print("\n📝 PRIMERAS 5 FACTURAS:")
print("=" * 60)
cursor.execute("""
    SELECT nit_emisor, prefijo, folio, fecha_emision, valor
    FROM maestro_dian_vs_erp
    ORDER BY id
    LIMIT 5
""")
for nit, pref, folio, fecha, valor in cursor.fetchall():
    print(f"  {nit} | {pref}-{folio} | Fecha: {fecha} | Valor: ${valor:,.0f}")

cursor.close()
conn.close()
