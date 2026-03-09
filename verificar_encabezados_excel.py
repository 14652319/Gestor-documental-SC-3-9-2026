#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VERIFICAR_ENCABEZADOS_EXCEL.py - Verificar columnas de los 3 archivos Excel
===========================================================================

Compara los encabezados reales de los archivos Excel con los esperados por el sistema.
"""

import pandas as pd
from pathlib import Path

# ========================================
# ARCHIVOS A VERIFICAR
# ========================================

FILES = {
    'ERP_COMERCIAL': r'C:/Users/Usuario/Downloads/Ricardo/ERP comercial 18 02 2026.xlsx',
    'ERP_FINANCIERO': r'C:/Users/Usuario/Downloads/Ricardo/ERP Financiero 18 02 2026.xlsx',
    'ACUSES': r'C:/Users/Usuario/Downloads/Ricardo/acuses 2.xlsx'
}

# ========================================
# ENCABEZADOS ESPERADOS (según documentación)
# ========================================

ESPERADOS = {
    'ERP_COMERCIAL': [
        'Proveedor',
        'Razón social proveedor',  # Opcional pero común
        'Fecha docto. prov.',
        'Docto. proveedor',       # CRÍTICO: debe contener "docto" Y "proveedor"
        'Valor bruto',
        'Valor imptos',
        'C.O.',                   # CRÍTICO: exactamente "C.O." con puntos
        'Usuario creación',
        'Clase docto.',
        'Nro documento'
    ],
    
    'ERP_FINANCIERO': [
        'Proveedor',
        'Razón social',
        'Fecha proveedor',
        'Factura proveedor',      # Similar a "Docto. proveedor"
        'Valor subtotal',
        'Valor impuestos',
        'C.O.',
        'Usuario creación',
        'Clase docto.',
        'Nro documento'
    ],
    
    'ACUSES': [
        'Fecha',
        'Adquiriente',
        'Factura',
        'Emisor',
        'Nit Emisor',
        'Nit PT',
        'Estado Docto',           # O "Estado Docto."
        'Descripcion Reclamo',
        'Tipo Documento',
        'CUFE',                   # CRÍTICO: columna clave
        'Valor'
    ]
}

# ========================================
# FUNCIÓN PRINCIPAL
# ========================================

def verificar_archivo(nombre, ruta):
    """Verifica encabezados de un archivo Excel"""
    
    print("\n" + "="*80)
    print(f"📂 {nombre}")
    print("="*80)
    
    # Verificar existencia
    if not Path(ruta).exists():
        print(f"❌ ERROR: Archivo no encontrado: {ruta}")
        return
    
    try:
        # Leer solo primera fila (encabezados)
        df = pd.read_excel(ruta, nrows=0)
        columnas_reales = list(df.columns)
        
        print(f"\n✅ Archivo leído correctamente")
        print(f"📊 Columnas detectadas: {len(columnas_reales)}\n")
        
        # Mostrar columnas reales
        print("🔍 ENCABEZADOS REALES (en el Excel):")
        print("-" * 80)
        for i, col in enumerate(columnas_reales, 1):
            print(f"{i:2d}. '{col}'")
        
        # Comparar con esperados
        print(f"\n" + "="*80)
        print("⚖️  COMPARACIÓN CON ENCABEZADOS ESPERADOS:")
        print("="*80)
        
        esperados = ESPERADOS.get(nombre, [])
        
        # Normalizar para comparación (lowercase)
        reales_norm = [c.lower().strip() for c in columnas_reales]
        esperados_norm = [c.lower().strip() for c in esperados]
        
        # Encontrados
        print("\n✅ COLUMNAS ESPERADAS ENCONTRADAS:")
        print("-" * 80)
        encontradas_count = 0
        for esp in esperados:
            esp_norm = esp.lower().strip()
            if esp_norm in reales_norm:
                idx = reales_norm.index(esp_norm)
                real = columnas_reales[idx]
                if esp == real:
                    print(f"  ✅ '{esp}' → EXACTA")
                else:
                    print(f"  ⚠️  '{esp}' → Encontrada como '{real}' (diferencia en mayúsculas/espacios)")
                encontradas_count += 1
            else:
                print(f"  ❌ '{esp}' → NO ENCONTRADA")
        
        # Extras
        print(f"\n📋 COLUMNAS ADICIONALES (no en lista esperada):")
        print("-" * 80)
        extras_count = 0
        for col in columnas_reales:
            col_norm = col.lower().strip()
            if col_norm not in esperados_norm:
                print(f"  ➕ '{col}'")
                extras_count += 1
        
        if extras_count == 0:
            print("  (Ninguna)")
        
        # Resumen
        print(f"\n" + "="*80)
        print("📊 RESUMEN:")
        print("="*80)
        print(f"  Columnas esperadas: {len(esperados)}")
        print(f"  Columnas encontradas: {encontradas_count}/{len(esperados)}")
        print(f"  Columnas reales: {len(columnas_reales)}")
        print(f"  Columnas adicionales: {extras_count}")
        
        if encontradas_count == len(esperados):
            print(f"\n  ✅ PERFECTO: Todas las columnas esperadas están presentes")
        elif encontradas_count >= len(esperados) * 0.8:
            print(f"\n  ⚠️  ADVERTENCIA: Faltan algunas columnas ({len(esperados) - encontradas_count})")
        else:
            print(f"\n  ❌ ERROR: Faltan muchas columnas ({len(esperados) - encontradas_count})")
        
    except Exception as e:
        print(f"❌ ERROR al leer archivo: {e}")

# ========================================
# MAIN
# ========================================

def main():
    """Ejecuta verificación de los 3 archivos"""
    
    print("\n" + "="*80)
    print("🔍 VERIFICACIÓN DE ENCABEZADOS EXCEL - DIAN vs ERP")
    print("="*80)
    print("Compara los encabezados reales con los esperados por el sistema")
    print("="*80)
    
    # Verificar cada archivo
    for nombre, ruta in FILES.items():
        verificar_archivo(nombre, ruta)
    
    # Resumen final
    print("\n" + "="*80)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("="*80)
    print("\n📝 NOTAS IMPORTANTES:")
    print("  • Las columnas con mayúsculas/minúsculas diferentes funcionan igual")
    print("  • Las columnas 'Docto. proveedor' deben contener 'docto' Y 'proveedor'")
    print("  • La columna 'C.O.' debe ser EXACTAMENTE 'C.O.' (con puntos)")
    print("  • La columna 'CUFE' es crítica en ACUSES (puede estar como 'cufe' o 'CUFE CUDE')")
    print("\n")

if __name__ == '__main__':
    main()
