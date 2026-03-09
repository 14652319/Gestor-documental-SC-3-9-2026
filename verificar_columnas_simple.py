"""
Script rapido para verificar solo columnas y primeras filas
"""
import pandas as pd
import sys

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')

# Rutas
dian_path = r"uploads\dian\Dian.xlsx"
acuses_path = r"uploads\acuses\acuses.xlsx"

print("=" * 80)
print("VERIFICACION RAPIDA DE COLUMNAS Y PRIMERAS FILAS")
print("=" * 80)

# DIAN - Solo primeras 10 filas
print(f"\nARCHIVO DIAN (primeras 10 filas)")
print(f"Ruta: {dian_path}\n")
try:
    dian_df = pd.read_excel(dian_path, nrows=10)
    print(f"OK - Columnas originales en DIAN:")
    for i, col in enumerate(dian_df.columns, 1):
        print(f"   {i}. '{col}'")
    
    # Buscar CUFE
    cufe_col = None
    for col in dian_df.columns:
        if 'cufe' in str(col).lower() or 'cude' in str(col).lower():
            cufe_col = col
            print(f"\nOK - CUFE encontrado: '{col}'")
            break
    
    if cufe_col:
        print(f"\nPrimeros 3 CUFEs de DIAN:")
        for i, cufe in enumerate(dian_df[cufe_col].head(3), 1):
            cufe_str = str(cufe)
            print(f"   {i}. Longitud: {len(cufe_str)}")
            print(f"      Inicio: {cufe_str[:40]}")
            print(f"      Fin:    ...{cufe_str[-40:]}")
            print()
except Exception as e:
    print(f"ERROR: {e}")

# ACUSES - Solo primeras 10 filas
print("\n" + "=" * 80)
print(f"ARCHIVO ACUSES (primeras 10 filas)")
print(f"Ruta: {acuses_path}\n")
try:
    acuses_df = pd.read_excel(acuses_path, nrows=10)
    print(f"OK - Columnas originales en ACUSES:")
    for i, col in enumerate(acuses_df.columns, 1):
        print(f"   {i}. '{col}'")
    
    # Buscar CUFE
    cufe_col = None
    for col in acuses_df.columns:
        if 'cufe' in str(col).lower() or 'cude' in str(col).lower():
            cufe_col = col
            print(f"\nOK - CUFE encontrado: '{col}'")
            break
    
    # Buscar ESTADO
    estado_col = None
    for col in acuses_df.columns:
        if 'estado' in str(col).lower():
            estado_col = col
            print(f"OK - ESTADO encontrado: '{col}'")
            break
    
    if cufe_col:
        print(f"\nPrimeros 3 CUFEs de ACUSES:")
        for i, cufe in enumerate(acuses_df[cufe_col].head(3), 1):
            cufe_str = str(cufe)
            estado = acuses_df[estado_col].iloc[i-1] if estado_col else 'N/A'
            print(f"   {i}. Longitud: {len(cufe_str)}, Estado: {estado}")
            print(f"      Inicio: {cufe_str[:40]}")
            print(f"      Fin:    ...{cufe_str[-40:]}")
            print()
            
    # COMPARACION DIRECTA
    if cufe_col:
        print("\n" + "=" * 80)
        print("COMPARACION DIRECTA (primeros 3)")
        print("=" * 80)
        
        # Leer DIAN nuevamente para tener los mismos 10 registros
        dian_test = pd.read_excel(dian_path, nrows=10)
        
        # Buscar columna CUFE en DIAN
        dian_cufe_col = None
        for col in dian_test.columns:
            if 'cufe' in str(col).lower() or 'cude' in str(col).lower():
                dian_cufe_col = col
                break
        
        if dian_cufe_col:
            # Obtener sets de CUFEs
            dian_cufes = set(str(c).strip() for c in dian_test[dian_cufe_col].head(10) if pd.notna(c))
            acuses_cufes = set(str(c).strip() for c in acuses_df[cufe_col].head(10) if pd.notna(c))
            
            # Buscar coincidencias
            coincidencias = dian_cufes.intersection(acuses_cufes)
            
            print(f"\nRESULTADO:")
            print(f"   CUFEs en DIAN (10): {len(dian_cufes)}")
            print(f"   CUFEs en ACUSES (10): {len(acuses_cufes)}")
            print(f"   Coincidencias: {len(coincidencias)}")
            
            if coincidencias:
                print(f"\nOK - SI HAY COINCIDENCIAS en las primeras 10 filas!")
                for cufe in list(coincidencias)[:3]:
                    print(f"      {cufe[:60]}...")
            else:
                print(f"\nERROR - NO HAY COINCIDENCIAS en las primeras 10 filas")
                print("\nPrimer CUFE de cada archivo:")
                print(f"\n   DIAN:")
                if dian_cufes:
                    print(f"   {list(dian_cufes)[0]}")
                else:
                    print(f"   VACIO")
                print(f"\n   ACUSES:")
                if acuses_cufes:
                    print(f"   {list(acuses_cufes)[0]}")
                else:
                    print(f"   VACIO")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("FIN")
print("=" * 80)
