# -*- coding: utf-8 -*-
"""
Script para agregar campos faltantes a facturas_digitales
- empresa
- ruta_carpeta
- ruta_archivo_principal
- ruta_archivo_anexo1
- ruta_archivo_anexo2
- ruta_archivo_seg_social
"""
from extensions import db
from app import app
from sqlalchemy import text

with app.app_context():
    print("\n🔧 Agregando campos faltantes a facturas_digitales...\n")
    
    campos = [
        ("empresa", "VARCHAR(10)", "Sigla de la empresa"),
        ("ruta_carpeta", "TEXT", "Ruta relativa de la carpeta"),
        ("ruta_archivo_principal", "TEXT", "Nombre del archivo principal"),
        ("ruta_archivo_anexo1", "TEXT", "Anexo 1"),
        ("ruta_archivo_anexo2", "TEXT", "Anexo 2"),
        ("ruta_archivo_seg_social", "TEXT", "Seguridad social")
    ]
    
    for nombre, tipo, descripcion in campos:
        try:
            # Verificar si la columna existe
            result = db.session.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'facturas_digitales' 
                AND column_name = '{nombre}'
            """))
            
            existe = result.fetchone()
            
            if not existe:
                # Agregar columna
                db.session.execute(text(f"""
                    ALTER TABLE facturas_digitales 
                    ADD COLUMN {nombre} {tipo}
                """))
                db.session.commit()
                print(f"✅ Campo '{nombre}' agregado ({descripcion})")
            else:
                print(f"⏭️  Campo '{nombre}' ya existe")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error con campo '{nombre}': {e}")
    
    print("\n✅ Proceso completado\n")
