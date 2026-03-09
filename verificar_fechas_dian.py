"""
Script para verificar las fechas de los registros DIAN más recientes
y diagnosticar por qué no aparecen en el visor
"""
import psycopg2
from datetime import datetime, timedelta

def verificar_fechas_dian():
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='gestor_documental',
            user='gestor_user',
            password='Gest0rP@ssw0rd2024'
        )
        cur = conn.cursor()
        
        print("=" * 80)
        print("📊 DIAGNÓSTICO DE FECHAS EN TABLA DIAN")
        print("=" * 80)
        
        # 1. Verificar registros del 2026
        cur.execute("""
            SELECT COUNT(*), MIN(fecha_factura), MAX(fecha_factura)
            FROM dian 
            WHERE EXTRACT(YEAR FROM fecha_factura) = 2026
        """)
        row = cur.fetchone()
        print(f"\n🔵 REGISTROS DEL AÑO 2026:")
        print(f"   Total: {row[0]}")
        print(f"   Fecha más antigua: {row[1]}")
        print(f"   Fecha más reciente: {row[2]}")
        
        # 2. Verificar registros del 2025
        cur.execute("""
            SELECT COUNT(*), MIN(fecha_factura), MAX(fecha_factura)
            FROM dian 
            WHERE EXTRACT(YEAR FROM fecha_factura) = 2025
        """)
        row = cur.fetchone()
        print(f"\n🟡 REGISTROS DEL AÑO 2025:")
        print(f"   Total: {row[0]}")
        print(f"   Fecha más antigua: {row[1]}")
        print(f"   Fecha más reciente: {row[2]}")
        
        # 3. Ver los últimos 10 registros insertados (por ID o fecha de carga)
        print(f"\n📋 ÚLTIMOS 10 REGISTROS INSERTADOS (ordenados por ID descendente):")
        cur.execute("""
            SELECT id, nit, razon_social, prefijo, folio, 
                   valor_total, fecha_factura, fecha_vencimiento
            FROM dian 
            ORDER BY id DESC 
            LIMIT 10
        """)
        
        print("\n" + "-" * 120)
        print(f"{'ID':<8} {'NIT':<15} {'Razón Social':<30} {'Prefijo':<8} {'Folio':<12} {'Valor':<15} {'Fecha Fact.':<12} {'Fecha Venc.':<12}")
        print("-" * 120)
        
        for row in cur.fetchall():
            id_val, nit, razon, prefijo, folio, valor, fecha_fact, fecha_venc = row
            print(f"{id_val:<8} {nit:<15} {razon[:30]:<30} {prefijo or '':<8} {folio or '':<12} {valor or 0:<15.2f} {str(fecha_fact):<12} {str(fecha_venc):<12}")
        
        # 4. Verificar distribución de registros por mes en 2026
        print(f"\n📅 DISTRIBUCIÓN DE REGISTROS POR MES EN 2026:")
        cur.execute("""
            SELECT 
                EXTRACT(MONTH FROM fecha_factura) as mes,
                TO_CHAR(fecha_factura, 'Month YYYY') as mes_nombre,
                COUNT(*) as cantidad
            FROM dian 
            WHERE EXTRACT(YEAR FROM fecha_factura) = 2026
            GROUP BY EXTRACT(MONTH FROM fecha_factura), TO_CHAR(fecha_factura, 'Month YYYY')
            ORDER BY EXTRACT(MONTH FROM fecha_factura)
        """)
        
        for row in cur.fetchall():
            mes_num, mes_nombre, cantidad = row
            print(f"   {mes_nombre.strip()}: {cantidad} registros")
        
        # 5. Verificar si hay registros con fecha NULL
        cur.execute("SELECT COUNT(*) FROM dian WHERE fecha_factura IS NULL")
        null_count = cur.fetchone()[0]
        if null_count > 0:
            print(f"\n⚠️  ADVERTENCIA: {null_count} registros tienen fecha_factura NULL")
        
        # 6. Total de registros en la tabla
        cur.execute("SELECT COUNT(*) FROM dian")
        total = cur.fetchone()[0]
        print(f"\n📊 TOTAL DE REGISTROS EN TABLA DIAN: {total}")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ Verificación completada")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_fechas_dian()
