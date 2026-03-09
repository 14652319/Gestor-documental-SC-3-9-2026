"""
PROBLEMA ENCONTRADO Y SOLUCION

EL PROBLEMA:
============
En el archivo routes.py, linea 1307-1312, el sistema usa:

    INSERT INTO dian (...)
    SELECT ... FROM temp_dian_nuevos
    ON CONFLICT (clave) DO NOTHING
                         ^^^^^^^^^^
Esto significa: Si la clave ya existe, se IGNORA el nuevo registro.

CAUSA:
======
Si el archivo Excel tiene prefijos NULL o vacios, muchas facturas
del mismo NIT generan la MISMA clave:

  Factura 1: NIT=805013653, Prefijo=NULL, Folio=37 
    -> clave = "80501365337" (PRIMERA, se inserta)
  
  Factura 2: NIT=805013653, Prefijo=NULL, Folio=37 (misma)
    -> clave = "80501365337" (DUPLICADA, se IGNORA)

Resultado: Solo 1 factura por NIT se inserta.

SOLUCION RECOMENDADA:
=====================
Eliminar el UNIQUE constraint en la columna 'clave'.

El CUFE/CUDE es el identificador UNICO OFICIAL de DIAN.
La columna 'clave' es solo para cross-reference interno.
No necesita ser UNIQUE en la base de datos.

PASOS A SEGUIR:
===============
1. Conectarse a pgAdmin
2. Abrir SQL Query Tool en la base de datos 'gestor_documental'
3. Ejecutar estos comandos:

-- Paso 1: Eliminar el constraint UNIQUE
ALTER TABLE dian DROP CONSTRAINT IF EXISTS uk_dian_clave;

-- Paso 2: Limpiar la tabla para recargar
TRUNCATE TABLE dian CASCADE;

-- Paso 3: Verificar que se elimino
SELECT conname, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'dian'::regclass AND conname = 'uk_dian_clave';

4. Luego recargar TODOS los archivos desde la interfaz web
5. Verificar que ahora se carguen TODOS los registros

COMANDO PARA EJECUTAR EN pgAdmin:
=================================
"""

print(__doc__)

# Generar el SQL
sql_fix = """
-- ============================================
-- SOLUCION: Eliminar UNIQUE constraint en clave
-- ============================================

-- 1. Eliminar constraint UNIQUE
ALTER TABLE dian DROP CONSTRAINT IF EXISTS uk_dian_clave;

-- 2. Limpiar tabla para recarga completa
TRUNCATE TABLE dian CASCADE;

-- 3. Verificar que se elimino (debe retornar 0 filas)
SELECT conname, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'dian'::regclass 
  AND conname = 'uk_dian_clave';

-- 4. Ver estructura actual de la tabla
SELECT 
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as definition
FROM pg_constraint 
WHERE conrelid = 'dian'::regclass
ORDER BY contype;

"""

# Guardar SQL en archivo
with open('FIX_UNIQUE_CONSTRAINT.sql', 'w', encoding='utf-8') as f:
    f.write(sql_fix)

print("\n✅ Archivo SQL generado: FIX_UNIQUE_CONSTRAINT.sql")
print("\n📋 INSTRUCCIONES:")
print("   1. Abrir pgAdmin")
print("   2. Conectar a base de datos 'gestor_documental'")
print("   3. Abrir Query Tool (Tools > Query Tool)")
print("   4. Abrir el archivo FIX_UNIQUE_CONSTRAINT.sql")
print("   5. Ejecutar el SQL (F5 o boton Execute)")
print("   6. Recargar archivos desde la interfaz web")
print("   7. Verificar que ahora se carguen TODOS los registros")

print("\n" + "="*60)
print("RESUMEN DEL PROBLEMA:")
print("="*60)
print(f"❌ Situacion actual: Solo 1,400 registros (1 por NIT)")
print(f"✅ Situacion esperada: ~10,000-50,000 registros")
print(f"🔍 Causa: UNIQUE constraint en 'clave' rechaza duplicados")
print(f"💡 Solucion: Eliminar el constraint y recargar datos")
print("="*60)
