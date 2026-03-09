"""
Crear tabla para historial de envíos a firma
Permite guardar TODAS las veces que se envía un documento
"""
from extensions import db
from app import app
from sqlalchemy import text

with app.app_context():
    print("\n📋 CREANDO TABLA historial_envios_firma\n")
    print("=" * 80)
    
    try:
        # Crear tabla de historial
        create_table = text("""
            CREATE TABLE IF NOT EXISTS historial_envios_firma (
                id SERIAL PRIMARY KEY,
                factura_id INTEGER NOT NULL,
                fecha_envio TIMESTAMP NOT NULL,
                usuario_envio VARCHAR(100) NOT NULL,
                destinatario_email VARCHAR(255),
                departamento VARCHAR(10),
                FOREIGN KEY (factura_id) REFERENCES facturas_digitales(id) ON DELETE CASCADE
            )
        """)
        
        db.session.execute(create_table)
        db.session.commit()
        
        print("✅ Tabla 'historial_envios_firma' creada exitosamente")
        print("\n📊 ESTRUCTURA:")
        print("  - id: Identificador único")
        print("  - factura_id: Referencia a facturas_digitales")
        print("  - fecha_envio: Cuándo se envió")
        print("  - usuario_envio: Quién lo envió")
        print("  - destinatario_email: Email del firmador")
        print("  - departamento: Departamento responsable")
        
        # Crear índice para búsquedas rápidas
        create_index = text("""
            CREATE INDEX IF NOT EXISTS idx_historial_factura 
            ON historial_envios_firma(factura_id)
        """)
        
        db.session.execute(create_index)
        db.session.commit()
        
        print("\n✅ Índice creado para búsquedas rápidas")
        
        print("\n" + "=" * 80)
        print("✅ ¡Tabla lista para usar!\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()
