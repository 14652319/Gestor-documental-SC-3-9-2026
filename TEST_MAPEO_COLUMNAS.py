"""
Script para cargar UN archivo DIAN y verificar detección de columnas
"""
import polars as pl
import unicodedata

# Archivo a probar (el más reciente: dian_prueba)
archivo = r"uploads\dian\dian_prueba_51a9bbe865.csv"

print(f"📁 Cargando: {archivo}\n")

# Leer con Polars
df = pl.read_csv(archivo)

print(f"📊 Total registros: {df.height}")
print(f"📊 Total columnas: {df.width}\n")

# Función de normalización (igual que en routes.py)
def normalizar_columna(nombre):
    """Normaliza nombre: lowercase, sin tildes, espacios→guion bajo"""
    sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', str(nombre))
        if unicodedata.category(c) != 'Mn'
    )
    return sin_tildes.lower().strip().replace(' ', '_')

# Crear diccionario de mapeo
columnas_originales = {}
for col in df.columns:
    col_norm = normalizar_columna(col)
    columnas_originales[col_norm] = col
    columnas_originales[col_norm.replace('_', '')] = col  # Sin guiones

print("🔍 MAPEO DE COLUMNAS:")
for norm, orig in sorted(columnas_originales.items()):
    if 'total' in norm or 'valor' in norm or 'fecha' in norm and 'emis' in norm:
        print(f"   '{norm}' → '{orig}'")

print("\n🔍 BUSCANDO 'TOTAL' o 'VALOR':")
for variante in ['total', 'valor']:
    if variante in columnas_originales:
        col_original = columnas_originales[variante]
        print(f"   ✅ '{variante}' encontrado como columna '{col_original}'")
        # Mostrar primeros valores
        valores = df[col_original].head(3).to_list()
        print(f"      Primeros valores: {valores}")
    else:
        print(f"   ❌ '{variante}' NO encontrado")

print("\n🔍 BUSCANDO 'FECHA_EMISION':")
for variante in ['fecha_emision', 'fechaemision']:
    if variante in columnas_originales:
        col_original = columnas_originales[variante]
        print(f"   ✅ '{variante}' encontrado como columna '{col_original}'")
        valores = df[col_original].head(3).to_list()
        print(f"      Primeros valores: {valores}")
    else:
        print(f"   ❌ '{variante}' NO encontrado")

print("\n✅ Diagnóstico completo")
print("\n💡 CONCLUSIÓN:")
print("   Si 'total' se mapea correctamente a 'Total', el código DEBERÍA funcionar.")
print("   Si no se mapea, hay un problema en la normalización.")
