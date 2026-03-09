# -*- coding: utf-8 -*-
"""Probar conexión a PostgreSQL"""
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text

# Probar con diferentes configuraciones
configs = [
    ("postgres directo", "postgresql://postgres:G3st0radm$2025.@localhost:5432/gestor_documental"),
    ("postgres URL encoded", f"postgresql://postgres:{quote_plus('G3st0radm$2025.')}@localhost:5432/gestor_documental"),
    ("postgres simple", "postgresql://postgres@localhost:5432/gestor_documental"),
]

for nombre, uri in configs:
    print(f"\n🔍 Probando: {nombre}")
    try:
        engine = create_engine(uri, echo=False)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM terceros"))
            count = result.scalar()
            print(f"   ✅ CONECTADO - {count} terceros en BD")
            break
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
