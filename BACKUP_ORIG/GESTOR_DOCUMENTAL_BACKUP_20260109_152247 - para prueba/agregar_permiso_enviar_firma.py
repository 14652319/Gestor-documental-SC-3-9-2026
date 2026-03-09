"""
Script para agregar el permiso 'enviar_a_firmar' a usuarios del módulo de facturas digitales
"""
import sys
from app import app, db
from sqlalchemy import text

def agregar_permiso_firma():
    with app.app_context():
        try:
            # Obtener todos los usuarios con permisos en facturas_digitales
            result = db.session.execute(text("""
                SELECT DISTINCT usuario_id 
                FROM permisos_usuarios 
                WHERE modulo = 'facturas_digitales'
            """)).fetchall()
            
            usuarios_con_permisos = [row[0] for row in result]
            
            if not usuarios_con_permisos:
                print("⚠️ No se encontraron usuarios con permisos en facturas_digitales")
                return
            
            print(f"📋 Encontrados {len(usuarios_con_permisos)} usuarios con permisos en facturas_digitales")
            
            # Agregar permiso 'enviar_a_firmar' a cada usuario
            permisos_agregados = 0
            for usuario_id in usuarios_con_permisos:
                # Verificar si ya tiene el permiso
                existe = db.session.execute(text("""
                    SELECT 1 FROM permisos_usuarios 
                    WHERE usuario_id = :usuario_id 
                    AND modulo = 'facturas_digitales' 
                    AND accion = 'enviar_a_firmar'
                """), {'usuario_id': usuario_id}).fetchone()
                
                if not existe:
                    # Insertar permiso
                    db.session.execute(text("""
                        INSERT INTO permisos_usuarios (usuario_id, modulo, accion, permitido)
                        VALUES (:usuario_id, 'facturas_digitales', 'enviar_a_firmar', true)
                    """), {'usuario_id': usuario_id})
                    permisos_agregados += 1
                    print(f"✅ Permiso 'enviar_a_firmar' agregado al usuario ID {usuario_id}")
                else:
                    print(f"ℹ️ Usuario ID {usuario_id} ya tiene el permiso 'enviar_a_firmar'")
            
            db.session.commit()
            
            print(f"\n✅ ¡Proceso completado!")
            print(f"📊 Total permisos agregados: {permisos_agregados}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("=" * 60)
    print("🔒 AGREGAR PERMISO 'ENVIAR_A_FIRMAR' A USUARIOS")
    print("=" * 60)
    agregar_permiso_firma()
