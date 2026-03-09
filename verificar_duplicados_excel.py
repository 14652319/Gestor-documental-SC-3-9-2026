"""
VERIFICAR SI EL EXCEL DIAN TIENE CUFEs DUPLICADOS
"""
import pandas as pd
import os

archivo = r'uploads\dian\Dian_23022026.xlsx'

print("\n" + "="*80)
print("VERIFICANDO DUPLICADOS EN EXCEL DIAN")
print("="*80)

if not os.path.exists(archivo):
    print(f"\n❌ Archivo no encontrado: {archivo}")
    exit()

print(f"\n📂 Leyendo: {archivo}")

# Leer el Excel
df = pd.read_excel(archivo)
print(f"✅ Total registros: {len(df):,}")

# Normalizar nombres de columnas
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('ó', 'o').str.replace('á', 'a').str.replace('é', 'e').str.replace('í', 'i').str.replace('ú', 'u')

print(f"✅ Columnas detectadas: {', '.join(df.columns[:5])}...")

# Buscar la columna CUFE
col_cufe = None
for col in df.columns:
    if 'cufe' in col or 'cude' in col:
        col_cufe = col
        break

if not col_cufe:
    print("\n❌ No se encontró columna CUFE/CUDE en el Excel")
    exit()

print(f"\n🔍 Columna CUFE encontrada: '{col_cufe}'")

# Verificar duplicados
df_cufe = df[[col_cufe]].copy()
df_cufe = df_cufe.dropna()  # Eliminar nulls

total_cufes = len(df_cufe)
cufes_unicos = df_cufe[col_cufe].nunique()
duplicados = total_cufes - cufes_unicos

print(f"\n📊 ANÁLISIS:")
print(f"   Total CUFEs: {total_cufes:,}")
print(f"   CUFEs únicos: {cufes_unicos:,}")
print(f"   CUFEs duplicados: {duplicados:,}")

if duplicados > 0:
    print(f"\n❌ ¡ENCONTRADOS {duplicados:,} CUFEs DUPLICADOS!")
    
    # Encontrar cuáles están duplicados
    duplicated_cufes = df_cufe[df_cufe.duplicated(col_cufe, keep=False)]
    cufes_problema = df_cufe[col_cufe].value_counts()
    cufes_problema = cufes_problema[cufes_problema > 1]
    
    print(f"\n🔍 Primeros 10 CUFEs duplicados:")
    for i, (cufe, count) in enumerate(cufes_problema.head(10).items()):
        print(f"   {i+1}. {cufe[:50]}... → {count} veces")
        
        # Verificar si es el CUFE del error
        cufe_error = "929f7761de9ff5fd92865b32d3aabbd4e056589f9cb854c0cfc15a570564f657aba35f6131872b4523c43152f393c793"
        if str(cufe).strip() == cufe_error:
            print(f"      ⚠️ ¡ESTE ES EL CUFE DEL ERROR!")
            
            # Mostrar las filas duplicadas
            filas_dup = df[df[col_cufe] == cufe]
            print(f"\n      📋 Filas con este CUFE:")
            for idx, row in filas_dup.iterrows():
                # Buscar columnas de nit, prefijo, folio
                nit = row.get('nit_proveedor', row.get('nit', 'N/A'))
                prefijo = row.get('prefijo', row.get('documento', 'N/A'))
                folio = row.get('folio', 'N/A')
                print(f"         Fila {idx}: NIT={nit}, Prefijo={prefijo}, Folio={folio}")
    
    print("\n" + "="*80)
    print("SOLUCIÓN:")
    print("="*80)
    print("El Excel tiene CUFEs duplicados. Necesitas LIMPIAR el archivo Excel")
    print("ANTES de cargarlo al sistema.")
    print("\nOpciones:")
    print("1. Eliminar las facturas duplicadas del Excel manualmente")
    print("2. Usar el siguiente script para limpiar automáticamente:")
    print("   python limpiar_duplicados_excel.py")
    print("="*80)
    
else:
    print(f"\n✅ ¡EXCELENTE! No hay CUFEs duplicados en el Excel")
    print("\nEl problema NO es el Excel. Debe ser algo en el proceso de inserción.")
    print("\n🔍 Siguiente paso:")
    print("   - Verificar que las tablas estén REALMENTE vacías")
    print("   - O revisar el código de inserción por si inserta dos veces")

print("\n")
