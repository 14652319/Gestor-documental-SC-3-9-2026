#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificar si existe la tabla usuario_departamento_firma
"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Verificar si la tabla existe
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'usuario_departamento_firma'
            )
        """
        existe = db.session.execute(text(query)).scalar()
        
        print("\n🔍 VERIFICACIÓN DE TABLA:")
        print("=" * 70)
        print(f"  usuario_departamento_firma: {'✅ SÍ EXISTE' if existe else '❌ NO EXISTE'}")
        
        if existe:
            # Contar registros
            count = db.session.execute(text(
                "SELECT COUNT(*) FROM usuario_departamento_firma"
            )).scalar()
            print(f"  Registros actuales: {count}")
            
            # Ver estructura
            cols_query = """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'usuario_departamento_firma' 
                ORDER BY ordinal_position
            """
            cols = db.session.execute(text(cols_query)).fetchall()
            print("\n  📋 Columnas:")
            for col in cols:
                print(f"    • {col[0]:30s} → {col[1]}")
        else:
            print("\n  ⚠️ Necesitas crear la tabla ejecutando:")
            print("     python crear_tabla_usuarios_permisos.py")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
