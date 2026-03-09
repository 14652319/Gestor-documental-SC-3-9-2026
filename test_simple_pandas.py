import pandas as pd

archivo = r"C:\Users\Usuario\Downloads\Ricardo\Dian.xlsx"

print("Leyendo Excel con pandas (como hace el fallback)...")
df = pd.read_excel(archivo, dtype=str, nrows=3)

print(f"\n✅ Leído: {len(df)} filas, {len(df.columns)} columnas\n")
print("📋 COLUMNAS ORIGINALES (primeras 15):")
for i, col in enumerate(df.columns[:15], 1):
    print(f"   {i:2}. '{col}' (repr: {repr(col)})")

print("\n📋 COLUMNAS DESPUÉS DE .lower():")
df_lower = df.rename(columns={c: c.strip().lower() for c in df.columns})
for i, col in enumerate(df_lower.columns[:15], 1):
    print(f"   {i:2}. '{col}' (repr: {repr(col)})")

print("\n📊 PRIMERA FILA (columnas críticas):")
columnas = ['folio', 'prefijo', 'fecha emisión', 'total', 'nit emisor']
for col in columnas:
    if col in df_lower.columns:
        val = df_lower[col].iloc[0]
        print(f"   '{col}': {val}")
    else:
        print(f"   '{col}': ❌ NO EXISTE")
        # Buscar similar
        similares = [c for c in df_lower.columns if col.replace(' ', '') in c.replace(' ', '')]
        if similares:
            print(f"      Similares: {similares}")
