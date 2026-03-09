"""
Script para crear tabla de observaciones de radicados SAGRILAFT
Guarda las observaciones de cambios de estado de radicados
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Conexión a base de datos
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://gestor_user:GestorPass2024!@localhost:5432/gestor_documental')

print("\n🔧 Creando tabla observaciones_radicado...")
print("=" * 60)

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Crear tabla
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS observaciones_radicado (
                id SERIAL PRIMARY KEY,
                radicado VARCHAR(20) NOT NULL,
                estado VARCHAR(30) NOT NULL,
                observacion TEXT,
                usuario VARCHAR(100),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_radicado FOREIGN KEY (radicado) 
                    REFERENCES solicitudes_registro(radicado) ON DELETE CASCADE
            );
        """))
        
        # Crear índice para búsqueda rápida
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_observaciones_radicado 
            ON observaciones_radicado(radicado);
        """))
        
        # Crear índice para ordenar por fecha
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_observaciones_fecha 
            ON observaciones_radicado(fecha_registro DESC);
        """))
        
        conn.commit()
    
    print("\n✅ Tabla 'observaciones_radicado' creada exitosamente")
    print("\nEstructura de la tabla:")
    print("  - id (SERIAL, PRIMARY KEY)")
    print("  - radicado (VARCHAR(20), FK)")
    print("  - estado (VARCHAR(30))")
    print("  - observacion (TEXT)")
    print("  - usuario (VARCHAR(100))")
    print("  - fecha_registro (TIMESTAMP)")
    print("\nÍndices:")
    print("  - idx_observaciones_radicado (radicado)")
    print("  - idx_observaciones_fecha (fecha_registro DESC)")
    
    # Verificar tabla existe
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'observaciones_radicado'
            );
        """))
        existe = result.scalar()
    
    if existe:
        print("\n✅ Verificación: Tabla existe en la base de datos")
    else:
        print("\n❌ Error: Tabla no se creó correctamente")
        
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("=" * 60)
