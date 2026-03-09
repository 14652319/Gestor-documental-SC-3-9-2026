#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear tabla terceros_extendidos
Fecha: 30 de Enero 2026
Contiene información detallada de contactos y tributaria
"""

from app import app, db
from sqlalchemy import text

def crear_terceros_extendidos():
    print("\n" + "="*70)
    print(" CREANDO TABLA: terceros_extendidos")
    print("="*70 + "\n")
    
    with app.app_context():
        try:
            # SQL para crear tabla
            sql_crear_tabla = """
            CREATE TABLE IF NOT EXISTS terceros_extendidos (
                id SERIAL PRIMARY KEY,
                tercero_id INTEGER NOT NULL REFERENCES terceros(id) ON DELETE CASCADE,
                
                -- CONTACTO TESORERÍA
                tesoreria_nombre VARCHAR(200),
                tesoreria_telefono VARCHAR(50),
                tesoreria_email VARCHAR(150),
                
                -- CONTACTO CONTABILIDAD
                contabilidad_nombre VARCHAR(200),
                contabilidad_telefono VARCHAR(50),
                contabilidad_email VARCHAR(150),
                
                -- CONTACTO PRINCIPAL (COMPRADOR)
                contacto_principal_nombre VARCHAR(200),
                contacto_principal_cargo VARCHAR(100),
                contacto_principal_telefono VARCHAR(50),
                contacto_principal_celular VARCHAR(50),
                contacto_principal_email VARCHAR(150),
                
                -- CONTACTO SECUNDARIO
                contacto_secundario_nombre VARCHAR(200),
                contacto_secundario_cargo VARCHAR(100),
                contacto_secundario_telefono VARCHAR(50),
                contacto_secundario_celular VARCHAR(50),
                contacto_secundario_email VARCHAR(150),
                
                -- INFORMACIÓN TRIBUTARIA
                actividad_economica_principal VARCHAR(500),
                codigo_ciiu_principal VARCHAR(20),
                actividad_economica_secundaria VARCHAR(500),
                codigo_ciiu_secundario VARCHAR(20),
                actividad_economica_terciaria VARCHAR(500),
                codigo_ciiu_terciario VARCHAR(20),
                
                -- RESPONSABILIDADES TRIBUTARIAS
                responsable_iva BOOLEAN DEFAULT FALSE,
                gran_contribuyente_dian BOOLEAN DEFAULT FALSE,
                gran_contribuyente_ica BOOLEAN DEFAULT FALSE,
                municipios_gran_contribuyente TEXT,  -- Separados por coma
                autorretenedor BOOLEAN DEFAULT FALSE,
                regimen_simple_tributacion BOOLEAN DEFAULT FALSE,
                agente_retencion_iva BOOLEAN DEFAULT FALSE,
                agente_retencion_fuente BOOLEAN DEFAULT FALSE,
                
                -- RÉGIMEN TRIBUTARIO
                regimen_tributario VARCHAR(50),  -- Común, Simplificado, Especial
                tipo_persona_tributaria VARCHAR(50),  -- Jurídica, Natural
                
                -- INFORMACIÓN BANCARIA
                banco_principal VARCHAR(100),
                tipo_cuenta_principal VARCHAR(50),  -- Ahorros, Corriente
                numero_cuenta_principal VARCHAR(100),
                banco_secundario VARCHAR(100),
                tipo_cuenta_secundario VARCHAR(50),
                numero_cuenta_secundario VARCHAR(100),
                
                -- OBSERVACIONES
                observaciones TEXT,
                observaciones_tributarias TEXT,
                observaciones_comerciales TEXT,
                
                -- AUDITORÍA
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario_creacion VARCHAR(100),
                usuario_actualizacion VARCHAR(100),
                
                -- CONSTRAINT ÚNICO
                CONSTRAINT uq_tercero_extendido UNIQUE (tercero_id)
            );
            
            -- Índices para mejorar consultas
            CREATE INDEX IF NOT EXISTS idx_terceros_ext_tercero ON terceros_extendidos(tercero_id);
            CREATE INDEX IF NOT EXISTS idx_terceros_ext_principal_email ON terceros_extendidos(contacto_principal_email);
            
            -- Comentarios en la tabla
            COMMENT ON TABLE terceros_extendidos IS 'Información detallada de terceros para SAGRILAFT';
            COMMENT ON COLUMN terceros_extendidos.tercero_id IS 'Relación 1:1 con tabla terceros';
            COMMENT ON COLUMN terceros_extendidos.responsable_iva IS 'Responsable de IVA régimen común';
            COMMENT ON COLUMN terceros_extendidos.gran_contribuyente_dian IS 'Gran contribuyente según DIAN';
            COMMENT ON COLUMN terceros_extendidos.gran_contribuyente_ica IS 'Gran contribuyente de ICA municipal';
            COMMENT ON COLUMN terceros_extendidos.autorretenedor IS 'Autorretenedor en la fuente';
            """
            
            print("🔧 Ejecutando migración...")
            db.session.execute(text(sql_crear_tabla))
            db.session.commit()
            
            print("✅ Tabla terceros_extendidos creada exitosamente\n")
            
            # Verificar estructura
            result = db.session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name='terceros_extendidos' 
                ORDER BY ordinal_position
            """))
            
            print("📋 ESTRUCTURA DE LA TABLA:\n")
            for row in result:
                print(f"   • {row[0]:<40} {row[1]}")
            
            print("\n" + "="*70)
            print("✅ MIGRACIÓN COMPLETADA")
            print("="*70)
            
            print("\n📝 CAMPOS CREADOS:")
            print("   • 4 contactos completos (tesorería, contabilidad, principal, secundario)")
            print("   • 3 actividades económicas + códigos CIIU")
            print("   • 8 responsabilidades tributarias")
            print("   • 2 cuentas bancarias")
            print("   • 3 campos de observaciones")
            print("   • Auditoría completa\n")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {e}\n")
            return False

if __name__ == '__main__':
    success = crear_terceros_extendidos()
    exit(0 if success else 1)
