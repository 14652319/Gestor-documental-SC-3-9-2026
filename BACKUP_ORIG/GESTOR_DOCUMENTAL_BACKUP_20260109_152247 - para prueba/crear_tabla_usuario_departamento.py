"""
Script para crear tabla usuario_departamento (relación muchos a muchos)
Permite que un usuario tenga múltiples departamentos con permisos diferentes
"""

from app import app, db
from sqlalchemy import text

print("\n" + "="*80)
print("🔧 CREANDO TABLA USUARIO_DEPARTAMENTO (MÚLTIPLES DEPARTAMENTOS POR USUARIO)")
print("="*80 + "\n")

with app.app_context():
    try:
        # 1. Verificar si la tabla ya existe
        print("1️⃣ Verificando si tabla 'usuario_departamento' existe...")
        existe = db.session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'usuario_departamento'
            )
        """)).scalar()
        
        if existe:
            print("   ⚠️ La tabla 'usuario_departamento' ya existe")
            respuesta = input("\n   ¿Deseas recrearla? (s/n): ").lower()
            if respuesta != 's':
                print("   ❌ Operación cancelada")
                exit(0)
            
            print("   🗑️ Eliminando tabla existente...")
            db.session.execute(text("DROP TABLE IF EXISTS usuario_departamento CASCADE"))
            db.session.commit()
            print("   ✅ Tabla eliminada")
        
        # 2. Crear la tabla
        print("\n2️⃣ Creando tabla 'usuario_departamento'...")
        db.session.execute(text("""
            CREATE TABLE usuario_departamento (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER NOT NULL,
                departamento VARCHAR(10) NOT NULL,
                puede_recibir BOOLEAN DEFAULT false,
                puede_aprobar BOOLEAN DEFAULT false,
                puede_rechazar BOOLEAN DEFAULT false,
                puede_firmar BOOLEAN DEFAULT false,
                activo BOOLEAN DEFAULT true,
                fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                CONSTRAINT fk_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                CONSTRAINT ck_departamento CHECK (departamento IN ('TIC', 'MER', 'FIN', 'DOM', 'MYP')),
                CONSTRAINT uk_usuario_departamento UNIQUE (usuario_id, departamento)
            )
        """))
        db.session.commit()
        print("   ✅ Tabla creada exitosamente")
        
        # 3. Crear índices
        print("\n3️⃣ Creando índices...")
        indices = [
            ("idx_usuario_departamento_usuario", "usuario_id"),
            ("idx_usuario_departamento_depto", "departamento"),
            ("idx_usuario_departamento_activo", "activo")
        ]
        
        for nombre_idx, columna in indices:
            db.session.execute(text(f"""
                CREATE INDEX IF NOT EXISTS {nombre_idx} ON usuario_departamento({columna})
            """))
            print(f"   ✅ Índice '{nombre_idx}' creado")
        
        db.session.commit()
        
        # 4. Agregar comentarios
        print("\n4️⃣ Agregando comentarios...")
        db.session.execute(text("""
            COMMENT ON TABLE usuario_departamento IS 'Relación muchos a muchos: usuarios pueden tener múltiples departamentos con permisos diferentes'
        """))
        db.session.commit()
        print("   ✅ Comentarios agregados")
        
        # 5. Migrar datos existentes de tabla usuarios (si existen)
        print("\n5️⃣ Verificando datos existentes en tabla 'usuarios'...")
        usuarios_con_depto = db.session.execute(text("""
            SELECT id, departamento, puede_recibir, puede_aprobar, puede_rechazar, puede_firmar
            FROM usuarios
            WHERE departamento IS NOT NULL AND departamento != ''
        """)).fetchall()
        
        if usuarios_con_depto:
            print(f"   ⚠️ Encontrados {len(usuarios_con_depto)} usuarios con departamento asignado")
            respuesta = input("   ¿Migrar estos datos a la nueva tabla? (s/n): ").lower()
            
            if respuesta == 's':
                print("   📦 Migrando datos...")
                for row in usuarios_con_depto:
                    db.session.execute(text("""
                        INSERT INTO usuario_departamento 
                            (usuario_id, departamento, puede_recibir, puede_aprobar, puede_rechazar, puede_firmar, activo)
                        VALUES 
                            (:usuario_id, :departamento, :puede_recibir, :puede_aprobar, :puede_rechazar, :puede_firmar, true)
                        ON CONFLICT (usuario_id, departamento) DO NOTHING
                    """), {
                        'usuario_id': row[0],
                        'departamento': row[1],
                        'puede_recibir': row[2] or False,
                        'puede_aprobar': row[3] or False,
                        'puede_rechazar': row[4] or False,
                        'puede_firmar': row[5] or False
                    })
                db.session.commit()
                print(f"   ✅ {len(usuarios_con_depto)} registros migrados")
        else:
            print("   ℹ️ No hay datos para migrar")
        
        # 6. Verificar tabla creada
        print("\n6️⃣ Verificando tabla creada...")
        columnas = db.session.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'usuario_departamento'
            ORDER BY ordinal_position
        """)).fetchall()
        
        print(f"\n   ✅ Tabla 'usuario_departamento' creada con {len(columnas)} columnas:\n")
        for col in columnas:
            print(f"      • {col[0]:20} | Tipo: {col[1]:20} | Nullable: {col[2]}")
        
        # 7. Mostrar ejemplo de uso
        print("\n" + "="*80)
        print("✅ TABLA CREADA EXITOSAMENTE")
        print("="*80 + "\n")
        
        print("📋 Ejemplo de uso: Usuario con 2 departamentos\n")
        print("   Usuario: jperez (ID: 23)")
        print("   Departamento 1: TIC")
        print("      • Puede Recibir: ✅")
        print("      • Puede Aprobar: ✅")
        print("      • Puede Rechazar: ❌")
        print("      • Puede Firmar: ✅")
        print("")
        print("   Departamento 2: FIN")
        print("      • Puede Recibir: ❌")
        print("      • Puede Aprobar: ✅")
        print("      • Puede Rechazar: ✅")
        print("      • Puede Firmar: ✅")
        print("\n   INSERT:")
        print("   INSERT INTO usuario_departamento VALUES")
        print("   (DEFAULT, 23, 'TIC', true, true, false, true, true, CURRENT_TIMESTAMP),")
        print("   (DEFAULT, 23, 'FIN', false, true, true, true, true, CURRENT_TIMESTAMP);")
        
        print("\n💡 Próximos pasos:")
        print("   1. Actualizar endpoints en config_routes.py")
        print("   2. Actualizar frontend para mostrar múltiples departamentos")
        print("   3. Modificar modal para agregar/eliminar departamentos")
        print("   4. Probar asignación de múltiples departamentos\n")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error durante la creación de tabla:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

print("="*80 + "\n")
