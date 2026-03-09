# -*- coding: utf-8 -*-
"""Script para verificar existencia y datos de tabla terceros"""
from app import app
from extensions import db
from sqlalchemy import text

with app.app_context():
  try:
    # Contar registros
    count = db.session.execute(text('SELECT COUNT(*) FROM terceros')).scalar()
    print(f"✅ Tabla terceros existe con {count} registros")
    
    # Mostrar ejemplos
    if count > 0:
        print("\n📋 Ejemplos de terceros:")
        ejemplos = db.session.execute(
            text('SELECT nit, razon_social FROM terceros LIMIT 5')
        ).fetchall()
        
        for nit, razon_social in ejemplos:
            print(f"  • {nit} - {razon_social}")
    else:
        print("⚠️ La tabla terceros está vacía")
        
  except Exception as e:
      print(f"❌ Error: {str(e)}")
      if "does not exist" in str(e):
          print("\n⚠️ La tabla terceros no existe en la base de datos")
          print("Necesitas crearla o importar datos de terceros")
