# -*- coding: utf-8 -*-
"""
Script para agregar permisos adicionales de validación
"""

from app import app, db
from sqlalchemy import text

def agregar_permisos_validacion():
    """Agrega permisos de validación faltantes"""
    with app.app_context():
        try:
            print("\n" + "="*70)
            print("🔐 AGREGANDO PERMISOS DE VALIDACIÓN")
            print("="*70)
            
            # Obtener TODOS los usuarios
            result = db.session.execute(text("""
                SELECT id, usuario, rol 
                FROM usuarios
            """))
            
            usuarios = list(result)
            print(f"\n✅ Encontrados {len(usuarios)} usuarios")
            
            # Permisos adicionales necesarios
            permisos_adicionales = [
                'validar_tercero',
                'buscar_tercero'
            ]
            
            for usuario_id, usuario, rol in usuarios:
                print(f"\n📝 Usuario: {usuario}")
                
                for accion in permisos_adicionales:
                    existe = db.session.execute(text("""
                        SELECT id FROM permisos_usuarios
                        WHERE usuario_id = :usuario_id
                          AND modulo = 'facturas_digitales'
                          AND accion = :accion
                    """), {
                        'usuario_id': usuario_id,
                        'accion': accion
                    }).fetchone()
                    
                    if not existe:
                        db.session.execute(text("""
                            INSERT INTO permisos_usuarios (usuario_id, modulo, accion, permitido)
                            VALUES (:usuario_id, 'facturas_digitales', :accion, TRUE)
                        """), {
                            'usuario_id': usuario_id,
                            'accion': accion
                        })
                        print(f"   ✅ Asignado: {accion}")
                    else:
                        print(f"   ✓ Ya tiene: {accion}")
            
            db.session.commit()
            
            print("\n" + "="*70)
            print("✨ ¡PERMISOS DE VALIDACIÓN ASIGNADOS!")
            print("="*70)
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    agregar_permisos_validacion()
