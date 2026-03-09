"""
Script para agregar campo empresa_id a las tablas de recibir_facturas
Ejecutar desde Flask app context para evitar problemas de encoding
"""
from flask import Flask
from extensions import db
from sqlalchemy import text

# Crear app Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Inicio2024*@localhost/gestor_documental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar db
db.init_app(app)

with app.app_context():
    try:
        print("🔧 Agregando campo empresa_id a tablas de recibir_facturas...")
        
        # SQL para agregar columna empresa_id a facturas_temporales
        db.session.execute(text("""
            -- Agregar columna empresa_id a facturas_temporales (permitir NULL temporalmente)
            ALTER TABLE facturas_temporales 
            ADD COLUMN IF NOT EXISTS empresa_id VARCHAR(10);
            
            -- Agregar foreign key (empresas usa 'sigla' como clave, no 'codigo')
            ALTER TABLE facturas_temporales
            DROP CONSTRAINT IF EXISTS fk_facturas_temporales_empresa;
            
            ALTER TABLE facturas_temporales
            ADD CONSTRAINT fk_facturas_temporales_empresa
            FOREIGN KEY (empresa_id) REFERENCES empresas(sigla)
            ON DELETE RESTRICT;
            
            -- Crear índice para mejorar rendimiento
            CREATE INDEX IF NOT EXISTS idx_facturas_temporales_empresa
            ON facturas_temporales(empresa_id);
        """))
        
        print("✅ Campo empresa_id agregado a facturas_temporales")
        
        # SQL para agregar columna empresa_id a facturas_recibidas
        db.session.execute(text("""
            -- Agregar columna empresa_id a facturas_recibidas (permitir NULL temporalmente)
            ALTER TABLE facturas_recibidas
            ADD COLUMN IF NOT EXISTS empresa_id VARCHAR(10);
            
            -- Agregar foreign key (empresas usa 'sigla' como clave, no 'codigo')
            ALTER TABLE facturas_recibidas
            DROP CONSTRAINT IF EXISTS fk_facturas_recibidas_empresa;
            
            ALTER TABLE facturas_recibidas
            ADD CONSTRAINT fk_facturas_recibidas_empresa
            FOREIGN KEY (empresa_id) REFERENCES empresas(sigla)
            ON DELETE RESTRICT;
            
            -- Crear índice para mejorar rendimiento
            CREATE INDEX IF NOT EXISTS idx_facturas_recibidas_empresa
            ON facturas_recibidas(empresa_id);
        """))
        
        print("✅ Campo empresa_id agregado a facturas_recibidas")
        
        # Commit de cambios
        db.session.commit()
        print("\n🎉 ¡Campos agregados exitosamente!")
        print("\n📋 Resumen:")
        print("   - facturas_temporales.empresa_id (VARCHAR(10), FK a empresas.codigo)")
        print("   - facturas_recibidas.empresa_id (VARCHAR(10), FK a empresas.codigo)")
        print("   - Índices creados para optimizar consultas")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
