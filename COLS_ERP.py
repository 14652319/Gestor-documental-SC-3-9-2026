from dotenv import load_dotenv; load_dotenv()
import os, pandas as pd

for ruta in [
    r'uploads\erp_cm\ERP_comercial_23022026.xlsx',
    r'uploads\erp_fn\erp_financiero_23022026.xlsx',
]:
    df = pd.read_excel(ruta, nrows=2, dtype=str)
    fname = ruta.split('\\')[-1]
    print(f"\n=== {fname} ===")
    print("Columnas:", df.columns.tolist())
    print("\nFila 1:")
    for col in df.columns:
        print(f"  {col:40} = {repr(str(df.iloc[0][col]))[:60]}")
