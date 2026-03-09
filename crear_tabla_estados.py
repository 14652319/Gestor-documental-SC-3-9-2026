"""Crear tabla estados_documentos si no existe"""
from extensions import db
from sqlalchemy import text

try:
    with db.engine.connect() as conn:
        print("\n📋 Creando tabla estados_documentos...")
        
        # SQL para crear la tabla
        crear_tabla_sql = text("""
        CREATE TABLE IF NOT EXISTS estados_documentos (
            id SERIAL PRIMARY KEY,
            documento_id INTEGER NOT NULL UNIQUE,
            estado VARCHAR(50) NOT NULL,
            observacion TEXT,
            usuario_revisor VARCHAR(100),
            fecha_revision TIMESTAMP,
            FOREIGN KEY (documento_id) REFERENCES documentos_tercero(id) ON DELETE CASCADE
        );
        
        CREATE INDEX IF NOT EXISTS idx_estados_documento_id 
        ON estados_documentos(documento_id);
        """)
        
        conn.execute(crear_tabla_sql)
        conn.commit()
        
        print("✅ Tabla 'estados_documentos' creada exitosamente")
        print("✅ Índice 'idx_estados_documento_id' creado")
        print("\n📊 Estructura:")
        print("   - id: SERIAL PRIMARY KEY")
        print("   - documento_id: INTEGER UNIQUE (FK a documentos_tercero)")
        print("   - estado: VARCHAR(50)")
        print("   - observacion: TEXT")
        print("   - usuario_revisor: VARCHAR(100)")
        print("   - fecha_revision: TIMESTAMP")
        
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print(f"Tipo: {type(e).__name__}")
