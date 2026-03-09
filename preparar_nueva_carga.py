"""
PREPARAR SISTEMA PARA NUEVA CARGA
==================================
Limpia tabla maestro manteniendo datos de causación
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/gestor_documental')
engine = create_engine(DATABASE_URL)

print("=" * 80)
print("PREPARACIÓN PARA NUEVA CARGA DE ARCHIVOS")
print("=" * 80)

with engine.connect() as conn:
    # 1. Verificar estado actual
    print(f"\n📊 ESTADO ACTUAL:")
    
    # Maestro
    result = conn.execute(text("SELECT COUNT(*) FROM maestro_dian_vs_erp"))
    total_maestro = result.fetchone()[0]
    print(f"   Maestro: {total_maestro:,} registros")
    
    # Con causación
    result = conn.execute(text("""
        SELECT COUNT(*) FROM maestro_dian_vs_erp
        WHERE causada = TRUE 
           OR rechazada = TRUE
           OR doc_causado_por IS NOT NULL
    """))
    con_causacion = result.fetchone()[0]
    print(f"   Con causación: {con_causacion:,} registros")
    
    # DIAN
    result = conn.execute(text("SELECT COUNT(*) FROM dian"))
    total_dian = result.fetchone()[0]
    print(f"   DIAN: {total_dian:,} registros")
    
    # ERP Financiero
    result = conn.execute(text("SELECT COUNT(*) FROM erp_financiero"))
    total_erp_fn = result.fetchone()[0]
    print(f"   ERP Financiero: {total_erp_fn:,} registros")
    
    # ERP Comercial
    result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial"))
    total_erp_cm = result.fetchone()[0]
    print(f"   ERP Comercial: {total_erp_cm:,} registros")
    
    # Acuses
    result = conn.execute(text("SELECT COUNT(*) FROM acuses"))
    total_acuses = result.fetchone()[0]
    print(f"   Acuses: {total_acuses:,} registros")
    
    # 2. Hacer backup de causación si existe
    if con_causacion > 0:
        print(f"\n💾 RESPALDANDO DATOS DE CAUSACIÓN...")
        conn.execute(text("DROP TABLE IF EXISTS backup_causacion_temp"))
        conn.execute(text("""
            CREATE TABLE backup_causacion_temp AS
            SELECT 
                nit_emisor,
                prefijo,
                folio,
                causada,
                fecha_causacion,
                usuario_causacion,
                doc_causado_por,
                recibida,
                fecha_recibida,
                usuario_recibio,
                rechazada,
                fecha_rechazo,
                motivo_rechazo,
                estado_contable,
                origen_sincronizacion
            FROM maestro_dian_vs_erp
            WHERE causada = TRUE 
               OR rechazada = TRUE
               OR doc_causado_por IS NOT NULL
        """))
        conn.commit()
        print(f"   ✅ {con_causacion:,} registros respaldados en backup_causacion_temp")
    
    # 3. Opción de limpieza
    print(f"\n⚠️  OPCIONES DE LIMPIEZA:")
    print(f"\n   1️⃣ LIMPIEZA COMPLETA (TODO de cero):")
    print(f"      - Borra DIAN, ERP, ACUSES, MAESTRO")
    print(f"      - Debes cargar todos los archivos nuevamente")
    print(f"      - Recomendado si quieres probar desde cero")
    
    print(f"\n   2️⃣ LIMPIEZA SOLO MAESTRO (más rápido):")
    print(f"      - Mantiene DIAN, ERP, ACUSES")
    print(f"      - Solo procesa nuevamente desde interfaz web")
    print(f"      - Recomendado si los archivos ya están cargados")
    
    print(f"\n   3️⃣ NO LIMPIAR (solo actualizar CUFE):")
    print(f"      - Ejecutar SOLUCIONAR_CUFE_ESTADOS.sql")
    print(f"      - No requiere re-cargar archivos")

print(f"\n" + "=" * 80)
print("INSTRUCCIONES:")
print("=" * 80)
print(f"""
Para hacer una carga limpia completa:

1️⃣ EJECUTAR LIMPIEZA (desde pgAdmin o psql):

   -- Opción 1: LIMPIEZA COMPLETA
   DELETE FROM maestro_dian_vs_erp;
   DELETE FROM dian;
   DELETE FROM erp_financiero;
   DELETE FROM erp_comercial;
   DELETE FROM acuses;
   
   -- Opción 2: SOLO MAESTRO (más rápido)
   DELETE FROM maestro_dian_vs_erp;

2️⃣ CARGAR ARCHIVOS desde interfaz web:
   
   • Ir a: http://localhost:8099/dian_vs_erp/
   • Click en "Procesar Archivos"
   • Seleccionar archivos:
     ✅ DIAN: uploads/dian/Dian.xlsx
     ✅ ERP Financiero: uploads/erp_fn/ERP_Financiero_18_02_2026.xlsx
     ✅ ERP Comercial: uploads/erp_cm/ERP_comercial_18_02_2026.xlsx
     ✅ ACUSES: uploads/acuses/acuses_2.xlsx
   
   • Click "Procesar"
   • Esperar a que termine (2-3 minutos)

