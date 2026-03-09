"""
Script para agregar CYS al constraint de departamentos
Fecha: 2025-12-08
"""

from app import app, db
from sqlalchemy import text

def actualizar_constraint():
    """Actualizar constraint ck_departamento para incluir CYS"""
    
    with app.app_context():
        try:
            print("🔧 Actualizando constraint ck_departamento...")
            
            # 1. Eliminar constraint antiguo
            print("   1️⃣ Eliminando constraint antiguo...")
            db.session.execute(text("""
                ALTER TABLE usuario_departamento 
                DROP CONSTRAINT IF EXISTS ck_departamento;
            """))
            db.session.commit()
            print("   ✅ Constraint antiguo eliminado")
            
            # 2. Crear constraint nuevo con CYS incluido (orden alfabético)
            print("   2️⃣ Creando constraint nuevo con CYS...")
            db.session.execute(text("""
                ALTER TABLE usuario_departamento 
                ADD CONSTRAINT ck_departamento 
                CHECK (departamento IN ('CYS', 'DOM', 'FIN', 'MER', 'MYP', 'TIC'));
            """))
            db.session.commit()
            print("   ✅ Constraint nuevo creado")
            
            # 3. Verificar
            print("\n🔍 Verificando constraint actualizado...")
            result = db.session.execute(text("""
                SELECT pg_get_constraintdef(c.oid) 
                FROM pg_constraint c 
                JOIN pg_class t ON c.conrelid = t.oid 
                WHERE t.relname = 'usuario_departamento' 
                AND conname = 'ck_departamento'
            """)).fetchone()
            
            if result:
                print(f"   📋 Constraint: {result[0]}")
            
            print("\n✅ ¡Constraint actualizado exitosamente!")
            print("📋 Departamentos permitidos: CYS, DOM, FIN, MER, MYP, TIC")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    actualizar_constraint()
