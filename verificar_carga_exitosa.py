"""
VERIFICACIÓN POST-CARGA - Script rápido para validar datos
Febrero 23, 2026
"""
import psycopg2
from datetime import datetime

print("=" * 80)
print("VERIFICACIÓN POST-CARGA DE DATOS DIAN")
print("=" * 80)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Conectar a base de datos
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="gestor_documental",
        user="postgres",
        password="G3st0radm$2025."
    )
    cursor = conn.cursor()
    print("\n✅ Conexión a base de datos exitosa")
except Exception as e:
    print(f"\n❌ Error de conexión: {e}")
    exit(1)

try:
    # 1. TOTAL DE REGISTROS
    print("\n" + "=" * 80)
    print("1. CONTEO DE REGISTROS")
    print("=" * 80)
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
    total = cursor.fetchone()[0]
    print(f"Total registros en maestro_dian_vs_erp: {total:,}")
    
    if total == 0:
        print("\n⚠️  TABLA VACÍA - No se cargaron datos")
        print("   Acciones:")
        print("   1. Verificar que el servidor esté corriendo")
        print("   2. Cargar archivos por navegador")
        print("   3. Ejecutar este script nuevamente")
        exit(0)
    elif total < 50000:
        print(f"⚠️  POCOS REGISTROS - Se esperaban ~66,000, hay {total:,}")
    else:
        print(f"✅ CANTIDAD CORRECTA - {total:,} registros cargados")
    
    # 2. VERIFICAR PREFIJOS
    print("\n" + "=" * 80)
    print("2. VERIFICACIÓN DE PREFIJOS")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN prefijo IS NULL OR prefijo = '' THEN 1 END) as nulos,
            COUNT(CASE WHEN prefijo IS NOT NULL AND prefijo != '' THEN 1 END) as validos
        FROM maestro_dian_vs_erp
    """)
    row = cursor.fetchone()
    total_reg, nulos, validos = row
    
    print(f"Total registros: {total_reg:,}")
    print(f"Prefijos NULL o vacíos: {nulos:,} ({nulos*100/total_reg:.1f}%)")
    print(f"Prefijos válidos: {validos:,} ({validos*100/total_reg:.1f}%)")
    
    if nulos > total_reg * 0.5:  # Más del 50% nulos
        print("❌ CRÍTICO - Mayoría de prefijos son NULL/vacíos")
        print("   → El servidor NO se reinició correctamente")
        print("   → Cerrar TODOS los procesos Python y reiniciar")
    elif nulos > 0:
        print(f"⚠️  ADVERTENCIA - {nulos:,} registros sin prefijo (posiblemente válido)")
    else:
        print("✅ PERFECTO - Todos los registros tienen prefijo")
    
    # Muestra de prefijos
    cursor.execute("""
        SELECT prefijo, COUNT(*) as cantidad
        FROM maestro_dian_vs_erp
        WHERE prefijo IS NOT NULL AND prefijo != ''
        GROUP BY prefijo
        ORDER BY cantidad DESC
        LIMIT 10
    """)
    print("\nPrefijos más comunes:")
    for prefijo, cantidad in cursor.fetchall():
        print(f"   '{prefijo}': {cantidad:,} registros")
    
    # 3. VERIFICAR FOLIOS
    print("\n" + "=" * 80)
    print("3. VERIFICACIÓN DE FOLIOS")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN folio IS NULL OR folio = '' OR folio = '0' THEN 1 END) as invalidos,
            COUNT(CASE WHEN folio IS NOT NULL AND folio != '' AND folio != '0' THEN 1 END) as validos
        FROM maestro_dian_vs_erp
    """)
    row = cursor.fetchone()
    total_reg, invalidos, validos = row
    
    print(f"Total registros: {total_reg:,}")
    print(f"Folios NULL/'0'/vacíos: {invalidos:,} ({invalidos*100/total_reg:.1f}%)")
    print(f"Folios válidos: {validos:,} ({validos*100/total_reg:.1f}%)")
    
    if invalidos > total_reg * 0.5:
        print("❌ CRÍTICO - Mayoría de folios son '0' o NULL")
    elif invalidos > 0:
        print(f"⚠️  {invalidos:,} registros con folio inválido")
    else:
        print("✅ PERFECTO - Todos los registros tienen folio válido")
    
    # 4. VERIFICAR TOTALES/VALORES
    print("\n" + "=" * 80)
    print("4. VERIFICACIÓN DE VALORES (TOTAL)")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN valor IS NULL OR valor = 0 THEN 1 END) as ceros,
            COUNT(CASE WHEN valor > 0 THEN 1 END) as validos,
            MIN(valor) as min_valor,
            MAX(valor) as max_valor,
            AVG(valor) as promedio
        FROM maestro_dian_vs_erp
    """)
    row = cursor.fetchone()
    total_reg, ceros, validos, min_val, max_val, promedio = row
    
    print(f"Total registros: {total_reg:,}")
    print(f"Valores 0 o NULL: {ceros:,} ({ceros*100/total_reg:.1f}%)")
    print(f"Valores > 0: {validos:,} ({validos*100/total_reg:.1f}%)")
    print(f"Valor mínimo: ${min_val:,.2f}")
    print(f"Valor máximo: ${max_val:,.2f}")
    print(f"Valor promedio: ${promedio:,.2f}")
    
    if ceros > total_reg * 0.5:
        print("❌ CRÍTICO - Mayoría de valores son 0")
    elif ceros > 0:
        print(f"⚠️  {ceros:,} registros con valor 0 (puede ser válido)")
    else:
        print("✅ PERFECTO - Todos los registros tienen valor > 0")
    
    # 5. VERIFICAR FECHAS
    print("\n" + "=" * 80)
    print("5. VERIFICACIÓN DE FECHAS DE EMISIÓN")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            MIN(fecha_emision) as fecha_min,
            MAX(fecha_emision) as fecha_max,
            COUNT(CASE WHEN fecha_emision = CURRENT_DATE THEN 1 END) as hoy
        FROM maestro_dian_vs_erp
    """)
    row = cursor.fetchone()
    total_reg, fecha_min, fecha_max, hoy = row
    
    print(f"Total registros: {total_reg:,}")
    print(f"Fecha más antigua: {fecha_min}")
    print(f"Fecha más reciente: {fecha_max}")
    print(f"Registros con fecha de hoy ({datetime.now().date()}): {hoy:,}")
    
    if hoy > total_reg * 0.9:  # Más del 90% con fecha de hoy
        print("❌ CRÍTICO - Casi todos los registros tienen fecha de hoy")
        print("   → Error en lectura de fechas del Excel")
    elif hoy > total_reg * 0.1:  # Más del 10% con fecha de hoy
        print(f"⚠️  {hoy:,} registros con fecha de hoy (verificar si es correcto)")
    else:
        print("✅ FECHAS CORRECTAS - Distribución normal")
    
    # 6. MUESTRA DE DATOS
    print("\n" + "=" * 80)
    print("6. MUESTRA DE PRIMEROS 10 REGISTROS")
    print("=" * 80)
    
    cursor.execute("""
        SELECT id, nit_emisor, nombre_emisor, prefijo, folio, valor, fecha_emision
        FROM maestro_dian_vs_erp
        ORDER BY id
        LIMIT 10
    """)
    
    print(f"\n{'ID':<8} {'NIT':<12} {'Nombre':<30} {'Prefijo':<8} {'Folio':<10} {'Valor':<15} {'Fecha'}")
    print("-" * 110)
    
    errores_muestra = 0
    for row in cursor.fetchall():
        id_reg, nit, nombre, prefijo, folio, valor, fecha = row
        
        # Verificar si hay errores en este registro
        errores = []
        if not prefijo or prefijo == '':
            errores.append("PREFIJO_VACIO")
        if not folio or folio == '0':
            errores.append("FOLIO_0")
        if not valor or valor == 0:
            errores.append("VALOR_0")
        if fecha == datetime.now().date():
            errores.append("FECHA_HOY")
        
        if errores:
            errores_muestra += 1
            estado = "❌"
        else:
            estado = "✅"
        
        nombre_corto = nombre[:28] + ".." if len(nombre) > 30 else nombre
        prefijo_str = prefijo if prefijo else "NULL"
        folio_str = folio if folio else "NULL"
        valor_str = f"${valor:,.2f}" if valor else "$0.00"
        
        print(f"{id_reg:<8} {nit:<12} {nombre_corto:<30} {prefijo_str:<8} {folio_str:<10} {valor_str:<15} {fecha} {estado}")
    
    # 7. RESUMEN FINAL
    print("\n" + "=" * 80)
    print("7. RESUMEN FINAL")
    print("=" * 80)
    
    # Calcular score general
    problemas = []
    
    if total < 50000:
        problemas.append(f"Pocos registros ({total:,})")
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE prefijo IS NULL OR prefijo = ''")
    prefijos_malos = cursor.fetchone()[0]
    if prefijos_malos > total * 0.1:
        problemas.append(f"Prefijos NULL ({prefijos_malos:,})")
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE folio IS NULL OR folio = '' OR folio = '0'")
    folios_malos = cursor.fetchone()[0]
    if folios_malos > total * 0.1:
        problemas.append(f"Folios inválidos ({folios_malos:,})")
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE valor IS NULL OR valor = 0")
    valores_malos = cursor.fetchone()[0]
    if valores_malos > total * 0.1:
        problemas.append(f"Valores 0 ({valores_malos:,})")
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE fecha_emision = CURRENT_DATE")
    fechas_hoy = cursor.fetchone()[0]
    if fechas_hoy > total * 0.5:
        problemas.append(f"Fechas incorrectas ({fechas_hoy:,})")
    
    if not problemas:
        print("\n✅✅✅ CARGA EXITOSA - TODOS LOS DATOS CORRECTOS ✅✅✅")
        print(f"\nTotal registros: {total:,}")
        print("Todos los campos críticos están correctos")
        print("\n🎉 SISTEMA LISTO PARA USAR 🎉")
    else:
        print("\n❌ PROBLEMAS DETECTADOS:")
        for problema in problemas:
            print(f"   • {problema}")
        
        print("\n🔧 ACCIONES RECOMENDADAS:")
        print("   1. Cerrar TODOS los procesos Python")
        print("   2. Verificar que routes.py tiene el código actualizado")
        print("   3. Reiniciar servidor: .\\1_iniciar_gestor.bat")
        print("   4. Borrar tabla: DELETE FROM maestro_dian_vs_erp;")
        print("   5. Cargar archivos nuevamente por navegador")
        print("   6. Ejecutar este script otra vez")
    
    print("\n" + "=" * 80)

finally:
    cursor.close()
    conn.close()
