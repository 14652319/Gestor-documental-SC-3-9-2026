"""Verificar si existe la tabla estados_documentos"""
from extensions import db
from sqlalchemy import text, inspect
import sys

try:
    # Conectar a la base de datos
    with db.engine.connect() as conn:
        # Obtener lista de tablas
        inspector = inspect(db.engine)
        tablas = inspector.get_table_names()
        
        print("\n🔍 VERIFICANDO TABLA estados_documentos...")
        print("=" * 50)
        
        if 'estados_documentos' in tablas:
            print("✅ Tabla 'estados_documentos' EXISTE\n")
            
            # Mostrar estructura
            columnas = inspector.get_columns('estados_documentos')
            print("📋 Estructura de la tabla:")
            for col in columnas:
                print(f"   - {col['name']}: {col['type']}")
            
            # Contar registros
            result = conn.execute(text("SELECT COUNT(*) FROM estados_documentos")).fetchone()
            print(f"\n📊 Registros actuales: {result[0]}")
            
        else:
            print("❌ Tabla 'estados_documentos' NO EXISTE")
            print("\n💡 SOLUCIÓN:")
            print("   Necesitas crear la tabla con este SQL:")
            print("""
CREATE TABLE estados_documentos (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL UNIQUE,
    estado VARCHAR(50) NOT NULL,
    observacion TEXT,
    usuario_revisor VARCHAR(100),
    fecha_revision TIMESTAMP,
    FOREIGN KEY (documento_id) REFERENCES documentos_tercero(id) ON DELETE CASCADE
);

CREATE INDEX idx_estados_documento_id ON estados_documentos(documento_id);
            """)
            
        print("\n" + "=" * 50)
        
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print(f"Tipo de error: {type(e).__name__}")
    sys.exit(1)
