#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ejecutor directo de SQL sin contexto Flask
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

def conectar_db():
    """Conecta directamente a PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="gestor_documental", 
            user="gestor_user",
            password="Canaveral2024*",
            port="5432",
            client_encoding="utf8"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        return None

def ejecutar_sql_monitoreo():
    """Ejecuta el SQL del sistema de monitoreo"""
    print("=" * 80)
    print("🔧 EJECUTANDO SQL DE MONITOREO DIRECTAMENTE")
    print("=" * 80)
    
    conn = conectar_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Leer SQL
        sql_file = 'sql/monitoreo_completo.sql'
        if not os.path.exists(sql_file):
            print(f"❌ No existe: {sql_file}")
            return
            
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Ejecutar cada comando
        comandos = [c.strip() for c in sql_content.split(';') if c.strip() and not c.strip().startswith('--')]
        
        exitos = 0
        errores = 0
        
        for i, comando in enumerate(comandos, 1):
            if not comando:
                continue
                
            try:
                print(f"📝 Ejecutando comando {i}...")
                cursor.execute(comando)
                exitos += 1
                print(f"   ✅ OK")
            except Exception as e:
                error_str = str(e)
                if 'already exists' in error_str or 'ya existe' in error_str:
                    print(f"   ⏭️ Ya existe (OK)")
                    exitos += 1
                else:
                    print(f"   ❌ Error: {error_str[:100]}")
                    errores += 1
        
        print(f"\n✅ Comandos exitosos: {exitos}")
        print(f"⚠️ Errores: {errores}")
        
        # Verificar tablas creadas
        print("\n📊 VERIFICANDO TABLAS:")
        tablas = ['sesiones_activas', 'logs_sistema', 'logs_auditoria', 
                 'alertas_sistema', 'metricas_rendimiento', 'ips_blancas']
        
        for tabla in tablas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"   ✅ {tabla:25s} | {count:3d} registros")
            except Exception as e:
                print(f"   ❌ {tabla:25s} | Error: {str(e)[:50]}")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Error general: {e}")
    finally:
        conn.close()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    ejecutar_sql_monitoreo()