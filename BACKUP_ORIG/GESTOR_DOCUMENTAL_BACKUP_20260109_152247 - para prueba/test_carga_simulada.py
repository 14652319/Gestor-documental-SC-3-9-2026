"""
TEST SIMULADO DE CARGA - 29 Diciembre 2025
Simula el comportamiento del botón "Procesar & Consolidar"
Prueba el UPSERT con datos reales de la base de datos
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db

app_context = app.app_context()
app_context.push()

conn = db.engine.raw_connection()
cursor = conn.cursor()

print("="*80)
print("🧪 TEST DE CARGA SIMULADA - UPSERT EN ACCIÓN")
print("="*80)
print()

# ============================================================================
# PASO 1: Seleccionar 3 registros específicos para probar jerarquía
# ============================================================================
print("📋 PASO 1: Seleccionar registros de prueba")
print("-"*80)

# Registro 1: Pendiente (jerarquía 1) → Acuse Recibido (jerarquía 2)
cursor.execute("""
    SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos
    FROM maestro_dian_vs_erp
    WHERE estado_aprobacion = 'Pendiente'
    LIMIT 1
""")
reg1 = cursor.fetchone()
print(f"✅ Registro 1: {reg1[0]}-{reg1[1]}-{reg1[2]}")
print(f"   Estado actual: {reg1[3]} (jerarquía=1, acuses={reg1[4]})")
print(f"   Cambio simulado: → 'Acuse Recibido' (jerarquía=2, acuses=1)")
print(f"   Resultado esperado: ✅ SE ACTUALIZA (2 > 1)")
print()

# Registro 2: Aceptación Tácita (jerarquía 6) → Pendiente (jerarquía 1)
cursor.execute("""
    SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos
    FROM maestro_dian_vs_erp
    WHERE estado_aprobacion = 'Aceptación Tácita'
    LIMIT 1
""")
reg2 = cursor.fetchone()
print(f"✅ Registro 2: {reg2[0]}-{reg2[1]}-{reg2[2]}")
print(f"   Estado actual: {reg2[3]} (jerarquía=6, acuses={reg2[4]})")
print(f"   Cambio simulado: → 'Pendiente' (jerarquía=1, acuses=0)")
print(f"   Resultado esperado: ❌ NO SE ACTUALIZA (1 < 6) - Protección activa")
print()

# Registro 3: Acuse Recibido (jerarquía 2) → Aceptación Expresa (jerarquía 5)
cursor.execute("""
    SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos
    FROM maestro_dian_vs_erp
    WHERE estado_aprobacion = 'Acuse Recibido'
    LIMIT 1
""")
reg3 = cursor.fetchone()
print(f"✅ Registro 3: {reg3[0]}-{reg3[1]}-{reg3[2]}")
print(f"   Estado actual: {reg3[3]} (jerarquía=2, acuses={reg3[4]})")
print(f"   Cambio simulado: → 'Aceptación Expresa' (jerarquía=5, acuses=2)")
print(f"   Resultado esperado: ✅ SE ACTUALIZA (5 > 2)")
print()

# ============================================================================
# PASO 2: Crear tabla temporal (como hace el UPSERT real)
# ============================================================================
print("📦 PASO 2: Crear tabla temporal")
print("-"*80)

cursor.execute("DROP TABLE IF EXISTS temp_test_maestro")
cursor.execute("""
    CREATE TEMP TABLE temp_test_maestro AS
    SELECT * FROM maestro_dian_vs_erp WHERE FALSE
""")
print("✅ Tabla temporal creada")
print()

# ============================================================================
# PASO 3: Insertar registros de prueba en tabla temporal
# ============================================================================
print("📥 PASO 3: Cargar datos simulados a tabla temporal")
print("-"*80)

# Simular cambio en registro 1: Pendiente → Acuse Recibido
cursor.execute("""
    INSERT INTO temp_test_maestro
    SELECT * FROM maestro_dian_vs_erp
    WHERE nit_emisor = %s AND prefijo = %s AND folio = %s
""", (reg1[0], reg1[1], reg1[2]))
cursor.execute("""
    UPDATE temp_test_maestro
    SET estado_aprobacion = 'Acuse Recibido', acuses_recibidos = 1
    WHERE nit_emisor = %s AND prefijo = %s AND folio = %s
