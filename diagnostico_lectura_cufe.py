"""
DIAGNÓSTICO FINAL: ¿Por qué CUFE llega vacío?
==============================================
Verificar si el Excel DIAN tiene la columna CUFE/CUDE
y si los valores están presentes
"""

import pandas as pd

print("=" * 80)
print("DIAGNÓSTICO: Lectura de CUFE desde Excel DIAN")
print("=" * 80)

# Leer Excel DIAN (primeras 10 filas)
print(f"\n📂 Leyendo: uploads/dian/Dian.xlsx")
dian_df = pd.read_excel("uploads/dian/Dian.xlsx", nrows=10)

print(f"\n📊 Total columnas: {len(dian_df.columns)}")
print(f"📊 Columnas:")
for i, col in enumerate(dian_df.columns, 1):
    print(f"   {i:2d}. '{col}'")

# Buscar columna de CUFE
print(f"\n🔍 BUSCANDO COLUMNA DE CUFE:")
cufe_col = None
for col in dian_df.columns:
    if 'CUFE' in col.upper() or 'CUDE' in col.upper():
        cufe_col = col
        print(f"   ✅ Encontrada: '{col}'")
        break

if not cufe_col:
    print(f"   ❌ NO SE ENCONTRÓ columna CUFE")
else:
    # Ver valores
    print(f"\n📝 VALORES EN COLUMNA '{cufe_col}':")
    for i, val in enumerate(dian_df[cufe_col], 1):
        val_str = str(val)
        if pd.isna(val):
            print(f"   {i}. NaN / NULL")
        elif val_str == '' or val_str == 'nan':
            print(f"   {i}. Vacío")
        else:
            print(f"   {i}. {val_str[:60]}... (len={len(val_str)})")
    
    # Verificar si hay valores no nulos
    no_nulos = dian_df[cufe_col].notna().sum()
    vacios = (dian_df[cufe_col] == '').sum()
    con_datos = no_nulos - vacios
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   Total filas: {len(dian_df)}")
    print(f"   No nulos: {no_nulos}")
    print(f"   Vacíos: {vacios}")
    print(f"   Con datos: {con_datos}")
    
    if con_datos == 0:
        print(f"\n   ❌ NO HAY VALORES DE CUFE en el Excel")
    else:
        print(f"\n   ✅ Hay {con_datos} registros con CUFE")

# Probar lectura con normalización
print(f"\n🔧 PROBANDO LECTURA CON CÓDIGO DE ROUTES.PY:")
print(f"   Intentando: row.get(columnas_originales.get('cufe_cude', 'CUFE/CUDE'), '')")

import unicodedata

def normalizar_columna(nombre):
    """Normaliza nombre: lowercase, sin tildes, espacios→guion bajo"""
    sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', str(nombre))
        if unicodedata.category(c) != 'Mn'
    )
    return sin_tildes.lower().strip().replace(' ', '_')

# Crear diccionario columnas_originales
columnas_originales = {}
for col in dian_df.columns:
    col_norm = normalizar_columna(col)
    columnas_originales[col_norm] = col
    columnas_originales[col_norm.replace('_', '')] = col

print(f"\n   Buscando 'cufe_cude' en columnas_originales...")
if 'cufe_cude' in columnas_originales:
    print(f"   ✅ Encontrado: '{columnas_originales['cufe_cude']}'")
    col_a_usar = columnas_originales['cufe_cude']
else:
    print(f"   ❌ NO encontrado, usando fallback: 'CUFE/CUDE'")
    col_a_usar = 'CUFE/CUDE'

# Intentar leer
print(f"\n   Leyendo primera fila con columna: '{col_a_usar}'")
if col_a_usar in dian_df.columns:
    primer_valor = dian_df[col_a_usar].iloc[0]
    print(f"   Valor leído: {str(primer_valor)[:80]}...")
    
    # Simular lo que hace el código
    cufe = str(primer_valor)
    print(f"\n   Después de str(): '{cufe[:80]}...'")
    print(f"   Longitud: {len(cufe)}")
    print(f"   Es 'nan': {cufe == 'nan'}")
    print(f"   Es vacío: {cufe == ''}")
    
    if cufe and cufe != 'nan' and cufe.strip():
        print(f"\n   ✅ CUFE VÁLIDO - Se guardaría en maestro")
    else:
        print(f"\n   ❌ CUFE INVÁLIDO - Se guardaría vacío en maestro")
else:
    print(f"   ❌ Columna '{col_a_usar}' NO existe en DataFrame")

print(f"\n" + "=" * 80)
print("CONCLUSIÓN:")
print("=" * 80)

if cufe_col and con_datos > 0 and cufe and cufe != 'nan':
    print(f"""
✅ EL EXCEL SÍ TIENE CUFEs

El archivo tiene columna '{cufe_col}' con valores válidos.
El problema entonces es en la BASE DE DATOS o en la carga anterior.

SOLUCIÓN:
1. Borrar tabla maestro: DELETE FROM maestro_dian_vs_erp;  
2. Re-procesar archivos desde la interfaz web
3. Verificar que ahora sí aparezcan los CUFEs
""")
elif not cufe_col:
    print(f"""
❌ EL EXCEL NO TIENE COLUMNA DE CUFE

El archivo no tiene una columna llamada 'CUFE' o 'CUDE'.
Verifica que el Excel exportado desde DIAN tenga esta columna.
""")
elif con_datos == 0:
    print(f"""
❌ LA COLUMNA EXISTE PERO ESTÁ VACÍA

El archivo tiene la columna '{cufe_col}' pero no tiene valores.
Verifica que el reporte de DIAN incluya los CUFEs.
""")
else:
    print(f"""
⚠️ PROBLEMA EN LA LECTURA

Los CUFEs se leen como 'nan' o vacío.
Esto puede ser un problema de tipos de datos en pandas.
""")

print("=" * 80)
