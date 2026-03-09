# -*- coding: utf-8 -*-
"""
Script para agregar permisos de facturas digitales a usuarios externos
"""

from app import app, db
from sqlalchemy import text

def agregar_permisos_externos():
    """Agrega permisos necesarios para usuarios externos"""
    with app.app_context():
        try:
            # Obtener todos los usuarios externos
            result = db.session.execute(text("""
                SELECT id, usuario, nit 
                FROM usuarios 
                WHERE tipo_usuario = 'externo'
            """))
            
            usuarios_externos = list(result)
            
            print(f"\n✅ Encontrados {len(usuarios_externos)} usuarios externos")
            
            for usuario_id, usuario, nit in usuarios_externos:
                print(f"\n📝 Procesando usuario: {usuario} (NIT: {nit})")
                
                # Permisos necesarios para usuarios externos
                permisos = [
                    ('facturas_digitales', 'acceder_modulo'),
                    ('facturas_digitales', 'cargar_factura'),
                    ('facturas_digitales', 'consultar_facturas'),
                ]
                
                for modulo, accion in permisos:
                    # Verificar si ya existe
                    existe = db.session.execute(text("""
                        SELECT id FROM permisos_usuarios
                        WHERE usuario_id = :usuario_id
                          AND modulo = :modulo
                          AND accion = :accion
                    """), {
                        'usuario_id': usuario_id,
                        'modulo': modulo,
                        'accion': accion
                    }).fetchone()
                    
                    if existe:
                        print(f"   ✓ Permiso ya existe: {modulo}.{accion}")
                    else:
                        # Insertar permiso
                        db.session.execute(text("""
                            INSERT INTO permisos_usuarios (usuario_id, modulo, accion, permitido)
                            VALUES (:usuario_id, :modulo, :accion, TRUE)
                        """), {
                            'usuario_id': usuario_id,
                            'modulo': modulo,
                            'accion': accion
                        })
                        print(f"   ✅ Permiso agregado: {modulo}.{accion}")
            
            db.session.commit()
            print(f"\n✨ ¡Permisos actualizados exitosamente!")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("="*70)
    print("🔐 AGREGANDO PERMISOS A USUARIOS EXTERNOS")
    print("="*70)
    agregar_permisos_externos()
