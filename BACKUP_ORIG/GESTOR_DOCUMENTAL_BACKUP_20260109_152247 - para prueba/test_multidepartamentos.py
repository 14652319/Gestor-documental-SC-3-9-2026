"""
Script de prueba para verificar el sistema de múltiples departamentos
"""

from app import app, db
from sqlalchemy import text

print("\n" + "="*80)
print("🧪 PRUEBA DEL SISTEMA DE MÚLTIPLES DEPARTAMENTOS")
print("="*80 + "\n")

with app.app_context():
    try:
        # 1. Verificar tabla usuario_departamento existe
        print("1️⃣ Verificando tabla 'usuario_departamento'...")
        existe = db.session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'usuario_departamento'
            )
        """)).scalar()
        
        if existe:
            print("   ✅ Tabla existe\n")
        else:
            print("   ❌ Tabla NO existe. Ejecuta: python crear_tabla_usuario_departamento.py\n")
            exit(1)
        
        # 2. Obtener un usuario de prueba
        print("2️⃣ Buscando usuario de prueba...")
        usuario = db.session.execute(text("""
            SELECT id, usuario, correo FROM usuarios WHERE activo = true LIMIT 1
        """)).fetchone()
        
        if not usuario:
            print("   ❌ No hay usuarios activos\n")
            exit(1)
        
        print(f"   ✅ Usuario encontrado: {usuario[1]} (ID: {usuario[0]})\n")
        
        # 3. Asignar 2 departamentos de prueba
        print("3️⃣ Asignando 2 departamentos al usuario...")
        
        # Departamento 1: TIC
        db.session.execute(text("""
            INSERT INTO usuario_departamento 
                (usuario_id, departamento, puede_recibir, puede_aprobar, puede_rechazar, puede_firmar, activo)
            VALUES 
                (:usuario_id, 'TIC', true, true, false, true, true)
            ON CONFLICT (usuario_id, departamento) DO UPDATE
            SET puede_recibir = EXCLUDED.puede_recibir,
                puede_aprobar = EXCLUDED.puede_aprobar,
                puede_rechazar = EXCLUDED.puede_rechazar,
                puede_firmar = EXCLUDED.puede_firmar
        """), {'usuario_id': usuario[0]})
        
        # Departamento 2: FIN
        db.session.execute(text("""
            INSERT INTO usuario_departamento 
                (usuario_id, departamento, puede_recibir, puede_aprobar, puede_rechazar, puede_firmar, activo)
            VALUES 
                (:usuario_id, 'FIN', false, true, true, true, true)
            ON CONFLICT (usuario_id, departamento) DO UPDATE
            SET puede_recibir = EXCLUDED.puede_recibir,
                puede_aprobar = EXCLUDED.puede_aprobar,
                puede_rechazar = EXCLUDED.puede_rechazar,
                puede_firmar = EXCLUDED.puede_firmar
        """), {'usuario_id': usuario[0]})
        
        db.session.commit()
        print("   ✅ Departamentos asignados: TIC, FIN\n")
        
        # 4. Consultar departamentos del usuario (query del endpoint)
        print("4️⃣ Consultando departamentos del usuario...")
        departamentos = db.session.execute(text("""
            SELECT 
                departamento,
                puede_recibir,
                puede_aprobar,
                puede_rechazar,
                puede_firmar
            FROM usuario_departamento
            WHERE usuario_id = :usuario_id AND activo = true
            ORDER BY departamento
        """), {'usuario_id': usuario[0]}).fetchall()
        
        if departamentos:
            print(f"   ✅ {len(departamentos)} departamentos encontrados:\n")
            for dept in departamentos:
                permisos = []
                if dept[1]: permisos.append('📥 Recibir')
                if dept[2]: permisos.append('✅ Aprobar')
                if dept[3]: permisos.append('❌ Rechazar')
                if dept[4]: permisos.append('✍️ Firmar')
                print(f"      🏢 {dept[0]}: {', '.join(permisos) if permisos else 'Sin permisos'}")
        
        print("\n5️⃣ Probando query de listado (endpoint GET /api/usuarios)...")
        listado = db.session.execute(text("""
            SELECT 
                u.id,
                u.usuario,
                COALESCE(u.correo, u.email_notificaciones, 'Sin correo') as email,
                STRING_AGG(DISTINCT ud.departamento, ', ' ORDER BY ud.departamento) as departamentos
            FROM usuarios u
            LEFT JOIN usuario_departamento ud ON u.id = ud.usuario_id AND ud.activo = true
            WHERE u.id = :usuario_id
            GROUP BY u.id, u.usuario, u.correo, u.email_notificaciones
        """), {'usuario_id': usuario[0]}).fetchone()
        
        print(f"   ✅ Resultado:")
        print(f"      ID: {listado[0]}")
        print(f"      Usuario: {listado[1]}")
        print(f"      Email: {listado[2]}")
        print(f"      Departamentos: {listado[3]}")
        
        print("\n" + "="*80)
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("="*80 + "\n")
        
        print("📋 Próximos pasos:")
        print("   1. Abre: http://localhost:8099/facturas-digitales/configuracion/")
        print("   2. Ve al tab '👥 Usuarios'")
        print(f"   3. Busca el usuario '{usuario[1]}'")
        print("   4. Deberías ver: 'FIN, TIC' en la columna Departamentos")
        print("   5. Click en 'Configurar' para ver los 2 departamentos con sus permisos")
        print("   6. Prueba agregar un tercer departamento (MER, DOM o MYP)")
        print("   7. Prueba eliminar un departamento")
        print("   8. Prueba cambiar permisos de un departamento\n")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error durante la prueba:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

print("="*80 + "\n")
