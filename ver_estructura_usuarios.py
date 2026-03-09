#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ver estructura real de la tabla usuarios
"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Ver columnas de la tabla usuarios
        query = """
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'usuarios' 
            ORDER BY ordinal_position
        """
        result = db.session.execute(text(query)).fetchall()
        
        print("\n📊 ESTRUCTURA DE TABLA 'usuarios':")
        print("=" * 70)
        for col in result:
            max_len = f"({col[2]})" if col[2] else ""
            print(f"  • {col[0]:30s} → {col[1]}{max_len}")
        
        print(f"\n✅ Total de columnas: {len(result)}")
        
        # Verificar si existe correo
        columnas = [col[0] for col in result]
        print("\n🔍 VERIFICACIÓN DE COLUMNAS DE EMAIL:")
        print(f"  • 'correo': {'✅ SÍ EXISTE' if 'correo' in columnas else '❌ NO EXISTE'}")
        print(f"  • 'email': {'✅ SÍ EXISTE' if 'email' in columnas else '❌ NO EXISTE'}")
        print(f"  • 'email_notificaciones': {'✅ SÍ EXISTE' if 'email_notificaciones' in columnas else '❌ NO EXISTE'}")
        
        # Contar usuarios activos
        count_query = "SELECT COUNT(*) FROM usuarios WHERE activo = true"
        count = db.session.execute(text(count_query)).scalar()
        print(f"\n👥 USUARIOS ACTIVOS: {count}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
