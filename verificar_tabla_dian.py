# -*- coding: utf-8 -*-
"""
Verificar el NOMBRE REAL de la tabla dian en PostgreSQL
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import db
from sqlalchemy import inspect

print("\n" + "="*80)
print("VERIFICANDO NOMBRE DE TABLA 'dian' EN POSTGRESQL")
print("="*80)

# Obtener inspector de la BD
inspector = inspect(db.engine)

# Listar todas las tablas
print("\n📋 TODAS LAS TABLAS EN gestor_documental:")
tablas = inspector.get_table_names()
tablas_dian = [t for t in tablas if 'dian' in t.lower()]

print(f"\n✅ Tablas que contienen 'dian': {len(tablas_dian)}")
for tabla in sorted(tablas_dian):
    # Contar registros
    try:
        resultado = db.session.execute(db.text(f"SELECT COUNT(*) FROM {tabla}"))
        count = resultado.scalar()
        print(f"   - {tabla:40s} = {count:,} registros")
    except Exception as e:
        print(f"   - {tabla:40s} = ERROR: {str(e)[:50]}")

# Verificar tabla 'dian' específicamente
print("\n🔍 VERIFICANDO TABLA 'dian':")
if 'dian' in tablas:
    print("   ✅ La tabla 'dian' EXISTE")
    
    # Obtener columnas
    columnas = inspector.get_columns('dian')
    print(f"   ✅ Tiene {len(columnas)} columnas:")
    for col in columnas[:10]:  # Mostrar primeras 10
        print(f"      - {col['name']:30s} ({col['type']})")
else:
    print("   ❌ La tabla 'dian' NO EXISTE")
    print("   Posibles nombres alternativos:")
    for tabla in tablas_dian:
        print(f"      - {tabla}")

print("\n" + "="*80)
