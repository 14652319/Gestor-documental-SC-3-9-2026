#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificador de estructura de tablas
"""
import psycopg2

def verificar_estructura():
    """Verifica la estructura de las tablas de monitoreo"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="gestor_documental",
            user="postgres", 
            password="G3st0radm$2025.",
            port="5432"
        )
        cursor = conn.cursor()
        
        tablas = ['ips_blancas', 'sesiones_activas', 'alertas_sistema']
        
        for tabla in tablas:
            print(f"\n🔍 ESTRUCTURA DE {tabla.upper()}:")
            print("-" * 40)
            
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = '{tabla}'
                ORDER BY ordinal_position
            """)
            
            columnas = cursor.fetchall()
            if columnas:
                for col in columnas:
                    print(f"   {col[0]:25s} | {col[1]:15s} | NULL: {col[2]}")
            else:
                print(f"   ⚠️ Tabla {tabla} no existe o no tiene columnas")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verificar_estructura()