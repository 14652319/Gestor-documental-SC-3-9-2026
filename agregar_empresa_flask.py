# -*- coding: utf-8 -*-
"""
Agregar columna empresa usando Flask context
"""
from extensions import db
from flask import Flask
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Inicio2024*@localhost/gestor_documental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    try:
        print("\n" + "="*70)
        print("AGREGANDO COLUMNA EMPRESA")
        print("="*70 + "\n")
        
        # Intentar agregar columna empresa
        try:
            db.session.execute(text("""
                ALTER TABLE facturas_digitales 
                ADD COLUMN IF NOT EXISTS empresa VARCHAR(10) NOT NULL DEFAULT 'SC'
            """))
            db.session.commit()
            print("✅ Columna 'empresa' agregada correctamente")
        except Exception as e:
            print(f"⚠️  Error o columna ya existe: {e}")
            db.session.rollback()
        
        # Verificar todas las columnas
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'facturas_digitales'
            ORDER BY ordinal_position
        """))
        
        columnas = [row[0] for row in result]
        
        print("\n📋 COLUMNAS EN LA TABLA:")
        print("-" * 70)
        for col in columnas:
            print(f"   - {col}")
        
        print(f"\n   Total: {len(columnas)} columnas")
        
        if 'empresa' in columnas:
            print("\n✅ COLUMNA 'empresa' EXISTE")
        else:
            print("\n❌ COLUMNA 'empresa' NO EXISTE")
        
        print("\n" + "="*70)
        print("PROCESO COMPLETADO")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
