"""
Script para agregar campo radicado_rfd y tabla de consecutivos
Ejecutar con: python agregar_radicado_rfd.py
"""
from app import app, db
from sqlalchemy import text
import sys

def agregar_radicado_rfd():
    """Agrega campo radicado_rfd y tabla consecutivos_rfd"""
    
    with app.app_context():
        try:
            print("=" * 80)
            print("🔧 AGREGANDO CAMPO RADICADO_RFD Y TABLA CONSECUTIVOS")
            print("=" * 80)
            
            # 1. Crear tabla de consecutivos si no existe
            print("\n📋 Paso 1: Verificando tabla consecutivos_rfd...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS consecutivos_rfd (
                    id SERIAL PRIMARY KEY,
                    tipo VARCHAR(50) UNIQUE NOT NULL,
                    ultimo_numero INTEGER NOT NULL DEFAULT 0,
                    prefijo VARCHAR(10) DEFAULT 'RFD',
                    longitud_numero INTEGER DEFAULT 6,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            db.session.commit()
            print("   ✅ Tabla consecutivos_rfd verificada/creada")
            
            # 2. Insertar registro inicial para facturas_digitales
            print("\n📋 Paso 2: Insertando consecutivo inicial...")
            db.session.execute(text("""
                INSERT INTO consecutivos_rfd (tipo, ultimo_numero, prefijo, longitud_numero)
                VALUES ('facturas_digitales', 0, 'RFD', 6)
                ON CONFLICT (tipo) DO NOTHING;
            """))
            db.session.commit()
            print("   ✅ Consecutivo inicial creado (RFD-000001)")
            
            # 3. Agregar campo radicado_rfd a facturas_digitales
            print("\n📋 Paso 3: Agregando campo radicado_rfd...")
            try:
                db.session.execute(text("""
                    ALTER TABLE facturas_digitales 
                    ADD COLUMN IF NOT EXISTS radicado_rfd VARCHAR(20) UNIQUE;
                """))
                db.session.commit()
                print("   ✅ Campo radicado_rfd agregado")
            except Exception as e:
                if 'already exists' in str(e).lower():
                    print("   ⚠️  Campo radicado_rfd ya existe (OK)")
                else:
                    raise
            
            # 4. Crear índice para búsquedas rápidas
            print("\n📋 Paso 4: Creando índice...")
            try:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_facturas_digitales_radicado_rfd 
                    ON facturas_digitales(radicado_rfd);
                """))
                db.session.commit()
                print("   ✅ Índice creado")
            except Exception as e:
                print(f"   ⚠️  Índice ya existe (OK)")
            
            # 5. Verificar estructura final
            print("\n📋 Paso 5: Verificando estructura...")
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'facturas_digitales' 
                AND column_name = 'radicado_rfd';
            """))
            columna = result.fetchone()
            
            if columna:
                print(f"   ✅ Campo verificado: {columna[0]} ({columna[1]}) - Nullable: {columna[2]}")
            else:
                print("   ❌ Error: Campo no encontrado")
                return False
            
            # 6. Mostrar consecutivo actual
            print("\n📋 Paso 6: Estado del consecutivo...")
            result = db.session.execute(text("""
                SELECT tipo, ultimo_numero, prefijo, longitud_numero
                FROM consecutivos_rfd
                WHERE tipo = 'facturas_digitales';
            """))
            consecutivo = result.fetchone()
            
            if consecutivo:
                siguiente = consecutivo[1] + 1
                formato = f"{consecutivo[2]}-{siguiente:0{consecutivo[3]}d}"
                print(f"   ✅ Consecutivo actual: {consecutivo[1]}")
                print(f"   📝 Próximo radicado: {formato}")
            
            print("\n" + "=" * 80)
            print("✅ SISTEMA DE RADICADOS RFD INSTALADO CORRECTAMENTE")
            print("=" * 80)
            print("\n📌 Próximos pasos:")
            print("   1. El servidor se recargará automáticamente (watchdog)")
            print("   2. Las nuevas facturas recibirán radicado RFD automático")
            print("   3. Se enviará correo al usuario con el radicado")
            print()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    exito = agregar_radicado_rfd()
    sys.exit(0 if exito else 1)
