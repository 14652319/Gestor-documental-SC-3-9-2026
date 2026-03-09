"""
VERIFICAR COLUMNAS DE ARCHIVOS ERP
Muestra las columnas de los CSV del ERP para entender qué campos concatenar
"""

import pandas as pd
from pathlib import Path

carpetas = [
    r'D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\ERP Financiero',
    r'D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\ERP Comercial'
]

for carpeta in carpetas:
    print("=" * 80)
    print(f"CARPETA: {carpeta}")
    print("=" * 80)
    
    path = Path(carpeta)
    if not path.exists():
        print(f"⚠️ Carpeta no existe")
        continue
    
    # Buscar archivos Excel
    archivos = list(path.glob("*.xlsx")) + list(path.glob("*.xls")) + list(path.glob("*.csv"))
    if not archivos:
        print(f"⚠️ No hay archivos")
        continue
    
    # Tomar el primer archivo
    archivo = archivos[0]
    print(f"\n📄 Archivo: {archivo.name}")
    
    try:
        # Leer con pandas
        if archivo.suffix == '.csv':
            df = pd.read_csv(archivo, nrows=5, dtype=str)
        else:
            df = pd.read_excel(archivo, nrows=5, dtype=str)
        
        print(f"\n📊 COLUMNAS ({len(df.columns)}):")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2}. {col}")
        
        print(f"\n🔍 PRIMERA FILA (muestra):")
        if len(df) > 0:
            for col in df.columns:
                valor = df[col].iloc[0]
                if pd.notna(valor) and str(valor).strip():
                    print(f"  - {col}: {valor}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
