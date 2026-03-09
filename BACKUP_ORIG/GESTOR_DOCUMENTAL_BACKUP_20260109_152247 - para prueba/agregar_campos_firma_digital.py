"""
Script para agregar campos de trazabilidad de firma digital
Fecha: 2025-12-08
"""

from app import app, db
from sqlalchemy import text

def agregar_campos_firma():
    """Agregar campos para trazabilidad completa de firma digital"""
    
    with app.app_context():
        try:
            print("🔧 Agregando campos de trazabilidad de firma...")
            
            # 1. Agregar usuario_firmador (quien firmó el documento)
            print("   1️⃣ Agregando usuario_firmador...")
            db.session.execute(text("""
                ALTER TABLE facturas_digitales 
                ADD COLUMN IF NOT EXISTS usuario_firmador VARCHAR(100);
            """))
            db.session.execute(text("""
                COMMENT ON COLUMN facturas_digitales.usuario_firmador 
                IS 'Usuario que firmó digitalmente el documento';
            """))
            
            # 2. Agregar token_firma (token único de la firma)
            print("   2️⃣ Agregando token_firma...")
            db.session.execute(text("""
                ALTER TABLE facturas_digitales 
                ADD COLUMN IF NOT EXISTS token_firma VARCHAR(100);
            """))
            db.session.execute(text("""
                COMMENT ON COLUMN facturas_digitales.token_firma 
                IS 'Token único de 6 dígitos usado para autorizar la firma';
            """))
            
            # 3. Agregar firma_digital_hash (SHA256 de la firma)
            print("   3️⃣ Agregando firma_digital_hash...")
            db.session.execute(text("""
                ALTER TABLE facturas_digitales 
                ADD COLUMN IF NOT EXISTS firma_digital_hash VARCHAR(64);
            """))
            db.session.execute(text("""
                COMMENT ON COLUMN facturas_digitales.firma_digital_hash 
                IS 'Hash SHA256 de la firma digital (garantiza integridad)';
            """))
            
            # 4. Agregar ip_firma (IP desde donde se firmó)
            print("   4️⃣ Agregando ip_firma...")
            db.session.execute(text("""
                ALTER TABLE facturas_digitales 
                ADD COLUMN IF NOT EXISTS ip_firma VARCHAR(45);
            """))
            db.session.execute(text("""
                COMMENT ON COLUMN facturas_digitales.ip_firma 
                IS 'Dirección IP desde donde se realizó la firma';
            """))
            
            # 5. Agregar user_agent_firma (navegador/dispositivo de firma)
            print("   5️⃣ Agregando user_agent_firma...")
            db.session.execute(text("""
                ALTER TABLE facturas_digitales 
                ADD COLUMN IF NOT EXISTS user_agent_firma TEXT;
            """))
            db.session.execute(text("""
                COMMENT ON COLUMN facturas_digitales.user_agent_firma 
                IS 'Navegador/dispositivo usado para firmar';
            """))
            
            db.session.commit()
            print("\n✅ ¡Campos de trazabilidad agregados exitosamente!")
            
            # Verificar columnas agregadas
            print("\n🔍 Verificando columnas nuevas...")
            result = db.session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'facturas_digitales'
                AND column_name IN ('usuario_firmador', 'token_firma', 'firma_digital_hash', 'ip_firma', 'user_agent_firma')
                ORDER BY column_name
            """)).fetchall()
            
            print(f"\n📋 COLUMNAS AGREGADAS:")
            for row in result:
                print(f"  ✅ {row[0]:<30} {row[1]}")
            
            print(f"\n🎯 Total agregadas: {len(result)}/5 columnas")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    agregar_campos_firma()
