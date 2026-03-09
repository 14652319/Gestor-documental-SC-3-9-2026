"""
Script para descubrir columnas de tablas y buscar datos de 2026
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

tablas = ['acuses', 'erp_financiero', 'erp_comercial']

print("=" * 100)
print("🔍 DESCUBRIENDO ESTRUCTURA DE TABLAS Y BUSCANDO DATOS 2026")
print("=" * 100)

datos_2026_encontrados = []

with engine.connect() as conn:
    for tabla in tablas:
        try:
            print(f"\n📋 Tabla: {tabla.upper()}")
            print("-" * 100)
            
            # Obtener columnaspor table
            result = conn.execute(text(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{tabla}'
                ORDER BY ordinal_position
            """))
            
            columnas = list(result)
            print(f"\n   Columnas ({len(columnas)}):")
            
            columnas_fecha = []
            for col in columnas:
                print(f"      • {col[0]} ({col[1]})")
                # Detectar columnas de tipo fecha
                if col[1] in ('date', 'timestamp without time zone', 'timestamp with time zone'):
                    columnas_fecha.append(col[0])
            
            # Contar registros totales
            result = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
            total = result.fetchone()[0]
            print(f"\n   Total registros: {total:,}")
            
            # Si hay columnas de fecha, buscar datos de 2026
            if columnas_fecha:
                print(f"\n   ✅ Columnas de fecha encontradas: {', '.join(columnas_fecha)}")
                
                for col_fecha in columnas_fecha:
                    try:
                        result = conn.execute(text(f"""
                            SELECT COUNT(*) 
                            FROM {tabla}
                            WHERE {col_fecha} >= '2026-01-01' 
                              AND {col_fecha} < '2027-01-01'
                        """))
                        count_2026 = result.fetchone()[0]
                        
                        if count_2026 > 0:
                            print(f"      ⚠️  {col_fecha}: {count_2026:,} registros de 2026")
                            datos_2026_encontrados.append({
                                'tabla': tabla,
                                'columna': col_fecha,
                                'cantidad': count_2026,
                                'total': total
                            })
                            
                            # Mostrar ejemplos
                            result = conn.execute(text(f"""
                                SELECT * FROM {tabla}
                                WHERE {col_fecha} >= '2026-01-01' 
                                  AND {col_fecha} < '2027-01-01'
                                LIMIT 2
                            """))
                            
                            print(f"\n      📄 Ejemplos de registros 2026:")
                            for i, row in enumerate(result, 1):
                                row_dict = dict(row)
                                # Mostrar solo primeros 5 campos
                                campos_mostrar = list(row_dict.items())[:5]
                                print(f"         {i}. {dict(campos_mostrar)}")
                        else:
                            print(f"      ✅ {col_fecha}: 0 registros de 2026")
                            
                    except Exception as e:
                        conn.rollback()
                        print(f"      ❌ Error verificando {col_fecha}: {str(e)[:100]}")
            else:
                print(f"\n   ⚠️  No se encontraron columnas de fecha")
                print(f"      Esta tabla puede no tener fechas o usa otro formato")
            
        except Exception as e:
            conn.rollback()
            print(f"\n❌ Error procesando tabla '{tabla}': {str(e)}")

# Resumen
print("\n" + "=" * 100)
print("📊 RESUMEN FINAL:")
print("=" * 100)

if datos_2026_encontrados:
    print(f"\n⚠️  SE ENCONTRARON DATOS DE 2026 EN {len(datos_2026_encontrados)} TABLA(S):\n")
    
    total_registros_2026 = 0
    for d in datos_2026_encontrados:
        print(f"   ❌ {d['tabla'].upper()} ({d['columna']}): {d['cantidad']:,} registros de 2026")
        print(f"      Total en tabla: {d['total']:,}")
        total_registros_2026 += d['cantidad']
    
    print(f"\n   📊 TOTAL: {total_registros_2026:,} registros de 2026 en otras tablas")
    
    print(f"\n💡 CONCLUSIÓN:")
    print(f"   Solo eliminaste 'Facturas DIAN', pero hay otras tablas con datos 2026.")
    
    print(f"\n🎯 RECOMENDACIÓN:")
    print(f"   Si estos datos de 2026 son TAMBIÉN corruptos (valor=0, etc):")
    print(f"   1. Ve a http://127.0.0.1:8099/dian_vs_erp/configuracion")
    print(f"   2. Marca TODOS los checkboxes:")
    print(f"      ✅ Facturas DIAN")
    print(f"      ✅ Acuses")
    print(f"      ✅ ERP Financiero")
    print(f"      ✅ ERP Comercial")
    print(f"   3. Solicita eliminación de 01/01/2026 a 17/02/2026")
    print(f"   4. Luego re-importa TODOS los archivos Excel")
    
    print(f"\n   Si estos datos de 2026 están OK:")
    print(f"   → Puedes proceder a importar solo Facturas DIAN") 
    
else:
    print(f"\n✅ NO SE ENCONTRARON DATOS DE 2026 EN OTRAS TABLAS")
    print(f"✅ Solo 'Facturas DIAN' tenía datos de 2026 (ya eliminados)")
    print(f"\n🚀 SIGUIENTE PASO:")
    print(f"   Proceder con la importación de archivos Excel de 2026")

print("=" * 100)
