# -*- coding: utf-8 -*-
"""Verificar campos creados en facturas_digitales"""
from app import app
from extensions import db
from sqlalchemy import text

with app.app_context():
    try:
        # Consultar columnas de la tabla
        resultado = db.session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'facturas_digitales'
            ORDER BY ordinal_position
        """)).fetchall()
        
        print("\n" + "="*80)
        print("COLUMNAS EN facturas_digitales")
        print("="*80)
        
        for col in resultado:
            print(f"{col[0]:30} | {col[1]:20} | Null: {col[2]:3} | Default: {col[3] or 'N/A'}")
        
        print("\n" + "="*80)
        print(f"TOTAL: {len(resultado)} columnas")
        print("="*80)
        
    except Exception as e:
        print(f"Error: {e}")
