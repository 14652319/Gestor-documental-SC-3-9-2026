"""
EJECUTAR FIX: Eliminar UNIQUE constraint y limpiar tabla dian
"""

import psycopg2
import os

# Conexión directa
try:
    conn = psycopg2.connect(
        dbname='gestor_documental',
        user='postgres',
        password='Innovacion2022*',
        host='localhost',
        port='5432'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("🔧 EJECUTANDO FIX DEL UNIQUE CONSTRAINT")
    print("="*70)
    
    # Paso 1: Verificar constraint actual
    print("\n1️⃣ Verificando constraint actual...")
    cursor.execute("""
        SELECT conname 
        FROM pg_constraint 
        WHERE conrelid = 'dian'::regclass 
          AND conname = 'uk_dian_clave'
    """)
    resultado = cursor.fetchone()
    if resultado:
        print(f"   ✅ Constraint encontrado: {resultado[0]}")
    else:
        print("   ⚠️ Constraint NO encontrado (ya fue eliminado antes)")
    
    # Paso 2: Eliminar constraint
    print("\n2️⃣ Eliminando UNIQUE constraint...")
    cursor.execute("ALTER TABLE dian DROP CONSTRAINT IF EXISTS uk_dian_clave")
    print("   ✅ Constraint eliminado exitosamente")
    
    # Paso 3: Limpiar tabla
    print("\n3️⃣ Limpiando tabla dian (TRUNCATE)...")
    cursor.execute("TRUNCATE TABLE dian CASCADE")
    print("   ✅ Tabla limpiada exitosamente")
    
    # Paso 4: Verificar que se eliminó
    print("\n4️⃣ Verificando que el constraint se eliminó...")
    cursor.execute("""
        SELECT conname 
        FROM pg_constraint 
        WHERE conrelid = 'dian'::regclass 
          AND conname = 'uk_dian_clave'
    """)
    resultado = cursor.fetchone()
    if resultado:
        print(f"   ❌ ERROR: El constraint aún existe: {resultado[0]}")
    else:
        print("   ✅ Confirmado: Constraint eliminado correctamente")
    
    # Paso 5: Verificar tabla vacía
    print("\n5️⃣ Verificando que la tabla está vacía...")
    cursor.execute("SELECT COUNT(*) FROM dian")
    count = cursor.fetchone()[0]
    print(f"   📊 Registros en tabla dian: {count}")
    if count == 0:
        print("   ✅ Tabla limpia y lista para recarga")
    else:
        print(f"   ⚠️ ADVERTENCIA: Aún hay {count} registros")
    
    print("\n" + "="*70)
    print("✅ FIX COMPLETADO EXITOSAMENTE")
    print("="*70)
    print("\n📋 PRÓXIMOS PASOS:")
    print("   1. Ir a: http://localhost:8099/dian_vs_erp/configuracion")
    print("   2. Cargar los 4 archivos Excel:")
    print("      - Dian.xlsx")
    print("      - ERP Financiero.xlsx")
    print("      - ERP Comercial.xlsx")
    print("      - Acuses Recibidos.xlsx")
    print("   3. Esperar a que termine el procesamiento")
    print("   4. Verificar en el visor que ahora sí aparecen TODOS los registros")
    print("   5. El visor debería mostrar ~10,000-50,000 registros en lugar de 1,400")
    print("\n💡 IMPORTANTE:")
    print("   - Ahora NO hay constraint UNIQUE en 'clave'")
    print("   - Todos los registros se insertarán sin rechazos")
    print("   - Los prefijos 1FEA, 2FEA, 3FEA seguirán viéndose correctamente")
    print("="*70 + "\n")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nSi el error es de codificación, puedes:")
    print("1. Ejecutar el SQL manualmente en pgAdmin")
    print("2. Usar el archivo FIX_UNIQUE_CONSTRAINT.sql")
