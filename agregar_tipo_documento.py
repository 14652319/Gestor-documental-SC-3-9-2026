"""
Migración: Agrega columna tipo_documento a la tabla terceros.

Ejecutar UNA SOLA VEZ antes de reiniciar el servidor:
    python agregar_tipo_documento.py

Valores válidos:
  Persona Jurídica : NIT
  Persona Natural  : CC, TI, CE, NIT, PA, PPT, PEP
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def migrar():
    with app.app_context():
        with db.engine.connect() as conn:
            # 1. Agregar columna si no existe
            existe = conn.execute(text("""
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'terceros' AND column_name = 'tipo_documento'
            """)).fetchone()

            if existe:
                print("✅ La columna tipo_documento ya existe. No se requiere migración.")
            else:
                conn.execute(text("""
                    ALTER TABLE terceros
                    ADD COLUMN tipo_documento VARCHAR(5)
                """))
                print("✅ Columna tipo_documento agregada.")

            # 2. Rellenar registros existentes con valor por defecto
            # Persona jurídica → NIT, persona natural → CC (cédula más común)
            conn.execute(text("""
                UPDATE terceros
                SET tipo_documento = CASE
                    WHEN tipo_persona = 'juridica' THEN 'NIT'
                    ELSE 'CC'
                END
                WHERE tipo_documento IS NULL
            """))
            conn.commit()
            print("✅ Registros existentes actualizados (jurídica→NIT, natural→CC).")

        # Verificar resultado
        with db.engine.connect() as conn:
            resultado = conn.execute(text("""
                SELECT tipo_documento, COUNT(*) as total
                FROM terceros
                GROUP BY tipo_documento
                ORDER BY tipo_documento
            """)).fetchall()
            print("\n📊 Distribución de tipo_documento en BD:")
            for row in resultado:
                print(f"   {row[0] or 'NULL':6} → {row[1]} registros")

if __name__ == '__main__':
    migrar()
    print("\n🎉 Migración completada. Reinicia el servidor Flask.")
