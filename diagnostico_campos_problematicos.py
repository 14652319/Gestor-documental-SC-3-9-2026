"""
DIAGNÓSTICO DE CAMPOS PROBLEMÁTICOS
====================================
Analizando los 3 problemas reportados:
1. Campo "Causador" (doc_causado_por) muestra "admin"
2. Razón Social en blanco
3. Estado Aprobación no sigue reglas de acuses
"""

import psycopg2
from datetime import datetime

# Conexión
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = psycopg2.connect(
    host="localhost",
    database="gestor_documental",
    user="gestor_user",
    password="Superadmin123",
    port=5432,
    client_encoding='UTF8'
)
cursor = conn.cursor()

print("=" * 80)
print("🔍 DIAGNÓSTICO DE CAMPOS PROBLEMÁTICOS")
print("=" * 80)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ============================================================================
# PROBLEMA 1: Campo "doc_causado_por" con valor "admin"
# ============================================================================
print("📋 PROBLEMA 1: Campo 'doc_causado_por' mostrando 'admin'")
print("-" * 80)

# Contar registros con doc_causado_por = 'admin'
cursor.execute("""
    SELECT COUNT(*) FROM maestro_dian_vs_erp
    WHERE doc_causado_por = 'admin'
""")
count_admin = cursor.fetchone()[0]
print(f"Total registros con doc_causado_por='admin': {count_admin:,}")

# Ver ejemplos
print("\nEjemplos de registros con 'admin':")
cursor.execute("""
    SELECT 
        nit_emisor,
        razon_social,
        prefijo,
        folio,
        fecha_emision,
        doc_causado_por,
        usuario_causacion,
        modulo,
        estado_contable
    FROM maestro_dian_vs_erp
    WHERE doc_causado_por = 'admin'
    LIMIT 10
""")
for row in cursor.fetchall():
    nit, razon, pref, folio, fecha, doc_caus, usuario_caus, modulo, estado = row
    print(f"  NIT: {nit} | {pref}-{folio} | Fecha: {fecha} | Módulo: {modulo} | Estado: {estado}")
    print(f"    Razón Social: {razon}")
    print(f"    doc_causado_por: '{doc_caus}' | usuario_causacion: '{usuario_caus}'")
    print()

# Contar registros con doc_causado_por en blanco
cursor.execute("""
    SELECT COUNT(*) FROM maestro_dian_vs_erp
    WHERE doc_causado_por IS NULL OR doc_causado_por = ''
""")
count_blank = cursor.fetchone()[0]
print(f"Total registros con doc_causado_por en blanco: {count_blank:,}")

# Contar registros con doc_causado_por correctamente formateado (con guiones)
cursor.execute("""
    SELECT COUNT(*) FROM maestro_dian_vs_erp
    WHERE doc_causado_por LIKE '%-%-%'
""")
count_correcto = cursor.fetchone()[0]
print(f"Total registros con formato correcto (C.O. - Usuario - Nro Doc): {count_correcto:,}")

print()

# ============================================================================
# PROBLEMA 2: Razón Social en blanco
# ============================================================================
print("📋 PROBLEMA 2: Razón Social en blanco")
print("-" * 80)

cursor.execute("""
    SELECT COUNT(*) FROM maestro_dian_vs_erp
    WHERE razon_social IS NULL OR razon_social = '' OR razon_social = 'None'
""")
count_sin_razon = cursor.fetchone()[0]
print(f"Total registros sin razón social: {count_sin_razon:,}")

# Ver ejemplos
print("\nEjemplos de registros sin razón social:")
cursor.execute("""
    SELECT 
        nit_emisor,
        razon_social,
        prefijo,
        folio,
        fecha_emision,
        tipo_tercero,
        modulo
    FROM maestro_dian_vs_erp
    WHERE razon_social IS NULL OR razon_social = '' OR razon_social = 'None'
    LIMIT 10
""")
for row in cursor.fetchall():
    nit, razon, pref, folio, fecha, tipo_terc, modulo = row
    print(f"  NIT: {nit} | {pref}-{folio} | Fecha: {fecha}")
    print(f"    Razón Social: '{razon}' (len={len(str(razon) if razon else '')})")
    print(f"    Tipo Tercero: {tipo_terc} | Módulo: {modulo}")
    print()

print()

# ============================================================================
# PROBLEMA 3: Estado Aprobación no sigue reglas de acuses
# ============================================================================
print("📋 PROBLEMA 3: Coherencia estado_aprobacion vs acuses_recibidos")
print("-" * 80)

