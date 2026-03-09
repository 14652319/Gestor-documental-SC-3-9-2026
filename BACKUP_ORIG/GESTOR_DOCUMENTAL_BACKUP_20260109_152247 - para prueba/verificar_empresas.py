# -*- coding: utf-8 -*-
import psycopg2
import sys
sys.stdout.reconfigure(encoding='utf-8')

try:
    conn = psycopg2.connect(
        host="localhost",
        database="gestor_documental",
        user="postgres",
        password="Inicio2024*",
        client_encoding='UTF8'
    )
    cursor = conn.cursor()
    
    print("=== VERIFICANDO TABLA EMPRESAS ===")
    cursor.execute("SELECT COUNT(*) FROM empresas")
    count = cursor.fetchone()[0]
    print(f"Total empresas: {count}")
    
    print("\n=== PRIMERAS 10 EMPRESAS ===")
    cursor.execute("SELECT id_empresa, nombre_empresa, codigo, activo FROM empresas LIMIT 10")
    empresas = cursor.fetchall()
    for emp in empresas:
        print(f"ID: {emp[0]}, Nombre: {emp[1]}, Codigo: {emp[2]}, Activo: {emp[3]}")
    
    print("\n=== VERIFICANDO NIT 14652319 EN TERCEROS ===")
    cursor.execute("SELECT nit, razon_social, estado FROM terceros WHERE nit = '14652319'")
    tercero = cursor.fetchone()
    if tercero:
        print(f"✅ NIT encontrado: {tercero[0]} - {tercero[1]} - Estado: {tercero[2]}")
    else:
        print("❌ NIT NO encontrado")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
