"""
Script para crear la tabla usuario_departamento_firma
Gestiona la asignación de usuarios a departamentos y sus permisos
"""

from app import app, db
from sqlalchemy import text

def crear_tabla():
    with app.app_context():
        print("\n" + "=" * 80)
        print("🔧 CREACIÓN DE TABLA: usuario_departamento_firma")
        print("=" * 80)
        
        try:
            # Leer el archivo SQL
            with open('sql/crear_tabla_usuario_departamento_firma.sql', 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Ejecutar el SQL
            print("\n📝 Ejecutando script SQL...")
            
            # Dividir por comandos (separados por ;)
            comandos = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
            
            for i, comando in enumerate(comandos, 1):
                if comando and 'CREATE' in comando.upper() or 'COMMENT' in comando.upper():
                    try:
                        db.session.execute(text(comando))
                        print(f"   ✅ Comando {i}/{len(comandos)} ejecutado")
                    except Exception as e:
                        if 'already exists' in str(e).lower():
                            print(f"   ℹ️ Comando {i}/{len(comandos)} - Ya existe")
                        else:
                            print(f"   ⚠️ Comando {i}/{len(comandos)} - {str(e)}")
            
            db.session.commit()
            print("\n✅ Tabla creada exitosamente")
            
            # Verificar que la tabla existe
            print("\n🔍 Verificando estructura de la tabla...")
            query = text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'usuario_departamento_firma'
                ORDER BY ordinal_position
            """)
            
            columnas = db.session.execute(query).fetchall()
            
            if columnas:
                print("\n📋 Columnas de la tabla:")
                for col in columnas:
                    nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                    print(f"   • {col[0]:25s} {col[1]:20s} {nullable}")
                
                print(f"\n✅ Tabla verificada: {len(columnas)} columnas creadas")
            else:
                print("\n❌ Error: La tabla no se creó correctamente")
            
            # Verificar índices
            print("\n🔍 Verificando índices...")
            query_indices = text("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'usuario_departamento_firma'
            """)
            
            indices = db.session.execute(query_indices).fetchall()
            
            if indices:
                print(f"\n📋 Índices creados: {len(indices)}")
                for idx in indices:
                    print(f"   • {idx[0]}")
            
            print("\n" + "=" * 80)
            print("✅ PROCESO COMPLETADO")
            print("=" * 80)
            print("\n💡 Próximos pasos:")
            print("   1. Accede a: http://localhost:8099/facturas-digitales/configuracion/")
            print("   2. Ve al tab 'Usuarios'")
            print("   3. Configura departamentos y permisos para cada usuario")
            print("\n📚 Permisos disponibles:")
            print("   📥 Recibir   - Puede recibir facturas y documentos digitales")
            print("   ✅ Aprobar   - Puede aprobar facturas revisadas")
            print("   ❌ Rechazar  - Puede rechazar facturas con observaciones")
            print("   ✍️ Firmar    - Puede firmar digitalmente facturas aprobadas")
            print("\n" + "=" * 80 + "\n")
            
        except FileNotFoundError:
            print("\n❌ Error: No se encontró el archivo SQL")
            print("   Ruta esperada: sql/crear_tabla_usuario_departamento_firma.sql")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al crear tabla: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    crear_tabla()
