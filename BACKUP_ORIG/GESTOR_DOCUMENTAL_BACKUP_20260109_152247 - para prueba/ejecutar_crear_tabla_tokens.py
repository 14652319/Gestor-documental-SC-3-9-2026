# -*- coding: utf-8 -*-
"""
Script para crear la tabla tokens_password en la base de datos
"""
import psycopg2
from psycopg2 import sql

def crear_tabla_tokens():
    """Crea la tabla tokens_password si no existe"""
    try:
        # Conexion a la base de datos
        conn = psycopg2.connect(
            host="localhost",
            database="gestor_documental",
            user="postgres",
            password="Inicio2024*"
        )
        cur = conn.cursor()
        
        print("[OK] Conectado a PostgreSQL")
        print("[...] Creando tabla tokens_password...")
        
        # SQL para crear la tabla
        sql_crear = """
        -- Tabla para almacenar tokens de recuperacion/establecimiento de contrasena
        CREATE TABLE IF NOT EXISTS tokens_password (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            token VARCHAR(255) NOT NULL UNIQUE,
            expiracion TIMESTAMP NOT NULL,
            usado BOOLEAN DEFAULT FALSE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Indice en el campo token para busquedas rapidas
        CREATE INDEX IF NOT EXISTS idx_tokens_password_token ON tokens_password(token);
        
        -- Indice en usuario_id para consultas por usuario
        CREATE INDEX IF NOT EXISTS idx_tokens_password_usuario ON tokens_password(usuario_id);
        
        -- Indice en expiracion para limpiar tokens expirados
        CREATE INDEX IF NOT EXISTS idx_tokens_password_expiracion ON tokens_password(expiracion);
        
        -- Restriccion unica: un usuario solo puede tener un token activo
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_usuario_token'
            ) THEN
                ALTER TABLE tokens_password ADD CONSTRAINT uq_usuario_token UNIQUE (usuario_id);
            END IF;
        END $$;
        
        -- Comentarios para documentacion
        COMMENT ON TABLE tokens_password IS 'Almacena tokens de recuperacion y establecimiento de contrasena';
        COMMENT ON COLUMN tokens_password.token IS 'Token unico generado con secrets.token_urlsafe(32)';
        COMMENT ON COLUMN tokens_password.expiracion IS 'Fecha y hora de expiracion del token (24 horas)';
        COMMENT ON COLUMN tokens_password.usado IS 'Indica si el token ya fue utilizado';
        """
        
        cur.execute(sql_crear)
        conn.commit()
        
        print("[OK] Tabla tokens_password creada exitosamente")
        print("[OK] Indices creados correctamente")
        print("[OK] Restriccion de unicidad aplicada")
        
        # Verificar que la tabla existe
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'tokens_password'
            ORDER BY ordinal_position;
        """)
        
        columnas = cur.fetchall()
        print("\nEstructura de la tabla:")
        for col in columnas:
            nullable = 'NULL' if col[2] == 'YES' else 'NOT NULL'
            print("   - %s: %s (%s)" % (col[0], col[1], nullable))
        
        cur.close()
        conn.close()
        
        print("\n[SUCCESS] Tabla lista para almacenar tokens de password.")
        return True
        
    except Exception as e:
        print("[ERROR] %s" % str(e))
        return False

if __name__ == "__main__":
    crear_tabla_tokens()
