#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ver schema de ERP_FINANCIERO y ERP_COMERCIAL
"""

import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'database': 'gestor_documental',
    'user': 'postgres',
    'password': 'G3st0radm$2025.'
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

print("="*80)
print("COLUMNAS DE erp_comercial")
print("="*80)
cursor.execute("""
    SELECT column_name, data_type, character_maximum_length
    FROM information_schema.columns
    WHERE table_name = 'erp_comercial'
    ORDER BY ordinal_position
""")
for row in cursor.fetchall():
    length = f"({row[2]})" if row[2] else ""
    print(f"  {row[0]:<30} {row[1]}{length}")

print("\n" + "="*80)
print("COLUMNAS DE erp_financiero")
print("="*80)
cursor.execute("""
    SELECT column_name, data_type, character_maximum_length
    FROM information_schema.columns
    WHERE table_name = 'erp_financiero'
    ORDER BY ordinal_position
""")
for row in cursor.fetchall():
    length = f"({row[2]})" if row[2] else ""
    print(f"  {row[0]:<30} {row[1]}{length}")

print("\n" + "="*80)
print("COLUMNAS DE acuses")
print("="*80)
cursor.execute("""
    SELECT column_name, data_type, character_maximum_length
    FROM information_schema.columns
    WHERE table_name = 'acuses'
    ORDER BY ordinal_position
""")
for row in cursor.fetchall():
    length = f"({row[2]})" if row[2] else ""
    print(f"  {row[0]:<30} {row[1]}{length}")

cursor.close()
conn.close()
