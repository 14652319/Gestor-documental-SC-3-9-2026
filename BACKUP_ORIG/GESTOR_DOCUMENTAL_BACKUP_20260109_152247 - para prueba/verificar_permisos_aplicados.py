"""
Verificar que los permisos se aplicaron correctamente
"""
from sqlalchemy import text
from app import app, db

def verificar_permisos():
    with app.app_context():
        print("\n" + "="*80)
        print("🔍 VERIFICACIÓN DE PERMISOS APLICADOS")
        print("="*80)
        
        # 1. Contar permisos totales
        result = db.session.execute(text("SELECT COUNT(*) FROM catalogo_permisos WHERE activo = true"))
        total = result.scalar()
        print(f"\n✅ TOTAL DE PERMISOS ACTIVOS: {total}")
        
        # 2. Distribución por módulo
        print("\n📊 DISTRIBUCIÓN POR MÓDULO:")
        print("-" * 60)
        query = text("""
            SELECT modulo, COUNT(*) as total
            FROM catalogo_permisos
            WHERE activo = true
            GROUP BY modulo
            ORDER BY total DESC, modulo
        """)
        result = db.session.execute(query)
        for row in result:
            print(f"   {row[0]:30} {row[1]:3} permisos")
        
        # 3. Nuevos permisos por módulo clave
        print("\n🆕 NUEVOS PERMISOS AGREGADOS (muestra):")
        print("-" * 60)
        
        modulos_clave = ['core', 'configuracion', 'monitoreo', 'notas_contables', 
                        'gestion_usuarios', 'archivo_digital', 'causaciones']
        
        for modulo in modulos_clave:
            query = text("""
                SELECT accion, accion_descripcion, es_critico
                FROM catalogo_permisos
                WHERE modulo = :modulo AND activo = true
                ORDER BY accion
                LIMIT 5
            """)
            result = db.session.execute(query, {'modulo': modulo})
            permisos = result.fetchall()
            
            if permisos:
                print(f"\n   📂 {modulo.upper()}:")
                for p in permisos:
                    critico = "🔴" if p.es_critico else "  "
                    print(f"      {critico} {p.accion:30} - {p.accion_descripcion[:50]}")
        
        # 4. Verificar permisos críticos
        print("\n⚠️  PERMISOS CRÍTICOS:")
        print("-" * 60)
        query = text("""
            SELECT modulo, accion, accion_descripcion
            FROM catalogo_permisos
            WHERE activo = true AND es_critico = true
            ORDER BY modulo, accion
        """)
        result = db.session.execute(query)
        criticos = result.fetchall()
        print(f"   Total de permisos críticos: {len(criticos)}")
        
        for c in criticos[:10]:  # Mostrar primeros 10
            print(f"   🔴 {c.modulo}.{c.accion}: {c.accion_descripcion}")
        
        if len(criticos) > 10:
            print(f"   ... y {len(criticos) - 10} más")
        
        # 5. Verificar estructura para frontend
        print("\n🌐 VERIFICACIÓN FRONTEND:")
        print("-" * 60)
        
        # Simular lo que hace obtener_estructura_modulos()
        query = text("""
            SELECT DISTINCT modulo, modulo_nombre, COUNT(*) as total_acciones
            FROM catalogo_permisos
            WHERE activo = true
            GROUP BY modulo, modulo_nombre
            ORDER BY modulo
        """)
        result = db.session.execute(query)
        
        print("   Módulos disponibles para asignar en frontend:")
        for row in result:
            print(f"   ✓ {row.modulo_nombre:30} ({row.total_acciones} acciones)")
        
        # 6. Comparar con permisos asignados
        print("\n👥 PERMISOS ASIGNADOS A USUARIOS:")
        print("-" * 60)
        
        result = db.session.execute(text("SELECT COUNT(*) FROM permisos_usuarios"))
        total_asignados = result.scalar()
        
        result = db.session.execute(text("SELECT COUNT(DISTINCT usuario_id) FROM permisos_usuarios"))
        usuarios_con_permisos = result.scalar()
        
        print(f"   - Total de asignaciones: {total_asignados}")
        print(f"   - Usuarios con permisos: {usuarios_con_permisos}")
        print(f"   - Permisos en catálogo: {total}")
        print(f"   - Permisos disponibles para asignar: {total}")
        
        print("\n" + "="*80)
        print("✅ VERIFICACIÓN COMPLETADA")
        print("="*80)
        print("\n💡 SIGUIENTE PASO:")
        print("   Accede a http://localhost:8099/admin/usuarios-permisos")
        print("   y verifica que los nuevos permisos aparezcan en los dropdowns")
        print("="*80 + "\n")

if __name__ == "__main__":
    verificar_permisos()
