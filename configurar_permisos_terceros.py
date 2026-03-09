"""
🔐 VERIFICAR PERMISOS DE TERCEROS
================================
Script para verificar y configurar permisos del módulo terceros
"""

from app import app, db
from sqlalchemy import text

def verificar_permisos_terceros():
    """Verificar si existen permisos para el módulo terceros"""
    print("🔍 Verificando permisos del módulo terceros...")
    
    with app.app_context():
        # Buscar permisos relacionados con terceros usando SQL directo
        result = db.session.execute(text("""
            SELECT usuario_id, modulo, accion, permitido
            FROM permisos_usuarios
            WHERE modulo = 'terceros'
        """))
        
        permisos_terceros = result.fetchall()
        
        print(f"📊 Encontrados {len(permisos_terceros)} permisos para módulo 'terceros'")
        
        for permiso in permisos_terceros:
            print(f"  - Usuario ID: {permiso.usuario_id}")
            print(f"    Módulo: {permiso.modulo}")
            print(f"    Acción: {permiso.accion}")
            print(f"    Permitido: {permiso.permitido}")
            print()
        
        if len(permisos_terceros) == 0:
            print("⚠️  No hay permisos configurados para el módulo 'terceros'")
            print("📝 Necesitamos crear permisos para que funcione el módulo")
            return False
        
        return True

def crear_permisos_admin():
    """Crear permisos de administrador para el módulo terceros"""
    print("🔧 Creando permisos de administrador para terceros...")
    
    # Usuario admin (ID=23 según los logs)
    admin_user_id = 23
    
    permisos_necesarios = [
        ('terceros', 'acceder_modulo'),
        ('terceros', 'consultar'),
        ('terceros', 'crear'),
        ('terceros', 'editar'),
        ('terceros', 'eliminar'),
        ('terceros', 'documentos'),
        ('terceros', 'configurar'),
        ('terceros', 'notificar_masivo'),
        ('terceros', 'validar'),
        ('terceros', 'obtener'),
        ('terceros', 'estadisticas')
    ]
    
    with app.app_context():
        for modulo, accion in permisos_necesarios:
            # Verificar si ya existe
            result = db.session.execute(text("""
                SELECT id FROM permisos_usuarios
                WHERE usuario_id = :usuario_id AND modulo = :modulo AND accion = :accion
            """), {
                'usuario_id': admin_user_id,
                'modulo': modulo,
                'accion': accion
            })
            
            if result.fetchone() is None:
                # Crear nuevo permiso
                db.session.execute(text("""
                    INSERT INTO permisos_usuarios (usuario_id, modulo, accion, permitido)
                    VALUES (:usuario_id, :modulo, :accion, :permitido)
                """), {
                    'usuario_id': admin_user_id,
                    'modulo': modulo,
                    'accion': accion,
                    'permitido': True
                })
                print(f"  ✅ Creado permiso: {modulo}.{accion}")
            else:
                print(f"  ⚪ Ya existe: {modulo}.{accion}")
        
        db.session.commit()
        print("💾 Permisos guardados en base de datos")

def main():
    """Función principal"""
    print("🚀 CONFIGURADOR DE PERMISOS - MÓDULO TERCEROS")
    print("=" * 50)
    
    try:
        if not verificar_permisos_terceros():
            print("\n🔧 Configurando permisos...")
            crear_permisos_admin()
            
            print("\n✅ ¡Configuración completada!")
            print("🌐 Ahora puedes acceder a:")
            print("   📊 http://localhost:8099/terceros/")
            print("   📋 http://localhost:8099/terceros/consulta")
            print("   ➕ http://localhost:8099/terceros/crear")
        else:
            print("✅ Los permisos ya están configurados")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()