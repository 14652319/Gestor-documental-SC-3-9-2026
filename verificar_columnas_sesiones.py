#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla sesiones_activas
"""

from app import app, db
from sqlalchemy import text

def verificar_columnas():
    with app.app_context():
        try:
            # Verificar columnas de sesiones_activas
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'sesiones_activas'
                ORDER BY ordinal_position
            """))
            
            columnas = result.fetchall()
            
            print("✅ ESTRUCTURA DE TABLA sesiones_activas:")
            print("-" * 50)
            for col in columnas:
                print(f"{col[0]:25} | {col[1]:15} | Nullable: {col[2]}")
            
            # Verificar algunos registros
            print("\n✅ REGISTROS DE EJEMPLO:")
            print("-" * 50)
            result = db.session.execute(text("SELECT * FROM sesiones_activas LIMIT 3"))
            registros = result.fetchall()
            for reg in registros:
                print(reg)
                
            print(f"\n✅ Total registros: {len(registros)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    verificar_columnas()