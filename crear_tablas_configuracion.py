"""
Script para crear las tablas de configuración de Facturas Digitales
"""
from extensions import db
from app import app
from sqlalchemy import text

def crear_tablas_configuracion():
    """Crea las tablas de configuración para el módulo de facturas digitales"""
    
    with app.app_context():
        try:
            # 1. TIPO_DOC_FACTURACION
            print("📄 Creando tabla TIPO_DOC_FACTURACION...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS tipo_doc_facturacion (
                    id SERIAL PRIMARY KEY,
                    sigla VARCHAR(10) NOT NULL UNIQUE,
                    descripcion VARCHAR(100) NOT NULL,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT NOW(),
                    usuario_creacion VARCHAR(50)
                );
            """))
            
            # Insertar datos iniciales
            db.session.execute(text("""
                INSERT INTO tipo_doc_facturacion (sigla, descripcion, usuario_creacion)
                VALUES 
                    ('FC', 'FACTURA', 'admin'),
                    ('NC', 'NOTA DÉBITO', 'admin'),
                    ('ND', 'NOTA CRÉDITO', 'admin')
                ON CONFLICT (sigla) DO NOTHING;
            """))
            
            # 2. FORMA_PAGO_FACTURACION
            print("💳 Creando tabla FORMA_PAGO_FACTURACION...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS forma_pago_facturacion (
                    id SERIAL PRIMARY KEY,
                    sigla VARCHAR(10) NOT NULL UNIQUE,
                    descripcion VARCHAR(100) NOT NULL,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT NOW(),
                    usuario_creacion VARCHAR(50)
                );
            """))
            
            # Insertar datos iniciales
            db.session.execute(text("""
                INSERT INTO forma_pago_facturacion (sigla, descripcion, usuario_creacion)
                VALUES 
                    ('EST', 'ESTÁNDAR', 'admin'),
                    ('TC', 'TARJETA DE CRÉDITO', 'admin')
                ON CONFLICT (sigla) DO NOTHING;
            """))
            
            # 3. TIPO_SERVICIO_FACTURACION
            print("🛠️ Creando tabla TIPO_SERVICIO_FACTURACION...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS tipo_servicio_facturacion (
                    id SERIAL PRIMARY KEY,
                    sigla VARCHAR(10) NOT NULL UNIQUE,
                    descripcion VARCHAR(100) NOT NULL,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT NOW(),
                    usuario_creacion VARCHAR(50)
                );
            """))
            
            # Insertar datos iniciales
            db.session.execute(text("""
                INSERT INTO tipo_servicio_facturacion (sigla, descripcion, usuario_creacion)
                VALUES 
                    ('COMP', 'COMPRA', 'admin'),
                    ('SERV', 'SERVICIO', 'admin'),
                    ('HONO', 'HONORARIO', 'admin'),
                    ('COMP-SERV', 'COMPRA Y SERVICIO', 'admin')
                ON CONFLICT (sigla) DO NOTHING;
            """))
            
            # 4. DEPARTAMENTOS_FACTURACION
            print("🏢 Creando tabla DEPARTAMENTOS_FACTURACION...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS departamentos_facturacion (
                    id SERIAL PRIMARY KEY,
                    sigla VARCHAR(10) NOT NULL UNIQUE,
                    nombre VARCHAR(100) NOT NULL,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT NOW(),
                    usuario_creacion VARCHAR(50)
                );
            """))
            
            # Insertar datos iniciales
            db.session.execute(text("""
                INSERT INTO departamentos_facturacion (sigla, nombre, usuario_creacion)
                VALUES 
                    ('TIC', 'TECNOLOGIA', 'admin'),
                    ('MER', 'MERCADEO', 'admin'),
                    ('MYP', 'MERCADEO ESTRATEGICO', 'admin'),
                    ('DOM', 'DOMICILIOS', 'admin'),
                    ('FIN', 'FINANCIERO', 'admin')
                ON CONFLICT (sigla) DO NOTHING;
            """))
            
            db.session.commit()
            
            print("\n✅ ¡Tablas creadas exitosamente!")
            print("\n📊 Resumen:")
            print("   • tipo_doc_facturacion: 3 registros")
            print("   • forma_pago_facturacion: 2 registros")
            print("   • tipo_servicio_facturacion: 4 registros")
            print("   • departamentos_facturacion: 5 registros")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    crear_tablas_configuracion()
