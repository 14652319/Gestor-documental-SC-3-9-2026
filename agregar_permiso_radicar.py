"""
Script para agregar permiso 'enviar_a_firmar' a todos los usuarios del módulo facturas_digitales
"""
from app import app, db
from sqlalchemy import text

def agregar_permiso_radicar():
    with app.app_context():
        print("🔧 Agregando permiso 'enviar_a_firmar' para facturas_digitales...")
        
        # Obtener todos los usuarios
        usuarios = db.session.execute(text("""
            SELECT id, usuario, rol 
            FROM usuarios 
            ORDER BY usuario
        """)).fetchall()
        
        print(f"✅ Encontrados {len(usuarios)} usuarios totales\n")
        
        for usuario_id, usuario, rol in usuarios:
            print(f"📝 Usuario: {usuario} (ROL: {rol})")
            
            # Verificar si ya tiene el permiso
            permiso_existe = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM permisos_usuarios 
                WHERE usuario_id = :usuario_id 
                AND modulo = 'facturas_digitales' 
                AND accion = 'enviar_a_firmar'
            """), {'usuario_id': usuario_id}).scalar()
            
            if permiso_existe > 0:
                print(f"   ✓ Ya tiene: enviar_a_firmar")
            else:
                # Insertar permiso
                db.session.execute(text("""
                    INSERT INTO permisos_usuarios (usuario_id, modulo, accion, permitido)
                    VALUES (:usuario_id, 'facturas_digitales', 'enviar_a_firmar', true)
                """), {'usuario_id': usuario_id})
                print(f"   ✅ Asignado: enviar_a_firmar")
            
            print()
        
        db.session.commit()
        print("✅ Permisos actualizados correctamente")

if __name__ == '__main__':
    agregar_permiso_radicar()
