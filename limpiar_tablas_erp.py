import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="gestor_documental",
    user="postgres",
    password="G3st0radm$2025."
)
cursor = conn.cursor()

print("\n1. Conteos ANTES de limpiar:")
cursor.execute("SELECT COUNT(*) FROM dian")
print(f"   DIAN: {cursor.fetchone()[0]:,}")
cursor.execute("SELECT COUNT(*) FROM erp_comercial")
print(f"   ERP CM: {cursor.fetchone()[0]:,}")
cursor.execute("SELECT COUNT(*) FROM erp_financiero")
print(f"   ERP FN: {cursor.fetchone()[0]:,}")
cursor.execute("SELECT COUNT(*) FROM acuses")
print(f"   ACUSES: {cursor.fetchone()[0]:,}")

print("\n2. Limpiando ERP COMERCIAL...");
cursor.execute("TRUNCATE TABLE erp_comercial RESTART IDENTITY")
conn.commit()
print("   [OK] Tabla limpiada")

print("\n3. Limpiando ERP FINANCIERO...")
cursor.execute("TRUNCATE TABLE erp_financiero RESTART IDENTITY")
conn.commit()
print("   [OK] Tabla limpiada")

print("\n4. Limpiando ACUSES...")
cursor.execute("TRUNCATE TABLE acuses RESTART IDENTITY")
conn.commit()
print("   [OK] Tabla limpiada")

print("\n5. Conteos DESPUES de limpiar:")
cursor.execute("SELECT COUNT(*) FROM dian")
print(f"   DIAN: {cursor.fetchone()[0]:,}")
cursor.execute("SELECT COUNT(*) FROM erp_comercial")
print(f"   ERP CM: {cursor.fetchone()[0]:,}")
cursor.execute("SELECT COUNT(*) FROM erp_financiero")
print(f"   ERP FN: {cursor.fetchone()[0]:,}")
cursor.execute("SELECT COUNT(*) FROM acuses")
print(f"   ACUSES: {cursor.fetchone()[0]:,}")

cursor.close()
conn.close()

print("\n[COMPLETADO] Tablas limpiadas")
