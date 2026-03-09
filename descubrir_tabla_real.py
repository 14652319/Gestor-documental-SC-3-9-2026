#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Descubrir estructura REAL de facturas_digitales y generar modelo correcto
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from sqlalchemy import text

with app.app_context():
    # Obtener todas las columnas
    result = db.session.execute(text("""
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'facturas_digitales'
        ORDER BY ordinal_position;
    """))
    
    columnas = result.fetchall()
    
    print("=" * 80)
    print("ESTRUCTURA REAL DE facturas_digitales")
    print("=" * 80)
    print(f"\nTotal columnas: {len(columnas)}\n")
    
    for col in columnas:
        nombre = col[0]
        tipo = col[1]
        longitud = col[2] if col[2] else ''
        nullable = col[3]
        default = col[4] if col[4] else ''
        
        print(f"{nombre:40} {tipo:20} {str(longitud):10} nullable={nullable}")
    
    print("\n" + "=" * 80)
    print("GENERAR MODELO CORRECTO:")
    print("=" * 80)
    print()