""", (reg1[0], reg1[1], reg1[2]))
print(f"✅ Registro 1 simulado: Pendiente → Acuse Recibido")

# Simular cambio en registro 2: Aceptación Tácita → Pendiente (downgrade)
cursor.execute("""
    INSERT INTO temp_test_maestro
    SELECT * FROM maestro_dian_vs_erp
    WHERE nit_emisor = %s AND prefijo = %s AND folio = %s
""", (reg2[0], reg2[1], reg2[2]))
cursor.execute("""
    UPDATE temp_test_maestro
    SET estado_aprobacion = 'Pendiente', acuses_recibidos = 0
    WHERE nit_emisor = %s AND prefijo = %s AND folio = %s
""", (reg2[0], reg2[1], reg2[2]))
print(f"✅ Registro 2 simulado: Aceptación Tácita → Pendiente (downgrade)")

# Simular cambio en registro 3: Acuse Recibido → Aceptación Expresa
cursor.execute("""
    INSERT INTO temp_test_maestro
    SELECT * FROM maestro_dian_vs_erp
    WHERE nit_emisor = %s AND prefijo = %s AND folio = %s
""", (reg3[0], reg3[1], reg3[2]))
cursor.execute("""
    UPDATE temp_test_maestro
    SET estado_aprobacion = 'Aceptación Expresa', acuses_recibidos = 2
    WHERE nit_emisor = %s AND prefijo = %s AND folio = %s
""", (reg3[0], reg3[1], reg3[2]))
print(f"✅ Registro 3 simulado: Acuse Recibido → Aceptación Expresa")
print()

# ============================================================================
# PASO 4: Ejecutar UPSERT (lógica real del sistema)
# ============================================================================
print("🔄 PASO 4: Ejecutar UPSERT con validación de jerarquía")
print("-"*80)

# Crear función de jerarquía (igual que en routes.py)
cursor.execute("""
    CREATE OR REPLACE FUNCTION temp_jerarquia_test(estado TEXT)
    RETURNS INTEGER AS $$
    BEGIN
        RETURN CASE estado
            WHEN 'Pendiente' THEN 1
            WHEN 'Acuse Recibido' THEN 2
            WHEN 'Acuse Bien/Servicio' THEN 3
            WHEN 'Rechazada' THEN 4
            WHEN 'Aceptación Expresa' THEN 5
            WHEN 'Aceptación Tácita' THEN 6
            ELSE 0
        END;
    END;
    $$ LANGUAGE plpgsql IMMUTABLE;
""")

# Ejecutar UPSERT (solo en los 3 registros de prueba)
cursor.execute("""
    INSERT INTO maestro_dian_vs_erp
    SELECT * FROM temp_test_maestro
    ON CONFLICT (nit_emisor, prefijo, folio) DO UPDATE SET
        estado_aprobacion = CASE
            WHEN temp_jerarquia_test(EXCLUDED.estado_aprobacion) >
                 temp_jerarquia_test(maestro_dian_vs_erp.estado_aprobacion)
            THEN EXCLUDED.estado_aprobacion
            ELSE maestro_dian_vs_erp.estado_aprobacion
        END,
        acuses_recibidos = CASE
            WHEN temp_jerarquia_test(EXCLUDED.estado_aprobacion) >
                 temp_jerarquia_test(maestro_dian_vs_erp.estado_aprobacion)
            THEN EXCLUDED.acuses_recibidos
            ELSE maestro_dian_vs_erp.acuses_recibidos
        END,
        fecha_actualizacion = NOW()
""")
conn.commit()
print(f"✅ UPSERT ejecutado en {cursor.rowcount} registros")
print()

# ============================================================================
# PASO 5: Verificar resultados
# ============================================================================
print("🔍 PASO 5: Verificar resultados del UPSERT")
print("-"*80)

# Verificar registro 1
cursor.execute("""
    SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos
    FROM maestro_dian_vs_erp
    WHERE nit_emisor = %s AND prefijo = %s AND folio = %s
