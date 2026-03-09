# -*- coding: utf-8 -*-
"""
Script para crear tabla de estados de documentos
"""
from app import app, db

# SQL para crear la tabla
SQL_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS estados_documentos (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documentos_tercero(id) ON DELETE CASCADE,
    estado VARCHAR(30) NOT NULL,  -- 'aprobado', 'rechazado', 'aprobado_condicionado', 'pendiente'
    observacion TEXT,
    usuario_revisor VARCHAR(100),
    fecha_revision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(documento_id)  -- Un solo estado por documento (el más reciente)
);

CREATE INDEX IF NOT EXISTS idx_estados_documentos_documento_id ON estados_documentos(documento_id);
CREATE INDEX IF NOT EXISTS idx_estados_documentos_estado ON estados_documentos(estado);
"""

with app.app_context():
    try:
        # SQLAlchemy 2.0 syntax
        from sqlalchemy import text
        
        with db.engine.connect() as connection:
            connection.execute(text(SQL_CREATE_TABLE))
            connection.commit()
        
        print("✅ Tabla 'estados_documentos' creada exitosamente")
        
        # Verificar que existe
        with db.engine.connect() as connection:
            result = connection.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'estados_documentos'
                ORDER BY ordinal_position;
            """))
            
            print("\n📋 Columnas de la tabla:")
            for row in result:
                print(f"   - {row[0]}: {row[1]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
