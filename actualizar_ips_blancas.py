#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Actualizador de estructura de ips_blancas
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def actualizar_ips_blancas():
    """Actualiza la tabla ips_blancas para que tenga la estructura completa"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="gestor_documental",
            user="postgres", 
            password="G3st0radm$2025.",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("🔧 ACTUALIZANDO ESTRUCTURA DE ips_blancas")
        print("-" * 50)
        
        # Agregar columnas faltantes una por una
        columnas_agregar = [
            ("id SERIAL PRIMARY KEY", "id auto-incremental"),
            ("descripcion VARCHAR(255)", "descripción de la IP"),
            ("usuario_agrego VARCHAR(100)", "usuario que agregó la IP"),
            ("fecha_agregada TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "fecha de agregado"),
            ("activa BOOLEAN DEFAULT TRUE", "si la IP está activa"),
            ("ultimo_acceso TIMESTAMP", "último acceso registrado"),
            ("total_accesos INTEGER DEFAULT 0", "total de accesos")
        ]
        
        for columna_sql, descripcion in columnas_agregar:
            try:
                print(f"📝 Agregando columna: {descripcion}...")
                cursor.execute(f"ALTER TABLE ips_blancas ADD COLUMN IF NOT EXISTS {columna_sql}")
                print(f"   ✅ Columna agregada")
            except Exception as e:
                print(f"   ⚠️ Error: {str(e)[:80]}")
        
        # Crear índice único en ip si no existe
        print(f"\n📝 Creando índice único en ip...")
        try:
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_ips_blancas_ip ON ips_blancas(ip)")
            print(f"   ✅ Índice creado")
        except Exception as e:
            print(f"   ⚠️ Error: {str(e)[:80]}")
        
        # Agregar IPs localhost iniciales
        print(f"\n📝 Agregando IPs localhost...")
        
        ips_localhost = [
            ('127.0.0.1', 'IPv4 localhost - Acceso local'),
            ('::1', 'IPv6 localhost - Acceso local'),
            ('192.168.11.33', 'IP local del servidor')
        ]
        
        for ip, desc in ips_localhost:
            try:
                cursor.execute("""
                    INSERT INTO ips_blancas (ip, descripcion, usuario_agrego, activa)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (ip) DO UPDATE SET descripcion = EXCLUDED.descripcion
                """, (ip, desc, 'sistema', True))
                print(f"   ✅ {ip} configurada")
            except Exception as e:
                print(f"   ⚠️ Error con {ip}: {str(e)[:80]}")
        
        # Verificar resultado
        print(f"\n📊 VERIFICANDO ESTRUCTURA FINAL:")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'ips_blancas'
            ORDER BY ordinal_position
        """)
        
        columnas = cursor.fetchall()
        for col in columnas:
            print(f"   ✅ {col[0]:20s} | {col[1]}")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM ips_blancas WHERE activa = true")
        count = cursor.fetchone()[0]
        print(f"\n📊 IPs activas en lista blanca: {count}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 ACTUALIZACIÓN COMPLETADA")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    actualizar_ips_blancas()