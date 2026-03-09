#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2

# Conectar DIRECTAMENTE con psycopg2
conn = psycopg2.connect(
    host="localhost",
    database="gestor_documental",
    user="postgres",
    password="Inicio2024*"
)

cur = conn.cursor()

# Obtener estructura
cur.execute("""
    SELECT column_name, data_type, character_maximum_length, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'facturas_digitales'
    ORDER BY ordinal_position;
""")

columnas = cur.fetchall()

print("\n" + "="*90)
print("ESTRUCTURA REAL DE LA TABLA facturas_digitales")
print("="*90)
print(f"\nTotal: {len(columnas)} columnas\n")
print(f"{'NOMBRE':<45} {'TIPO':<20} {'MAX_LEN':<10} {'NULL':<10}")
print("-"*90)

for col in columnas:
    nombre = col[0]
    tipo = col[1]
    longitud = str(col[2]) if col[2] else 'N/A'
    nullable = col[3]
    print(f"{nombre:<45} {tipo:<20} {longitud:<10} {nullable:<10}")

print("\n" + "="*90)

cur.close()
conn.close()
