#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para agregar campos de contacto a la tabla terceros
Fecha: 30 de Enero 2026
"""

from app import app, db
from sqlalchemy import text

def ejecutar_migracion():
    print("\n" + "="*60)
    print(" MIGRACIÓN: Agregar Campos de Contacto a Terceros")
    print("="*60 + "\n")
    
    with app.app_context():
        try:
            # SQL para agregar columnas
            sql_statements = [
                # direccion
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='terceros' AND column_name='direccion'
                    ) THEN
                        ALTER TABLE terceros ADD COLUMN direccion VARCHAR(255);
                        RAISE NOTICE '✅ Columna direccion agregada';
                    ELSE
                        RAISE NOTICE '⚠️ Columna direccion ya existe';
                    END IF;
                END $$;
                """,
                # ciudad
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='terceros' AND column_name='ciudad'
                    ) THEN
                        ALTER TABLE terceros ADD COLUMN ciudad VARCHAR(100);
                        RAISE NOTICE '✅ Columna ciudad agregada';
                    ELSE
                        RAISE NOTICE '⚠️ Columna ciudad ya existe';
                    END IF;
                END $$;
                """,
                # departamento
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='terceros' AND column_name='departamento'
                    ) THEN
                        ALTER TABLE terceros ADD COLUMN departamento VARCHAR(100);
                        RAISE NOTICE '✅ Columna departamento agregada';
                    ELSE
                        RAISE NOTICE '⚠️ Columna departamento ya existe';
                    END IF;
                END $$;
                """,
                # telefono
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='terceros' AND column_name='telefono'
                    ) THEN
                        ALTER TABLE terceros ADD COLUMN telefono VARCHAR(30);
                        RAISE NOTICE '✅ Columna telefono agregada';
                    ELSE
                        RAISE NOTICE '⚠️ Columna telefono ya existe';
                    END IF;
                END $$;
                """
            ]
            
            print("🔧 Ejecutando migración...\n")
            
            for sql in sql_statements:
                db.session.execute(text(sql))
            
            db.session.commit()
            
            print("\n" + "-"*60)
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("-"*60)
            
            # Verificar columnas
            result = db.session.execute(text("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'terceros'
                ORDER BY ordinal_position
            """))
            
            print("\n📋 Estructura actual de tabla terceros:\n")
            for row in result:
                nombre = row[0]
                tipo = row[1]
                longitud = row[2] if row[2] else ''
                print(f"   • {nombre:<25} {tipo:<20} {longitud}")
            
            print("\n" + "="*60)
            print("📝 Campos agregados:")
            print("   1. direccion   VARCHAR(255)")
            print("   2. ciudad      VARCHAR(100)")
            print("   3. departamento VARCHAR(100)")
            print("   4. telefono    VARCHAR(30)")
            print("="*60 + "\n")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {e}\n")
            return False

if __name__ == '__main__':
    success = ejecutar_migracion()
    exit(0 if success else 1)
