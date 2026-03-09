"""
VERIFICACIÓN DEL BUG DE NORMALIZACIÓN DE COLUMNAS
==================================================

El problema está en cómo se normaliza el nombre de la columna "CUFE/CUDE"
"""

import unicodedata

def normalizar_columna(nombre):
    """Normaliza nombre: lowercase, sin tildes, espacios→guion bajo"""
    # Quitar tildes
    sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', str(nombre))
        if unicodedata.category(c) != 'Mn'
    )
    # Lowercase y espacios→guion bajo
    return sin_tildes.lower().strip().replace(' ', '_')

print("=" * 80)
print("VERIFICACIÓN DEL BUG DE NORMALIZACIÓN")
print("=" * 80)

# CASO 1: Columna de DIAN
columna_dian = "CUFE/CUDE"
normalizada_dian = normalizar_columna(columna_dian)
print(f"\n1️⃣ COLUMNA DIAN:")
print(f"   Original:    '{columna_dian}'")
print(f"   Normalizada: '{normalizada_dian}'")
print(f"   ❓ Problema: El código busca '{columna_dian}' con clave 'cufe_cude' (guion bajo)")
print(f"   ❌ PERO la normalización produce: '{normalizada_dian}' (con SLASH)")

# CASO 2: Lo que el código busca
busqueda_codigo = 'cufe_cude'
print(f"\n2️⃣ LO QUE BUSCA EL CÓDIGO:")
print(f"   Clave buscada: '{busqueda_codigo}'")
print(f"   En línea 1584: row.get(columnas_originales.get('cufe_cude', 'CUFE/CUDE'), '')")

# CASO 3: Match?
print(f"\n3️⃣ ¿COINCIDEN?")
print(f"   '{normalizada_dian}' == '{busqueda_codigo}' → {normalizada_dian == busqueda_codigo}")

if normalizada_dian != busqueda_codigo:
    print(f"\n❌ BUG CONFIRMADO:")
    print(f"   La columna '{columna_dian}' se normaliza a '{normalizada_dian}'")
    print(f"   Pero el código busca la clave '{busqueda_codigo}'")
    print(f"   ➡️  NO ENCUENTRA LA COLUMNA")
    print(f"   ➡️  Usa el fallback 'CUFE/CUDE' directamente")
    print(f"   ➡️  row.get('CUFE/CUDE') SÍ funciona (nombre exacto)")

# CASO 4: Columna de ACUSES
columna_acuses = "CUFE"
normalizada_acuses = normalizar_columna(columna_acuses)
print(f"\n4️⃣ COLUMNA ACUSES:")
print(f"   Original:    '{columna_acuses}'")
print(f"   Normalizada: '{normalizada_acuses}'")
print(f"   ✅ Esta SÍ se detecta correctamente en líneas 1363-1371")

print("\n" + "=" * 80)
print("CONCLUSIÓN:")
print("=" * 80)
print("""
El código TIENE un mecanismo de FALLBACK que salva el bug:
- Si no encuentra 'cufe_cude' en columnas_originales
- Usa directamente 'CUFE/CUDE' como nombre de columna
- row.get(columnas_originales.get('cufe_cude', 'CUFE/CUDE'), '')
                                                  ^^^^^^^^^ FALLBACK

Entonces el DIAN SÍ se lee correctamente por el fallback.

PERO... necesitamos verificar si el ACUSES también se lee bien.
Veamos las líneas 1363-1371 donde se detecta CUFE en acuses...
""")

print("\n" + "=" * 80)
print("VERIFICANDO DETECCIÓN DE CUFE EN ACUSES")
print("=" * 80)

# Simular detección en acuses
columnas_acuses = ["Razón Social", "NIT", "Prefijo", "Folio", "Fecha", "Total", "Estado Docto.", "CUFE", "Otro"]
print(f"\nColumnas en archivo ACUSES:")
for i, col in enumerate(columnas_acuses, 1):
    print(f"  {i}. '{col}'")

print(f"\nBuscando columna CUFE en acuses (líneas 1363-1371):")
cufe_col = None
for col in columnas_acuses:
    col_lower = col.lower().strip()
    if 'cufe' in col_lower or 'cude' in col_lower:
        cufe_col = col
        print(f"  ✅ Columna CUFE detectada: '{col}'")
        break

if cufe_col:
    print(f"\n✅ ACUSES: Detección correcta")
else:
    print(f"\n❌ ACUSES: NO detectó columna")

print("\n" + "=" * 80)
print("RESUMEN FINAL")
print("=" * 80)
print("""
1. DIAN: Lee correctamente 'CUFE/CUDE' por el fallback
2. ACUSES: Detecta correctamente 'CUFE' por búsqueda case-insensitive

ENTONCES... ¿Por qué no hace match?

Posibles causas:
A) Los CUFEs en los archivos son DIFERENTES (no coinciden)
B) Hay espacios o caracteres extra en los CUFEs
C) La normalización de los valores CUFE no es consistente

Necesitamos verificar los VALORES, no las columnas.
""")
