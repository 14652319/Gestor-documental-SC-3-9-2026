"""
Script para verificar QUÉ FECHAS hay realmente en PostgreSQL

Consulta DIRECTA sin Flask app context
"""

import psycopg2
from collections import Counter

# Configuración PostgreSQL (tomada del .env)
DB_CONFIG = {
    'dbname': 'gestor_documental',
    'user': 'postgres',
    'password': r'G3st0radm$2025.',  # Raw string para evitar escape
    'host': 'localhost',
    'port': 5432
}

def main():
    try:
        print("\n🔍 Conectando a PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 1. Total de registros
        cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total de registros: {total:,}")
        
        # 2. Primeras 10 fechas + valores
        print("\n📅 PRIMERAS 10 REGISTROS (para ver fechas y valores):")
        print("=" * 80)
        cursor.execute("""
            SELECT id, nit_emisor, prefijo, folio, fecha_emision, valor 
            FROM maestro_dian_vs_erp 
            ORDER BY id 
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            id_reg, nit, prefijo, folio, fecha, valor = row
            print(f"ID: {id_reg:6d} | NIT: {nit:15s} | {prefijo}-{folio:10s} | Fecha: {fecha} | Valor: {valor:>15,.2f}")
        
        # 3. Distribución de fechas (contar cuántos registros por fecha)
        print("\n📆 DISTRIBUCIÓN DE FECHAS (Top 20):")
        print("=" * 80)
        cursor.execute("""
            SELECT fecha_emision, COUNT(*) as cantidad 
            FROM maestro_dian_vs_erp 
            GROUP BY fecha_emision 
            ORDER BY cantidad DESC 
            LIMIT 20
        """)
        
        for fecha, cantidad in cursor.fetchall():
            porcentaje = (cantidad / total * 100) if total > 0 else 0
            print(f"  {fecha} : {cantidad:>8,} registros ({porcentaje:>6.2f}%)")
        
        # 4. ¿Cuántos registros tienen fecha = 2026-02-17?
        cursor.execute("""
            SELECT COUNT(*) 
            FROM maestro_dian_vs_erp 
            WHERE fecha_emision = '2026-02-17'
        """)
        con_17_feb = cursor.fetchone()[0]
        porcentaje_17_feb = (con_17_feb / total * 100) if total > 0 else 0
        
        print(f"\n⚠️  REGISTROS CON FECHA 2026-02-17: {con_17_feb:,} ({porcentaje_17_feb:.2f}%)")
        
        if con_17_feb == total:
            print("\n❌ ¡TODOS LOS REGISTROS TIENEN FECHA 2026-02-17!")
            print("   El reprocesamiento NO aplicó las fechas correctas.")
        elif con_17_feb > 0:
            print(f"\n⚠️  Hay {con_17_feb:,} registros con fecha incorrecta (17-Feb-2026)")
            print("   Pero también hay registros con fechas correctas.")
        else:
            print("\n✅ NO hay registros con fecha 2026-02-17")
            print("   Las fechas están correctas en la BD.")
        
        # 5. Registros con valor = 0
        cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE valor = 0 OR valor IS NULL")
        con_cero = cursor.fetchone()[0]
        print(f"\n💰 REGISTROS CON VALOR = 0: {con_cero:,} ({(con_cero/total*100):.2f}%)")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ Verificación completada")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\nPresiona ENTER para salir...")
