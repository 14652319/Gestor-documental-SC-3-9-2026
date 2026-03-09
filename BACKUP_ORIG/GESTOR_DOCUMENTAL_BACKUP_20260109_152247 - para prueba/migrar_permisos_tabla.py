"""
Script para migrar datos únicos de permisos_usuario a permisos_usuarios
y después eliminar la tabla vieja de forma segura
"""
from app import app, db
from sqlalchemy import text

print('=' * 80)
print('🔄 MIGRACIÓN DE PERMISOS - TABLA DUPLICADA')
print('=' * 80)
print()

with app.app_context():
    try:
        # PASO 1: Identificar registros únicos
        print('📊 PASO 1: Identificando registros únicos en tabla singular...')
        
        result = db.session.execute(text("""
            SELECT usuario_id, modulo, accion, permitido, fecha_asignacion
            FROM permisos_usuario
            WHERE NOT EXISTS (
                SELECT 1 FROM permisos_usuarios 
                WHERE permisos_usuarios.usuario_id = permisos_usuario.usuario_id
                  AND permisos_usuarios.modulo = permisos_usuario.modulo
                  AND permisos_usuarios.accion = permisos_usuario.accion
            )
            ORDER BY usuario_id, modulo, accion
        """))
        
        registros_unicos = result.fetchall()
        
        print(f'✅ Encontrados {len(registros_unicos)} registros únicos')
        print()
        
        if registros_unicos:
            print('📋 Registros a migrar:')
            for r in registros_unicos[:10]:
                print(f'   • Usuario {r[0]} | {r[1]}.{r[2]} | permitido={r[3]}')
            if len(registros_unicos) > 10:
                print(f'   ... y {len(registros_unicos) - 10} más')
            print()
            
            # PASO 2: Migrar datos únicos
            print('🔄 PASO 2: Migrando registros únicos...')
            
            for registro in registros_unicos:
                usuario_id, modulo, accion, permitido, fecha_asignacion = registro
                
                db.session.execute(text("""
                    INSERT INTO permisos_usuarios 
                    (usuario_id, modulo, accion, permitido, fecha_asignacion)
                    VALUES (:uid, :mod, :acc, :perm, :fecha)
                    ON CONFLICT (usuario_id, modulo, accion) DO NOTHING
                """), {
                    'uid': usuario_id,
                    'mod': modulo,
                    'acc': accion,
                    'perm': permitido,
                    'fecha': fecha_asignacion
                })
            
            db.session.commit()
            print(f'✅ {len(registros_unicos)} registros migrados exitosamente')
            print()
        else:
            print('✅ No hay registros únicos para migrar')
            print()
        
        # PASO 3: Renombrar tabla vieja como backup
        print('🗑️  PASO 3: Renombrando tabla vieja como backup...')
        
        db.session.execute(text("""
            ALTER TABLE permisos_usuario RENAME TO permisos_usuario_backup_20251127
        """))
        db.session.commit()
        
        print('✅ Tabla renombrada a: permisos_usuario_backup_20251127')
        print()
        
        # PASO 4: Verificar resultado
        print('✅ PASO 4: Verificación final')
        
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM permisos_usuarios
        """))
        total_plural = result.fetchone()[0]
        
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM permisos_usuario_backup_20251127
        """))
        total_backup = result.fetchone()[0]
        
        print(f'   • Tabla activa (permisos_usuarios): {total_plural} registros')
        print(f'   • Tabla backup: {total_backup} registros')
        print()
        
        print('=' * 80)
        print('✅ MIGRACIÓN COMPLETADA EXITOSAMENTE')
        print('=' * 80)
        print()
        print('📝 Próximos pasos:')
        print('   1. Verificar que el sistema funciona correctamente')
        print('   2. Si todo está bien después de 1 semana:')
        print('      DROP TABLE permisos_usuario_backup_20251127;')
        print()
        
    except Exception as e:
        print(f'❌ ERROR: {e}')
        db.session.rollback()
        print()
        print('💡 La tabla original NO fue modificada')
