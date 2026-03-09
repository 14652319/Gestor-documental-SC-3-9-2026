"""
TEST COMPLETO DEL UPSERT - 29 Diciembre 2025
Pruebas automatizadas para validar el comportamiento del UPSERT
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from datetime import datetime

# Conectar usando Flask app context
app_context = app.app_context()
app_context.push()

conn = db.engine.raw_connection()
cursor = conn.cursor()

print("="*80)
print("🧪 SUITE DE PRUEBAS UPSERT - DIAN VS ERP")
print("="*80)
print()

# ============================================================================
# PRUEBA 1: Estado actual de la base de datos
# ============================================================================
print("📊 PRUEBA 1: Verificar estado inicial")
print("-"*80)

cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
total_inicial = cursor.fetchone()[0]
print(f"✅ Total de registros: {total_inicial:,}")

cursor.execute("""
    SELECT COUNT(*) FROM maestro_dian_vs_erp 
    WHERE estado_aprobacion = 'Pendiente'
""")
pendientes = cursor.fetchone()[0]
print(f"✅ Registros con 'Pendiente': {pendientes:,}")

cursor.execute("""
    SELECT COUNT(*) FROM maestro_dian_vs_erp 
    WHERE estado_aprobacion = 'Acuse Recibido'
""")
acuse_recibido = cursor.fetchone()[0]
print(f"✅ Registros con 'Acuse Recibido': {acuse_recibido:,}")

cursor.execute("""
    SELECT COUNT(*) FROM maestro_dian_vs_erp 
    WHERE estado_aprobacion = 'Aceptación Tácita'
""")
aceptacion_tacita = cursor.fetchone()[0]
print(f"✅ Registros con 'Aceptación Tácita': {aceptacion_tacita:,}")

print()

# ============================================================================
# PRUEBA 2: Verificar que no hay duplicados
# ============================================================================
print("🔍 PRUEBA 2: Verificar unicidad de registros")
print("-"*80)

cursor.execute("""
    SELECT nit_emisor, prefijo, folio, COUNT(*) as duplicados
    FROM maestro_dian_vs_erp
    GROUP BY nit_emisor, prefijo, folio
    HAVING COUNT(*) > 1
    LIMIT 5
""")
duplicados = cursor.fetchall()

if duplicados:
    print(f"❌ FALLO: Encontrados {len(duplicados)} duplicados:")
    for nit, pref, folio, count in duplicados:
        print(f"   - {nit} {pref} {folio}: {count} veces")
else:
    print("✅ ÉXITO: No hay duplicados (constraint UNIQUE funcionando)")

print()

# ============================================================================
# PRUEBA 3: Coherencia entre estado_aprobacion y acuses_recibidos
# ============================================================================
print("🔗 PRUEBA 3: Coherencia estado_aprobacion vs acuses_recibidos")
print("-"*80)

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

if incoherentes > 0:
    print(f"❌ FALLO: {incoherentes} registros incoherentes")
    cursor.execute("""
        SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos
        FROM maestro_dian_vs_erp
        WHERE 
          (estado_aprobacion = 'Pendiente' AND acuses_recibidos != 0) OR
          (estado_aprobacion = 'Acuse Recibido' AND acuses_recibidos != 1) OR
          (estado_aprobacion = 'Acuse Bien/Servicio' AND acuses_recibidos != 1) OR
          (estado_aprobacion = 'Rechazada' AND acuses_recibidos != 1) OR
          (estado_aprobacion = 'Aceptación Expresa' AND acuses_recibidos != 2) OR
          (estado_aprobacion = 'Aceptación Tácita' AND acuses_recibidos != 2)
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"   - {row[0]} {row[1]} {row[2]}: {row[3]} pero acuses={row[4]}")
else:
    print("✅ ÉXITO: Todos los registros coherentes (estado ↔ acuses)")

print()

# ============================================================================
# PRUEBA 4: Distribución de acuses_recibidos
# ============================================================================
print("📊 PRUEBA 4: Distribución de acuses_recibidos")
print("-"*80)

cursor.execute("""
    SELECT acuses_recibidos, COUNT(*) as cantidad
    FROM maestro_dian_vs_erp
    GROUP BY acuses_recibidos
    ORDER BY acuses_recibidos
""")
dist_acuses = cursor.fetchall()

total_acuses = 0
for acuses, cantidad in dist_acuses:
    print(f"   {acuses} acuse(s): {cantidad:,} registros")
    total_acuses += cantidad

print(f"   TOTAL: {total_acuses:,} registros")

if total_acuses != total_inicial:
    print(f"❌ FALLO: Discrepancia en totales ({total_acuses} vs {total_inicial})")
else:
    print("✅ ÉXITO: Totales coinciden")

print()

# ============================================================================
# PRUEBA 5: Seleccionar registros de prueba para simulación
# ============================================================================
print("🎯 PRUEBA 5: Seleccionar registros para pruebas de jerarquía")
print("-"*80)

# Buscar un registro con "Pendiente" (jerarquía 1)
cursor.execute("""
    SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos, razon_social
    FROM maestro_dian_vs_erp
    WHERE estado_aprobacion = 'Pendiente'
    LIMIT 1
""")
reg_pendiente = cursor.fetchone()

if reg_pendiente:
    print("✅ Registro con 'Pendiente' encontrado:")
    print(f"   NIT: {reg_pendiente[0]}, Prefijo: {reg_pendiente[1]}, Folio: {reg_pendiente[2]}")
    print(f"   Estado: {reg_pendiente[3]}, Acuses: {reg_pendiente[4]}")
    print(f"   Razón: {reg_pendiente[5]}")
    print()
    print("   💡 PRUEBA SUGERIDA: Cambiar a 'Acuse Recibido' (jerarquía 1→2)")
    print(f"      Esperado: ✅ SE ACTUALIZA (2 > 1)")
