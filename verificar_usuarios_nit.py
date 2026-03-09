"""
Verificar si la tabla usuarios_asignados_dian_vs_erp existe y qué datos tiene
"""

from app import app, db

with app.app_context():
    print("\n" + "=" * 80)
    print("🔍 VERIFICANDO TABLA DE USUARIOS POR NIT")
    print("=" * 80)
    
    # Verificar si la tabla existe
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tablas = inspector.get_table_names()
    
    print(f"\n📋 Buscando tabla 'usuarios_asignados_dian_vs_erp'...")
    
    if 'usuarios_asignados_dian_vs_erp' in tablas:
        print("   ✅ Tabla existe")
        
        # Consultar registros
        try:
            from modules.dian_vs_erp.models import UsuarioAsignadoDianVsErp
            usuarios = UsuarioAsignadoDianVsErp.query.all()
            
            print(f"\n📊 Registros encontrados: {len(usuarios)}")
            
            if len(usuarios) > 0:
                print("\n👥 Usuarios configurados:")
                for usuario in usuarios:
                    estado = "✅" if usuario.activo else "❌"
                    print(f"   {estado} NIT: {usuario.nit} | {usuario.nombre or 'Sin nombre'} | {usuario.correo}")
            else:
                print("\n⚠️  NO HAY USUARIOS CONFIGURADOS")
                print("\n💡 SOLUCIÓN:")
                print("   1. Ve a la pestaña 'Usuarios por NIT'")
                print("   2. Haz clic en 'Agregar Usuario'")
                print("   3. Llena los datos:")
                print("      - NIT: 805013653")
                print("      - Nombre: Ricardo Riascos")
                print("      - Correo: ricardoriascos07@gmail.com")
                print("      - Tipo: APROBADOR")
                print("   4. Marca como 'Activo'")
                print("   5. Guarda")
        except Exception as e:
            print(f"\n❌ Error consultando usuarios: {e}")
    else:
        print("   ❌ Tabla NO existe")
        print("\n💡 Creando tabla...")
        
        try:
            from modules.dian_vs_erp.models import UsuarioAsignadoDianVsErp
            db.create_all()
            print("   ✅ Tabla creada")
            
            # Agregar usuario de ejemplo
            nuevo_usuario = UsuarioAsignadoDianVsErp(
                nit='805013653',
                nombre='Ricardo Riascos',
                correo='ricardoriascos07@gmail.com',
                activo=True,
                usuario_creacion='SYSTEM'
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            print(f"\n✅ Usuario de ejemplo creado:")
            print(f"   NIT: 805013653")
            print(f"   Nombre: Ricardo Riascos")
            print(f"   Correo: ricardoriascos07@gmail.com")
        except Exception as e:
            print(f"   ❌ Error creando tabla: {e}")
    
    print("\n" + "=" * 80)
