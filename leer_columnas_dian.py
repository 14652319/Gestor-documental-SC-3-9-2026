"""
Script para leer y mostrar las columnas exactas del archivo Dian.xlsx
"""
import pandas as pd
import sys

archivo = r"C:\Users\Usuario\Downloads\Ricardo\Dian.xlsx"

try:
    print(f"\n{'='*80}")
    print(f"📂 LEYENDO ARCHIVO: {archivo}")
    print(f"{'='*80}\n")
    
    # Leer Excel con Pandas
    df = pd.read_excel(archivo, engine='openpyxl')
    
    print(f"✅ Archivo leído exitosamente")
    print(f"📊 Total de filas: {len(df):,}")
    print(f"📋 Total de columnas: {len(df.columns)}\n")
    
    print(f"{'='*80}")
    print(f"📋 COLUMNAS EXACTAS DEL EXCEL (como Polars las lee)")
    print(f"{'='*80}\n")
    
    for i, col in enumerate(df.columns, 1):
        print(f"{i:3}. '{col}'")
    
    print(f"\n{'='*80}")
    print(f"🔍 BUSCANDO COLUMNAS CRÍTICAS")
    print(f"{'='*80}\n")
    
    # Buscar columnas específicas (normalizado)
    columnas_lower = [c.lower() for c in df.columns]
    
    criticas = {
        'folio': ['folio', 'numero', 'número', 'numero factura', 'número factura'],
        'prefijo': ['prefijo'],
        'total': ['total', 'valor', 'valor total', 'total factura'],
        'fecha_emision': ['fecha emision', 'fecha emisión', 'fecha de emision', 'fecha de emisión']
    }
    
    for campo, variantes in criticas.items():
        print(f"\n🔎 Buscando '{campo}':")
        encontradas = []
        for i, col_lower in enumerate(columnas_lower):
            for variante in variantes:
                if variante in col_lower:
                    encontradas.append(f"  ✅ Columna {i+1}: '{df.columns[i]}'")
                    break
        
        if encontradas:
            for e in encontradas:
                print(e)
        else:
            print(f"  ❌ NO ENCONTRADA (variantes buscadas: {variantes})")
    
    print(f"\n{'='*80}")
    print(f"📊 PRIMERAS 3 FILAS DE DATOS")
    print(f"{'='*80}\n")
    
    # Mostrar las primeras 3 filas de las columnas críticas
    columnas_mostrar = []
    for col in df.columns:
        col_lower = col.lower()
        if any(palabra in col_lower for palabra in ['folio', 'prefijo', 'total', 'fecha', 'nit', 'nombre']):
            columnas_mostrar.append(col)
            if len(columnas_mostrar) >= 8:
                break
    
    if columnas_mostrar:
        print(df[columnas_mostrar].head(3).to_string())
    
except FileNotFoundError:
    print(f"❌ ERROR: Archivo no encontrado en: {archivo}")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
