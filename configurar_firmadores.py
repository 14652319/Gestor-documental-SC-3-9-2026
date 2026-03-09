"""
Script interactivo para configurar firmadores por departamento
Permite asignar usuarios como firmadores de departamentos específicos
"""

import sys
from app import app, db
from sqlalchemy import text

def listar_usuarios():
    """Lista todos los usuarios disponibles"""
    query = text("""
        SELECT 
            id,
            usuario,
            COALESCE(email_notificaciones, email, correo, 'SIN EMAIL') as email
        FROM usuarios
        WHERE activo = true
        ORDER BY usuario
    """)
    
    result = db.session.execute(query)
    usuarios = result.fetchall()
    
    if not usuarios:
        print("\n❌ No hay usuarios activos en el sistema")
        return []
    
    print("\n" + "=" * 80)
    print("👥 USUARIOS DISPONIBLES")
    print("=" * 80)
    
    for id, usuario, email in usuarios:
        print(f"   {id:3d}. {usuario:20s} | {email}")
    
    print("=" * 80)
    return usuarios

def listar_firmadores_actuales():
    """Muestra configuración actual de firmadores"""
    query = text("""
        SELECT 
            udf.id,
            u.usuario,
            udf.departamento,
            COALESCE(u.email_notificaciones, u.email, u.correo, 'SIN EMAIL') as email,
            udf.activo
        FROM usuario_departamento_firma udf
        JOIN usuarios u ON u.id = udf.usuario_id
        WHERE udf.es_firmador = true
        ORDER BY udf.departamento, u.usuario
    """)
    
    result = db.session.execute(query)
    firmadores = result.fetchall()
    
    if not firmadores:
        print("\n📋 No hay firmadores configurados actualmente")
        return
    
    print("\n" + "=" * 80)
    print("📋 FIRMADORES ACTUALES")
    print("=" * 80)
    
    depto_actual = None
    for id, usuario, depto, email, activo in firmadores:
        if depto != depto_actual:
            print(f"\n📂 {depto}:")
            depto_actual = depto
        
        estado = "✅ ACTIVO" if activo else "❌ INACTIVO"
        print(f"   {id:3d}. {usuario:20s} | {email:40s} | {estado}")
    
    print("=" * 80)

def asignar_firmador():
    """Asigna un usuario como firmador de un departamento"""
    usuarios = listar_usuarios()
    
    if not usuarios:
        return
    
    print("\n" + "=" * 80)
    print("➕ ASIGNAR NUEVO FIRMADOR")
    print("=" * 80)
    
    try:
        # Solicitar ID de usuario
        usuario_id = input("\n🔢 Ingresa el ID del usuario (o 'salir'): ").strip()
        
        if usuario_id.lower() == 'salir':
            return
        
        usuario_id = int(usuario_id)
        
        # Verificar que el usuario exista
        usuario_valido = any(u[0] == usuario_id for u in usuarios)
        if not usuario_valido:
            print(f"\n❌ El usuario con ID {usuario_id} no existe o no está activo")
            return
        
        # Mostrar departamentos disponibles
        print("\n📂 DEPARTAMENTOS DISPONIBLES:")
        departamentos = {
            '1': 'TIC',
            '2': 'MER',
            '3': 'FIN',
            '4': 'DOM',
            '5': 'MYP'
        }
        
        for key, dept in departamentos.items():
            print(f"   {key}. {dept}")
        
        depto_opcion = input("\n🔢 Selecciona el departamento (1-5): ").strip()
        
        if depto_opcion not in departamentos:
            print(f"\n❌ Opción inválida")
            return
        
        departamento = departamentos[depto_opcion]
        
        # Confirmar
        confirmacion = input(f"\n¿Asignar usuario ID {usuario_id} como firmador de {departamento}? (s/n): ").strip().lower()
        
        if confirmacion != 's':
            print("\n❌ Operación cancelada")
            return
        
        # Insertar en base de datos
        query = text("""
            INSERT INTO usuario_departamento_firma 
                (usuario_id, departamento, es_firmador, activo)
            VALUES 
                (:usuario_id, :departamento, true, true)
            ON CONFLICT (usuario_id, departamento) 
            DO UPDATE SET 
                es_firmador = true, 
                activo = true,
                fecha_asignacion = CURRENT_TIMESTAMP
        """)
        
        db.session.execute(query, {
            'usuario_id': usuario_id,
            'departamento': departamento
        })
        db.session.commit()
        
        print(f"\n✅ Usuario asignado exitosamente como firmador de {departamento}")
        
    except ValueError:
        print("\n❌ Debes ingresar un número válido")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al asignar firmador: {str(e)}")

