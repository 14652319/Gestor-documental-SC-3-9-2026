#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear tablas de configuración de backup
"""
import psycopg2
from psycopg2 import sql

# Configuración de conexión
DB_CONFIG = {
    'dbname': 'gestor_documental',
    'user': 'gestor_user',
    'password': 'Temporal2024*',
    'host': 'localhost',
    'port': 5432
}

SQL_CREAR_TABLAS = """
-- Tabla de configuración de backups
CREATE TABLE IF NOT EXISTS configuracion_backup (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL UNIQUE,
    habilitado BOOLEAN DEFAULT TRUE,
    destino VARCHAR(500) NOT NULL,
    horario_cron VARCHAR(50) DEFAULT '0 2 * * *',
    dias_retencion INTEGER DEFAULT 7,
    ultima_ejecucion TIMESTAMP,
    proximo_backup TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para búsqueda por tipo
CREATE INDEX IF NOT EXISTS idx_config_backup_tipo ON configuracion_backup(tipo);

-- Tabla de historial de backups
CREATE TABLE IF NOT EXISTS historial_backup (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP,
    estado VARCHAR(20) NOT NULL,
    ruta_archivo VARCHAR(500),
    tamano_bytes BIGINT,
    duracion_segundos INTEGER,
    mensaje VARCHAR(1000),
    error VARCHAR(2000),
    usuario VARCHAR(50)
);

-- Índices para mejorar consultas
CREATE INDEX IF NOT EXISTS idx_historial_tipo ON historial_backup(tipo);
CREATE INDEX IF NOT EXISTS idx_historial_fecha ON historial_backup(fecha_inicio DESC);
CREATE INDEX IF NOT EXISTS idx_historial_estado ON historial_backup(estado);

-- Insertar configuración por defecto
INSERT INTO configuracion_backup (tipo, destino, horario_cron, dias_retencion, habilitado)
VALUES 
    ('base_datos', 'C:\\Backups_GestorDocumental\\base_datos', '0 2 * * *', 7, TRUE),
    ('archivos', 'C:\\Backups_GestorDocumental\\documentos', '0 3 * * *', 14, TRUE),
    ('codigo', 'C:\\Backups_GestorDocumental\\codigo', '0 4 * * 0', 30, TRUE)
ON CONFLICT (tipo) DO NOTHING;
"""

def main():
    print("=" * 70)
    print("  CREANDO TABLAS DE CONFIGURACION DE BACKUP")
    print("=" * 70)
    
    try:
        # Conectar a la base de datos
        print("\nConectando a PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Conexion exitosa\n")
        
        # Ejecutar script SQL
        print("Ejecutando script SQL...")
        cursor.execute(SQL_CREAR_TABLAS)
        conn.commit()
        
        print("Tablas creadas exitosamente\n")
        
        # Verificar tablas
        print("Verificando tablas creadas:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('configuracion_backup', 'historial_backup')
            ORDER BY table_name
        """)
        
        tablas = cursor.fetchall()
        for tabla in tablas:
            print(f"   OK: {tabla[0]}")
        
        # Verificar configuracion insertada
        print("\nConfiguracion de backup insertada:")
        cursor.execute("SELECT tipo, habilitado, dias_retencion FROM configuracion_backup ORDER BY tipo")
        configs = cursor.fetchall()
        
        for config in configs:
            tipo, habilitado, dias = config
            estado = "Habilitado" if habilitado else "Deshabilitado"
            print(f"   - {tipo:15} | {estado} | Retencion: {dias} dias")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("  TABLAS CREADAS CORRECTAMENTE")
        print("=" * 70)
        print("\nAhora puedes ejecutar: python ejecutar_backup.py todos\n")
        
        return True
        
    except psycopg2.Error as e:
        print(f"\nERROR DE BASE DE DATOS:")
        print(f"   {str(e)}")
        return False
        
    except Exception as e:
        print(f"\nERROR INESPERADO:")
        print(f"   {str(e)}")
        return False

if __name__ == '__main__':
    main()
