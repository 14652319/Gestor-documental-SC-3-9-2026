#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Obtener estructura REAL de facturas_digitales SIN importar el modelo roto
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Crear app minima sin imports
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Inicio2024*@localhost/gestor_documental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():
    result = db.session.execute(text("""
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable
        FROM information_schema.columns
        WHERE table_name = 'facturas_digitales'
        ORDER BY ordinal_position;
    """))
    
    columnas = result.fetchall()
    
    print("\n" + "="*80)
    print("ESTRUCTURA REAL DE facturas_digitales")
    print("="*80)
    print(f"\nTotal: {len(columnas)} columnas\n")
    
    for col in columnas:
        print(f"{col[0]:45} {col[1]:20} max_len={str(col[2]) if col[2] else 'N/A':10} nullable={col[3]}")
    
    print("\n" + "="*80)
