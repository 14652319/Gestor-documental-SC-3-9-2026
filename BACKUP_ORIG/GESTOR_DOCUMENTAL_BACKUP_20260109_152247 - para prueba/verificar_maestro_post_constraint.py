"""
Verifica el estado de maestro_dian_vs_erp después de agregar constraint UNIQUE
"""
import sys
import os

# Agregar el directorio raíz al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db

# Conectar usando Flask app context
app_context = app.app_context()
app_context.push()

# Obtener conexión desde SQLAlchemy
conn = db.engine.raw_connection()
cursor = conn.cursor()

print("="*80)
print("📊 VERIFICACIÓN POST-CONSTRAINT")
print("="*80)
print()

# 1. Total de registros
cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
total = cursor.fetchone()[0]
print(f"✅ Total de registros: {total:,}")

# 2. Claves únicas
cursor.execute("""
    SELECT COUNT(DISTINCT CONCAT(nit_emisor, '-', prefijo, '-', folio)) 
    FROM maestro_dian_vs_erp
""")
claves_unicas = cursor.fetchone()[0]
print(f"🔑 Claves únicas (NIT+Prefijo+Folio): {claves_unicas:,}")

# 3. Verificar que no hay duplicados
cursor.execute("""
    SELECT nit_emisor, prefijo, folio, COUNT(*)
    FROM maestro_dian_vs_erp
    GROUP BY nit_emisor, prefijo, folio
    HAVING COUNT(*) > 1
    LIMIT 5
""")
duplicados = cursor.fetchall()

if duplicados:
    print(f"⚠️  Aún hay {len(duplicados)} duplicados (esto NO debería pasar):")
    for nit, pref, folio, count in duplicados:
        print(f"   - {nit} {pref} {folio}: {count} veces")
else:
    print("✅ No hay duplicados (correcto)")

print()

# 4. Distribución por estado_aprobacion
print("📋 Distribución por estado_aprobacion:")
cursor.execute("""
    SELECT estado_aprobacion, COUNT(*) as total
    FROM maestro_dian_vs_erp
    GROUP BY estado_aprobacion
    ORDER BY total DESC
""")
estados = cursor.fetchall()
for estado, count in estados[:10]:  # Top 10
    print(f"   - {estado or '(Vacío)'}: {count:,}")

print()

# 5. Distribución por estado_contable
print("📋 Distribución por estado_contable:")
cursor.execute("""
    SELECT estado_contable, COUNT(*) as total
    FROM maestro_dian_vs_erp
    GROUP BY estado_contable
    ORDER BY total DESC
""")
estados = cursor.fetchall()
for estado, count in estados[:10]:  # Top 10
    print(f"   - {estado or '(Vacío)'}: {count:,}")

print()
print("="*80)
print("✅ VERIFICACIÓN COMPLETA")
print("="*80)

cursor.close()
conn.close()
