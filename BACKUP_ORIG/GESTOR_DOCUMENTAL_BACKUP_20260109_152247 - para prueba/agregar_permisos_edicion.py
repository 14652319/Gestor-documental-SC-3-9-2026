"""
Script para agregar permisos de edición de facturas
"""
from app import app, db
from sqlalchemy import text

def agregar_permisos_edicion():
    with app.app_context():
        print("🔧 Agregando permisos de edición de facturas...")
        
        # Permisos a agregar
        permisos_nuevos = [
            ('ver_detalle_factura', True),  # Para ver los datos
            ('editar_factura', True)         # Para actualizar
        ]
        
        # Obtener todos los usuarios
        usuarios = db.session.execute(text("""
            SELECT id, usuario, rol 
            FROM usuarios 
            ORDER BY usuario
        """)).fetchall()
        
        print(f"✅ Encontrados {len(usuarios)} usuarios\n")
        
        for usuario_id, usuario, rol in usuarios:
            print(f"📝 Usuario: {usuario} (ROL: {rol})")
            
            for accion, permitido in permisos_nuevos:
                # Verificar si ya tiene el permiso
                permiso_existe = db.session.execute(text("""
                    SELECT COUNT(*) 
                    FROM permisos_usuarios 
                    WHERE usuario_id = :usuario_id 
                    AND modulo = 'facturas_digitales' 
                    AND accion = :accion
                """), {'usuario_id': usuario_id, 'accion': accion}).scalar()
                
                if permiso_existe > 0:
                    print(f"   ✓ Ya tiene: {accion}")
                else:
                    # Insertar permiso
                    db.session.execute(text("""
                        INSERT INTO permisos_usuarios (usuario_id, modulo, accion, permitido)
                        VALUES (:usuario_id, 'facturas_digitales', :accion, :permitido)
                    """), {'usuario_id': usuario_id, 'accion': accion, 'permitido': permitido})
                    print(f"   ✅ Asignado: {accion}")
            
            print()
        
        db.session.commit()
        print("✅ Permisos de edición actualizados correctamente")

if __name__ == '__main__':
    agregar_permisos_edicion()
