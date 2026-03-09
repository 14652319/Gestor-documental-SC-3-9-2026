#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificador simple de BD sin Flask
"""
import psycopg2
import os

def verificar_tablas_existentes():
    """Verifica qué tablas de monitoreo existen"""
    try:
        # Conectar con las credenciales correctas
        conn = psycopg2.connect(
            host="localhost",
            database="gestor_documental",
            user="postgres", 
            password="G3st0radm$2025.",
            port="5432"
        )
            
        cursor = conn.cursor()
        
        print("🔍 VERIFICANDO TABLAS DE MONITOREO:")
        print("-" * 50)
        
        tablas = [
            'sesiones_activas',
            'logs_sistema', 
            'logs_auditoria',
            'alertas_sistema',
            'metricas_rendimiento',
            'ips_blancas'
        ]
        
        for tabla in tablas:
            try:
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_name = '{tabla}'
                """)
                existe = cursor.fetchone()[0] > 0
                
                if existe:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    count = cursor.fetchone()[0]
                    print(f"✅ {tabla:25s} | {count:3d} registros")
                else:
                    print(f"❌ {tabla:25s} | NO EXISTE")
                    
            except Exception as e:
                print(f"⚠️ {tabla:25s} | Error: {str(e)[:40]}")
        
        # Verificar también las tablas originales de IP
        print("\n🔍 VERIFICANDO TABLAS DE IP ORIGINALES:")
        print("-" * 50)
        
        tablas_ip = ['ips_negras', 'ips_sospechosas', 'ips_lista_negra']
        
        for tabla in tablas_ip:
            try:
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_name = '{tabla}'
                """)
                existe = cursor.fetchone()[0] > 0
                
                if existe:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    count = cursor.fetchone()[0]
                    print(f"✅ {tabla:25s} | {count:3d} registros")
                else:
                    print(f"❌ {tabla:25s} | NO EXISTE")
                    
            except Exception as e:
                print(f"⚠️ {tabla:25s} | Error: {str(e)[:40]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    verificar_tablas_existentes()