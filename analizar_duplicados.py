import pandas as pd

print("ANALISIS DE DUPLICADOS EN EXCEL")
print("="*80)

# Leer ERP COMERCIAL
df = pd.read_excel(r"C:/Users/Usuario/Downloads/Ricardo/ERP comercial 18 02 2026.xlsx", dtype=str)
print(f"\nERP COMERCIAL: {len(df):,} filas")

# Normalizar
df.columns = [c.lower().strip() for c in df.columns]

# Ver primeras filas
print("\nPrimeras 10 filas (columnas clave):")
print(df[['proveedor', 'docto. proveedor', 'nro documento']].head(10).to_string(index=False))

# Contar valores únicos
print("\n" + "-"*80)
print("VALORES UNICOS:")
print(f"  Proveedores únicos:     {df['proveedor'].nunique():,}")
print(f"  Docto proveedor únicos: {df['docto. proveedor'].nunique():,}")
print(f"  Nro documento únicos:   {df['nro documento'].nunique():,}")

# Crear claves como lo hace el script
df['clave1'] = df['proveedor'] + '|' + df['docto. proveedor'].fillna('') + '|' + df['nro documento'].fillna('')
print(f"  Claves únicas (método actual): {df['clave1'].nunique():,}")

# Probar solo con docto_proveedor
df['clave2'] = df['docto. proveedor'].fillna('')
print(f"  Claves únicas (solo docto):    {df['clave2'].nunique():,}")

# Ver duplicados más comunes
print("\n" + "-"*80)
print("TOP 10 VALORES DE NRO DOCUMENTO:")
print(df['nro documento'].value_counts().head(10))

print("\n" + "-"*80)
print("TOP 10 VALORES DE DOCTO PROVEEDOR:")
print(df['docto. proveedor'].value_counts().head(10))

# Verificar si hay valores vacíos
print("\n" + "-"*80)
print("VALORES VACIOS/NULOS:")
print(f"  Proveedor vacío:         {df['proveedor'].isna().sum():,}")
print(f"  Docto proveedor vacío:   {df['docto. proveedor'].isna().sum():,}")
print(f"  Nro documento vacío:     {df['nro documento'].isna().sum():,}")
