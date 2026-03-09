"""
Script para agregar soporte de envíos de supervisión general
Agrega campos necesarios para usuarios supervisores que reciben TODOS los documentos
Fecha: 28 de Diciembre de 2025
"""

from extensions import db
from app import app
from sqlalchemy import text

def agregar_campos_supervision():
    """Agregar campos para envíos de supervisión"""
    
    with app.app_context():
        try:
            print("=" * 80)
            print("AGREGANDO SOPORTE PARA ENVÍOS DE SUPERVISIÓN")
            print("=" * 80)
            
            # 1. Agregar campo es_supervision (indica si es envío general o por NIT)
            print("\n1️⃣ Agregando campo 'es_supervision'...")
            try:
                db.session.execute(text("""
                    ALTER TABLE envios_programados_dian_vs_erp 
                    ADD COLUMN IF NOT EXISTS es_supervision BOOLEAN DEFAULT FALSE
                """))
                db.session.commit()
                print("   ✅ Campo 'es_supervision' agregado")
            except Exception as e:
                print(f"   ⚠️ Campo ya existe o error: {e}")
                db.session.rollback()
            
            # 2. Agregar campo email_supervisor (destinatario principal de supervisión)
            print("\n2️⃣ Agregando campo 'email_supervisor'...")
            try:
                db.session.execute(text("""
                    ALTER TABLE envios_programados_dian_vs_erp 
                    ADD COLUMN IF NOT EXISTS email_supervisor VARCHAR(255)
                """))
                db.session.commit()
                print("   ✅ Campo 'email_supervisor' agregado (email principal del supervisor)")
            except Exception as e:
                print(f"   ⚠️ Campo ya existe o error: {e}")
                db.session.rollback()
            
            # 2B. Agregar campo nombre_supervisor
            print("\n2B️⃣ Agregando campo 'nombre_supervisor'...")
            try:
                db.session.execute(text("""
                    ALTER TABLE envios_programados_dian_vs_erp 
                    ADD COLUMN IF NOT EXISTS nombre_supervisor VARCHAR(200)
                """))
                db.session.commit()
                print("   ✅ Campo 'nombre_supervisor' agregado")
            except Exception as e:
                print(f"   ⚠️ Campo ya existe o error: {e}")
                db.session.rollback()
            
            # 2C. Agregar campo emails_cc_supervision (copias adicionales)
            print("\n2C️⃣ Agregando campo 'emails_cc_supervision'...")
            try:
                db.session.execute(text("""
                    ALTER TABLE envios_programados_dian_vs_erp 
                    ADD COLUMN IF NOT EXISTS emails_cc_supervision TEXT
                """))
                db.session.commit()
                print("   ✅ Campo 'emails_cc_supervision' agregado (emails separados por coma)")
            except Exception as e:
                print(f"   ⚠️ Campo ya existe o error: {e}")
                db.session.rollback()
            
            # 2D. Agregar campo asunto_personalizado
            print("\n2D️⃣ Agregando campo 'asunto_personalizado'...")
            try:
                db.session.execute(text("""
                    ALTER TABLE envios_programados_dian_vs_erp 
                    ADD COLUMN IF NOT EXISTS asunto_personalizado VARCHAR(255)
                """))
                db.session.commit()
                print("   ✅ Campo 'asunto_personalizado' agregado")
            except Exception as e:
                print(f"   ⚠️ Campo ya existe o error: {e}")
                db.session.rollback()
            
            # 2E. Agregar campo mensaje_adicional
            print("\n2E️⃣ Agregando campo 'mensaje_adicional'...")
            try:
                db.session.execute(text("""
                    ALTER TABLE envios_programados_dian_vs_erp 
                    ADD COLUMN IF NOT EXISTS mensaje_adicional TEXT
                """))
                db.session.commit()
                print("   ✅ Campo 'mensaje_adicional' agregado (mensaje extra en el correo)")
            except Exception as e:
                print(f"   ⚠️ Campo ya existe o error: {e}")
                db.session.rollback()
            
            # 2F. Agregar campo incluir_estadisticas
            print("\n2F️⃣ Agregando campo 'incluir_estadisticas'...")
            try:
                db.session.execute(text("""
                    ALTER TABLE envios_programados_dian_vs_erp 
                    ADD COLUMN IF NOT EXISTS incluir_estadisticas BOOLEAN DEFAULT TRUE
                """))
                db.session.commit()
                print("   ✅ Campo 'incluir_estadisticas' agregado (mostrar resumen en correo)")
            except Exception as e:
                print(f"   ⚠️ Campo ya existe o error: {e}")
                db.session.rollback()
            
            # 2G. Agregar campo incluir_conteo_envios
            print("\n2G️⃣ Agregando campo 'incluir_conteo_envios'...")
            try:
                db.session.execute(text("""
                    ALTER TABLE envios_programados_dian_vs_erp 
                    ADD COLUMN IF NOT EXISTS incluir_conteo_envios BOOLEAN DEFAULT TRUE
                """))
                db.session.commit()
                print("   ✅ Campo 'incluir_conteo_envios' agregado (mostrar cuántas veces se envió cada doc)")
            except Exception as e:
                print(f"   ⚠️ Campo ya existe o error: {e}")
                db.session.rollback()
            
            # 3. Agregar campo frecuencia_dias (para "cada X días")
            print("\n3️⃣ Agregando campo 'frecuencia_dias'...")
            try:
                db.session.execute(text("""
                    ALTER TABLE envios_programados_dian_vs_erp 
                    ADD COLUMN IF NOT EXISTS frecuencia_dias INTEGER DEFAULT 1
                """))
                db.session.commit()
                print("   ✅ Campo 'frecuencia_dias' agregado (1=diario, 7=semanal, 4=cada 4 días)")
            except Exception as e:
                print(f"   ⚠️ Campo ya existe o error: {e}")
                db.session.rollback()
            
            # 4. Crear tabla de tracking de envíos por documento
            print("\n4️⃣ Creando tabla 'tracking_envios_documentos'...")
            try:
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS tracking_envios_documentos (
                        id SERIAL PRIMARY KEY,
                        nit_emisor VARCHAR(20) NOT NULL,
                        prefijo VARCHAR(10),
                        folio VARCHAR(20) NOT NULL,
                        tipo_envio VARCHAR(50) NOT NULL,
                        configuracion_id INTEGER,
                        fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        email_destinatario VARCHAR(255),
                        estado VARCHAR(20) DEFAULT 'ENVIADO',
                        INDEX idx_documento (nit_emisor, prefijo, folio),
                        INDEX idx_tipo_envio (tipo_envio),
                        INDEX idx_fecha_envio (fecha_envio)
                    )
                """))
                db.session.commit()
                print("   ✅ Tabla 'tracking_envios_documentos' creada")
                print("      Esta tabla registra cada vez que se envía un documento")
            except Exception as e:
                print(f"   ⚠️ Tabla ya existe o error: {e}")
                db.session.rollback()
            
            # 5. Crear índices para mejor performance
            print("\n5️⃣ Creando índices adicionales...")
            try:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_maestro_estado_contable 
                    ON maestro_dian_vs_erp(estado_contable)
                """))
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_maestro_acuses 
                    ON maestro_dian_vs_erp(acuses_recibidos, acuses_requeridos)
                """))
                db.session.commit()
                print("   ✅ Índices creados para optimizar consultas")
            except Exception as e:
                print(f"   ⚠️ Índices ya existen o error: {e}")
                db.session.rollback()
            
            print("\n" + "=" * 80)
            print("✅ CONFIGURACIÓN COMPLETADA")
            print("=" * 80)
            print("\n📋 Próximos pasos:")
            print("   1. Crear configuraciones de envíos de supervisión")
            print("   2. Asignar emails de supervisores")
            print("   3. Configurar frecuencia (diario, semanal, cada 4 días)")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ ERROR GENERAL: {e}")
            db.session.rollback()

if __name__ == "__main__":
    agregar_campos_supervision()