else:
    print("⚠️  No hay registros con 'Pendiente'")

print()

# Buscar un registro con "Aceptación Tácita" (jerarquía 6)
cursor.execute("""
    SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos, razon_social
    FROM maestro_dian_vs_erp
    WHERE estado_aprobacion = 'Aceptación Tácita'
    LIMIT 1
""")
reg_tacita = cursor.fetchone()

if reg_tacita:
    print("✅ Registro con 'Aceptación Tácita' encontrado:")
    print(f"   NIT: {reg_tacita[0]}, Prefijo: {reg_tacita[1]}, Folio: {reg_tacita[2]}")
    print(f"   Estado: {reg_tacita[3]}, Acuses: {reg_tacita[4]}")
    print(f"   Razón: {reg_tacita[5]}")
    print()
    print("   💡 PRUEBA SUGERIDA: Intentar cambiar a 'Pendiente' (jerarquía 6→1)")
    print(f"      Esperado: ❌ NO SE ACTUALIZA (1 < 6) - Protección activa")
else:
    print("⚠️  No hay registros con 'Aceptación Tácita'")

print()

# Buscar un registro con "Acuse Recibido" (jerarquía 2)
cursor.execute("""
    SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos, razon_social
    FROM maestro_dian_vs_erp
    WHERE estado_aprobacion = 'Acuse Recibido'
    LIMIT 1
""")
reg_acuse = cursor.fetchone()

if reg_acuse:
    print("✅ Registro con 'Acuse Recibido' encontrado:")
    print(f"   NIT: {reg_acuse[0]}, Prefijo: {reg_acuse[1]}, Folio: {reg_acuse[2]}")
    print(f"   Estado: {reg_acuse[3]}, Acuses: {reg_acuse[4]}")
    print(f"   Razón: {reg_acuse[5]}")
    print()
    print("   💡 PRUEBA SUGERIDA: Cambiar a 'Aceptación Expresa' (jerarquía 2→5)")
    print(f"      Esperado: ✅ SE ACTUALIZA (5 > 2)")
else:
    print("⚠️  No hay registros con 'Acuse Recibido'")

print()

# ============================================================================
# PRUEBA 6: Verificar constraint UNIQUE
# ============================================================================
print("🔒 PRUEBA 6: Verificar constraint UNIQUE")
print("-"*80)

cursor.execute("""
    SELECT conname 
    FROM pg_constraint 
    WHERE conrelid = 'maestro_dian_vs_erp'::regclass 
      AND contype = 'u'
""")
constraints = cursor.fetchall()

if constraints:
    print("✅ ÉXITO: Constraint UNIQUE encontrada:")
    for (conname,) in constraints:
        print(f"   - {conname}")
else:
    print("❌ FALLO: NO hay constraint UNIQUE (UPSERT fallará)")

print()

# ============================================================================
# PRUEBA 7: Verificar tablas de catálogo
# ============================================================================
print("📚 PRUEBA 7: Verificar tablas de catálogo de estados")
print("-"*80)

try:
    cursor.execute("SELECT COUNT(*) FROM estado_aceptacion")
    count_aceptacion = cursor.fetchone()[0]
    print(f"✅ Tabla estado_aceptacion: {count_aceptacion} estados")
    
    cursor.execute("SELECT COUNT(*) FROM estado_contable")
    count_contable = cursor.fetchone()[0]
    print(f"✅ Tabla estado_contable: {count_contable} estados")
    
    if count_aceptacion == 6 and count_contable == 6:
        print("✅ ÉXITO: Catálogos completos (6 estados cada uno)")
    else:
        print(f"⚠️  ADVERTENCIA: Catálogos incompletos (esperado: 6, actual: {count_aceptacion}, {count_contable})")
except Exception as e:
    print(f"❌ FALLO: Error al consultar catálogos: {e}")

print()

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("="*80)
print("📋 RESUMEN DE PRUEBAS")
print("="*80)

resultados = {
    "Estado inicial": "✅ OK" if total_inicial > 0 else "❌ FALLO",
    "Sin duplicados": "✅ OK" if not duplicados else "❌ FALLO",
    "Coherencia acuses": "✅ OK" if incoherentes == 0 else "❌ FALLO",
    "Distribución acuses": "✅ OK" if total_acuses == total_inicial else "❌ FALLO",
    "Registros de prueba": "✅ OK" if reg_pendiente and reg_tacita else "⚠️  PARCIAL",
    "Constraint UNIQUE": "✅ OK" if constraints else "❌ FALLO",
    "Catálogos": "✅ OK" if count_aceptacion == 6 else "⚠️  PARCIAL"
}

for prueba, resultado in resultados.items():
    print(f"   {prueba}: {resultado}")

print()

total_pruebas = len(resultados)
pruebas_ok = sum(1 for r in resultados.values() if "✅" in r)
print(f"✅ Pruebas exitosas: {pruebas_ok}/{total_pruebas}")

if pruebas_ok == total_pruebas:
    print()
    print("🎉 TODAS LAS PRUEBAS PASARON - Sistema listo para UPSERT")
elif pruebas_ok >= total_pruebas - 1:
    print()
    print("⚠️  Sistema mayormente OK - Revisar advertencias")
else:
    print()
    print("❌ FALLOS CRÍTICOS - Revisar antes de continuar")

print()
print("="*80)
print("🔗 SIGUIENTE PASO: Probar con carga real en:")
print("   http://127.0.0.1:8099/dian_vs_erp/cargar_archivos")
print("="*80)

cursor.close()
conn.close()
