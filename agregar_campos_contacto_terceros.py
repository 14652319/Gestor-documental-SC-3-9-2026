#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para agregar campos de contacto a la tabla terceros
Fecha: 30 de Enero 2026
Objetivo: Agregar columnas direccion, ciudad, departamento, telefono a tabla terceros
"""

import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'gestor_documental'),
    'user': os.getenv('DB_USER', 'gestor_user'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

# SQL para agregar columnas
SQL_AGREGAR_COLUMNAS = """
-- Agregar columna direccion
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='terceros' AND column_name='direccion'
    ) THEN
        ALTER TABLE terceros ADD COLUMN direccion VARCHAR(255);
        RAISE NOTICE '✅ Columna direccion agregada';
    ELSE
        RAISE NOTICE '⚠️ Columna direccion ya existe';
    END IF;
END $$;

-- Agregar columna ciudad
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='terceros' AND column_name='ciudad'
    ) THEN
        ALTER TABLE terceros ADD COLUMN ciudad VARCHAR(100);
        RAISE NOTICE '✅ Columna ciudad agregada';
    ELSE
        RAISE NOTICE '⚠️ Columna ciudad ya existe';
    END IF;
END $$;

-- Agregar columna departamento
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='terceros' AND column_name='departamento'
    ) THEN
        ALTER TABLE terceros ADD COLUMN departamento VARCHAR(100);
        RAISE NOTICE '✅ Columna departamento agregada';
    ELSE
        RAISE NOTICE '⚠️ Columna departamento ya existe';
    END IF;
END $$;

-- Agregar columna telefono (además de celular)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='terceros' AND column_name='telefono'
    ) THEN
        ALTER TABLE terceros ADD COLUMN telefono VARCHAR(30);
        RAISE NOTICE '✅ Columna telefono agregada';
    ELSE
        RAISE NOTICE '⚠️ Columna telefono ya existe';
    END IF;
END $$;

-- Comentarios en las columnas
COMMENT ON COLUMN terceros.direccion IS 'Dirección del tercero';
COMMENT ON COLUMN terceros.ciudad IS 'Ciudad del tercero';
COMMENT ON COLUMN terceros.departamento IS 'Departamento del tercero';
COMMENT ON COLUMN terceros.telefono IS 'Teléfono fijo (diferente a celular)';
"""

def main():
    print("\n" + "="*60)
    print(" MIGRACIÓN: Agregar Campos de Contacto a Terceros")
    print("="*60 + "\n")
    
    try:
        # Conectar a la base de datos
        print("📡 Conectando a la base de datos...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"✅ Conectado a: {DB_CONFIG['database']} en {DB_CONFIG['host']}\n")
        
        # Ejecutar SQL
        print("🔧 Ejecutando migración...\n")
        cursor.execute(SQL_AGREGAR_COLUMNAS)
        conn.commit()
        
        print("\n" + "-"*60)
        
        # Verificar columnas agregadas
        print("\n📋 Verificando estructura actual de tabla terceros:")
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'terceros'
            ORDER BY ordinal_position
        """)
        
        columnas = cursor.fetchall()
        for col in columnas:
            nombre = col[0]
            tipo = col[1]
            longitud = col[2] if col[2] else ''
            print(f"   • {nombre:<25} {tipo:<20} {longitud}")
        
        print("\n" + "="*60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        
        print("\n📝 Campos agregados:")
        print("   1. direccion   VARCHAR(255)")
        print("   2. ciudad      VARCHAR(100)")
        print("   3. departamento VARCHAR(100)")
        print("   4. telefono    VARCHAR(30)")
        
        print("\n🎯 PRÓXIMO PASO:")
        print("   Actualizar modelo Tercero en app.py línea 995:")
        print("   direccion = db.Column(db.String(255))")
        print("   ciudad = db.Column(db.String(100))")
        print("   departamento = db.Column(db.String(100))")
        print("   telefono = db.Column(db.String(30))")
        print()
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"\n❌ ERROR DE BASE DE DATOS: {e}")
        print(f"   Código: {e.pgcode}")
        print(f"   Mensaje: {e.pgerror}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