3️⃣ VERIFICAR RESULTADOS:
   
   • Ir a Visor V2
   • Verificar columna "Estado Aprobación"
   • Deberías ver:
     ✅ Acuse Bien/Servicio
     ✅ Aceptación Expresa
     ✅ Acuse Recibido
     ✅ etc.
   
   En lugar de solo "No Registra"

4️⃣ SI HAY DATOS DE CAUSACIÓN RESPALDADOS:
   
   Después de procesar, ejecutar:
   
   UPDATE maestro_dian_vs_erp m
   SET causada = b.causada,
       fecha_causacion = b.fecha_causacion,
       usuario_causacion = b.usuario_causacion,
       doc_causado_por = b.doc_causado_por,
       recibida = b.recibida,
       fecha_recibida = b.fecha_recibida,
       usuario_recibio = b.usuario_recibio,
       rechazada = b.rechazada,
       fecha_rechazo = b.fecha_rechazo,
       motivo_rechazo = b.motivo_rechazo,
       estado_contable = b.estado_contable,
       origen_sincronizacion = b.origen_sincronizacion
   FROM backup_causacion_temp b
   WHERE m.nit_emisor = b.nit_emisor
     AND m.prefijo = b.prefijo
     AND m.folio = b.folio;
""")

print("=" * 80)

# 4. Crear script SQL automático
print(f"\n📝 CREANDO SCRIPT SQL...")

sql_content = """-- SCRIPT DE LIMPIEZA PARA NUEVA CARGA
-- Fecha: 19 de febrero, 2026
-- ======================================

-- PASO 1: Respaldar datos de causación (si existen)
DROP TABLE IF EXISTS backup_causacion_temp;

CREATE TABLE backup_causacion_temp AS
SELECT 
    nit_emisor, prefijo, folio,
    causada, fecha_causacion, usuario_causacion, doc_causado_por,
    recibida, fecha_recibida, usuario_recibio,
    rechazada, fecha_rechazo, motivo_rechazo,
    estado_contable, origen_sincronizacion
FROM maestro_dian_vs_erp
WHERE causada = TRUE 
   OR rechazada = TRUE
   OR doc_causado_por IS NOT NULL;

-- PASO 2: Limpiar tablas
-- Opción A: LIMPIEZA COMPLETA (descomentar si quieres empezar de cero)
-- DELETE FROM dian;
-- DELETE FROM erp_financiero;
-- DELETE FROM erp_comercial;
-- DELETE FROM acuses;
-- DELETE FROM maestro_dian_vs_erp;

-- Opción B: SOLO MAESTRO (recomendado si ya tienes los datos cargados)
DELETE FROM maestro_dian_vs_erp;

-- PASO 3: Verificar limpieza
SELECT 'DIAN' as tabla, COUNT(*) as registros FROM dian
UNION ALL
SELECT 'ERP Financiero', COUNT(*) FROM erp_financiero
UNION ALL
SELECT 'ERP Comercial', COUNT(*) FROM erp_comercial
UNION ALL
SELECT 'Acuses', COUNT(*) FROM acuses
UNION ALL
SELECT 'Maestro', COUNT(*) FROM maestro_dian_vs_erp
UNION ALL
SELECT 'Backup Causación', COUNT(*) FROM backup_causacion_temp;

-- ======================================
-- DESPUÉS DE PROCESAR DESDE LA WEB:
-- ======================================

-- PASO 4: Restaurar datos de causación (ejecutar DESPUÉS de procesar)
-- UPDATE maestro_dian_vs_erp m
-- SET causada = b.causada,
--     fecha_causacion = b.fecha_causacion,
--     usuario_causacion = b.usuario_causacion,
--     doc_causado_por = b.doc_causado_por,
--     recibida = b.recibida,
--     fecha_recibida = b.fecha_recibida,
--     usuario_recibio = b.usuario_recibio,
--     rechazada = b.rechazada,
--     fecha_rechazo = b.fecha_rechazo,
--     motivo_rechazo = b.motivo_rechazo,
--     estado_contable = b.estado_contable,
--     origen_sincronizacion = b.origen_sincronizacion
-- FROM backup_causacion_temp b
-- WHERE m.nit_emisor = b.nit_emisor
--   AND m.prefijo = b.prefijo
--   AND m.folio = b.folio;

-- PASO 5: Verificar resultados finales
SELECT 
    estado_aprobacion,
    COUNT(*) as cantidad,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as porcentaje
FROM maestro_dian_vs_erp
GROUP BY estado_aprobacion
ORDER BY cantidad DESC;

-- Verificar CUFEs
SELECT 
    'Con CUFE' as descripcion,
    COUNT(*) as cantidad
FROM maestro_dian_vs_erp
WHERE cufe IS NOT NULL AND cufe != ''
UNION ALL
SELECT 
    'Con estado != No Registra',
    COUNT(*)
FROM maestro_dian_vs_erp
WHERE estado_aprobacion != 'No Registra';
"""

with open('LIMPIAR_PARA_NUEVA_CARGA.sql', 'w', encoding='utf-8') as f:
    f.write(sql_content)

print(f"✅ Script creado: LIMPIAR_PARA_NUEVA_CARGA.sql")
print("=" * 80)
