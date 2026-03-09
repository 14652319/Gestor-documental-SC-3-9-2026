"""
Script para agregar campos de firmador/aprobador a la tabla usuarios
"""
import sys
from app import app, db
from sqlalchemy import text

def agregar_campos_firmadores():
    with app.app_context():
        try:
            print("=" * 70)
            print("🔧 AGREGAR CAMPOS FIRMADOR/APROBADOR A TABLA USUARIOS")
            print("=" * 70)
            
            # 1. Agregar columnas si no existen
            print("\n📋 Verificando columnas...")
            
            columnas_a_agregar = [
                ("es_firmador", "BOOLEAN DEFAULT FALSE"),
                ("es_aprobador", "BOOLEAN DEFAULT FALSE"),
                ("departamentos_firma", "TEXT"),  # JSON array con departamentos que puede firmar
                ("departamentos_aprueba", "TEXT"),  # JSON array con departamentos que puede aprobar
                ("email_notificaciones", "VARCHAR(255)"),  # Email específico para notificaciones (opcional)
            ]
            
            for columna, tipo in columnas_a_agregar:
                # Verificar si la columna existe
                existe = db.session.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'usuarios' 
                    AND column_name = '{columna}'
                """)).fetchone()
                
                if not existe:
                    print(f"➕ Agregando columna: {columna} ({tipo})")
                    db.session.execute(text(f"""
                        ALTER TABLE usuarios 
                        ADD COLUMN {columna} {tipo}
                    """))
                    print(f"   ✅ Columna '{columna}' agregada exitosamente")
                else:
                    print(f"   ℹ️ Columna '{columna}' ya existe")
            
            db.session.commit()
            
            # 2. Crear tabla de relación usuarios_departamentos_firma (alternativa más estructurada)
            print("\n📋 Creando tabla de relación usuarios_departamentos...")
            
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS usuarios_departamentos_firma (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                    departamento VARCHAR(50) NOT NULL,  -- TIC, MER, MYP, DOM, FIN
                    es_firmador BOOLEAN DEFAULT TRUE,
                    es_aprobador BOOLEAN DEFAULT FALSE,
                    orden_firma INTEGER DEFAULT 1,  -- Para múltiples firmadores en orden
                    fecha_asignacion TIMESTAMP DEFAULT NOW(),
                    activo BOOLEAN DEFAULT TRUE,
                    UNIQUE(usuario_id, departamento)
                )
            """))
            
            print("✅ Tabla 'usuarios_departamentos_firma' creada")
            
            # 3. Crear índices para optimizar consultas
            print("\n📋 Creando índices...")
            
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_usuarios_firmador 
                ON usuarios(es_firmador) WHERE es_firmador = TRUE
            """))
            
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_usuarios_departamentos_firma_activo 
                ON usuarios_departamentos_firma(departamento, activo) 
                WHERE activo = TRUE
            """))
            
            print("✅ Índices creados")
            
            db.session.commit()
            
            print("\n" + "=" * 70)
            print("✅ ¡PROCESO COMPLETADO EXITOSAMENTE!")
            print("=" * 70)
            print("\n📊 Resumen:")
            print("   ✅ Columnas agregadas a tabla 'usuarios'")
            print("   ✅ Tabla 'usuarios_departamentos_firma' creada")
            print("   ✅ Índices creados para optimización")
            print("\n💡 Próximos pasos:")
            print("   1. Ejecutar: python asignar_firmadores_departamentos.py")
            print("   2. Configurar firmadores desde el módulo de administración")
            print()
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    agregar_campos_firmadores()
