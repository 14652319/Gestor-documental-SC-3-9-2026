# -*- coding: utf-8 -*-
"""Agregar campos faltantes a facturas_digitales"""
from app import app
from extensions import db
from sqlalchemy import text

print("\n" + "="*60)
print("AGREGANDO CAMPOS FALTANTES")
print("="*60 + "\n")

with app.app_context():
    campos = [
        ("departamento", "VARCHAR(50) NOT NULL DEFAULT 'FINANCIERO'", "Departamento que carga"),
        ("forma_pago", "VARCHAR(20) NOT NULL DEFAULT 'ESTANDAR'", "Forma de pago"),
        ("estado_firma", "VARCHAR(30) DEFAULT 'PENDIENTE_FIRMA'", "Estado del documento"),
        ("archivo_firmado_path", "TEXT", "Ruta del PDF firmado"),
        ("numero_causacion", "VARCHAR(50)", "Número de causación"),
        ("fecha_pago", "TIMESTAMP", "Fecha de pago"),
    ]
    
    for nombre, tipo, descripcion in campos:
        try:
            sql = f"ALTER TABLE facturas_digitales ADD COLUMN IF NOT EXISTS {nombre} {tipo}"
            db.session.execute(text(sql))
            db.session.commit()
            print(f"✅ {nombre:25} agregado correctamente")
        except Exception as e:
            if "already exists" in str(e) or "ya existe" in str(e).lower():
                print(f"⚠️  {nombre:25} ya existe (saltando)")
                db.session.rollback()
            else:
                print(f"❌ {nombre:25} ERROR: {str(e)[:50]}")
                db.session.rollback()
    
    # Crear índices
    print("\n" + "="*60)
    print("CREANDO ÍNDICES")
    print("="*60 + "\n")
    
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_facturas_digitales_departamento ON facturas_digitales(departamento)",
        "CREATE INDEX IF NOT EXISTS idx_facturas_digitales_forma_pago ON facturas_digitales(forma_pago)",
        "CREATE INDEX IF NOT EXISTS idx_facturas_digitales_estado_firma ON facturas_digitales(estado_firma)",
        "CREATE INDEX IF NOT EXISTS idx_facturas_digitales_numero_causacion ON facturas_digitales(numero_causacion)",
    ]
    
    for idx_sql in indices:
        try:
            db.session.execute(text(idx_sql))
            db.session.commit()
            nombre_idx = idx_sql.split("idx_facturas_digitales_")[1].split(" ON")[0]
            print(f"✅ Índice {nombre_idx} creado")
        except Exception as e:
            print(f"⚠️  Índice ya existe o error: {str(e)[:50]}")
            db.session.rollback()
    
    print("\n" + "="*60)
    print("✅ ACTUALIZACIÓN COMPLETADA")
    print("="*60)
