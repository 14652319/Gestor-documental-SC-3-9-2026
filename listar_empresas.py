# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        result = db.session.execute(text("""
            SELECT sigla, nombre, activo 
            FROM empresas 
            ORDER BY sigla
        """))
        
        print("=== EMPRESAS EN LA BASE DE DATOS ===")
        empresas = result.fetchall()
        
        if not empresas:
            print("❌ NO HAY EMPRESAS REGISTRADAS")
        else:
            for empresa in empresas:
                estado = "✅ ACTIVA" if empresa[2] else "❌ INACTIVA"
                print(f"{empresa[0]} - {empresa[1]} [{estado}]")
        
        print(f"\nTotal: {len(empresas)} empresas")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
