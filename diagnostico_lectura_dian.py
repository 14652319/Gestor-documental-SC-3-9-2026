"""
Diagnóstico: ¿Por qué no se está leyendo el CUFE de DIAN?
Este script imita EXACTAMENTE el proceso de routes.py líneas 1350-1600
"""
import pandas as pd
import io
import sys

# Configurar encoding
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("DIAGNÓSTICO DE LECTURA DE CUFE EN ARCHIVO DIAN")
print("=" * 80)

# Función de normalización EXACTA de routes.py línea 1418
def normalizar_nombre_columna(nombre):
    """Normaliza el nombre de la columna"""
    if nombre is None:
        return ''
    nombre_str = str(nombre).strip()
    # Eliminar espacios extras y convertir a minúsculas
    nombre_norm = ' '.join(nombre_str.split()).lower()
    # Reemplazar espacios y caracteres especiales por guión bajo
    nombre_norm = nombre_norm.replace(' ', '_').replace('/', '_').replace('-', '_')
    return nombre_norm

# 1. Leer archivo DIAN (mismo path que usa el sistema)
archivo_dian = r'uploads\dian\Dian.xlsx'
print(f"\n📂 Leyendo archivo: {archivo_dian}")

try:
    df_dian = pd.read_excel(archivo_dian, engine='openpyxl')
    print(f"   ✅ Archivo leído correctamente")
    print(f"   📊 Total filas: {len(df_dian):,}")
    print(f"   📊 Total columnas: {len(df_dian.columns)}")
except Exception as e:
    print(f"   ❌ Error leyendo archivo: {e}")
    sys.exit(1)

# 2. Mostrar columnas ORIGINALES
print(f"\n📋 COLUMNAS ORIGINALES EN EL EXCEL:")
for i, col in enumerate(df_dian.columns, 1):
    print(f"   {i:2d}. '{col}' (tipo: {type(col).__name__})")

# 3. Normalizar columnas (EXACTAMENTE como routes.py)
print(f"\n🔄 NORMALIZACIÓN DE COLUMNAS:")
columnas_normalizadas = {}
columnas_originales = {}

for col_original in df_dian.columns:
    col_normalizada = normalizar_nombre_columna(col_original)
    columnas_normalizadas[col_normalizada] = col_original
    columnas_originales[col_original] = col_normalizada
    print(f"   '{col_original}' → '{col_normalizada}'")

# 4. Buscar columna CUFE (EXACTAMENTE como routes.py línea 1518-1528)
print(f"\n🔍 BÚSQUEDA DE COLUMNA CUFE:")
columna_cufe_detectada = None

for col in df_dian.columns:
    col_lower = str(col).lower()
    if 'cufe' in col_lower or 'cude' in col_lower:
        columna_cufe_detectada = col
        print(f"   ✅ CUFE detectado: '{col}'")
        break

if not columna_cufe_detectada:
    print(f"   ❌ NO se encontró columna CUFE/CUDE")
    print(f"   ⚠️  Columnas buscadas con 'cufe' o 'cude' en el nombre")
else:
    # 5. Obtener nombre normalizado
    cufe_normalizado = normalizar_nombre_columna(columna_cufe_detectada)
    print(f"   📝 Columna CUFE normalizada: '{cufe_normalizado}'")
    
    # 6. Verificar cómo se accedería en el código
    # En routes.py línea 1584: cufe = str(row.get(columnas_originales.get('cufe_cude', 'CUFE/CUDE'), ''))
    print(f"\n🔧 VERIFICACIÓN DE ACCESO AL CUFE:")
    print(f"   1. columnas_originales contiene:")
    for k, v in columnas_originales.items():
        if 'cufe' in k.lower():
            print(f"      - '{k}' → '{v}'")
    
    # El código busca 'cufe_cude' en columnas_originales
    print(f"\n   2. El código busca: columnas_originales.get('cufe_cude', 'CUFE/CUDE')")
    
    # ¿Existe 'cufe_cude' en columnas_originales?
    if 'cufe_cude' in columnas_originales:
        print(f"      ✅ SE ENCUENTRA 'cufe_cude' → '{columnas_originales['cufe_cude']}'")
        col_a_usar = columnas_originales['cufe_cude']
    elif 'CUFE/CUDE' in columnas_originales:
        print(f"      ✅ SE ENCUENTRA 'CUFE/CUDE' (fallback) → '{columnas_originales['CUFE/CUDE']}'")
        col_a_usar = columnas_originales['CUFE/CUDE']
    else:
        print(f"      ❌ NO SE ENCUENTRA ni 'cufe_cude' ni 'CUFE/CUDE'")
        print(f"      ⚠️  ESTE ES EL PROBLEMA")
        col_a_usar = None
    
    # 7. Intentar leer un valor de ejemplo
    if col_a_usar:
        print(f"\n📖 LECTURA DE VALORES DE EJEMPLO:")
        for i in range(min(5, len(df_dian))):
            try:
                # Simular: row.get(col_a_usar, '')
                valor = df_dian.iloc[i].get(col_a_usar, '')
                valor_str = str(valor) if pd.notna(valor) else ''
                if valor_str and valor_str != 'nan':
                    print(f"   Fila {i+1}: '{valor_str[:50]}...' (len={len(valor_str)})")
                else:
                    print(f"   Fila {i+1}: VACÍO o NaN")
            except Exception as e:
                print(f"   Fila {i+1}: ERROR - {e}")
    else:
        print(f"\n❌ No se puede leer valores porque no se detectó la columna correctamente")

# 8. Diagnóstico del problema
print(f"\n" + "=" * 80)
print("DIAGNÓSTICO FINAL:")
print("=" * 80)

if not columna_cufe_detectada:
    print("❌ PROBLEMA 1: No hay columna CUFE/CUDE en el Excel")
    print("   Solución: Verifica que el archivo tenga la columna")
elif not col_a_usar:
    print("❌ PROBLEMA 2: La columna existe pero el código no la encuentra")
    print(f"   La columna original es: '{columna_cufe_detectada}'")
    print(f"   La columna normalizada es: '{cufe_normalizado}'")
    print(f"   El código busca: 'cufe_cude' o 'CUFE/CUDE'")
    print(f"   ⚠️  HAY UN DESAJUSTE EN LA NORMALIZACIÓN")
    print(f"\n   💡 SOLUCIÓN:")
    print(f"      El código debe buscar: columnas_originales.get('{columna_cufe_detectada}', ...)")
    print(f"      O normalizar: columnas_normalizadas.get('{cufe_normalizado}', ...)")
else:
    print("✅ La columna se detecta y se lee correctamente")
    print(f"   Si aún no funciona, revisa la lógica de escritura en maestro")

print("=" * 80)
