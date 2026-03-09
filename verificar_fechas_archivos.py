"""
VERIFICAR FECHAS Y PERÍODOS DE ARCHIVOS
========================================
"""

import pandas as pd
from pathlib import Path

print("=" * 80)
print("VERIFICACIÓN DE PERÍODOS Y FECHAS")
print("=" * 80)

# Leer primeras 100 filas
dian_df = pd.read_excel("uploads/dian/Dian.xlsx", nrows=100)
acuses_df = pd.read_excel("uploads/acuses/acuses_2.xlsx", nrows=100)

print(f"\n📊 ARCHIVO DIAN:")
print(f"   Columnas: {', '.join(dian_df.columns[:10])}...")

# Buscar columnas de fecha y NIT
fecha_cols = [c for c in dian_df.columns if 'fecha' in c.lower() or 'emis' in c.lower()]
nit_cols = [c for c in dian_df.columns if 'nit' in c.lower()]

if fecha_cols:
    print(f"\n   Columnas de fecha encontradas:")
    for col in fecha_cols:
        print(f"      - {col}")
        try:
            valores = dian_df[col].dropna()
            if len(valores) > 0:
                print(f"        Valores (primeros 5): {list(valores[:5])}")
        except:
            pass

if nit_cols:
    print(f"\n   Columnas de NIT encontradas:")
    for col in nit_cols:
        print(f"      - {col}")
        try:
            valores = dian_df[col].dropna().unique()
            print(f"        NITs únicos: {list(valores[:5])}")
        except:
            pass

print(f"\n" + "=" * 80)
print(f"📊 ARCHIVO ACUSES:")
print(f"   Columnas: {', '.join(acuses_df.columns[:10])}...")

# Buscar columnas de fecha y NIT
fecha_cols_acuses = [c for c in acuses_df.columns if 'fecha' in c.lower() or 'emis' in c.lower()]
nit_cols_acuses = [c for c in acuses_df.columns if 'nit' in c.lower()]

if fecha_cols_acuses:
    print(f"\n   Columnas de fecha encontradas:")
    for col in fecha_cols_acuses:
        print(f"      - {col}")
        try:
            valores = acuses_df[col].dropna()
            if len(valores) > 0:
                print(f"        Valores (primeros 5): {list(valores[:5])}")
        except:
            pass

if nit_cols_acuses:
    print(f"\n   Columnas de NIT encontradas:")
    for col in nit_cols_acuses:
        print(f"      - {col}")
        try:
            valores = acuses_df[col].dropna().unique()
            print(f"        NITs únicos: {list(valores[:5])}")
        except:
            pass

print(f"\n" + "=" * 80)
print("CONCLUSIÓN:")
print("=" * 80)
print("""
Si las fechas o NITs son diferentes, eso explica por qué
NO hay coincidencias de CUFEs.

SOLUCIÓN:
1. Pedir al usuario que verifique los períodos de ambos archivos
2. Asegurarse de que DIAN y ACUSES cubran el MISMO rango de fechas
3. Verificar que sean de la MISMA EMPRESA (NIT)
""")
