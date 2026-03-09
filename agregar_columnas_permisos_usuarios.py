"""
Script para agregar columnas de departamento y permisos a la tabla usuarios
"""

from app import app, db
from sqlalchemy import text

def agregar_columnas():
    with app.app_context():
        print("\n" + "=" * 80)
        print("🔧 AGREGANDO COLUMNAS DE DEPARTAMENTO Y PERMISOS A TABLA USUARIOS")
        print("=" * 80)
        
        columnas_agregar = [
            ("departamento", "VARCHAR(10)", "Departamento al que pertenece"),
            ("puede_recibir", "BOOLEAN DEFAULT false", "Puede recibir facturas"),
            ("puede_aprobar", "BOOLEAN DEFAULT false", "Puede aprobar facturas"),
            ("puede_rechazar", "BOOLEAN DEFAULT false", "Puede rechazar facturas"),
            ("puede_firmar", "BOOLEAN DEFAULT false", "Puede firmar facturas")
        ]
        
        try:
            # Verificar columnas existentes
            query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'usuarios'
            """)
            
            resultado = db.session.execute(query)
            columnas_existentes = [row[0] for row in resultado]
            
            print(f"\n✅ Tabla 'usuarios' encontrada con {len(columnas_existentes)} columnas")
            
            # Agregar cada columna si no existe
            for nombre_col, tipo_col, descripcion in columnas_agregar:
                if nombre_col in columnas_existentes:
                    print(f"   ℹ️  Columna '{nombre_col}' ya existe")
                else:
                    try:
                        alter_query = text(f"ALTER TABLE usuarios ADD COLUMN {nombre_col} {tipo_col}")
                        db.session.execute(alter_query)
                        db.session.commit()
                        print(f"   ✅ Columna '{nombre_col}' agregada ({descripcion})")
                    except Exception as e:
                        db.session.rollback()
                        print(f"   ❌ Error al agregar '{nombre_col}': {str(e)}")
            
            # Verificar columnas finales
            resultado = db.session.execute(query)
            columnas_finales = [row[0] for row in resultado]
            
            print(f"\n📋 Columnas actuales en tabla 'usuarios': {len(columnas_finales)}")
            
            # Mostrar columnas relacionadas con permisos
            print("\n🔐 Columnas de permisos:")
            for col in ['departamento', 'puede_recibir', 'puede_aprobar', 'puede_rechazar', 'puede_firmar']:
                if col in columnas_finales:
                    print(f"   ✅ {col}")
                else:
                    print(f"   ❌ {col} (NO EXISTE)")
            
            print("\n" + "=" * 80)
            print("✅ PROCESO COMPLETADO")
            print("=" * 80)
            print("\n💡 Próximos pasos:")
            print("   1. Refresca la página: http://localhost:8099/facturas-digitales/configuracion/")
            print("   2. Ve al tab 'Usuarios'")
            print("   3. Deberías ver todos los usuarios de la tabla")
            print("   4. Click en 'Configurar' para asignar departamento y permisos")
            print("\n" + "=" * 80 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    agregar_columnas()