# Reglas de validación según documentación
print("\n🔍 Validando reglas de jerarquía de acuses...")
print("Reglas esperadas:")
print("  - Pendiente → 0 acuses")
print("  - Acuse Recibido / Acuse Bien/Servicio / Rechazada → 1 acuse")
print("  - Aceptación Expresa / Aceptación Tácita → 2 acuses")
print()

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
count_incoherentes = cursor.fetchone()[0]
print(f"Total registros con incoherencia: {count_incoherentes:,}")

if count_incoherentes > 0:
    print("\n❌ INCOHERENCIAS ENCONTRADAS - Ejemplos:")
    cursor.execute("""
        SELECT 
            nit_emisor,
            prefijo,
            folio,
            fecha_emision,
            estado_aprobacion,
            acuses_recibidos
        FROM maestro_dian_vs_erp
        WHERE 
          (estado_aprobacion = 'Pendiente' AND acuses_recibidos != 0) OR
          (estado_aprobacion = 'Acuse Recibido' AND acuses_recibidos != 1) OR
          (estado_aprobacion = 'Acuse Bien/Servicio' AND acuses_recibidos != 1) OR
          (estado_aprobacion = 'Rechazada' AND acuses_recibidos != 1) OR
          (estado_aprobacion = 'Aceptación Expresa' AND acuses_recibidos != 2) OR
          (estado_aprobacion = 'Aceptación Tácita' AND acuses_recibidos != 2)
        LIMIT 15
    """)
    for row in cursor.fetchall():
        nit, pref, folio, fecha, estado_aprob, acuses = row
        print(f"  {nit} | {pref}-{folio} | Fecha: {fecha}")
        print(f"    Estado Aprobación: '{estado_aprob}' | Acuses: {acuses}")
        # Validar qué debería ser
        if estado_aprob == 'Pendiente':
            print(f"    ❌ Debería tener 0 acuses, tiene {acuses}")
        elif estado_aprob in ['Acuse Recibido', 'Acuse Bien/Servicio', 'Rechazada']:
            print(f"    ❌ Debería tener 1 acuse, tiene {acuses}")
        elif estado_aprob in ['Aceptación Expresa', 'Aceptación Tácita']:
            print(f"    ❌ Debería tener 2 acuses, tiene {acuses}")
        print()
else:
    print("✅ NO hay incoherencias - Todos los registros son coherentes")

print()

# ============================================================================
# DISTRIBUCIÓN DE ESTADOS
# ============================================================================
print("📊 DISTRIBUCIÓN DE ESTADOS")
print("-" * 80)

print("\nEstado Aprobación:")
cursor.execute("""
    SELECT estado_aprobacion, COUNT(*) as cantidad
    FROM maestro_dian_vs_erp
    GROUP BY estado_aprobacion
    ORDER BY cantidad DESC
""")
for estado, count in cursor.fetchall():
    print(f"  {estado or '(NULL)'}: {count:,} registros")

print("\nEstado Contable:")
cursor.execute("""
    SELECT estado_contable, COUNT(*) as cantidad
    FROM maestro_dian_vs_erp
    GROUP BY estado_contable
    ORDER BY cantidad DESC
""")
for estado, count in cursor.fetchall():
    print(f"  {estado or '(NULL)'}: {count:,} registros")

print()

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("=" * 80)
print("📋 RESUMEN DE PROBLEMAS IDENTIFICADOS")
print("=" * 80)
print(f"1. doc_causado_por='admin': {count_admin:,} registros")
print(f"2. doc_causado_por en blanco: {count_blank:,} registros")
print(f"3. doc_causado_por correcto: {count_correcto:,} registros")
print()
print(f"4. Razón social en blanco: {count_sin_razon:,} registros")
print()
print(f"5. Incoherencias estado_aprobacion vs acuses: {count_incoherentes:,} registros")
print()

# Calcular porcentajes
cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
total_registros = cursor.fetchone()[0]

if total_registros > 0:
    perc_admin = (count_admin / total_registros) * 100
    perc_blank_causador = (count_blank / total_registros) * 100
    perc_correcto = (count_correcto / total_registros) * 100
    perc_sin_razon = (count_sin_razon / total_registros) * 100
    perc_incoherentes = (count_incoherentes / total_registros) * 100
    
    print("PORCENTAJES:")
    print(f"  - doc_causado_por='admin': {perc_admin:.3f}%")
    print(f"  - doc_causado_por en blanco: {perc_blank_causador:.2f}%")
    print(f"  - doc_causado_por correcto: {perc_correcto:.2f}%")
    print(f"  - Sin razón social: {perc_sin_razon:.2f}%")
    print(f"  - Incoherencias acuses: {perc_incoherentes:.3f}%")
    print()

print("=" * 80)

cursor.close()
conn.close()
