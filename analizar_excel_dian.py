"""Analiza el archivo Dian.xlsx y compara con la tabla dian"""
import os
import polars as pl
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# Ruta del archivo Excel
excel_path = r"C:\Users\Usuario\Downloads\Ricardo\Dian.xlsx"

print("="*80)
print("🔍 ANÁLISIS DEL ARCHIVO DIAN.XLSX vs TABLA DIAN")
print("="*80)

try:
    # Leer el archivo Excel con Polars
    print(f"\n📂 Leyendo archivo: {excel_path}")
    df = pl.read_excel(excel_path)
    
    print(f"✅ Archivo leído correctamente")
    print(f"   Total de filas en Excel: {len(df):,}")
    print(f"   Columnas: {df.columns}")
    
    # Filtrar por el NIT 805013653
    nit_buscado = "805013653"
    
    # Buscar en diferentes columnas posibles (a veces el NIT puede estar en diferentes columnas)
    columnas_posibles = [col for col in df.columns if 'nit' in col.lower() or 'emisor' in col.lower()]
    
    print(f"\n🔍 Columnas que podrían contener NIT: {columnas_posibles}")
    
    # Intentar buscar el NIT en cada columna
    total_encontrados = 0
    for col in columnas_posibles:
        try:
            # Convertir a string y buscar
            df_filtrado = df.filter(pl.col(col).cast(pl.Utf8).str.contains(nit_buscado))
            if len(df_filtrado) > 0:
                print(f"\n✅ Encontrados {len(df_filtrado):,} registros en columna '{col}'")
                total_encontrados = len(df_filtrado)
                
                # Buscar columna de prefijo
                cols_prefijo = [c for c in df.columns if 'prefijo' in c.lower() or 'tipo' in c.lower()]
                print(f"   Columnas de prefijo posibles: {cols_prefijo}")
                
                if cols_prefijo:
                    # Mostrar prefijos únicos
                    for col_pref in cols_prefijo:
                        try:
                            prefijos = df_filtrado.select(pl.col(col_pref).cast(pl.Utf8)).unique()
                            print(f"   Prefijos únicos en '{col_pref}': {prefijos[col_pref].to_list()[:10]}")
                        except:
                            pass
                
                # Mostrar primeras 3 filas
                print("\n   Primeras 3 filas:")
                print(df_filtrado.head(3))
                
                break
        except Exception as e:
            continue
    
    if total_encontrados == 0:
        print(f"\n⚠️  NO se encontró el NIT {nit_buscado} en el archivo Excel")
        print(f"   El archivo tiene {len(df):,} filas totales")
        
        # Mostrar primeras 3 filas para entender la estructura
        print("\n   Primeras 3 filas del Excel completo:")
        print(df.head(3))
    
    # Comparar con la base de datos
    print("\n" + "="*80)
    print("📊 COMPARACIÓN CON BASE DE DATOS")
    print("="*80)
    
    with engine.connect() as conn:
        # Contar en la tabla dian
        result = conn.execute(text(f"""
            SELECT COUNT(*) 
            FROM dian 
            WHERE nit_emisor = '{nit_buscado}'
        """))
        count_bd = result.scalar()
        
        print(f"\n🗄️  Registros en TABLA DIAN: {count_bd:,}")
        print(f"📄 Registros en ARCHIVO EXCEL: {total_encontrados:,}")
        print(f"❌ DIFERENCIA: {total_encontrados - count_bd:,} registros NO se cargaron")
        
        if count_bd > 0:
            # Mostrar qué sí se cargó
            result = conn.execute(text(f"""
                SELECT prefijo, folio, fecha_emision, cufe_cude
                FROM dian 
                WHERE nit_emisor = '{nit_buscado}'
                LIMIT 5
            """))
            
            print(f"\n   Registro(s) que SÍ se cargó a la BD:")
            for prefijo, folio, fecha, cufe in result:
                print(f"   - Prefijo: {prefijo if prefijo else 'NULL'} | Folio: {folio} | Fecha: {fecha} | CUFE: {cufe[:20] if cufe else 'NULL'}...")

except FileNotFoundError:
    print(f"❌ ERROR: No se encontró el archivo en {excel_path}")
except Exception as e:
    print(f"❌ ERROR al leer el archivo: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("💡 POSIBLES CAUSAS SI NO SE CARGÓ TODO:")
print("="*80)
print("""
1. Error durante la carga (se detuvo antes de terminar)
2. Validación que rechazó algunos registros
3. Duplicados que se omitieron
4. Formato de datos incompatible en algunas filas
5. Límite de caracteres en algún campo (VARCHAR overflow)
""")
print("="*80)
