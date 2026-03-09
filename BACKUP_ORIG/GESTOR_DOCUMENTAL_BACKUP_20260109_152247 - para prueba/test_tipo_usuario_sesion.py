"""
Script de prueba para validar corrección de tipo_usuario en sesión
Fecha: 8 de Diciembre 2025
"""

from app import app, db
from sqlalchemy import text

print("\n" + "="*80)
print("🧪 PRUEBA: Corrección tipo_usuario en sesión")
print("="*80 + "\n")

with app.app_context():
    try:
        # 1. Verificar usuarios por rol
        print("1️⃣ Verificando usuarios en base de datos...")
        
        usuarios = db.session.execute(text("""
            SELECT 
                id,
                usuario,
                rol,
                correo,
                activo,
                tercero_id
            FROM usuarios
            WHERE activo = true
            ORDER BY rol, usuario
        """)).fetchall()
        
        usuarios_por_rol = {
            'admin': [],
            'interno': [],
            'externo': [],
            'usuario': []
        }
        
        for u in usuarios:
            rol = u[2] or 'usuario'
            usuarios_por_rol[rol].append({
                'id': u[0],
                'usuario': u[1],
                'rol': rol,
                'correo': u[3],
                'tercero_id': u[5]
            })
        
        print("\n   📊 DISTRIBUCIÓN DE USUARIOS POR ROL:")
        print(f"   - Administradores: {len(usuarios_por_rol['admin'])}")
        print(f"   - Internos: {len(usuarios_por_rol['interno'])}")
        print(f"   - Externos: {len(usuarios_por_rol['externo'])}")
        print(f"   - Usuarios: {len(usuarios_por_rol['usuario'])}")
        
        # 2. Mostrar usuarios externos (los más afectados)
        if usuarios_por_rol['externo']:
            print("\n   👤 USUARIOS EXTERNOS (Afectados por el bug):")
            for u in usuarios_por_rol['externo'][:5]:  # Mostrar máximo 5
                print(f"      - {u['usuario']} ({u['correo']})")
        else:
            print("\n   ⚠️ NO hay usuarios externos en el sistema")
        
        # 3. Verificar facturas en TEMPORALES
        print("\n2️⃣ Verificando facturas en carpeta TEMPORALES...")
        
        facturas_temp = db.session.execute(text("""
            SELECT 
                id,
                numero_factura,
                nit_proveedor,
                razon_social_proveedor,
                estado,
                ruta_carpeta,
                usuario_carga,
                fecha_carga
            FROM facturas_digitales
            WHERE ruta_carpeta LIKE '%TEMPORALES%'
            ORDER BY fecha_carga DESC
            LIMIT 10
        """)).fetchall()
        
        if facturas_temp:
            print(f"\n   📄 Encontradas {len(facturas_temp)} facturas en TEMPORALES:")
            for f in facturas_temp[:5]:  # Mostrar máximo 5
                print(f"      - {f[1]} | {f[2]} | {f[4]} | {f[6]} | {f[7].strftime('%Y-%m-%d')}")
        else:
            print("\n   ✅ No hay facturas en TEMPORALES (correcto si no hay externos)")
        
        # 4. Verificar facturas pendientes de revisión
        print("\n3️⃣ Verificando facturas con estado 'pendiente_revision'...")
        
        facturas_revision = db.session.execute(text("""
            SELECT 
                COUNT(*) as total,
                estado
            FROM facturas_digitales
            WHERE estado = 'pendiente_revision'
            GROUP BY estado
        """)).fetchone()
        
        if facturas_revision:
            print(f"\n   📋 Facturas pendiente_revision: {facturas_revision[0]}")
            print("   ℹ️ Estas son facturas cargadas por usuarios EXTERNOS")
        else:
            print("\n   ✅ No hay facturas pendiente_revision")
        
        # 5. Simular cálculo de tipo_usuario
        print("\n4️⃣ Simulando cálculo de tipo_usuario...")
        
        print("\n   🔧 LÓGICA IMPLEMENTADA:")
        print("   session['tipo_usuario'] = 'externo' if user.rol == 'externo' else 'interno'")
        
        print("\n   📊 RESULTADO POR ROL:")
        for rol in ['admin', 'interno', 'externo', 'usuario']:
            tipo_usuario = 'externo' if rol == 'externo' else 'interno'
            print(f"      - rol='{rol}' → tipo_usuario='{tipo_usuario}'")
        
        # 6. Verificar estructura de carpetas
        print("\n5️⃣ Verificando estructura de carpetas esperada...")
        
        import os
        from modules.facturas_digitales.models import ConfigRutasFacturas
        
        config = ConfigRutasFacturas.query.filter_by(activa=True).first()
        if config:
            ruta_base = config.ruta_local
            print(f"\n   📁 Ruta base: {ruta_base}")
            
            # Verificar carpeta TEMPORALES
            ruta_temp = os.path.join(ruta_base, 'TEMPORALES')
            if os.path.exists(ruta_temp):
                carpetas = os.listdir(ruta_temp)
                print(f"   ✅ Carpeta TEMPORALES existe ({len(carpetas)} subcarpetas)")
                if carpetas:
                    print(f"      Ejemplo: {carpetas[0]}")
            else:
                print(f"   ℹ️ Carpeta TEMPORALES no existe (se creará cuando usuario externo cargue)")
        else:
            print("\n   ⚠️ No hay configuración de rutas activa")
        
        print("\n" + "="*80)
        print("✅ VALIDACIÓN COMPLETADA")
        print("="*80 + "\n")
        
        # Resumen de acciones
        print("📝 PRÓXIMOS PASOS:")
        print("   1. Reiniciar el servidor: python app.py")
        print("   2. Hacer logout/login con usuario externo")
        print("   3. Verificar que redirige a /mis-facturas")
        print("   4. Intentar cargar factura sin campos de interno")
        print("   5. Verificar que se guarda en TEMPORALES/")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
