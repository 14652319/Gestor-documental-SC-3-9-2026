"""
Crear tabla usuarios_asignados_dian_vs_erp y agregar usuario de prueba
"""

from app import app, db
from modules.dian_vs_erp.models import UsuarioAsignadoDianVsErp

with app.app_context():
    print("\n" + "=" * 80)
    print("📋 CREANDO TABLA Y USUARIO DE PRUEBA")
    print("=" * 80)
    
    # Crear tabla
    try:
        db.create_all()
        print("✅ Tabla 'usuarios_asignados_dian_vs_erp' creada/verificada")
    except Exception as e:
        print(f"⚠️  Error creando tabla: {e}")
    
    # Verificar si ya existe el usuario
    usuario_existente = UsuarioAsignadoDianVsErp.query.filter_by(
        nit='805013653',
        correo='ricardoriascos07@gmail.com'
    ).first()
    
    if usuario_existente:
        print(f"\n✅ Usuario ya existe: {usuario_existente.correo} para NIT {usuario_existente.nit}")
        if not usuario_existente.activo:
            usuario_existente.activo = True
            db.session.commit()
            print("   ✅ Usuario activado")
    else:
        # Agregar usuario de prueba
        nuevo_usuario = UsuarioAsignadoDianVsErp(
            nit='805013653',
            correo='ricardoriascos07@gmail.com',
            nombre='Ricardo Riascos',
            activo=True,
            usuario_creacion='SYSTEM'
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        print(f"\n✅ Usuario creado:")
        print(f"   NIT: {nuevo_usuario.nit}")
        print(f"   Correo: {nuevo_usuario.correo}")
        print(f"   Nombre: {nuevo_usuario.nombre}")
        print(f"   Activo: {nuevo_usuario.activo}")
    
    # Listar todos los usuarios
    print(f"\n📋 Usuarios asignados en el sistema:")
    usuarios = UsuarioAsignadoDianVsErp.query.all()
    
    if len(usuarios) == 0:
        print("   (No hay usuarios)")
    else:
        for usuario in usuarios:
            estado = "✅ Activo" if usuario.activo else "❌ Inactivo"
            print(f"   {estado} | NIT {usuario.nit} | {usuario.correo} ({usuario.nombre or 'Sin nombre'})")
    
    print("\n" + "=" * 80)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 80)
    print("\nAhora puedes:")
    print("1. Ejecutar el envío programado desde la interfaz web")
    print("2. Verificar que el correo se envía a ricardoriascos07@gmail.com")
    print("=" * 80)
