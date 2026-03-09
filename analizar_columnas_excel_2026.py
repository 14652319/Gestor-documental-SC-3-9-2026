#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analizar encabezados de archivos Excel de 2026
"""
import os
import pandas as pd
from pathlib import Path

directorio = r"C:\Users\Usuario\Downloads\Ricardo - copia"

print("=" * 100)
print("ANÁLISIS DE ENCABEZADOS DE ARCHIVOS EXCEL - 2026")
print("=" * 100)

if not os.path.exists(directorio):
    print(f"\n❌ El directorio no existe: {directorio}")
    print("Por favor verifica la ruta de los archivos Excel.")
    exit(1)

# Buscar archivos Excel
archivos_excel = list(Path(directorio).glob("*.xlsx"))

if not archivos_excel:
    print(f"\n❌ No se encontraron archivos .xlsx en: {directorio}")
    exit(1)

print(f"\n📁 Se encontraron {len(archivos_excel)} archivos Excel")
print("=" * 100)

for archivo in archivos_excel:
    print(f"\n📄 Archivo: {archivo.name}")
    print("-" * 100)
    
    try:
        # Leer solo las primeras 2 filas para ver encabezados
        df = pd.read_excel(archivo, nrows=2)
        
        print(f"   📊 Total de columnas: {len(df.columns)}")
        print(f"\n   📋 Encabezados de columnas:")
        
        for idx, col in enumerate(df.columns, 1):
            # Buscar columnas relacionadas con valor, fecha, prefijo, etc.
            col_lower = str(col).lower()
            emoji = "   "
            if 'valor' in col_lower or 'total' in col_lower or 'importe' in col_lower:
                emoji = "💰"
            elif 'fecha' in col_lower:
                emoji = "📅"
            elif 'prefijo' in col_lower:
                emoji = "🔤"
            elif 'folio' in col_lower or 'numero' in col_lower:
                emoji = "🔢"
            elif 'forma' in col_lower and 'pago' in col_lower:
                emoji = "💳"
            elif 'nit' in col_lower or 'emisor' in col_lower or 'proveedor' in col_lower:
                emoji = "🏢"
            elif 'razon' in col_lower or 'social' in col_lower:
                emoji = "📝"
                
            print(f"      {emoji} {idx:2d}. {col}")
        
        # Mostrar ejemplo de datos en las columnas con "valor" en el nombre
        columnas_valor = [col for col in df.columns if 'valor' in str(col).lower() or 'total' in str(col).lower() or 'importe' in str(col).lower()]
        
        if columnas_valor:
            print(f"\n   💰 Columnas relacionadas con VALOR encontradas:")
            for col in columnas_valor:
                print(f"      ✅ '{col}'")
                # Mostrar primeras 2 filas de ejemplo
                print(f"         Ejemplo fila 1: {df[col].iloc[0] if len(df) > 0 else 'N/A'}")
                if len(df) > 1:
                    print(f"         Ejemplo fila 2: {df[col].iloc[1]}")
        else:
            print(f"\n   ⚠️  NO se encontraron columnas con 'valor', 'total' o 'importe' en el nombre")
            print(f"      El script CARGA_DIRECTA_SIMPLE.py busca: row.get('valor', 0)")
            print(f"      Por eso todos los registros tienen valor = 0.00")
        
        print()
        
    except Exception as e:
        print(f"   ❌ Error al leer archivo: {str(e)}")
        print()
    
print("=" * 100)
print("FIN DEL ANÁLISIS")
print("=" * 100)
