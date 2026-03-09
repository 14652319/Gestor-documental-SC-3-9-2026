import pandas as pd

print("Columnas en archivos ERP:")
print("="*80)

# ERP COMERCIAL
print("\nERP COMERCIAL:")
df_cm = pd.read_excel(r"C:/Users/Usuario/Downloads/Ricardo/ERP comercial 18 02 2026.xlsx", nrows=2)
print(f"  Total columnas: {len(df_cm.columns)}")
for i, col in enumerate(df_cm.columns, 1):
    print(f"  {i:2d}. {col}")

# ERP FINANCIERO
print("\n" + "-"*80)
print("\nERP FINANCIERO:")
df_fn = pd.read_excel(r"C:/Users/Usuario/Downloads/Ricardo/ERP Financiero 18 02 2026.xlsx", nrows=2)
print(f"  Total columnas: {len(df_fn.columns)}")
for i, col in enumerate(df_fn.columns, 1):
    print(f"  {i:2d}. {col}")

# ACUSES
print("\n" + "-"*80)
print("\nACUSES:")
df_ac = pd.read_excel(r"C:/Users/Usuario/Downloads/Ricardo/acuses 2.xlsx", nrows=2)
print(f"  Total columnas: {len(df_ac.columns)}")
for i, col in enumerate(df_ac.columns, 1):
    print(f"  {i:2d}. {col}")

print("\n" + "="*80)
