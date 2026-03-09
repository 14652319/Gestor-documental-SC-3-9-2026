# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')

from extensions import db
from flask import Flask
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Inicio2024*@localhost/gestor_documental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    try:
        print("Agregando restriccion UNIQUE a usuario_id...")
        
        # Primero eliminar duplicados si existen
        db.session.execute(text("""
            DELETE FROM tokens_password 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM tokens_password 
                GROUP BY usuario_id
            );
        """))
        
        # Agregar la restricción UNIQUE
        db.session.execute(text("""
            ALTER TABLE tokens_password 
            DROP CONSTRAINT IF EXISTS tokens_password_usuario_id_key CASCADE;
            
            ALTER TABLE tokens_password 
            ADD CONSTRAINT tokens_password_usuario_id_key UNIQUE (usuario_id);
        """))
        
        db.session.commit()
        
        print("[OK] Restriccion UNIQUE agregada exitosamente")
        print("[OK] Ahora ON CONFLICT funcionara correctamente")
        
    except Exception as e:
        print("[ERROR] %s" % str(e))
        db.session.rollback()