def desactivar_firmador():
    """Desactiva un firmador existente"""
    listar_firmadores_actuales()
    
    print("\n" + "=" * 80)
    print("➖ DESACTIVAR FIRMADOR")
    print("=" * 80)
    
    try:
        id_firmador = input("\n🔢 Ingresa el ID del firmador a desactivar (o 'salir'): ").strip()
        
        if id_firmador.lower() == 'salir':
            return
        
        id_firmador = int(id_firmador)
        
        confirmacion = input(f"\n¿Desactivar firmador ID {id_firmador}? (s/n): ").strip().lower()
        
        if confirmacion != 's':
            print("\n❌ Operación cancelada")
            return
        
        query = text("""
            UPDATE usuario_departamento_firma
            SET activo = false
            WHERE id = :id
        """)
        
        result = db.session.execute(query, {'id': id_firmador})
        db.session.commit()
        
        if result.rowcount > 0:
            print(f"\n✅ Firmador ID {id_firmador} desactivado exitosamente")
        else:
            print(f"\n❌ No se encontró firmador con ID {id_firmador}")
        
    except ValueError:
        print("\n❌ Debes ingresar un número válido")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al desactivar firmador: {str(e)}")

def menu_principal():
    """Muestra el menú principal"""
    while True:
        print("\n" + "=" * 80)
        print("⚙️  CONFIGURACIÓN DE FIRMADORES POR DEPARTAMENTO")
        print("=" * 80)
        print("\n1. Ver firmadores actuales")
        print("2. Asignar nuevo firmador")
        print("3. Desactivar firmador")
        print("4. Listar usuarios disponibles")
        print("5. Salir")
        
        opcion = input("\n🔢 Selecciona una opción (1-5): ").strip()
        
        if opcion == '1':
            listar_firmadores_actuales()
        elif opcion == '2':
            asignar_firmador()
        elif opcion == '3':
            desactivar_firmador()
        elif opcion == '4':
            listar_usuarios()
        elif opcion == '5':
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("\n❌ Opción inválida")
        
        input("\nPresiona Enter para continuar...")

def verificar_tabla():
    """Verifica si la tabla existe, si no la crea"""
    try:
        query = text("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_name = 'usuario_departamento_firma'
            )
        """)
        
        result = db.session.execute(query)
        existe = result.scalar()
        
        if not existe:
            print("\n⚠️ La tabla 'usuario_departamento_firma' no existe")
            print("   Creando tabla...")
            
            create_query = text("""
                CREATE TABLE usuario_departamento_firma (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                    departamento VARCHAR(10) NOT NULL,
                    es_firmador BOOLEAN DEFAULT true,
                    activo BOOLEAN DEFAULT true,
                    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(usuario_id, departamento)
                )
            """)
            
            db.session.execute(create_query)
            db.session.commit()
            
            print("✅ Tabla creada exitosamente")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error al verificar/crear tabla: {str(e)}")
        return False

def main():
    with app.app_context():
        print("\n" + "=" * 80)
        print("🚀 CONFIGURADOR DE FIRMADORES - Gestor Documental Cañaveral")
        print("=" * 80)
        
        # Verificar que la tabla exista
        if not verificar_tabla():
            print("\n❌ No se pudo inicializar el sistema")
            return
        
        # Mostrar menú principal
        menu_principal()

if __name__ == "__main__":
    main()
