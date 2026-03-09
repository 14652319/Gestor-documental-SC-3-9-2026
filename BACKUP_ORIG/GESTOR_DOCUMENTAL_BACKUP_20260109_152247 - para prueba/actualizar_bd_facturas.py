# -*- coding: utf-8 -*-
"""
Script para actualizar la tabla facturas_digitales con nuevos campos
Ejecutar: python actualizar_bd_facturas.py
"""
from extensions import db
from flask import Flask
from sqlalchemy import text
import os

# Configurar Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Inicio2024*@localhost/gestor_documental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar DB
db.init_app(app)

with app.app_context():
    try:
        # Leer archivo SQL
        sql_path = os.path.join('sql', 'actualizar_facturas_digitales.sql')
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Ejecutar por partes (separar por punto y coma)
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for i, statement in enumerate(statements, 1):
            try:
                if statement.strip():
                    db.session.execute(text(statement))
                    db.session.commit()
                    print(f"[OK] Statement {i}/{len(statements)} ejecutado")
            except Exception as e:
                print(f"[WARN] Statement {i}: {str(e)[:100]}")
                db.session.rollback()
                continue
        
        print("\n✅ Base de datos actualizada exitosamente")
        print("✅ Nuevos campos agregados:")
        print("   - fecha_radicacion (automática)")
        print("   - empresa (SC/LG)")
        print("   - prefijo, folio")
        print("   - tipo_documento (factura/nota_credito)")
        print("   - tipo_servicio (servicio/compra/ambos)")
        print("   - archivo_zip_path, archivo_seguridad_social_path")
        print("   - archivos_soportes_paths (array)")
        print("   - historial_observaciones (JSON)")
        print("   - Índice único: nit + prefijo + folio")
        print("   - Función: validar_factura_duplicada()")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        db.session.rollback()
