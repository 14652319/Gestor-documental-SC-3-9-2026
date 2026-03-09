# -*- coding: utf-8 -*-
"""
Agrega columna tipos_tercero a la tabla envios_programados_dian_vs_erp
"""
from app import app, db
import sqlalchemy

print("=" * 80)
print("🔧 AGREGANDO COLUMNA tipos_tercero")
print("=" * 80)

with app.app_context():
    try:
        # Verificar si la columna ya existe
        inspector = sqlalchemy.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('envios_programados_dian_vs_erp')]
        
        if 'tipos_tercero' in columns:
            print("✅ La columna tipos_tercero ya existe")
        else:
            print("\n📝 Agregando columna tipos_tercero...")
            db.session.execute(sqlalchemy.text("""
                ALTER TABLE envios_programados_dian_vs_erp 
                ADD COLUMN tipos_tercero TEXT
            """))
            db.session.commit()
            print("✅ Columna tipos_tercero agregada exitosamente")
            print("   Valores permitidos (JSON): PROVEEDORES, ACREEDORES, PROVEEDORES Y ACREEDORES, NO REGISTRADOS")
        
        print("\n" + "=" * 80)
        print("✅ PROCESO COMPLETADO")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.session.rollback()
