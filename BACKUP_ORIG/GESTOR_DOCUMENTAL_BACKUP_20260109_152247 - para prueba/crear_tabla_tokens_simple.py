# coding: utf-8
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
        print("Conectando a la base de datos...")
        
        sql = """
        CREATE TABLE IF NOT EXISTS tokens_password (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            token VARCHAR(255) NOT NULL UNIQUE,
            expiracion TIMESTAMP NOT NULL,
            usado BOOLEAN DEFAULT FALSE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_tokens_password_token ON tokens_password(token);
        CREATE INDEX IF NOT EXISTS idx_tokens_password_usuario ON tokens_password(usuario_id);
        CREATE INDEX IF NOT EXISTS idx_tokens_password_expiracion ON tokens_password(expiracion);
        """
        
        db.session.execute(text(sql))
        db.session.commit()
        
        print("[OK] Tabla tokens_password creada exitosamente")
        
        # Verificar
        result = db.session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'tokens_password'
            ORDER BY ordinal_position
        """))
        
        print("\nEstructura de la tabla:")
        for row in result:
            print("  - %s: %s" % (row[0], row[1]))
            
        print("\n[SUCCESS] Todo listo!")
        
    except Exception as e:
        print("[ERROR] %s" % str(e))
