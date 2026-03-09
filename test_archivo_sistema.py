"""
Test del archivo REALMENTE subido al sistema
"""
import pandas as pd
import os

archivo_sistema = r"modules\dian_vs_erp\uploads\dian\test_desde_navegador.xlsx"

if not os.path.exists(archivo_sistema):
    print(f"❌ Archivo NO existe: {archivo_sistema}")
else:
    print(f"✅ Archivo existe: {archivo_sistema}")
    print(f"📊 Tamaño: {os.path.getsize(archivo_sistema) / 1024 / 1024:.2f} MB")
    print(f"📅 Última modificación: {pd.Timestamp.fromtimestamp(os.path.getmtime(archivo_sistema))}")
    
    print("\n" + "="*80)
    print("📋 LEYENDO ARCHIVO (primeras 5 filas)...")
    print("="*80)
    
    df = pd.read_excel(archivo_sistema, dtype=str, nrows=5)
    
    print(f"\n✅ Leído: {len(df)} filas, {len(df.columns)} columnas")
    
    print("\n📋 Columnas originales (primeras 15):")
    for i, col in enumerate(df.columns[:15], 1):
        print(f"   {i:2}. '{col}'")
    
    # Normalizar a lowercase
    df_lower = df.rename(columns={c: c.strip().lower() for c in df.columns})
    
    # Ver si tiene las columnas críticas
    print("\n🔍 Columnas críticas en DataFrame:")
    for col in ['folio', 'prefijo', 'fecha emisión', 'total']:
        if col in df_lower.columns:
            val = df_lower[col].iloc[0] if len(df_lower) > 0 else "N/A"
            print(f"   ✅ '{col}': {val}")
        else:
            print(f"   ❌ '{col}': NO EXISTE")
            # Buscar similares
            similares = [c for c in df_lower.columns if col.split()[0] in c]
            if similares:
                print(f"      Candidatos: {similares}")
    
    print("\n" + "="*80)
    print("📊 PRIMERA FILA completa (primeras 10 columnas):")
    print("="*80)
    print(df_lower[df_lower.columns[:10]].head(1).to_string())
