import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno
load_dotenv()

# Conexión a la base de datos
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ No se encontró DATABASE_URL en .env")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

print("=" * 80)
print("🔍 DIAGNÓSTICO: ¿EN QUÉ FECHAS ESTÁN LOS REGISTROS 'CONTADO'?")
print("=" * 80)

with engine.connect() as conn:
    # Obtener rango de fechas con registros Contado
    query = text("""
        SELECT 
            MIN(fecha_emision) as fecha_minima,
            MAX(fecha_emision) as fecha_maxima,
            COUNT(*) as total_contado
        FROM maestro_dian_vs_erp
        WHERE forma_pago = 'Contado'
    """)
    
    result = conn.execute(query).fetchone()
    
    print(f"\n📅 RANGO DE FECHAS CON REGISTROS 'CONTADO':")
    print(f"   Fecha Mínima: {result[0]}")
    print(f"   Fecha Máxima: {result[1]}")
    print(f"   Total:        {result[2]:,}")
    
    # Obtener muestra de 10 registros Contado distribuidos en el tiempo
    query_muestra = text("""
        SELECT 
            nit_emisor,
            nombre_emisor,
            fecha_emision,
            prefijo,
            folio,
            valor,
            forma_pago,
            estado_contable
        FROM maestro_dian_vs_erp
        WHERE forma_pago = 'Contado'
        ORDER BY fecha_emision DESC
        LIMIT 10
    """)
    
    rows = conn.execute(query_muestra).fetchall()
    
    print(f"\n📋 MUESTRA DE 10 REGISTROS 'CONTADO' (más recientes):")
    print("-" * 150)
    print(f"{'NIT':<15} {'Fecha Emisión':<15} {'Prefijo':<10} {'Folio':<12} {'Valor':<15} {'Estado':<20} {'Nombre Emisor':<30}")
    print("-" * 150)
    
    for row in rows:
        nit, nombre, fecha, prefijo, folio, valor, forma_pago, estado = row
        nombre_corto = nombre[:27] + "..." if len(nombre) > 30 else nombre
        print(f"{nit:<15} {str(fecha):<15} {prefijo or 'N/A':<10} {folio:<12} ${valor:>13,.2f} {estado or 'N/A':<20} {nombre_corto:<30}")
    
    # Contar registros Contado por mes
    query_por_mes = text("""
        SELECT 
            DATE_TRUNC('month', fecha_emision) as mes,
            COUNT(*) as registros_contado
        FROM maestro_dian_vs_erp
        WHERE forma_pago = 'Contado'
        GROUP BY DATE_TRUNC('month', fecha_emision)
        ORDER BY mes DESC
        LIMIT 12
    """)
    
    rows_mes = conn.execute(query_por_mes).fetchall()
    
    print(f"\n📅 DISTRIBUCIÓN POR MES (últimos 12 meses con Contado):")
    print("-" * 50)
    print(f"{'Mes':<15} {'Registros Contado':<20}")
    print("-" * 50)
    
    for row in rows_mes:
        mes, registros = row
        mes_str = mes.strftime('%Y-%m')
        print(f"{mes_str:<15} {registros:>15,}")
    
    print("\n" + "=" * 80)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("=" * 80)
    print("\n💡 RECOMENDACIÓN:")
    print("   Si en el visor no ves registros 'Contado', intenta:")
    print("   1. Ampliar el rango de fechas para incluir las fechas arriba mostradas")
    print("   2. Limpiar el filtro del header en la columna 'Forma de Pago' (borrar texto)")
    print("   3. Hacer Ctrl+F5 para limpiar caché del navegador")
    print("   4. Verificar en la consola del navegador (F12) cuántos registros se cargaron")
