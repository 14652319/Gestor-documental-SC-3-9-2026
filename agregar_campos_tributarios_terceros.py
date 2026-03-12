#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Migración: Agregar campos tributarios DIAN y correos adicionales a la tabla terceros
Fecha: Marzo 2026
Columnas nuevas:
  - email_contabilidad, email_tesoreria, email_comercial
  - codigo_ciiu
  - responsable_iva, autorretenedor_renta, gran_contribuyente
  - gran_contribuyente_ica, dept_gc_ica, mun_gc_ica
  - autorretenedor_ica, dept_autorretenedor_ica, mun_autorretenedor_ica
  - agente_retenedor_iva, regimen_simple
  - otras_responsabilidades (JSON)
  - categoria_tercero (si no existe)
  - notificaciones_activas (si no existe)
  - telefono_secundario, contacto_principal, cargo_contacto (si no existen)
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(encoding='latin-1')

# Prefer DATABASE_URL (used by the app); fall back to individual vars
DATABASE_URL = os.getenv('DATABASE_URL', '')
if DATABASE_URL:
    DB_CONNECT = DATABASE_URL
    DB_CONFIG = None
else:
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'gestor_documental'),
        'user': os.getenv('DB_USER', 'gestor_user'),
        'password': os.getenv('DB_PASSWORD', 'password'),
    }
    DB_CONNECT = None

COLUMNAS = [
    # (nombre, tipo, default)
    ('categoria_tercero',          'VARCHAR(50)',  None),
    ('telefono_secundario',        'VARCHAR(30)',  None),
    ('contacto_principal',         'VARCHAR(150)', None),
    ('cargo_contacto',             'VARCHAR(100)', None),
    ('notificaciones_activas',     'BOOLEAN',      'TRUE'),
    ('email_contabilidad',         'VARCHAR(150)', None),
    ('email_tesoreria',            'VARCHAR(150)', None),
    ('email_comercial',            'VARCHAR(150)', None),
    ('codigo_ciiu',                'VARCHAR(20)',  None),
    ('responsable_iva',            'BOOLEAN',      'FALSE'),
    ('autorretenedor_renta',       'BOOLEAN',      'FALSE'),
    ('gran_contribuyente',         'BOOLEAN',      'FALSE'),
    ('gran_contribuyente_ica',     'BOOLEAN',      'FALSE'),
    ('dept_gc_ica',                'VARCHAR(100)', None),
    ('mun_gc_ica',                 'VARCHAR(100)', None),
    ('autorretenedor_ica',         'BOOLEAN',      'FALSE'),
    ('dept_autorretenedor_ica',    'VARCHAR(100)', None),
    ('mun_autorretenedor_ica',     'VARCHAR(100)', None),
    ('agente_retenedor_iva',       'BOOLEAN',      'FALSE'),
    ('regimen_simple',             'BOOLEAN',      'FALSE'),
    ('otras_responsabilidades',    'TEXT',         None),
    ('fecha_actualizacion',        'TIMESTAMP',    None),
]

def ejecutar_migracion():
    try:
        if DB_CONNECT:
            conn = psycopg2.connect(DB_CONNECT)
        else:
            conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cur = conn.cursor()

        agregadas = []
        ya_existen = []

        for nombre, tipo, default in COLUMNAS:
            cur.execute("""
                SELECT 1 FROM information_schema.columns
                WHERE table_name='terceros' AND column_name=%s
            """, (nombre,))
            existe = cur.fetchone()

            if not existe:
                if default:
                    sql = f"ALTER TABLE terceros ADD COLUMN {nombre} {tipo} DEFAULT {default}"
                else:
                    sql = f"ALTER TABLE terceros ADD COLUMN {nombre} {tipo}"
                cur.execute(sql)
                agregadas.append(nombre)
                print(f"  ✅ Columna agregada: {nombre} ({tipo})")
            else:
                ya_existen.append(nombre)
                print(f"  ℹ️  Ya existe: {nombre}")

        conn.commit()
        cur.close()
        conn.close()

        print(f"\n✅ Migración completada.")
        print(f"   Columnas nuevas:   {len(agregadas)}")
        print(f"   Ya existían:       {len(ya_existen)}")
        if agregadas:
            print(f"   Agregadas: {', '.join(agregadas)}")

    except Exception as e:
        print(f"\n❌ Error en migración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🔄 Iniciando migración de campos tributarios y correos...")
    ejecutar_migracion()
