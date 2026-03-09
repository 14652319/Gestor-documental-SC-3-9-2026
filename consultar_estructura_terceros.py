#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Consultar estructura de tabla terceros"""

from app import app, db
from sqlalchemy import text

with app.app_context():
    result = db.session.execute(text("""
        SELECT column_name, data_type, character_maximum_length 
        FROM information_schema.columns 
        WHERE table_name='terceros' 
        ORDER BY ordinal_position
    """))
    
    print("\n📋 ESTRUCTURA ACTUAL tabla terceros:\n")
    for row in result:
        nombre = row[0]
        tipo = row[1]
        longitud = row[2] if row[2] else ''
        print(f"   • {nombre:<30} {tipo:<25} {longitud}")
    
    print("\n" + "="*70)
    print("\n💡 RECOMENDACIÓN:")
    print("   Crear tabla 'terceros_extendidos' con relación 1:1")
    print("   - terceros: Campos básicos (usado por recepción facturas)")
    print("   - terceros_extendidos: Campos detallados (SAGRILAFT)\n")
