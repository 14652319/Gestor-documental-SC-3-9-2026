"""
Script de verificación del módulo de usuarios
Verifica que las columnas se agregaron correctamente y muestra datos de prueba
"""

from app import app, db
from sqlalchemy import text

print("\n" + "="*80)
print("🔍 VERIFICACIÓN DEL MÓDULO DE USUARIOS")
print("="*80 + "\n")

with app.app_context():
    try:
        # 1. Verificar columnas en tabla usuarios
        print("1️⃣ Verificando columnas en tabla 'usuarios'...")
        columnas = db.session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'usuarios'
            AND column_name IN ('departamento', 'puede_recibir', 'puede_aprobar', 'puede_rechazar', 'puede_firmar')
            ORDER BY ordinal_position
        """)).fetchall()
        
        if columnas:
            print(f"   ✅ {len(columnas)} columnas de permisos encontradas:\n")
            for col in columnas:
                print(f"      • {col[0]:20} | Tipo: {col[1]:20} | Nullable: {col[2]:5} | Default: {col[3]}")
        else:
            print("   ❌ No se encontraron las columnas de permisos")
            exit(1)
        
        # 2. Contar usuarios activos
        print("\n2️⃣ Contando usuarios activos...")
        total = db.session.execute(text("SELECT COUNT(*) FROM usuarios WHERE activo = true")).scalar()
        print(f"   ✅ {total} usuarios activos en el sistema")
        
        # 3. Mostrar usuarios con sus permisos actuales
        print("\n3️⃣ Usuarios y sus configuraciones actuales:")
        usuarios = db.session.execute(text("""
            SELECT 
                id,
                usuario,
                COALESCE(correo, email_notificaciones, 'Sin correo') as email,
                COALESCE(departamento, 'Sin asignar') as departamento,
                COALESCE(puede_recibir, false) as puede_recibir,
                COALESCE(puede_aprobar, false) as puede_aprobar,
                COALESCE(puede_rechazar, false) as puede_rechazar,
                COALESCE(puede_firmar, false) as puede_firmar
            FROM usuarios
            WHERE activo = true
            ORDER BY usuario
            LIMIT 10
        """)).fetchall()
        
        if usuarios:
            print(f"\n   Mostrando primeros {len(usuarios)} usuarios:\n")
            print(f"   {'ID':<6} {'Usuario':<20} {'Email':<30} {'Depto':<8} {'Permisos'}")
            print("   " + "-"*100)
            for u in usuarios:
                permisos = []
                if u[4]: permisos.append('📥Rec')
                if u[5]: permisos.append('✅Apr')
                if u[6]: permisos.append('❌Rech')
                if u[7]: permisos.append('✍️Firma')
                permisos_str = ' '.join(permisos) if permisos else 'Sin permisos'
                
                print(f"   {u[0]:<6} {u[1]:<20} {u[2]:<30} {u[3]:<8} {permisos_str}")
        else:
            print("   ⚠️ No hay usuarios activos")
        
        # 4. Test de query que usa el endpoint
        print("\n4️⃣ Probando query del endpoint GET /api/usuarios...")
        try:
            query = text("""
                SELECT 
                    id,
                    usuario,
                    COALESCE(correo, email_notificaciones, 'Sin correo') as email,
                    COALESCE(departamento, 'Sin asignar') as departamento,
                    COALESCE(puede_recibir, false) as puede_recibir,
                    COALESCE(puede_aprobar, false) as puede_aprobar,
                    COALESCE(puede_rechazar, false) as puede_rechazar,
                    COALESCE(puede_firmar, false) as puede_firmar
                FROM usuarios
                WHERE activo = true
                ORDER BY usuario
            """)
            resultado = db.session.execute(query).fetchall()
            print(f"   ✅ Query ejecutada exitosamente: {len(resultado)} registros")
        except Exception as e:
            print(f"   ❌ Error en query: {str(e)}")
            exit(1)
        
        # 5. Mostrar próximos pasos
        print("\n" + "="*80)
        print("✅ VERIFICACIÓN COMPLETADA - TODO ESTÁ LISTO")
        print("="*80 + "\n")
        
        print("📋 Próximos pasos:")
        print("   1. Abre tu navegador en: http://localhost:8099/facturas-digitales/configuracion/")
        print("   2. Ve al tab '👥 Usuarios'")
        print("   3. Deberías ver la lista completa de usuarios")
        print("   4. Click en 'Configurar' en cualquier usuario")
        print("   5. Asigna departamento (TIC, MER, FIN, DOM, MYP)")
        print("   6. Marca los permisos que desees (Recibir, Aprobar, Rechazar, Firmar)")
        print("   7. Guarda los cambios")
        print("   8. Verifica que los cambios se reflejan en la tabla\n")
        
        print("💡 Sugerencias:")
        print("   • El campo 'departamento' acepta valores: TIC, MER, FIN, DOM, MYP")
        print("   • Por defecto todos los usuarios tienen permisos en 'false'")
        print("   • Los cambios se guardan inmediatamente al confirmar")
        print("   • Puedes cambiar la configuración en cualquier momento\n")
        
    except Exception as e:
        print(f"\n❌ Error durante la verificación:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

print("="*80 + "\n")
