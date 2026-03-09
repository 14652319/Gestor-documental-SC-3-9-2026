# -*- coding: utf-8 -*-
"""Script para identificar datos con problemas de encoding"""
import sys
import os

# Agregar path del proyecto
proyecto_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, proyecto_path)

from extensions import db
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Conectar a la base de datos
DATABASE_URI = 'postgresql://gestor_user:Rriascos07_1@localhost:5432/gestor_documental'
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

print("🔍 Buscando registros con problemas de encoding...\n")

# Consultar todos los terceros y solicitudes
query = text("""
    SELECT 
        sr.id,
        sr.radicado,
        t.nit,
        t.razon_social,
        sr.estado,
        sr.observaciones,
        length(t.razon_social) as len_razon,
        length(sr.observaciones) as len_obs
    FROM solicitudes_registro sr
    JOIN terceros t ON sr.tercero_id = t.id
    ORDER BY sr.fecha_solicitud ASC
""")

try:
    result = session.execute(query)
    count = 0
    problemas = 0
    
    for row in result:
        count += 1
        rad = row[1]
        nit = row[2]
        razon = row[3]
        estado = row[4]
        obs = row[5]
        
        # Intentar codificar/decodificar
        try:
            if razon:
                test = str(razon).encode('utf-8').decode('utf-8')
            if obs:
                test = str(obs).encode('utf-8').decode('utf-8')
            print(f"✅ {rad} | {nit} | OK")
        except Exception as e:
            problemas += 1
            print(f"❌ {rad} | {nit} | ERROR: {e}")
            print(f"   Razón social: {repr(razon)}")
            if obs:
                print(f"   Observaciones: {repr(obs)}")
    
    print(f"\n📊 Total registros: {count}")
    print(f"⚠️ Con problemas: {problemas}")
    
except Exception as e:
    print(f"❌ Error en consulta: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()
