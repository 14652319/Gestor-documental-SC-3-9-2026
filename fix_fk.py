# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        print("Agregando columna empresa_id y FKs...")
        
        # Facturas temporales - Agregar columna
        db.session.execute(text(
            "ALTER TABLE facturas_temporales ADD COLUMN IF NOT EXISTS empresa_id VARCHAR(10)"
        ))
        # Eliminar FK anterior si existe
        db.session.execute(text(
            "ALTER TABLE facturas_temporales DROP CONSTRAINT IF EXISTS fk_facturas_temporales_empresa"
        ))
        # Agregar FK correcta
        db.session.execute(text(
            "ALTER TABLE facturas_temporales ADD CONSTRAINT fk_facturas_temporales_empresa "
            "FOREIGN KEY (empresa_id) REFERENCES empresas(sigla) ON DELETE RESTRICT"
        ))
        # Crear índice
        db.session.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_facturas_temporales_empresa ON facturas_temporales(empresa_id)"
        ))
        print("✅ facturas_temporales")
        
        # Facturas recibidas - Agregar columna
        db.session.execute(text(
            "ALTER TABLE facturas_recibidas ADD COLUMN IF NOT EXISTS empresa_id VARCHAR(10)"
        ))
        # Eliminar FK anterior si existe
        db.session.execute(text(
            "ALTER TABLE facturas_recibidas DROP CONSTRAINT IF EXISTS fk_facturas_recibidas_empresa"
        ))
        # Agregar FK correcta
        db.session.execute(text(
            "ALTER TABLE facturas_recibidas ADD CONSTRAINT fk_facturas_recibidas_empresa "
            "FOREIGN KEY (empresa_id) REFERENCES empresas(sigla) ON DELETE RESTRICT"
        ))
        # Crear índice
        db.session.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_facturas_recibidas_empresa ON facturas_recibidas(empresa_id)"
        ))
        print("✅ facturas_recibidas")
        
        db.session.commit()
        print("\n✅ COLUMNAS Y FKs CREADAS EXITOSAMENTE")
        
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
        sys.exit(1)