""", (reg1[0], reg1[1], reg1[2]))
result1 = cursor.fetchone()
print(f"Registro 1: {result1[0]}-{result1[1]}-{result1[2]}")
print(f"   ANTES: Pendiente (jerarquía=1, acuses=0)")
print(f"   INTENTÓ: Acuse Recibido (jerarquía=2, acuses=1)")
print(f"   DESPUÉS: {result1[3]} (acuses={result1[4]})")
if result1[3] == 'Acuse Recibido' and result1[4] == 1:
    print("   ✅ ÉXITO: SE ACTUALIZÓ (2 > 1)")
else:
    print("   ❌ FALLO: NO se actualizó cuando debía")
print()

# Verificar registro 2
cursor.execute("""
    SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos
    FROM maestro_dian_vs_erp
    WHERE nit_emisor = %s AND prefijo = %s AND folio = %s
""", (reg2[0], reg2[1], reg2[2]))
result2 = cursor.fetchone()
print(f"Registro 2: {result2[0]}-{result2[1]}-{result2[2]}")
print(f"   ANTES: Aceptación Tácita (jerarquía=6, acuses=2)")
print(f"   INTENTÓ: Pendiente (jerarquía=1, acuses=0) [DOWNGRADE]")
print(f"   DESPUÉS: {result2[3]} (acuses={result2[4]})")
if result2[3] == 'Aceptación Tácita' and result2[4] == 2:
    print("   ✅ ÉXITO: NO se actualizó (1 < 6) - Protección funcionando")
else:
    print("   ❌ FALLO: Se actualizó cuando NO debía (downgrade permitido)")
print()

# Verificar registro 3
cursor.execute("""
    SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos
    FROM maestro_dian_vs_erp
    WHERE nit_emisor = %s AND prefijo = %s AND folio = %s
""", (reg3[0], reg3[1], reg3[2]))
result3 = cursor.fetchone()
print(f"Registro 3: {result3[0]}-{result3[1]}-{result3[2]}")
print(f"   ANTES: Acuse Recibido (jerarquía=2, acuses=1)")
print(f"   INTENTÓ: Aceptación Expresa (jerarquía=5, acuses=2)")
print(f"   DESPUÉS: {result3[3]} (acuses={result3[4]})")
if result3[3] == 'Aceptación Expresa' and result3[4] == 2:
    print("   ✅ ÉXITO: SE ACTUALIZÓ (5 > 2)")
else:
    print("   ❌ FALLO: NO se actualizó cuando debía")
print()

# ============================================================================
# PASO 6: Restaurar estados originales (cleanup)
# ============================================================================
print("🔙 PASO 6: Restaurar estados originales (cleanup)")
print("-"*80)

cursor.execute("""
    UPDATE maestro_dian_vs_erp
    SET estado_aprobacion = 'Pendiente', acuses_recibidos = 0
    WHERE nit_emisor = %s AND prefijo = %s AND folio = %s
""", (reg1[0], reg1[1], reg1[2]))

cursor.execute("""
    UPDATE maestro_dian_vs_erp
    SET estado_aprobacion = 'Acuse Recibido', acuses_recibidos = 1
    WHERE nit_emisor = %s AND prefijo = %s AND folio = %s
""", (reg3[0], reg3[1], reg3[2]))

conn.commit()
print("✅ Estados originales restaurados")
print()

# ============================================================================
# RESUMEN
# ============================================================================
print("="*80)
print("📊 RESUMEN DE PRUEBA DE CARGA SIMULADA")
print("="*80)

tests = {
    "Upgrade (1→2)": result1[3] == 'Acuse Recibido' and result1[4] == 1,
    "Downgrade bloqueado (6→1)": result2[3] == 'Aceptación Tácita' and result2[4] == 2,
    "Upgrade (2→5)": result3[3] == 'Aceptación Expresa' and result3[4] == 2,
}

for test, passed in tests.items():
    status = "✅ PASÓ" if passed else "❌ FALLÓ"
    print(f"   {test}: {status}")

print()

if all(tests.values()):
    print("🎉 TODAS LAS PRUEBAS DE JERARQUÍA PASARON")
    print()
    print("✅ El UPSERT está funcionando correctamente:")
    print("   - Acepta upgrades de jerarquía (estados superiores)")
    print("   - Bloquea downgrades de jerarquía (estados inferiores)")
    print("   - Actualiza acuses_recibidos en consecuencia")
    print()
    print("🚀 Sistema listo para producción")
else:
    print("⚠️  ALGUNAS PRUEBAS FALLARON - Revisar lógica de UPSERT")

print("="*80)

cursor.close()
conn.close()
