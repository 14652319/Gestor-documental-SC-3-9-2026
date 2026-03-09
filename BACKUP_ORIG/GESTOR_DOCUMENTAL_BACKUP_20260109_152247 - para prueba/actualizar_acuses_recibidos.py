"""
ACTUALIZAR CAMPO acuses_recibidos - 29 Diciembre 2025
Los registros actuales tienen acuses_recibidos = 0
Este script recalcula el campo basándose en estado_aprobacion
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db

# Conectar usando Flask app context
app_context = app.app_context()
app_context.push()

conn = db.engine.raw_connection()
cursor = conn.cursor()

print("="*80)
print("🔧 ACTUALIZAR CAMPO acuses_recibidos")
print("="*80)
print()

# Ver estado actual
print("📊 Estado ANTES de actualizar:")
print("-"*80)
cursor.execute("""
    SELECT acuses_recibidos, COUNT(*) as cantidad
    FROM maestro_dian_vs_erp
    GROUP BY acuses_recibidos
    ORDER BY acuses_recibidos
""")
for acuses, count in cursor.fetchall():
    print(f"   {acuses} acuse(s): {count:,} registros")

print()

# Actualizar según estado_aprobacion
print("🔄 Actualizando acuses_recibidos según estado_aprobacion...")
print()

# Estados con 0 acuses
print("   Actualizando 'Pendiente' → 0 acuses...")
cursor.execute("""
    UPDATE maestro_dian_vs_erp
    SET acuses_recibidos = 0
    WHERE estado_aprobacion = 'Pendiente'
""")
conn.commit()
print(f"   ✅ {cursor.rowcount:,} registros actualizados")

# Estados con 1 acuse
estados_1_acuse = ['Acuse Recibido', 'Acuse Bien/Servicio', 'Rechazada']
for estado in estados_1_acuse:
    print(f"   Actualizando '{estado}' → 1 acuse...")
    cursor.execute(f"""
        UPDATE maestro_dian_vs_erp
        SET acuses_recibidos = 1
        WHERE estado_aprobacion = '{estado}'
    """)
    conn.commit()
    print(f"   ✅ {cursor.rowcount:,} registros actualizados")

# Estados con 2 acuses
estados_2_acuses = ['Aceptación Expresa', 'Aceptación Tácita']
for estado in estados_2_acuses:
    print(f"   Actualizando '{estado}' → 2 acuses...")
    cursor.execute(f"""
        UPDATE maestro_dian_vs_erp
        SET acuses_recibidos = 2
        WHERE estado_aprobacion = '{estado}'
    """)
    conn.commit()
    print(f"   ✅ {cursor.rowcount:,} registros actualizados")

print()

# Ver estado después
print("📊 Estado DESPUÉS de actualizar:")
print("-"*80)
cursor.execute("""
    SELECT acuses_recibidos, COUNT(*) as cantidad
    FROM maestro_dian_vs_erp
    GROUP BY acuses_recibidos
    ORDER BY acuses_recibidos
""")
for acuses, count in cursor.fetchall():
    print(f"   {acuses} acuse(s): {count:,} registros")

print()

# Verificar coherencia
print("🔍 Verificando coherencia...")
cursor.execute("""
    SELECT COUNT(*) as incoherentes FROM maestro_dian_vs_erp
    WHERE 
      (estado_aprobacion = 'Pendiente' AND acuses_recibidos != 0) OR
      (estado_aprobacion = 'Acuse Recibido' AND acuses_recibidos != 1) OR
      (estado_aprobacion = 'Acuse Bien/Servicio' AND acuses_recibidos != 1) OR
      (estado_aprobacion = 'Rechazada' AND acuses_recibidos != 1) OR
      (estado_aprobacion = 'Aceptación Expresa' AND acuses_recibidos != 2) OR
      (estado_aprobacion = 'Aceptación Tácita' AND acuses_recibidos != 2)
""")
incoherentes = cursor.fetchone()[0]

if incoherentes == 0:
    print("✅ ÉXITO: Todos los registros coherentes")
else:
    print(f"❌ FALLO: Aún hay {incoherentes:,} registros incoherentes")

print()
print("="*80)
print("✅ CAMPO acuses_recibidos ACTUALIZADO")
print("="*80)

cursor.close()
conn.close()
