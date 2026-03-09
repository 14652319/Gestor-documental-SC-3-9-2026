# -*- coding: utf-8 -*-
"""
Script para crear permisos del módulo Facturas Digitales
y asignarlos automáticamente a usuarios externos
"""

from app import app, db
from sqlalchemy import text

def crear_permisos_modulo():
    """Crea los permisos del módulo Facturas Digitales"""
    with app.app_context():
        try:
            print("\n" + "="*70)
            print("📋 ASIGNANDO PERMISOS DEL MÓDULO FACTURAS DIGITALES")
            print("="*70)
            
            # Definir permisos del módulo (sin crear tabla modulos)
            permisos = [
                # Permisos para TODOS los usuarios
                ('acceder_modulo', 'Acceder al módulo de Facturas Digitales', 'externo,interno,admin'),
                ('cargar_factura', 'Radicar nuevas facturas', 'externo,interno,admin'),
                ('consultar_facturas', 'Consultar facturas propias', 'externo,interno,admin'),
                ('ver_factura', 'Ver detalles de facturas', 'externo,interno,admin'),
                
                # Permisos solo para INTERNOS y ADMIN
                ('ver_dashboard', 'Ver dashboard completo', 'interno,admin'),
                ('aprobar_factura', 'Aprobar facturas de externos', 'interno,admin'),
                ('rechazar_factura', 'Rechazar facturas', 'interno,admin'),
                ('editar_factura', 'Editar datos de facturas', 'interno,admin'),
                ('eliminar_factura', 'Eliminar facturas', 'admin'),
                ('enviar_firma', 'Enviar facturas a firma', 'interno,admin'),
                ('causar_factura', 'Causar facturas', 'interno,admin'),
                ('pagar_factura', 'Registrar pago de facturas', 'interno,admin'),
                
                # Permisos de configuración (solo ADMIN)
                ('configurar_modulo', 'Configurar parámetros del módulo', 'admin'),
                ('gestionar_catalogos', 'Gestionar catálogos (empresas, tipos, etc)', 'admin'),
            ]
            
            # Asignar permisos directamente a usuarios (sin tabla permisos intermedia)
            print("\n" + "="*70)
            print("👥 ASIGNANDO PERMISOS A USUARIOS EXTERNOS")
            print("="*70)
            
            result = db.session.execute(text("""
                SELECT u.id, u.usuario, t.nit, u.tipo_usuario 
                FROM usuarios u
                LEFT JOIN terceros t ON u.tercero_id = t.id
                WHERE u.tipo_usuario = 'externo'
            """))
            
            usuarios = list(result)
            print(f"\n✅ Encontrados {len(usuarios)} usuarios externos")
            
            # Permisos para externos
            permisos_externos = [
                'acceder_modulo',
                'cargar_factura',
                'consultar_facturas',
                'ver_factura'
            ]
            
            for usuario_id, usuario, nit, tipo in usuarios:
                print(f"\n📝 Usuario: {usuario} (NIT: {nit if nit else 'N/A'})")
                
                for accion in permisos_externos:
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
                        print(f"   ✅ Permiso asignado: {accion}")
            
            # 4. Asignar TODOS los permisos a usuarios admin
            print("\n" + "="*70)
            print("👨‍💼 ASIGNANDO TODOS LOS PERMISOS A ADMINISTRADORES")
            print("="*70)
            
            result_admin = db.session.execute(text("""
                SELECT id, usuario, tipo_usuario 
                FROM usuarios 
                WHERE tipo_usuario = 'admin' OR rol = 'admin'
            """))
            
            admins = list(result_admin)
            print(f"\n✅ Encontrados {len(admins)} administradores")
            
            todas_las_acciones = [p[0] for p in permisos]
            
            for usuario_id, usuario, tipo in admins:
                print(f"\n📝 Admin: {usuario}")
                
                for accion in todas_las_acciones:
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
                        print(f"   ✅ Permiso asignado: {accion}")
            
            # 5. Asignar permisos a usuarios internos
            print("\n" + "="*70)
            print("👔 ASIGNANDO PERMISOS A USUARIOS INTERNOS")
            print("="*70)
            
            result_interno = db.session.execute(text("""
                SELECT id, usuario 
                FROM usuarios 
                WHERE tipo_usuario = 'interno'
            """))
            
            internos = list(result_interno)
            print(f"\n✅ Encontrados {len(internos)} usuarios internos")
            
            permisos_internos = [
                'acceder_modulo', 'cargar_factura', 'consultar_facturas', 'ver_factura',
                'ver_dashboard', 'aprobar_factura', 'rechazar_factura', 'editar_factura',
                'enviar_firma', 'causar_factura', 'pagar_factura'
            ]
            
            for usuario_id, usuario in internos:
                print(f"\n📝 Interno: {usuario}")
                
                for accion in permisos_internos:
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
                        print(f"   ✅ Permiso asignado: {accion}")
            
            db.session.commit()
            
            print("\n" + "="*70)
            print("✨ ¡PERMISOS CREADOS Y ASIGNADOS EXITOSAMENTE!")
            print("="*70)
            print("\n💡 Los permisos ahora se pueden gestionar desde:")
            print("   📍 /admin/usuarios-permisos")
            print("\n📋 Permisos creados:")
            for accion, descripcion, roles in permisos:
                print(f"   • {accion}: {descripcion} ({roles})")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    crear_permisos_modulo()
