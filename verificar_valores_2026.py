#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificar valores en la columna 'valor' para registros de 2026
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# Configurar conexión
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

print("=" * 80)
print("VERIFICACIÓN DE VALORES EN COLUMNA 'valor' - AÑO 2026")
print("=" * 80)

with engine.connect() as conn:
    # Total de registros 2026
    result = conn.execute(text("""
        SELECT COUNT(*) as total
        FROM maestro_dian_vs_erp
        WHERE EXTRACT(YEAR FROM fecha_emision) = 2026
    """))
    total_2026 = result.fetchone()[0]
    print(f"\n📊 Total registros 2026: {total_2026:,}")
    
    # Registros con valor = 0
    result = conn.execute(text("""
        SELECT COUNT(*) as total
        FROM maestro_dian_vs_erp
        WHERE EXTRACT(YEAR FROM fecha_emision) = 2026
          AND (valor IS NULL OR valor = 0)
    """))
    cero_2026 = result.fetchone()[0]
    print(f"❌ Registros con valor NULL o 0: {cero_2026:,} ({cero_2026/total_2026*100:.1f}%)")
    
    # Registros con valor > 0
    result = conn.execute(text("""
        SELECT COUNT(*) as total
        FROM maestro_dian_vs_erp
        WHERE EXTRACT(YEAR FROM fecha_emision) = 2026
          AND valor > 0
    """))
    con_valor_2026 = result.fetchone()[0]
    print(f"✅ Registros con valor > 0: {con_valor_2026:,} ({con_valor_2026/total_2026*100:.1f}%)")
    
    # Ejemplos de registros con valor 0
    print(f"\n📋 Ejemplos de registros 2026 con valor = 0:")
    result = conn.execute(text("""
        SELECT fecha_emision, prefijo, folio, valor, nit_emisor
        FROM maestro_dian_vs_erp
        WHERE EXTRACT(YEAR FROM fecha_emision) = 2026
          AND (valor IS NULL OR valor = 0)
        LIMIT 5
    """))
    for row in result:
        print(f"   Fecha: {row[0]} | Prefijo: {row[1]} | Folio: {row[2]} | Valor: {row[3]} | NIT: {row[4]}")
    
    # Ejemplos de registros con valor > 0 (si hay)
    if con_valor_2026 > 0:
        print(f"\n📋 Ejemplos de registros 2026 con valor > 0:")
        result = conn.execute(text("""
            SELECT fecha_emision, prefijo, folio, valor, nit_emisor
            FROM maestro_dian_vs_erp
            WHERE EXTRACT(YEAR FROM fecha_emision) = 2026
              AND valor > 0
            LIMIT 5
        """))
        for row in result:
            print(f"   Fecha: {row[0]} | Prefijo: {row[1]} | Folio: {row[2]} | Valor: {row[3]:,.2f} | NIT: {row[4]}")
    
    # Comparación con 2025
    print(f"\n" + "=" * 80)
    print("COMPARACIÓN CON AÑO 2025")
    print("=" * 80)
    
    result = conn.execute(text("""
        SELECT COUNT(*) as total
        FROM maestro_dian_vs_erp
        WHERE EXTRACT(YEAR FROM fecha_emision) = 2025
    """))
    total_2025 = result.fetchone()[0]
    print(f"\n📊 Total registros 2025: {total_2025:,}")
    
    result = conn.execute(text("""
        SELECT COUNT(*) as total
        FROM maestro_dian_vs_erp
        WHERE EXTRACT(YEAR FROM fecha_emision) = 2025
          AND (valor IS NULL OR valor = 0)
    """))
    cero_2025 = result.fetchone()[0]
    print(f"❌ Registros con valor NULL o 0: {cero_2025:,} ({cero_2025/total_2025*100:.1f}%)")
    
    result = conn.execute(text("""
        SELECT COUNT(*) as total
        FROM maestro_dian_vs_erp
        WHERE EXTRACT(YEAR FROM fecha_emision) = 2025
          AND valor > 0
    """))
    con_valor_2025 = result.fetchone()[0]
    print(f"✅ Registros con valor > 0: {con_valor_2025:,} ({con_valor_2025/total_2025*100:.1f}%)")

print("\n" + "=" * 80)
print("FIN DE VERIFICACIÓN")
print("=" * 80)
