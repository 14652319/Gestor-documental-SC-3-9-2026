"""
TEST DE PROCESAMIENTO CON DEBUG COMPLETO
Verifica por qué actualizar_maestro() no procesa archivos
"""

import sys
from pathlib import Path
import psycopg2

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'gestor_documental',
    'user': 'postgres',
    'password': 'G3st0radm$2025.'
}

print("=" * 80)
print("🔍 DEBUG DE PROCESAMIENTO - PASO A PASO")
print("=" * 80)

# 1. Verificar archivos en uploads/
print("\n📁 PASO 1: Verificar archivos en carpetas uploads/")
print("-" * 80)

carpetas = {
    'DIAN': Path('uploads/dian'),
    'ERP_CM': Path('uploads/erp_cm'),
    'ERP_FN': Path('uploads/erp_fn'),
    'ACUSES': Path('uploads/acuses')
}

archivos_encontrados = {}
for nombre, carpeta in carpetas.items():
    if carpeta.exists():
        # Buscar .xlsx, .xlsm, .csv
        archivos = list(carpeta.glob('*.xlsx')) + list(carpeta.glob('*.xlsm')) + list(carpeta.glob('*.csv'))
        if archivos:
            # Ordenar por fecha de modificación (más reciente primero)
            archivos.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            mas_reciente = archivos[0]
            archivos_encontrados[nombre] = mas_reciente
            print(f"✅ {nombre}: {mas_reciente.name}")
            print(f"   Tamaño: {mas_reciente.stat().st_size / (1024*1024):.2f} MB")
            print(f"   Modificado: {mas_reciente.stat().st_mtime}")
        else:
            print(f"❌ {nombre}: No se encontraron archivos Excel/CSV")
    else:
        print(f"❌ {nombre}: Carpeta no existe ({carpeta})")

if not archivos_encontrados:
    print("\n❌ ERROR: No se encontraron archivos para procesar")
    sys.exit(1)

# 2. Verificar conexión a base de datos
print("\n🔌 PASO 2: Verificar conexión a base de datos")
print("-" * 80)

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Test simple
    cursor.execute("SELECT version()")
    version = cursor.fetchone()[0]
    print(f"✅ Conexión exitosa a PostgreSQL")
    print(f"   {version[:50]}...")
    
    # Verificar tablas existen
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('dian', 'erp_comercial', 'erp_financiero', 'acuses', 'maestro_dian_vs_erp')
    """)
    tablas = [row[0] for row in cursor.fetchall()]
    print(f"✅ Tablas encontradas: {', '.join(tablas)}")
    
    # Verificar conteo actual
    for tabla in ['dian', 'erp_comercial', 'erp_financiero', 'acuses', 'maestro_dian_vs_erp']:
        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
        count = cursor.fetchone()[0]
        print(f"   {tabla}: {count:,} registros")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ ERROR de conexión: {e}")
    sys.exit(1)

# 3. Intentar importar módulos necesarios
print("\n📦 PASO 3: Verificar librerías Python")
print("-" * 80)

try:
    import polars as pl
    print(f"✅ Polars: {pl.__version__}")
except ImportError as e:
    print(f"❌ Polars no instalado: {e}")

try:
    import pandas as pd
    print(f"✅ Pandas: {pd.__version__}")
except ImportError as e:
    print(f"❌ Pandas no instalado: {e}")

try:
    import openpyxl
    print(f"✅ OpenPyXL instalado")
except ImportError as e:
    print(f"❌ OpenPyXL no instalado: {e}")

# 4. Intentar leer archivo DIAN
print("\n📖 PASO 4: Intentar leer archivo DIAN directamente")
print("-" * 80)

if 'DIAN' in archivos_encontrados:
    archivo_dian = archivos_encontrados['DIAN']
    print(f"Leyendo: {archivo_dian}")
    
    try:
        import polars as pl
        df = pl.read_excel(archivo_dian)
        print(f"✅ Archivo leído con Polars")
        print(f"   Filas: {len(df):,}")
        print(f"   Columnas: {len(df.columns)}")
        print(f"   Primeras columnas: {df.columns[:5]}")
        
        # Verificar si tiene las columnas necesarias
        columnas_requeridas = ['NIT Emisor', 'Prefijo', 'Folio', 'Total']
        for col in columnas_requeridas:
            if col in df.columns or col.lower() in [c.lower() for c in df.columns]:
                print(f"   ✅ Columna encontrada: {col}")
            else:
                print(f"   ⚠️ Columna NO encontrada: {col}")
    
    except Exception as e:
        print(f"❌ Error al leer archivo: {e}")
        print(f"   Tipo de error: {type(e).__name__}")

# 5. Verificar función actualizar_maestro()
print("\n🔧 PASO 5: Verificar función actualizar_maestro()")
print("-" * 80)

try:
    # Importar módulo de rutas
    sys.path.insert(0, str(Path.cwd()))
    from modules.dian_vs_erp import routes
    
    print("✅ Módulo routes.py importado exitosamente")
    
    # Verificar funciones existen
    funciones_requeridas = [
        'actualizar_maestro',
        'insertar_dian_bulk',
        'insertar_erp_comercial_bulk',
        'insertar_erp_financiero_bulk',
        'insertar_acuses_bulk'
    ]
    
    for func in funciones_requeridas:
        if hasattr(routes, func):
            print(f"   ✅ Función encontrada: {func}()")
        else:
            print(f"   ❌ Función NO encontrada: {func}()")

except Exception as e:
    print(f"❌ Error al importar módulo: {e}")
    print(f"   Tipo de error: {type(e).__name__}")

print("\n" + "=" * 80)
print("✅ DEBUG COMPLETADO")
print("=" * 80)
print("\n💡 SIGUIENTE PASO:")
print("   1. Si todos los pasos son ✅ → El problema está en CÓMO se llama actualizar_maestro()")
print("   2. Si hay ❌ en archivos → Subir archivos correctos a uploads/")
print("   3. Si hay ❌ en librerías → pip install polars pandas openpyxl")
print("   4. Si hay ❌ en BD → Verificar credenciales en DB_CONFIG")
print("\n")
