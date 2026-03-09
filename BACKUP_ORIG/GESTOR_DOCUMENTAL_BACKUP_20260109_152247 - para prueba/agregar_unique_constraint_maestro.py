"""
Agregar constraint UNIQUE a maestro_dian_vs_erp para UPSERT
Fecha: 29 de diciembre de 2025

La constraint debe existir antes de poder usar ON CONFLICT en el UPSERT
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from sqlalchemy import create_engine, text
from app import app

print("=" * 80)
print("🔧 AGREGANDO CONSTRAINT UNIQUE PARA UPSERT")
print("=" * 80)

try:
    with app.app_context():
        database_url = app.config['SQLALCHEMY_DATABASE_URI']
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Verificar si ya existe la constraint
            print("\n🔍 Verificando si existe constraint...")
            result = conn.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'maestro_dian_vs_erp' 
                AND constraint_type = 'UNIQUE'
                AND constraint_name LIKE '%nit%prefijo%folio%'
            """))
            
            existing = result.fetchone()
            
            if existing:
                print(f"✅ Constraint ya existe: {existing[0]}")
                print("✅ No es necesario crear nueva constraint")
            else:
                print("⚠️  Constraint no existe, creando...")
                
                # Primero, eliminar duplicados si existen
                print("\n🧹 Buscando y eliminando duplicados...")
                result = conn.execute(text("""
                    SELECT nit_emisor, prefijo, folio, COUNT(*) as cantidad
                    FROM maestro_dian_vs_erp
                    GROUP BY nit_emisor, prefijo, folio
                    HAVING COUNT(*) > 1
                """))
                
                duplicados = result.fetchall()
                
                if duplicados:
                    print(f"⚠️  Encontrados {len(duplicados)} claves duplicadas")
                    print("📋 Eliminando duplicados (manteniendo el más reciente)...")
                    
                    conn.execute(text("""
                        DELETE FROM maestro_dian_vs_erp
                        WHERE id IN (
                            SELECT id
                            FROM (
                                SELECT id,
                                       ROW_NUMBER() OVER (
                                           PARTITION BY nit_emisor, prefijo, folio 
                                           ORDER BY fecha_actualizacion DESC, id DESC
                                       ) as rn
                                FROM maestro_dian_vs_erp
                            ) t
                            WHERE rn > 1
                        )
                    """))
                    conn.commit()
                    print("✅ Duplicados eliminados")
                else:
                    print("✅ No hay duplicados")
                
                # Crear constraint UNIQUE
                print("\n🔨 Creando constraint UNIQUE...")
                conn.execute(text("""
                    ALTER TABLE maestro_dian_vs_erp
                    ADD CONSTRAINT unique_nit_prefijo_folio
                    UNIQUE (nit_emisor, prefijo, folio)
                """))
                conn.commit()
                print("✅ Constraint UNIQUE creada exitosamente")
            
            # Verificar constraint
            print("\n🔍 Verificando constraint final...")
            result = conn.execute(text("""
                SELECT 
                    constraint_name,
                    constraint_type
                FROM information_schema.table_constraints 
                WHERE table_name = 'maestro_dian_vs_erp'
                AND (constraint_type = 'UNIQUE' OR constraint_type = 'PRIMARY KEY')
            """))
            
            print("\n📋 Constraints en maestro_dian_vs_erp:")
            for row in result:
                print(f"   - {row[0]}: {row[1]}")
            
            print("\n" + "=" * 80)
            print("✅ PROCESO COMPLETADO EXITOSAMENTE")
            print("=" * 80)
            print("\n💡 Ahora el UPSERT puede usar:")
            print("   ON CONFLICT (nit_emisor, prefijo, folio) DO UPDATE SET ...")
            
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
