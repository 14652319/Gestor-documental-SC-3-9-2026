"""
Validación completa del sistema de permisos
Tabla correcta: permisos_usuarios (716 registros)
Catálogo: catalogo_permisos (171 permisos disponibles)
"""
from app import app, db
from sqlalchemy import text

# Módulos físicos existentes
MODULOS_FISICOS = [
    'admin',
    'causaciones',
    'configuracion',
    'dian_vs_erp',
    'facturas_digitales',
    'notas_contables',
    'recibir_facturas',
    'relaciones',
    'terceros'
]

with app.app_context():
    print("\n" + "="*100)
    print("🔍 VALIDACIÓN COMPLETA DEL SISTEMA DE PERMISOS")
    print("="*100 + "\n")
    
    # 1. Resumen de tablas
    print("📊 PASO 1: Resumen de tablas del sistema\n")
    
    result = db.session.execute(text("SELECT COUNT(*) FROM catalogo_permisos"))
    total_catalogo = result.scalar()
    
    result = db.session.execute(text("SELECT COUNT(*) FROM permisos_usuarios"))
    total_asignados = result.scalar()
    
    result = db.session.execute(text("SELECT COUNT(DISTINCT usuario_id) FROM permisos_usuarios"))
    total_usuarios = result.scalar()
    
    print(f"   📚 catalogo_permisos:    {total_catalogo:4} permisos disponibles (catálogo maestro)")
    print(f"   👤 permisos_usuarios:    {total_asignados:4} permisos asignados a usuarios")
    print(f"   👥 Usuarios con permisos: {total_usuarios:4} usuarios diferentes")
    
    # 2. Permisos en catálogo por módulo FÍSICO
    print(f"\n📦 PASO 2: Permisos disponibles por módulo FÍSICO\n")
    
    for modulo in sorted(MODULOS_FISICOS):
        result = db.session.execute(text("""
            SELECT COUNT(*) 
            FROM catalogo_permisos 
            WHERE modulo = :modulo
        """), {"modulo": modulo})
        
        count = result.scalar()
        
        if count > 0:
            result = db.session.execute(text("""
                SELECT accion, es_critico 
                FROM catalogo_permisos 
                WHERE modulo = :modulo 
                ORDER BY accion
            """), {"modulo": modulo})
            
            permisos = result.fetchall()
            criticos = sum(1 for p in permisos if p[1])
            
            print(f"   ✅ {modulo:25} → {count:2} permisos ({criticos} críticos)")
        else:
            print(f"   ❌ {modulo:25} → SIN PERMISOS EN CATÁLOGO")
    
    # 3. Permisos asignados por módulo
    print(f"\n👤 PASO 3: Permisos asignados a usuarios por módulo\n")
    
    result = db.session.execute(text("""
        SELECT modulo, COUNT(*) as total_asignaciones
        FROM permisos_usuarios
        WHERE permitido = TRUE
        GROUP BY modulo
        ORDER BY modulo
    """))
    
    asignaciones_modulo = {}
    for row in result:
        asignaciones_modulo[row[0]] = row[1]
        print(f"   📊 {row[0]:25} → {row[1]:3} permisos asignados")
    
    # 4. Cobertura por módulo físico
    print(f"\n🎯 PASO 4: Cobertura de permisos en módulos FÍSICOS\n")
    
    for modulo in sorted(MODULOS_FISICOS):
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM catalogo_permisos WHERE modulo = :modulo
        """), {"modulo": modulo})
        disponibles = result.scalar()
        
        asignados = asignaciones_modulo.get(modulo, 0)
        
        if disponibles > 0:
            cobertura = (asignados / total_asignados * 100) if total_asignados > 0 else 0
            uso = "✅" if asignados > 0 else "⚠️ "
            print(f"   {uso} {modulo:25} → {disponibles:2} disponibles | {asignados:3} asignados ({cobertura:.1f}% del total)")
        else:
            print(f"   ❌ {modulo:25} → NO HAY PERMISOS EN CATÁLOGO")
    
    # 5. Módulos con permisos pero sin carpeta física
    print(f"\n📂 PASO 5: Módulos en catálogo SIN carpeta física\n")
    
    result = db.session.execute(text("""
        SELECT DISTINCT modulo 
        FROM catalogo_permisos 
        ORDER BY modulo
    """))
    
    modulos_catalogo = [row[0] for row in result]
    modulos_virtuales = set(modulos_catalogo) - set(MODULOS_FISICOS)
    
    if modulos_virtuales:
        for modulo in sorted(modulos_virtuales):
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM catalogo_permisos WHERE modulo = :modulo
            """), {"modulo": modulo})
            count = result.scalar()
            
            asignados = asignaciones_modulo.get(modulo, 0)
            print(f"   ℹ️  {modulo:25} → {count:2} en catálogo | {asignados:3} asignados (módulo virtual)")
    else:
        print("   ✅ No hay módulos virtuales")
    
    # 6. Permisos críticos
    print(f"\n🔴 PASO 6: Permisos CRÍTICOS del sistema\n")
    
    result = db.session.execute(text("""
        SELECT modulo, accion, accion_descripcion
        FROM catalogo_permisos
        WHERE es_critico = TRUE
        ORDER BY modulo, accion
    """))
    
    criticos_por_modulo = {}
    for row in result:
        if row[0] not in criticos_por_modulo:
            criticos_por_modulo[row[0]] = []
        criticos_por_modulo[row[0]].append((row[1], row[2]))
    
    for modulo in sorted(criticos_por_modulo.keys()):
        if modulo in MODULOS_FISICOS:
            print(f"   🔴 {modulo}:")
            for accion, desc in criticos_por_modulo[modulo]:
                print(f"      • {accion:30} → {desc[:60]}")
            print()
    
    # 7. Usuarios con más permisos
    print(f"\n👥 PASO 7: Usuarios con más permisos asignados\n")
    
    result = db.session.execute(text("""
        SELECT 
            u.id, 
            u.usuario, 
            t.razon_social,
            COUNT(*) as total_permisos
        FROM permisos_usuarios pu
        JOIN usuarios u ON pu.usuario_id = u.id
        LEFT JOIN terceros t ON u.tercero_id = t.id
        WHERE pu.permitido = TRUE
        GROUP BY u.id, u.usuario, t.razon_social
        ORDER BY total_permisos DESC
        LIMIT 10
    """))
    
    for row in result:
        razon = row[2] or 'N/A'
        print(f"   👤 {row[1]:20} | {razon[:30]:30} | {row[3]:3} permisos")
    
    # 8. Resumen final
    print(f"\n" + "="*100)
    print("📈 RESUMEN EJECUTIVO")
    print("="*100 + "\n")
    
    result = db.session.execute(text("""
        SELECT COUNT(DISTINCT modulo) FROM catalogo_permisos
    """))
    modulos_total = result.scalar()
    
    result = db.session.execute(text("""
        SELECT COUNT(*) FROM catalogo_permisos WHERE es_critico = TRUE
    """))
    total_criticos = result.scalar()
    
    modulos_fisicos_con_permisos = sum(1 for m in MODULOS_FISICOS if asignaciones_modulo.get(m, 0) > 0)
    
    print(f"   📚 Permisos en catálogo maestro:     {total_catalogo}")
    print(f"   📦 Módulos diferentes en catálogo:   {modulos_total}")
    print(f"   🔴 Permisos críticos:                {total_criticos}")
    print(f"   📂 Módulos físicos existentes:       {len(MODULOS_FISICOS)}")
    print(f"   ✅ Módulos físicos con permisos:     {modulos_fisicos_con_permisos}")
    print(f"   👤 Permisos asignados a usuarios:    {total_asignados}")
    print(f"   👥 Usuarios con permisos:            {total_usuarios}")
    
    cobertura = (modulos_fisicos_con_permisos / len(MODULOS_FISICOS) * 100)
    print(f"\n   🎯 Cobertura de módulos físicos:     {cobertura:.1f}%")
    
    if cobertura == 100:
        print("\n   ✅ ¡TODOS LOS MÓDULOS FÍSICOS TIENEN PERMISOS EN EL CATÁLOGO!")
    else:
        print(f"\n   ⚠️  Faltan permisos en {len(MODULOS_FISICOS) - modulos_fisicos_con_permisos} módulos físicos")
    
    print("\n" + "="*100 + "\n")

if __name__ == '__main__':
    pass
