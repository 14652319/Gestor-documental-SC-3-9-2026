# -*- coding: utf-8 -*-
"""
Script SIMPLIFICADO para asignar permisos básicos de Facturas Digitales
a TODOS los usuarios
"""

from app import app, db
from sqlalchemy import text

def asignar_permisos_basicos():
    """Asigna permisos básicos a todos los usuarios"""
    with app.app_context():
        try:
            print("\n" + "="*70)
            print("🔐 ASIGNANDO PERMISOS BÁSICOS - FACTURAS DIGITALES")
            print("="*70)
            
            # Obtener TODOS los usuarios
            result = db.session.execute(text("""
                SELECT id, usuario, rol 
                FROM usuarios
            """))
            
            usuarios = list(result)
            print(f"\n✅ Encontrados {len(usuarios)} usuarios totales")
            
            # Permisos básicos para TODOS
            permisos_basicos = [
                'acceder_modulo',
                'cargar_factura',
                'consultar_facturas',
                'ver_factura'
            ]
            
            for usuario_id, usuario, rol in usuarios:
                print(f"\n📝 Usuario: {usuario} (ROL: {rol})")
                
                for accion in permisos_basicos:
                    # Verificar si ya tiene el permiso
                    existe = db.session.execute(text("""
                        SELECT id FROM permisos_usuarios
                        WHERE usuario_id = :usuario_id
                          AND modulo = 'facturas_digitales'
                          AND accion = :accion
                    """), {
                        'usuario_id': usuario_id,
                        'accion': accion
                    }).fetchone()
                    
                    if existe:
                        print(f"   ✓ Ya tiene: {accion}")
                    else:
                        db.session.execute(text("""
                            INSERT INTO permisos_usuarios (usuario_id, modulo, accion, permitido)
                            VALUES (:usuario_id, 'facturas_digitales', :accion, TRUE)
                        """), {
                            'usuario_id': usuario_id,
                            'accion': accion
                        })
                        print(f"   ✅ Asignado: {accion}")
            
            db.session.commit()
            
            print("\n" + "="*70)
            print("✨ ¡PERMISOS ASIGNADOS EXITOSAMENTE!")
            print("="*70)
            print("\n📋 Permisos asignados:")
            for permiso in permisos_basicos:
                print(f"   • {permiso}")
            print("\n✅ Ahora intenta acceder al módulo desde el menú")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    asignar_permisos_basicos()
