"""
Verificar campo tipos_tercero en envíos programados
"""
import psycopg2
import json

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='gestor_documental',
    user='postgres',
    password='G3st0radm$2025.'
)
cursor = conn.cursor()

print("\n" + "="*100)
print("🔍 VERIFICACIÓN DEL CAMPO 'tipos_tercero' EN ENVÍOS PROGRAMADOS")
print("="*100 + "\n")

# 1. Verificar si existe la columna
print("1️⃣ VERIFICAR SI EXISTE LA COLUMNA EN LA TABLA")
print("-"*100)

cursor.execute("""
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name = 'envios_programados_dian_vs_erp' 
    AND column_name = 'tipos_tercero'
""")
columna = cursor.fetchone()

if columna:
    print(f"✅ La columna 'tipos_tercero' SÍ EXISTE en la tabla")
    print(f"   • Nombre: {columna[0]}")
    print(f"   • Tipo de dato: {columna[1]}")
    print(f"   • Permite NULL: {columna[2]}")
else:
    print("❌ La columna 'tipos_tercero' NO EXISTE en la tabla")
    print("\n⚠️ ADVERTENCIA: El campo no está definido en la base de datos")
    cursor.close()
    conn.close()
    exit(1)

# 2. Consultar configuraciones con valores en tipos_tercero
print("\n\n2️⃣ CONSULTAR CONFIGURACIONES CON VALORES EN 'tipos_tercero'")
print("-"*100)

cursor.execute("""
    SELECT 
        id,
        nombre,
        tipos_tercero,
        activo
    FROM envios_programados_dian_vs_erp
    WHERE tipos_tercero IS NOT NULL AND tipos_tercero != ''
    ORDER BY id
""")
configs_con_tipos = cursor.fetchall()

if configs_con_tipos:
    print(f"\n✅ {len(configs_con_tipos)} configuraciones CON valores en 'tipos_tercero':\n")
    
    for cfg in configs_con_tipos:
        id_, nombre, tipos_tercero, activo = cfg
        estado = "✅ ACTIVA" if activo else "⚪ INACTIVA"
        
        print(f"📌 ID {id_}: {nombre}")
        print(f"   Estado: {estado}")
        print(f"   Tipos de tercero (JSON): {tipos_tercero}")
        
        # Intentar parsear el JSON
        try:
            tipos_list = json.loads(tipos_tercero)
            print(f"   Tipos parseados: {', '.join(tipos_list)}")
        except:
            print(f"   ⚠️ No se pudo parsear como JSON")
        
        print()
else:
    print("\n⚪ NO hay configuraciones con valores en 'tipos_tercero'")
    print("   (Todas las configuraciones tienen este campo NULL o vacío)")

# 3. Consultar configuraciones SIN valores en tipos_tercero
print("\n3️⃣ CONSULTAR CONFIGURACIONES SIN VALORES EN 'tipos_tercero'")
print("-"*100)

cursor.execute("""
    SELECT 
        id,
        nombre,
        activo
    FROM envios_programados_dian_vs_erp
    WHERE tipos_tercero IS NULL OR tipos_tercero = ''
    ORDER BY id
""")
configs_sin_tipos = cursor.fetchall()

if configs_sin_tipos:
    print(f"\n⚪ {len(configs_sin_tipos)} configuraciones SIN valores en 'tipos_tercero':\n")
    
    for cfg in configs_sin_tipos:
        id_, nombre, activo = cfg
        estado = "✅ ACTIVA" if activo else "⚪ INACTIVA"
        print(f"   • ID {id_}: {nombre} ({estado})")
else:
    print("\n✅ Todas las configuraciones tienen valores en 'tipos_tercero'")

# 4. Resumen estadístico
print("\n\n4️⃣ RESUMEN ESTADÍSTICO")
print("-"*100)

cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN tipos_tercero IS NOT NULL AND tipos_tercero != '' THEN 1 ELSE 0 END) as con_tipos,
        SUM(CASE WHEN tipos_tercero IS NULL OR tipos_tercero = '' THEN 1 ELSE 0 END) as sin_tipos
    FROM envios_programados_dian_vs_erp
""")
stats = cursor.fetchone()

total, con_tipos, sin_tipos = stats

print(f"\n📊 Total de configuraciones: {total}")
print(f"   ✅ Con tipos de tercero definidos: {con_tipos} ({(con_tipos*100//total if total > 0 else 0)}%)")
print(f"   ⚪ Sin tipos de tercero: {sin_tipos} ({(sin_tipos*100//total if total > 0 else 0)}%)")

# 5. Valores únicos encontrados
print("\n\n5️⃣ VALORES ÚNICOS ENCONTRADOS EN 'tipos_tercero'")
print("-"*100)

cursor.execute("""
    SELECT DISTINCT tipos_tercero
    FROM envios_programados_dian_vs_erp
    WHERE tipos_tercero IS NOT NULL AND tipos_tercero != ''
""")
valores_unicos = cursor.fetchall()

if valores_unicos:
    print(f"\n🎯 {len(valores_unicos)} valores únicos encontrados:\n")
    
    for i, (valor,) in enumerate(valores_unicos, 1):
        print(f"{i}. {valor}")
        try:
            tipos_list = json.loads(valor)
            print(f"   → Tipos: {', '.join(tipos_list)}")
        except:
            print(f"   ⚠️ No es JSON válido")
        print()
else:
    print("\n⚪ No hay valores únicos (todas las configuraciones tienen NULL o vacío)")

# 6. Conclusión
print("\n" + "="*100)
print("📋 CONCLUSIÓN")
print("="*100)

if columna:
    print("\n✅ El campo 'tipos_tercero' SÍ está definido en la base de datos")
else:
    print("\n❌ El campo 'tipos_tercero' NO está definido en la base de datos")

if con_tipos > 0:
    print(f"✅ El campo SÍ se está usando ({con_tipos} configuraciones lo tienen)")
    print("✅ El formulario frontend está funcionando correctamente")
else:
    print("⚠️ El campo NO se está usando (ninguna configuración tiene valores)")
    print("⚠️ Posible problema en el frontend o en el endpoint de guardado")

print("\n" + "="*100 + "\n")

cursor.close()
conn.close()
